# tests/backend/core/test_portfolio.py
import pytest
import uuid
import pandas as pd

from backend.core.interfaces.portfolio import Tradable
from backend.core.portfolio import Portfolio
from backend.dtos.execution.execution_directive import ExecutionDirective

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
def sample_directive() -> ExecutionDirective:
    """A fixture for a sample long execution directive."""
    return ExecutionDirective(
        correlation_id=uuid.uuid4(),
        signal_type='TEST_SIGNAL_LONG',
        entry_time=pd.to_datetime("2023-01-01 10:00:00"),
        asset="BTC/EUR",
        direction='long',
        entry_price=20000.0,
        sl_price=19800.0,
        tp_price=20400.0,
        position_value_quote=1000.0,
        position_size_asset=0.05,
        order_type='limit'  # Toegevoegd verplicht veld
    )

@pytest.fixture
def sample_short_directive() -> ExecutionDirective:
    """A fixture for a sample short execution directive."""
    return ExecutionDirective(
        correlation_id=uuid.uuid4(),
        signal_type='TEST_SIGNAL_SHORT',
        entry_time=pd.to_datetime("2023-01-02 10:00:00"),
        asset="ETH/EUR",
        direction='short',
        entry_price=1500.0,
        sl_price=1520.0,
        tp_price=1460.0,
        position_value_quote=1500.0,
        position_size_asset=1.0,
        order_type='market' # Toegevoegd verplicht veld
    )

# --- Test Cases ---

def test_portfolio_fulfills_tradable_contract(empty_portfolio: Portfolio):
    assert isinstance(empty_portfolio, Tradable)

def test_portfolio_initialization(empty_portfolio: Portfolio):
    assert empty_portfolio.balance == 10000.0
    assert empty_portfolio.initial_capital == 10000.0
    assert not empty_portfolio.active_trades
    assert len(empty_portfolio.closed_trades) == 0

def test_open_trade_success(empty_portfolio: Portfolio, sample_directive: ExecutionDirective):
    empty_portfolio.open_trade(sample_directive)
    assert len(empty_portfolio.active_trades) == 1
    active_trade_data = empty_portfolio.active_trades[sample_directive.correlation_id]
    assert active_trade_data['direction'] == 'long'
    assert active_trade_data['entry_price'] == 20000.0
    assert active_trade_data['position_size_asset'] == 0.05

def test_open_multiple_trades_on_different_assets(empty_portfolio: Portfolio, sample_directive: ExecutionDirective):
    eth_directive = sample_directive.model_copy(update={
        'correlation_id': uuid.uuid4(),
        'signal_type': 'TEST_SIGNAL_ETH_LONG',
        'entry_time': pd.to_datetime("2023-01-01 11:00:00"),
        'asset': "ETH/EUR",
        'entry_price': 1500.0,
        'sl_price': 1480.0,
        'tp_price': 1550.0,
        'position_value_quote': 500.0,
        'position_size_asset': 0.33
    })
    empty_portfolio.open_trade(sample_directive)
    empty_portfolio.open_trade(eth_directive)
    
    active_trades_dict = empty_portfolio.active_trades
    assert len(active_trades_dict) == 2
    assert sample_directive.correlation_id in active_trades_dict
    assert eth_directive.correlation_id in active_trades_dict

def test_process_candle_closes_long_trade_on_stop_loss(empty_portfolio: Portfolio, sample_directive: ExecutionDirective):
    empty_portfolio.open_trade(sample_directive)
    assert empty_portfolio.active_trade_count == 1

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
    assert closed_trade.pnl_quote < 0

def test_process_candle_closes_long_trade_on_take_profit(empty_portfolio: Portfolio, sample_directive: ExecutionDirective):
    empty_portfolio.open_trade(sample_directive)
    assert empty_portfolio.active_trade_count == 1

    profit_candle_timestamp = pd.to_datetime("2023-01-01 12:00:00")
    profit_candle = pd.Series({
        "open": 20200.0, "high": 20400.0,
        "low": 20150.0, "close": 20350.0
    }, name=profit_candle_timestamp)

    empty_portfolio.process_candle(profit_candle)

    assert empty_portfolio.active_trade_count == 0
    assert len(empty_portfolio.closed_trades) == 1

    closed_trade = empty_portfolio.closed_trades[0]
    assert closed_trade.exit_price == 20400.0
    assert closed_trade.pnl_quote > 0

def test_process_candle_closes_short_trade_on_stop_loss(empty_portfolio: Portfolio, sample_short_directive: ExecutionDirective):
    empty_portfolio.open_trade(sample_short_directive)
    assert empty_portfolio.active_trade_count == 1

    killer_candle_timestamp = pd.to_datetime("2023-01-02 11:00:00")
    killer_candle = pd.Series({
        "open": 1510.0, "high": 1520.0,
        "low": 1505.0, "close": 1515.0
    }, name=killer_candle_timestamp)

    empty_portfolio.process_candle(killer_candle)

    assert empty_portfolio.active_trade_count == 0
    assert len(empty_portfolio.closed_trades) == 1

    closed_trade = empty_portfolio.closed_trades[0]
    assert closed_trade.exit_price == 1520.0
    assert closed_trade.pnl_quote < 0

def test_process_candle_closes_short_trade_on_take_profit(empty_portfolio: Portfolio, sample_short_directive: ExecutionDirective):
    empty_portfolio.open_trade(sample_short_directive)
    assert empty_portfolio.active_trade_count == 1

    profit_candle_timestamp = pd.to_datetime("2023-01-02 12:00:00")
    profit_candle = pd.Series({
        "open": 1470.0, "high": 1475.0,
        "low": 1460.0, "close": 1465.0
    }, name=profit_candle_timestamp)

    empty_portfolio.process_candle(profit_candle)

    assert empty_portfolio.active_trade_count == 0
    assert len(empty_portfolio.closed_trades) == 1

    closed_trade = empty_portfolio.closed_trades[0]
    assert closed_trade.exit_price == 1460.0
    assert closed_trade.pnl_quote > 0
