# backend/core/strategy_engine.py
"""
Contains the StrategyEngine, the core component for executing the
signal-driven phases (3-9) of the trading strategy pipeline.

@layer: Backend (Core)
@dependencies:
    - backend.core.interfaces: For adhering to the Environment contract.
    - backend.dtos: For processing the DTO chain.
    - .directive_flattener: To flatten the final trade plan.
@responsibilities:
    - Orchestrates the event-driven loop, timed by the Environment's Clock.
    - Manages the DTO dataflow from Signal generation to final RoutedTradePlan.
    - Flattens approved plans into ExecutionDirectives.
    - Detects critical system-wide events.
    - Bundles all results into a final EngineCycleResult for each tick.
"""
from typing import Dict, List, Any, Generator

from backend.core.interfaces import (
    Clock, BaseStrategyEngine, SignalGenerator, SignalRefiner, EntryPlanner,
    ExitPlanner, SizePlanner, OrderRouter, CriticalEventDetector
)
from backend.dtos.state.trading_context import TradingContext
from backend.dtos.pipeline.signal import Signal
from backend.dtos.pipeline.routed_trade_plan import RoutedTradePlan
from backend.dtos.results.engine_cycle_result import EngineCycleResult
from backend.dtos.execution.critical_event import CriticalEvent
from .directive_flattener import DirectiveFlattener


class StrategyEngine(BaseStrategyEngine):
    """
    The engine that orchestrates the signal-driven workflow (Fase 3-9).
    """

    def __init__(self, active_workers: Dict[str, Any]):
        """Initializes the StrategyEngine with a pre-built set of workers."""
        super().__init__(active_workers=active_workers)

        self._signal_generators: List[SignalGenerator] = active_workers.get('signal_generator', [])
        self._signal_refiners: List[SignalRefiner] = active_workers.get('signal_refiner', [])
        self._entry_planner: EntryPlanner | None = active_workers.get('entry_planner')
        self._exit_planner: ExitPlanner | None = active_workers.get('exit_planner')
        self._size_planner: SizePlanner | None = active_workers.get('size_planner')
        self._order_routers: List[OrderRouter] = active_workers.get('order_router', [])
        self._critical_event_detectors: List[CriticalEventDetector] = active_workers.get(
            'critical_event_detector', []
        )
        self._flattener = DirectiveFlattener()

    def run(self,
            trading_context: TradingContext,
            clock: Clock) -> Generator[EngineCycleResult, None, None]:
        """
        Starts the main event loop and yields a complete result for each cycle.
        """
        for _timestamp, _row in clock.tick():
            final_routed_plans: List[RoutedTradePlan] = []

            raw_signals: List[Signal] = []
            for generator in self._signal_generators:
                raw_signals.extend(generator.process(context=trading_context))

            for signal in raw_signals:
                routed_plan = self._process_single_signal(signal, trading_context)
                if routed_plan:
                    final_routed_plans.append(routed_plan)

            directives = [self._flattener.flatten(plan) for plan in final_routed_plans]

            events: List[CriticalEvent] = []
            for detector in self._critical_event_detectors:
                events.extend(detector.process(final_routed_plans, trading_context))

            yield EngineCycleResult(
                execution_directives=directives,
                critical_events=events
            )

    def _process_single_signal(
        self, signal: Signal, context: TradingContext
    ) -> RoutedTradePlan | None:
        """Leidt één enkel signaal door de trechter van Fase 4 tot 8."""

        approved_signal: Signal | None = signal
        for refiner in self._signal_refiners:
            if not (approved_signal := refiner.process(approved_signal, context)):
                return None

        if not self._entry_planner:
            return None
        if not (entry_signal := self._entry_planner.process(approved_signal, context)):
            return None

        if not self._exit_planner:
            return None
        if not (risk_defined_signal := self._exit_planner.process(entry_signal, context)):
            return None

        if not self._size_planner:
            return None
        if not (trade_plan := self._size_planner.process(risk_defined_signal, context)):
            return None

        final_routed_plan: RoutedTradePlan | None = None
        for router in self._order_routers:
            if final_routed_plan := router.process(trade_plan, context):
                break

        return final_routed_plan
