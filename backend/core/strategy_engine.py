# services/strategy_engine.py
"""
Contains the StrategyEngine, the core component for executing the
signal-driven phases (3-6) of the trading strategy pipeline.

@layer: Service
@dependencies:
    - backend.core.interfaces: For adhering to the Environment contract.
    - backend.dtos: For processing the DTO chain (Signal to TradePlan).
@responsibilities:
    - Orchestrates the event-driven loop, timed by the Environment's Clock.
    - Manages the DTO dataflow from Signal generation to final TradePlan.
    - Operates on a pre-built toolbox of worker instances for max performance.
    - Submits approved TradePlans to the ExecutionHandler.
"""
from typing import Dict, List, Any, Generator

from backend.core.interfaces import Clock, BaseStrategyEngine
from backend.dtos import (TradingContext, Signal, EntrySignal,
                          RiskDefinedSignal, TradePlan)


class StrategyEngine(BaseStrategyEngine):
    """
    The engine that orchestrates the signal-driven workflow (Fase 3-6).

    This service acts as the "regisseur" for the core trading logic. It is
    designed as a high-performance, immutable motor. It receives a complete,
    pre-built "toolbox" of all necessary plugin workers during initialization.
    Its sole responsibility is to iterate through time (driven by the
    Environment's Clock) and efficiently process the DTO pipeline.
    """

    def __init__(self, active_workers: Dict[str, Any]):
        """Initializes the StrategyEngine with a pre-built set of workers.

        Args:
            active_workers (Dict[str, Any]): A dictionary containing all the
                pre-instantiated and validated plugin workers for this run.
                This toolbox is prepared by a higher-level service (e.g.,
                BacktestService) and makes the engine itself stateless and
                highly performant.
        """
        super().__init__(active_workers=active_workers)

        # Haal de specialisten één keer op uit de gereedschapskist en sla ze op.
        # Dit is de kern van het "bouw één keer, gebruik vaak" principe.
        self._signal_generators = active_workers.get('signal_generator', [])
        self._signal_refiners = active_workers.get('signal_refiner', [])
        self._entry_planner = active_workers.get('entry_planner')
        self._exit_planner = active_workers.get('exit_planner')
        self._size_planner = active_workers.get('size_planner')
        self._portfolio_overlays = active_workers.get('portfolio_overlay', [])

    def run(self, trading_context: TradingContext, clock: Clock) -> Generator[TradePlan,
                                                                              None, None]:
        """
        Starts the main event loop and yields approved TradePlans.

        Args:
            trading_context (TradingContext): The shared context object.
            clock (Clock): The clock that controls the flow of time.

        Yields:
            TradePlan: A fully validated and approved trade plan, ready for execution.
        """
        for _timestamp, _row in clock.tick():
            raw_signals: List[Signal] = []
            for generator in self._signal_generators:
                raw_signals.extend(generator.process(context=trading_context))

            for signal in raw_signals:
                # CORRECTIE: Vang het resultaat van de sub-proces op.
                final_plan = self._process_single_signal(signal, trading_context)
                # Als er een geldig plan is, 'yield' het dan naar de aanroeper.
                if final_plan:
                    yield final_plan

    def _process_single_signal(
        self,
        signal: Signal,
        context: TradingContext,
    ) -> TradePlan | None:
        """Leidt één enkel signaal door de resterende fasen van de trechter."""

        # Fase 4: Signaal Verfijning
        approved_signal: Signal | None = signal
        for refiner in self._signal_refiners:
            if approved_signal is None:
                break
            approved_signal = refiner.process(approved_signal, context)

        if approved_signal is None:
            return  # Signaal is afgekeurd in de verfijningsfase.

        # Fase 5a: Entry Planning
        if not self._entry_planner:
            return
        entry_signal: EntrySignal | None
        entry_signal = self._entry_planner.process(approved_signal, context)

        if entry_signal is None:
            return

        # Fase 5b: Exit Planning
        if not self._exit_planner:
            return
        risk_defined_signal: RiskDefinedSignal | None
        risk_defined_signal = self._exit_planner.process(entry_signal, context)

        if risk_defined_signal is None:
            return

        # Fase 5c: Size Planning
        if not self._size_planner:
            return
        trade_plan: TradePlan | None
        trade_plan = self._size_planner.process(risk_defined_signal, context)

        if trade_plan is None:
            return

        # Fase 6: Portfolio Overlay
        approved_trade_plan = trade_plan
        for overlay in self._portfolio_overlays:
            if approved_trade_plan is None:
                break
            approved_trade_plan = overlay.process(approved_trade_plan, context)

        if approved_trade_plan:
            return approved_trade_plan

        return None
