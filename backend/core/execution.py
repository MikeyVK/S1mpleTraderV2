"""Contains the concrete implementation of an execution handler for backtests.

This module provides the `BacktestExecutionHandler`, which is a concrete
implementation of the `ExecutionHandler` interface. It is responsible for
simulating the execution of trading directives within a backtesting environment.

@layer: Backend (Core)
@dependencies: [backend.core.interfaces, backend.dtos, backend.utils]
@responsibilities:
    - Implement the `ExecutionHandler` interface for simulated backtests.
    - Receive `ExecutionDirective` objects and translate them into trade actions.
    - Interact with a `Tradable` component (e.g., Portfolio) to open trades.
    - Log all execution activities.
"""
from typing import List

# --- CORRECTIE: Importeer de GECENTRALISEERDE interface ---
from backend.core.interfaces.execution import ExecutionHandler
from backend.core.interfaces.portfolio import Tradable
from backend.dtos import ExecutionDirective
from backend.utils.app_logger import LogEnricher

class BacktestExecutionHandler(ExecutionHandler):
    """
    Handles the execution of directives within a simulated backtest environment.
    """
    def __init__(self, tradable: Tradable, logger: LogEnricher):
        self._tradable = tradable
        self._logger = logger

    def execute_plan(self, directives: List[ExecutionDirective]):
        """
        Processes a list of execution directives by calling the appropriate
        methods on the tradable entity (Portfolio).
        """
        for directive in directives:
            # Hier kun je in de toekomst logica toevoegen voor verschillende directive types
            # De huidige implementatie geeft de directive direct door.
            self._tradable.open_trade(directive)
