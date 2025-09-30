# backend/core/interfaces/environment.py
"""
Contains the behavioral contracts (ABCs) for the Execution Environment
and its sub-components.

@layer: Backend (Core Interfaces)
@dependencies: [abc, typing, pandas, backend.dtos]
@responsibilities:
    - Defines the abstract contracts for the operational "world".
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generator, Tuple, TYPE_CHECKING
import pandas as pd

# --- CORRECTIE: Importeer de ExecutionHandler interface HIER ---
if TYPE_CHECKING:
    from backend.core.interfaces.execution import ExecutionHandler

class DataSource(ABC):
    """Abstract contract for any component that provides market data."""
    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        """Returns the complete historical dataset for the environment."""
        ...

class Clock(ABC):
    """Abstract contract for any component that controls the flow of time."""
    @abstractmethod
    def tick(self) -> Generator[Tuple[pd.Timestamp, pd.Series], None, None]:
        """Yields the next moment in time (timestamp and data row)."""
        ...

class BaseEnvironment(ABC):
    """
    Abstract contract for an Execution Environment.
    This interface defines the "world" in which a strategy operates.
    """
    @property
    @abstractmethod
    def source(self) -> DataSource:
        """The data source for this environment."""
        ...

    @property
    @abstractmethod
    def clock(self) -> Clock:
        """The clock that controls time in this environment."""
        ...

    @property
    @abstractmethod
    def handler(self) -> "ExecutionHandler":
        """The execution handler for this environment."""
        ...
