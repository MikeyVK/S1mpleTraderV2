# tests/backend/core/test_portfolio.py
import pytest
import uuid
import pandas as pd

from backend.core.interfaces.portfolio import Tradable
from backend.core.portfolio import Portfolio
from backend.dtos.trade_plan import TradePlan

class MockLogger:
    def info(self, *args, **kwargs): pass
    def trade(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass

class MockContextRecorder:
    def add_data(self, *args, **kwargs): pass

@pytest.fixture
def empty_portfolio() -> Portfolio:
    return Portfolio(
        initial_capital=10000.0, fees_pct=0.001,
        logger=MockLogger(), context_recorder=MockContextRecorder()
    )

@pytest.fixture
def sample_trade_plan() -> TradePlan:
    return TradePlan(
        correlation_id=uuid.uuid4(), signal_type='TEST_SIGNAL_LONG',
        entry_time=pd.to_datetime("2023-01-01 10:00:00"), asset="BTC/EUR",
        direction='long', entry_price=20000.0, sl_price=19800.0,
        tp_price=20400.0, position_value_eur=1000.0, position_size_asset=0.05
    )

# --- Test Cases ---

def test_portfolio_fulfills_tradable_contract(empty_portfolio: Portfolio):
    assert isinstance(empty_portfolio, Tradable)

def test_portfolio_initialization(empty_portfolio: Portfolio):
    assert empty_portfolio.balance == 10000.0
    assert empty_portfolio.initial_capital == 10000.0
    # FIX: Controleer of de dictionary leeg is
    assert not empty_portfolio.active_trades
    # FIX: Verwijzing naar .trades moet nu .closed_trades zijn
    assert len(empty_portfolio.closed_trades) == 0

def test_open_trade_success(empty_portfolio: Portfolio, sample_trade_plan: TradePlan):
    empty_portfolio.open_trade(sample_trade_plan)
    # FIX: Controleer de nieuwe property 'active_trades'
    assert len(empty_portfolio.active_trades) == 1
    active_trade_data = empty_portfolio.active_trades[sample_trade_plan.correlation_id]
    assert active_trade_data['direction'] == 'long'
    assert active_trade_data['entry_price'] == 20000.0
    assert active_trade_data['position_size_asset'] == 0.05

def test_open_multiple_trades_on_different_assets(empty_portfolio: Portfolio, sample_trade_plan: TradePlan):
    eth_trade_plan = TradePlan(
        correlation_id=uuid.uuid4(), signal_type='TEST_SIGNAL_ETH_LONG',
        entry_time=pd.to_datetime("2023-01-01 11:00:00"), asset="ETH/EUR",
        direction='long', entry_price=1500.0, sl_price=1480.0, tp_price=1550.0,
        position_value_eur=500.0, position_size_asset=0.33
    )
    empty_portfolio.open_trade(sample_trade_plan)
    empty_portfolio.open_trade(eth_trade_plan)
    
    active_trades_dict = empty_portfolio.active_trades
    assert len(active_trades_dict) == 2
    assert sample_trade_plan.correlation_id in active_trades_dict
    assert eth_trade_plan.correlation_id in active_trades_dict

def test_process_candle_closes_long_trade_on_stop_loss(empty_portfolio: Portfolio, sample_trade_plan: TradePlan):
    empty_portfolio.open_trade(sample_trade_plan)
    assert empty_portfolio.active_trade_count == 1

    # FIX: De candle moet een 'name' hebben die de timestamp vertegenwoordigt.
    candle_timestamp = pd.to_datetime("2023-01-01 11:00:00")
    killer_candle = pd.Series({
        "open": 19900.0, "high": 19950.0,
        "low": 19800.0, "close": 19850.0
    }, name=candle_timestamp)

    empty_portfolio.process_candle(killer_candle)

    assert empty_portfolio.active_trade_count == 0
    assert len(empty_portfolio.closed_trades) == 1

    closed_trade = empty_portfolio.closed_trades[0]
    assert closed_trade.exit_price == 19800.0
    assert closed_trade.pnl_eur < 0

def test_process_candle_closes_long_trade_on_take_profit(empty_portfolio: Portfolio, sample_trade_plan: TradePlan):
    """
    Tests if process_candle correctly closes an active long trade when the
    high of a candle hits the take-profit price.
    """
    # Arrange: Open de trade
    empty_portfolio.open_trade(sample_trade_plan)
    assert empty_portfolio.active_trade_count == 1

    # Creëer een "profit candle" waarvan de 'high' precies de take-profit raakt
    profit_candle_timestamp = pd.to_datetime("2023-01-01 12:00:00")
    profit_candle = pd.Series({
        "open": 20200.0,
        "high": 20400.0,  # Exact de TP prijs van de sample_trade_plan
        "low": 20150.0,
        "close": 20350.0
    }, name=profit_candle_timestamp)

    # Act: Verwerk de candle
    empty_portfolio.process_candle(profit_candle)

    # Assert
    assert empty_portfolio.active_trade_count == 0, "Trade should be closed after TP hit."
    assert len(empty_portfolio.closed_trades) == 1, "There should be one closed trade."

    closed_trade = empty_portfolio.closed_trades[0]
    assert closed_trade.exit_price == 20400.0, "Exit price should be the take-profit price."
    assert closed_trade.pnl_eur > 0, "The PnL for a take-profit trade should be positive."

@pytest.fixture
def sample_short_trade_plan() -> TradePlan:
    """A fixture for a sample short trade plan."""
    return TradePlan(
        correlation_id=uuid.uuid4(),
        signal_type='TEST_SIGNAL_SHORT',
        entry_time=pd.to_datetime("2023-01-02 10:00:00"),
        asset="ETH/EUR",
        direction='short',
        entry_price=1500.0,
        sl_price=1520.0,  # Stop-loss is BOVEN de entry voor een short
        tp_price=1460.0,
        position_value_eur=1500.0,
        position_size_asset=1.0
    )

def test_process_candle_closes_short_trade_on_stop_loss(empty_portfolio: Portfolio, sample_short_trade_plan: TradePlan):
    """
    Tests if process_candle correctly closes an active short trade when the
    high of a candle hits the stop-loss price.
    """
    # Arrange: Open de short trade
    empty_portfolio.open_trade(sample_short_trade_plan)
    assert empty_portfolio.active_trade_count == 1

    # Creëer een "killer candle" waarvan de 'high' de stop-loss raakt
    killer_candle_timestamp = pd.to_datetime("2023-01-02 11:00:00")
    killer_candle = pd.Series({
        "open": 1510.0,
        "high": 1520.0,  # Exact de SL prijs
        "low": 1505.0,
        "close": 1515.0
    }, name=killer_candle_timestamp)

    # Act: Verwerk de candle
    empty_portfolio.process_candle(killer_candle)

    # Assert
    assert empty_portfolio.active_trade_count == 0, "Short trade should be closed after SL hit."
    assert len(empty_portfolio.closed_trades) == 1, "There should be one closed trade."

    closed_trade = empty_portfolio.closed_trades[0]
    assert closed_trade.exit_price == 1520.0, "Exit price should be the stop-loss price."
    assert closed_trade.pnl_eur < 0, "PnL for a stopped-out short trade should be negative."

def test_process_candle_closes_short_trade_on_take_profit(empty_portfolio: Portfolio, sample_short_trade_plan: TradePlan):
    """
    Tests if process_candle correctly closes an active short trade when the
    low of a candle hits the take-profit price.
    """
    # Arrange: Open de short trade
    empty_portfolio.open_trade(sample_short_trade_plan)
    assert empty_portfolio.active_trade_count == 1

    # Creëer een "profit candle" waarvan de 'low' de take-profit raakt
    profit_candle_timestamp = pd.to_datetime("2023-01-02 12:00:00")
    profit_candle = pd.Series({
        "open": 1470.0,
        "high": 1475.0,
        "low": 1460.0,  # Exact de TP prijs
        "close": 1465.0
    }, name=profit_candle_timestamp)

    # Act: Verwerk de candle
    empty_portfolio.process_candle(profit_candle)

    # Assert
    assert empty_portfolio.active_trade_count == 0, "Short trade should be closed after TP hit."
    assert len(empty_portfolio.closed_trades) == 1, "There should be one closed trade."

    closed_trade = empty_portfolio.closed_trades[0]
    assert closed_trade.exit_price == 1460.0, "Exit price should be the take-profit price."
    assert closed_trade.pnl_eur > 0, "PnL for a take-profit short trade should be positive."
