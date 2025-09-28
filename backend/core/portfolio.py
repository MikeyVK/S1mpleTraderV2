# backend/core/portfolio.py
"""
Contains the Portfolio class, which manages the financial state of a backtest.

@layer: Backend
@dependencies:
    - backend.core.interfaces.portfolio: Implements the Tradable protocol.
    - backend.dtos: Uses TradePlan and ClosedTrade DTOs.
@responsibilities:
    - Manages the account balance based on a starting capital.
    - Executes fully-formed TradePlan objects without strategic validation.
    - Holds the state for multiple active trades.
    - Maintains a list of all closed trades as ClosedTrade DTOs.
@inputs:
    - `initial_capital` (float) and `fees_pct` (float) on initialization.
    - `TradePlan` DTOs to be executed.
@outputs:
    - A list of `ClosedTrade` DTOs.
"""
from typing import Any, Dict, List
from uuid import UUID
import pandas as pd

from backend.core.interfaces.portfolio import Tradable
from backend.dtos.trade_plan import TradePlan
from backend.dtos.closed_trade import ClosedTrade
from backend.utils.app_logger import LogEnricher
from backend.core.context_recorder import ContextRecorder


class Portfolio(Tradable):
    """
    Manages account capital, active trades, and a list of closed trades.

    This class acts as a stateful ledger. Its primary responsibility is to
    maintain the financial state of the simulation by executing pre-calculated
    TradePlan objects and updating the balance. It is a concrete implementation
    of the Tradable protocol, capable of managing multiple concurrent trades.
    """

    def __init__(self,
                 initial_capital: float,
                 fees_pct: float,
                 logger: LogEnricher,
                 context_recorder: ContextRecorder):
        """
        Initializes the Portfolio.
        """
        self._initial_capital: float = initial_capital
        self._balance: float = initial_capital
        self._fees_pct: float = fees_pct
        self.logger = logger
        self.context_recorder = context_recorder

        self._closed_trades: List[ClosedTrade] = []
        self._active_trades: Dict[UUID, Dict[str, Any]] = {}

    @property
    def initial_capital(self) -> float:
        """Returns the starting capital of the portfolio."""
        return self._initial_capital

    @property
    def balance(self) -> float:
        """Returns the current account balance."""
        return self._balance

    @property
    def closed_trades(self) -> List[ClosedTrade]:
        """Returns the list of all closed trades."""
        return self._closed_trades

    @property
    def active_trades(self) -> Dict[UUID, Dict[str, Any]]:
        """A dictionary of all currently open trades, keyed by correlation_id."""
        return self._active_trades

    @property
    def active_trade_count(self) -> int:
        """Returns the number of active trades."""
        return len(self._active_trades)

    def get_active_trades(self) -> Dict[UUID, Dict[str, Any]]:
        """Returns the dictionary of active trades."""
        return self.active_trades

    def open_trade(self, trade_plan: TradePlan):
        """
        Opens a new trade based on a pre-calculated TradePlan object.
        """
        for trade in self._active_trades.values():
            if trade['asset'] == trade_plan.asset:
                self.logger.error(
                    "Attempted to open a trade on an asset with an existing position.",
                    values={'asset': trade_plan.asset}
                )
                return

        if trade_plan.position_value_eur > self._balance:
            self.logger.error(
                "Insufficient capital to open trade.",
                values={'required': trade_plan.position_value_eur, 'available': self._balance}
            )
            return

        # Sla ALLE benodigde data op, inclusief correlation_id en signal_type
        self._active_trades[trade_plan.correlation_id] = {
            "correlation_id": trade_plan.correlation_id,
            "signal_type": trade_plan.signal_type,
            "entry_time": trade_plan.entry_time,
            "asset": trade_plan.asset,
            "direction": trade_plan.direction,
            "entry_price": trade_plan.entry_price,
            "sl_price": trade_plan.sl_price,
            "tp_price": trade_plan.tp_price,
            "position_size_asset": trade_plan.position_size_asset,
            "position_value_eur": trade_plan.position_value_eur,
        }

        self.logger.trade(
            'portfolio.open_trade',
            values={
                'direction': trade_plan.direction.upper(),
                'price': f"{trade_plan.entry_price:,.2f}",
                'sl': f"{trade_plan.sl_price:,.2f}",
                'tp': f"{trade_plan.tp_price:,.2f}" if trade_plan.tp_price else "N/A"
            }
        )

    def process_candle(self, candle: pd.Series):
        """
        Processes the latest market data candle to check for SL/TP hits
        for all active trades.
        """
        if not self._active_trades:
            return

        # FIX: Controleer of de index van de candle (candle.name) een geldig Timestamp-object is
        if not isinstance(candle.name, pd.Timestamp):
            # Log een waarschuwing of negeer de candle
            return

        exit_timestamp = candle.name # Nu weten we zeker dat het een Timestamp is

        trade_ids_to_check = list(self._active_trades.keys())

        for correlation_id in trade_ids_to_check:
            trade = self._active_trades.get(correlation_id)
            if not trade:
                continue

            exit_price = None

            # TODO: In a multi-asset scenario, the candle should contain the asset
            # it belongs to, to match against the trade's asset.

            if trade['direction'] == 'long':
                if candle['low'] <= trade['sl_price']:
                    exit_price = trade['sl_price']
                elif trade['tp_price'] and candle['high'] >= trade['tp_price']:
                    exit_price = trade['tp_price']

            elif trade['direction'] == 'short':
                if candle['high'] >= trade['sl_price']:
                    exit_price = trade['sl_price']
                elif trade['tp_price'] and candle['low'] <= trade['tp_price']:
                    exit_price = trade['tp_price']

            if exit_price:
                self._close_trade(correlation_id, exit_timestamp, exit_price)

    def _close_trade(self, correlation_id: UUID, exit_timestamp: pd.Timestamp, exit_price: float):
        """
        Closes an active trade, calculates PnL, updates the balance, and archives
        the transaction.
        """
        trade_to_close = self._active_trades.pop(correlation_id, None)
        if not trade_to_close:
            return

        price_delta = exit_price - trade_to_close['entry_price']
        if trade_to_close['direction'] == 'short':
            price_delta *= -1

        gross_pnl = price_delta * trade_to_close['position_size_asset']
        fees = trade_to_close['position_value_eur'] * self._fees_pct * 2
        net_pnl = gross_pnl - fees

        self._balance += net_pnl

        # FIX: Voeg de ontbrekende correlation_id en signal_type velden toe
        closed_trade = ClosedTrade(
            correlation_id=trade_to_close['correlation_id'],
            signal_type=trade_to_close['signal_type'],
            entry_time=trade_to_close['entry_time'],
            exit_time=exit_timestamp,
            asset=trade_to_close['asset'],
            direction=trade_to_close['direction'],
            entry_price=trade_to_close['entry_price'],
            exit_price=exit_price,
            sl_price=trade_to_close['sl_price'],
            tp_price=trade_to_close['tp_price'],
            position_value_eur=trade_to_close['position_value_eur'],
            position_size_asset=trade_to_close['position_size_asset'],
            pnl_eur=net_pnl,
        )
        self._closed_trades.append(closed_trade)

        self.logger.trade(
            'portfolio.close_trade',
            values={
                'direction': closed_trade.direction.upper(),
                'price': f"{closed_trade.exit_price:,.2f}",
                'pnl': f"{closed_trade.pnl_eur:,.2f}",
                'result': "WIN" if closed_trade.pnl_eur > 0 else "LOSS"
            }
        )
