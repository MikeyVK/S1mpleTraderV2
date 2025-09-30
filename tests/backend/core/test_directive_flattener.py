# tests/backend/core/test_directive_flattener.py
"""
Unit tests for the DirectiveFlattener utility.
"""

import uuid
import pandas as pd
from backend.dtos.signal import Signal
from backend.dtos.entry_signal import EntrySignal
from backend.dtos.risk_defined_signal import RiskDefinedSignal
from backend.dtos.trade_plan import TradePlan
from backend.dtos.routed_trade_plan import RoutedTradePlan
from backend.dtos.execution_directive import ExecutionDirective
from backend.core.directive_flattener import DirectiveFlattener

def test_flatten_routed_trade_plan_to_directive():
    """
    Tests if a deeply nested RoutedTradePlan is correctly flattened into a
    simple ExecutionDirective.
    """
    # --- Arrange (De Voorbereiding) ---
    test_corr_id = uuid.uuid4()
    test_timestamp = pd.Timestamp("2023-01-01 10:00:00", tz='UTC')

    signal = Signal(correlation_id=test_corr_id, timestamp=test_timestamp, asset="BTC/EUR", direction="long", signal_type="fvg_entry_signal")
    entry_signal = EntrySignal(correlation_id=test_corr_id, signal=signal, entry_price=25000.0)
    risk_defined_signal = RiskDefinedSignal(correlation_id=test_corr_id, entry_signal=entry_signal, sl_price=24800.0, tp_price=25500.0)
    trade_plan = TradePlan(correlation_id=test_corr_id, risk_defined_signal=risk_defined_signal, position_value_quote=1000.0, position_size_asset=0.04)
    routed_trade_plan = RoutedTradePlan(correlation_id=test_corr_id, trade_plan=trade_plan, order_type='limit', limit_price=25000.0, time_in_force='GTC', post_only=True)
    
    expected_directive = ExecutionDirective(
        correlation_id=test_corr_id,
        signal_type="fvg_entry_signal",
        asset="BTC/EUR",
        direction="long",
        entry_price=25000.0,
        sl_price=24800.0,
        tp_price=25500.0,
        position_value_quote=1000.0,
        position_size_asset=0.04,
        order_type='limit',
        limit_price=25000.0,
        time_in_force='GTC',
        post_only=True,
        entry_time=test_timestamp
    )

    # --- Act (De Actie) ---
    flattener = DirectiveFlattener()
    actual_directive = flattener.flatten(routed_trade_plan)

    # --- Assert (De Controle) ---
    assert actual_directive == expected_directive
