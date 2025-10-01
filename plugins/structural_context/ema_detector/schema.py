# plugins/structural_context/ema_detector/schema.py
"""
Contains the Pydantic validation schema for the EmaDetector plugin.

@layer: Plugin
@dependencies: [Pydantic]
@responsibilities:
    - Defines and validates the configuration parameters for the EmaDetector.
"""
from pydantic import BaseModel, Field

class EmaDetectorParams(BaseModel):
    """
    Validation schema for the parameters of the EmaDetector.
    It ensures that the 'period' is a positive integer.
    """
    period: int = Field(
        default=20,
        gt=0,
        description="The lookback period for the EMA calculation."
    )
