"""Defines the abstract contract for all execution handlers.

This module contains the `ExecutionHandler` Abstract Base Class (ABC), which
enforces a standard interface for any component that executes trading
directives.

@layer: Backend (Core Interfaces)
@dependencies: [abc, backend.dtos]
@responsibilities:
    - Define the `ExecutionHandler` abstract base class.
    - Specify the `execute_plan` method as the required contract for all execution environments.
"""
from abc import ABC, abstractmethod
from typing import List
from backend.dtos import ExecutionDirective

class ExecutionHandler(ABC):
    """
    Abstract Base Class that defines the contract for any component capable
    of executing trade directives.
    """

    @abstractmethod
    def execute_plan(self, directives: List[ExecutionDirective]) -> None:
        """
        Processes a list of execution directives.

        Args:
            directives (List[ExecutionDirective]): The directives to be executed.
        """
        raise NotImplementedError
