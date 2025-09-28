# tests/backend/core/test_strategy_engine.py
"""Unit tests for the StrategyEngine."""

import pandas as pd
import uuid
from pytest_mock import MockerFixture

# Importeer alle DTOs en Interfaces die we nodig hebben
from backend.dtos import (Signal, EntrySignal, RiskDefinedSignal,
                          TradePlan, TradingContext)
from backend.core.interfaces import Clock
# De motor wordt nu vanuit de backend geïmporteerd
from backend.core.strategy_engine import StrategyEngine


def test_strategy_engine_yields_correct_trade_plan(mocker: MockerFixture):
    """
    Tests that the StrategyEngine correctly processes the DTO pipeline and
    yields a final, approved TradePlan.
    """
    # Arrange (De Voorbereiding)

    # 1. Maak de "stuntman" voor de Clock aan.
    mock_clock = mocker.MagicMock(spec=Clock)
    test_time = pd.Timestamp("2023-01-01 10:00:00", tz='UTC')
    mock_clock.tick.return_value = [(test_time, pd.Series())]

    # 2. Maak de "nep-gereedschappen" (de plugins) en hun "scripts".
    corr_id = uuid.uuid4()
    signal_dto = Signal(correlation_id=corr_id, timestamp=test_time, asset="BTC/EUR", direction="long", signal_type="test_signal")
    entry_signal_dto = EntrySignal(correlation_id=corr_id, entry_time=test_time, asset="BTC/EUR", direction="long", signal_type="test_signal", entry_price=100.0)
    risk_defined_dto = RiskDefinedSignal(**entry_signal_dto.model_dump(), sl_price=95.0)
    final_trade_plan = TradePlan(**risk_defined_dto.model_dump(), position_size_asset=1.0, position_value_eur=10000.0)

    mock_signal_generator = mocker.MagicMock(process=mocker.Mock(return_value=[signal_dto]))
    mock_entry_planner = mocker.MagicMock(process=mocker.Mock(return_value=entry_signal_dto))
    mock_exit_planner = mocker.MagicMock(process=mocker.Mock(return_value=risk_defined_dto))
    mock_size_planner = mocker.MagicMock(process=mocker.Mock(return_value=final_trade_plan))
    mock_portfolio_overlay = mocker.MagicMock(process=mocker.Mock(return_value=final_trade_plan))

    # 3. Stel de kant-en-klare "gereedschapskist" samen.
    active_workers = {
        'signal_generator': [mock_signal_generator],
        'signal_refiner': [],
        'entry_planner': mock_entry_planner,
        'exit_planner': mock_exit_planner,
        'size_planner': mock_size_planner,
        'portfolio_overlay': [mock_portfolio_overlay]
    }

    # Act (De Actie)
    engine = StrategyEngine(active_workers=active_workers)
    generated_plans = list(engine.run(
        trading_context=mocker.MagicMock(spec=TradingContext),
        clock=mock_clock
    ))

    # Assert (De Controle)
    assert len(generated_plans) == 1
    assert generated_plans[0] == final_trade_plan
    mock_signal_generator.process.assert_called_once()
    mock_entry_planner.process.assert_called_once_with(signal_dto, mocker.ANY)
    mock_exit_planner.process.assert_called_once_with(entry_signal_dto, mocker.ANY)
    mock_size_planner.process.assert_called_once_with(risk_defined_dto, mocker.ANY)
    mock_portfolio_overlay.process.assert_called_once_with(final_trade_plan, mocker.ANY)
