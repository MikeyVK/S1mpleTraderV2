# plugins/structural_context/ema_detector/tests/test_worker.py
"""
Unit tests for the EmaDetector worker.

@layer: Plugin
@dependencies: [pandas, pytest]
@responsibilities:
    - Tests that the EmaDetector correctly calculates and adds an EMA column.
"""
import pandas as pd
from unittest.mock import MagicMock

# Import de componenten die we testen
from ..worker import EmaDetector
from ..schema import EmaDetectorParams
from backend.dtos.state.trading_context import TradingContext

def test_ema_detector_adds_correct_column():
    """
    Tests if the worker adds a correctly named and calculated EMA column.
    """
    # Arrange
    params = EmaDetectorParams(period=3)
    logger = MagicMock()
    worker = EmaDetector(name="test_ema", params=params, logger=logger)

    # Maak een mock context object aan
    mock_context = MagicMock(spec=TradingContext)

    # Maak test-data
    data = {'close': [10, 20, 30, 40]}
    df = pd.DataFrame(data)

    # Handmatige berekening van de EMA (span=3 -> alpha=0.5)
    # 1: 10
    # 2: (20 * 0.5) + (10 * 0.5) = 15
    # 3: (30 * 0.5) + (15 * 0.5) = 22.5
    # 4: (40 * 0.5) + (22.5 * 0.5) = 31.25
    expected_ema = [10.0, 15.0, 22.5, 31.25]

    # Act
    result_df = worker.process(df, mock_context)

    # Assert
    expected_col = "ema_3"
    assert expected_col in result_df.columns

    # CORRECTIE: 'check_almost_equal' vervangen door 'check_exact=False' en 'atol'
    pd.testing.assert_series_equal(
        result_df[expected_col],
        pd.Series(expected_ema, name=expected_col),
        check_exact=False,
        atol=0.01  # Absolute tolerance voor floating point vergelijkingen
    )
