# backend/core/base_worker.py
"""
Contains optional, concrete base classes for Strategy Workers to simplify
plugin development by automating DTO nesting and providing direct access
to key identifiers like the correlation_id.

@layer: Backend (Core)
@dependencies: [abc, typing, uuid]
@responsibilities:
    - Provide a generic BaseStrategyWorker that handles DTO nesting.
    - Provide specific, inheritable base classes for each worker category
      to minimize boilerplate code in plugins.
    - Automate the propagation of the correlation_id.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, Dict, Generic, Optional, TypeVar
from uuid import UUID

if TYPE_CHECKING:
    from backend.dtos import (
        EntrySignal,
        RiskDefinedSignal,
        RoutedTradePlan,
        Signal,
        TradePlan,
        TradingContext,
        CriticalEvent,
    )


# --- Generieke Type Variabelen (volgens PEP 484 conventie) ---
InputDTO_T = TypeVar("InputDTO_T")  # pylint: disable=invalid-name
OutputDTO_T = TypeVar("OutputDTO_T")  # pylint: disable=invalid-name


class BaseStrategyWorker(ABC, Generic[InputDTO_T, OutputDTO_T]):
    """
    A generic base class that automates DTO creation and `correlation_id` handling.

    This class should typically not be inherited from directly. Use the
    specific, category-based classes below (e.g., BaseEntryPlanner) instead,
    as they pre-configure the DTO types and field names, resulting in
    minimal boilerplate for the plugin developer.
    """

    def __init__(self, params: Any):
        self.params = params

    def proces(
        self, input_dto: InputDTO_T, context: "TradingContext"
    ) -> Optional[OutputDTO_T]:
        """
        Public method called by the StrategyEngine. It extracts the correlation_id,
        calls the plugin's specific logic, and wraps the result in the
        correct output DTO.
        """
        # Haal de gepromote correlation_id direct van de input DTO
        correlation_id = getattr(input_dto, "correlation_id", None)
        if not isinstance(correlation_id, UUID):
            return None  # Veiligheid: stop als er geen ID is in de keten

        # Roep de kernlogica van de plugin aan
        new_data = self._process_internal(input_dto, correlation_id, context)

        if new_data is None:
            return None

        output_dto_class = self._get_output_dto_class()
        source_field_name = self._get_source_field_name()

        # Bouw de argumenten voor de constructor van de nieuwe DTO
        constructor_args: Dict[str, Any] = {
            "correlation_id": correlation_id,
            source_field_name: input_dto,
            **new_data,
        }

        return output_dto_class(**constructor_args)

    @abstractmethod
    def _process_internal(
        self,
        input_dto: InputDTO_T,
        correlation_id: UUID,
        context: "TradingContext",
    ) -> Optional[Dict[str, Any]]:
        """
        Plugin-specific logic must be implemented here by the developer.

        Args:
            input_dto: The DTO from the previous pipeline stage.
            correlation_id: The unique ID of the signal chain, provided for convenience.
            context: The full trading context.

        Returns:
            A dictionary with the new fields for the output DTO,
            or None if no output should be generated.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_output_dto_class(self) -> type[OutputDTO_T]:
        """Must specify the output DTO type."""
        raise NotImplementedError

    @abstractmethod
    def _get_source_field_name(self) -> str:
        """Must specify the field name for the nested source DTO."""
        raise NotImplementedError


# --- Categorie-Specifieke Basisklassen ---

class BaseSignalGenerator(ABC):
    """Base class for SignalGenerator plugins (Fase 3)."""
    def __init__(self, params: Any):
        self.params = params

    @abstractmethod
    def process(self, context: "TradingContext") -> List["Signal"]:
        """
        Generates a list of raw Signal DTOs based on the market context.

        Args:
            context: The full trading context, including the enriched DataFrame.

        Returns:
            A list of Signal DTOs, or an empty list if no opportunities are found.
        """
        raise NotImplementedError

class BaseSignalRefiner(BaseStrategyWorker["Signal", "Signal"]):
    """Base class for SignalRefiner plugins (Fase 4)."""

    def execute(
        self, input_dto: "Signal", context: "TradingContext"
    ) -> Optional["Signal"]:
        """
        Overrides the base execute method for the specific case of a refiner,
        which acts as a filter (1-to-1 or 1-to-0).
        """
        is_valid = self._process(input_dto, input_dto.correlation_id, context)
        return input_dto if is_valid else None

    @abstractmethod
    def _process(  # type: ignore
        self,
        input_dto: "Signal",
        correlation_id: UUID,
        context: "TradingContext",
    ) -> bool:
        """Return True to keep the signal, False to discard it."""
        raise NotImplementedError


class BaseEntryPlanner(BaseStrategyWorker["Signal", "EntrySignal"]):
    """Base class for EntryPlanner plugins (Fase 5)."""

    def _get_output_dto_class(self) -> type["EntrySignal"]:
        # pylint: disable=import-outside-toplevel
        from backend.dtos import EntrySignal

        return EntrySignal

    def _get_source_field_name(self) -> str:
        return "signal"


class BaseExitPlanner(BaseStrategyWorker["EntrySignal", "RiskDefinedSignal"]):
    """Base class for ExitPlanner plugins (Fase 6)."""

    def _get_output_dto_class(self) -> type["RiskDefinedSignal"]:
        # pylint: disable=import-outside-toplevel
        from backend.dtos import RiskDefinedSignal

        return RiskDefinedSignal

    def _get_source_field_name(self) -> str:
        return "entry_signal"


class BaseSizePlanner(BaseStrategyWorker["RiskDefinedSignal", "TradePlan"]):
    """Base class for SizePlanner plugins (Fase 7)."""

    def _get_output_dto_class(self) -> type["TradePlan"]:
        # pylint: disable=import-outside-toplevel
        from backend.dtos import TradePlan

        return TradePlan

    def _get_source_field_name(self) -> str:
        return "risk_defined_signal"


class BaseOrderRouter(BaseStrategyWorker["TradePlan", "RoutedTradePlan"]):
    """Base class for OrderRouter plugins (Fase 8)."""

    def _get_output_dto_class(self) -> type["RoutedTradePlan"]:
        # pylint: disable=import-outside-toplevel
        from backend.dtos import RoutedTradePlan

        return RoutedTradePlan

    def _get_source_field_name(self) -> str:
        return "trade_plan"

class BaseCriticalEventDetector(ABC):
    """Base class for CriticalEventDetector plugins (Fase 9)."""
    def __init__(self, params: Any):
        self.params = params

    @abstractmethod
    def process(
        self, routed_trade_plans: List["RoutedTradePlan"], context: "TradingContext"
    ) -> List["CriticalEvent"]:
        """
        Detects and returns a list of critical events based on the final context.

        Args:
            routed_trade_plans: The list of proposed trades for the current cycle.
            context: The full trading context.

        Returns:
            A list of CriticalEvent DTOs, or an empty list if no events are detected.
        """
        raise NotImplementedError
