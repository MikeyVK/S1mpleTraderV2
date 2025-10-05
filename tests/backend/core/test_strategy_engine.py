# tests/backend/core/test_strategy_engine.py
"""Unit tests for the StrategyEngine."""

import uuid
import pandas as pd
from pytest_mock import MockerFixture

from backend.dtos.pipeline.signal import Signal
from backend.dtos.pipeline.entry_signal import EntrySignal
from backend.dtos.pipeline.risk_defined_signal import RiskDefinedSignal
from backend.dtos.pipeline.trade_plan import TradePlan
from backend.dtos.pipeline.routed_trade_plan import RoutedTradePlan
from backend.dtos.state.trading_context import TradingContext
from backend.dtos.results.engine_cycle_result import EngineCycleResult
from backend.dtos.execution.execution_directive import ExecutionDirective
from backend.dtos.execution.critical_event import CriticalEvent
from backend.core.interfaces import Clock
from backend.core.strategy_engine import StrategyEngine
from backend.core.directive_flattener import DirectiveFlattener

def test_strategy_engine_yields_correct_result(mocker: MockerFixture):
    """
    Tests that the StrategyEngine correctly processes the full 9-phase pipeline
    and yields a final, complete EngineCycleResult.
    """
    # --- Arrange (De Voorbereiding) ---
    mock_clock = mocker.MagicMock(spec=Clock)
    test_time = pd.Timestamp("2023-01-01 10:00:00", tz='UTC')
    mock_clock.tick.return_value = [(test_time, pd.Series())]
    corr_id = uuid.uuid4()

    # 1. Bouw de volledige, geneste DTO-keten op
    signal_dto = Signal(correlation_id=corr_id, timestamp=test_time, asset="BTC/EUR", direction="long", signal_type="test_signal")
    entry_signal_dto = EntrySignal(correlation_id=corr_id, signal=signal_dto, entry_price=100.0)
    risk_defined_dto = RiskDefinedSignal(correlation_id=corr_id, entry_signal=entry_signal_dto, sl_price=95.0, tp_price=110.0)
    trade_plan_dto = TradePlan(correlation_id=corr_id, risk_defined_signal=risk_defined_dto, position_value_quote=10000.0, position_size_asset=1.0)
    routed_plan_dto = RoutedTradePlan(correlation_id=corr_id, trade_plan=trade_plan_dto, order_type='limit', limit_price=100.0)
    
    expected_directive = DirectiveFlattener().flatten(routed_plan_dto)

    # 2. Mocks voor elke worker, nu geconfigureerd voor de .process() methode
    # --- DE FIX: Gebruik overal .process in de mocks ---
    mock_signal_generator = mocker.MagicMock(process=mocker.Mock(return_value=[signal_dto]))
    mock_signal_refiner = mocker.MagicMock(process=mocker.Mock(return_value=signal_dto))
    mock_entry_planner = mocker.MagicMock(process=mocker.Mock(return_value=entry_signal_dto))
    mock_exit_planner = mocker.MagicMock(process=mocker.Mock(return_value=risk_defined_dto))
    mock_size_planner = mocker.MagicMock(process=mocker.Mock(return_value=trade_plan_dto))
    mock_order_router = mocker.MagicMock(process=mocker.Mock(return_value=routed_plan_dto))
    mock_event_detector = mocker.MagicMock(process=mocker.Mock(return_value=[]))

    active_workers = {
        'signal_generator': [mock_signal_generator],
        'signal_refiner': [mock_signal_refiner],
        'entry_planner': mock_entry_planner,
        'exit_planner': mock_exit_planner,
        'size_planner': mock_size_planner,
        'order_router': [mock_order_router],
        'critical_event_detector': [mock_event_detector]
    }

    # --- Act (De Actie) ---
    engine = StrategyEngine(active_workers=active_workers)
    cycle_results = list(engine.run(
        trading_context=mocker.MagicMock(spec=TradingContext),
        clock=mock_clock
    ))

    # --- Assert (De Controle) ---
    assert len(cycle_results) == 1
    result = cycle_results[0]
    
    assert isinstance(result, EngineCycleResult)
    assert len(result.execution_directives) == 1
    assert len(result.critical_events) == 0
    assert result.execution_directives[0] == expected_directive

    # Valideer dat de correcte methodes zijn aangeroepen
    mock_signal_generator.process.assert_called_once()
    mock_signal_refiner.process.assert_called_once_with(signal_dto, mocker.ANY)
    mock_entry_planner.process.assert_called_once_with(signal_dto, mocker.ANY)
    mock_exit_planner.process.assert_called_once_with(entry_signal_dto, mocker.ANY)
    mock_size_planner.process.assert_called_once_with(risk_defined_dto, mocker.ANY)
    mock_order_router.process.assert_called_once_with(trade_plan_dto, mocker.ANY)
    mock_event_detector.process.assert_called_once()
