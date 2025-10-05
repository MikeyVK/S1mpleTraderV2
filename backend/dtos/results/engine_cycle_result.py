# backend/dtos/engine_cycle_result.py
"""
Contains the DTO that represents the complete output of a single StrategyEngine cycle.

@layer: Backend (DTO)
@dependencies: [pydantic, .execution_directive, .critical_event]
@responsibilities:
    - Bundles all outcomes of a single engine tick into one object.
    - Decouples new trade instructions from systemic event notifications.
"""
from typing import List
from pydantic import BaseModel, ConfigDict
from backend.dtos.execution.execution_directive import ExecutionDirective
from backend.dtos.execution.critical_event import CriticalEvent

class EngineCycleResult(BaseModel):
    """
    Represents the complete output of a single processing cycle (tick)
    of the StrategyEngine. It decouples trade proposals from critical events.

    This object is yielded by the StrategyEngine on every tick and allows the
    consuming service (e.g., BacktestService) to intelligently decide on the
    next course of action.

    Attributes:
        execution_directives (List[ExecutionDirective]): A list of new trades to be executed.
        critical_events (List[CriticalEvent]): A list of detected systemic events.
    """
    execution_directives: List[ExecutionDirective]
    critical_events: List[CriticalEvent]

    model_config = ConfigDict(arbitrary_types_allowed=True)
