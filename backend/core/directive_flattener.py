# backend/core/directive_flattener.py
"""
Contains a utility class to flatten a deeply nested RoutedTradePlan DTO
into a simple, flat ExecutionDirective.

@layer: Backend (Core)
@dependencies: [backend.dtos, pydantic]
@responsibilities:
    - Decouples the StrategyEngine's complex data structure from the simple
      contract required by the ExecutionHandler.
    - Dynamically unnests DTOs to create a flat data structure.
"""
from typing import Any, Dict, cast
from backend.dtos.routed_trade_plan import RoutedTradePlan
from backend.dtos.execution_directive import ExecutionDirective

class DirectiveFlattener:
    """
    A utility responsible for dynamically flattening the nested trade plan
    structure into a final, flat execution directive.
    """

    def _flatten_recursively(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively unnests Pydantic models within a dictionary.
        """
        flat_dict: Dict[str, Any] = {}
        for key, value in data.items():
            # --- DE FIX: Controleer op 'dict' in plaats van 'BaseModel' ---
            if isinstance(value, dict):
                # We willen de geneste container-keys (zoals 'signal', 'trade_plan') niet meenemen.
                # We pakken alleen de inhoud ervan uit.
                flat_dict.update(self._flatten_recursively(cast(Dict[str, Any], value)))
            else:
                flat_dict[key] = value
        return flat_dict

    def flatten(self, routed_trade_plan: RoutedTradePlan) -> ExecutionDirective:
        """
        Transforms a deeply nested RoutedTradePlan into a flat ExecutionDirective
        using a dynamic, recursive approach.

        Args:
            routed_trade_plan (RoutedTradePlan): The complete, nested output
                                                 from the OrderRouter (Fase 8).

        Returns:
            ExecutionDirective: A flat DTO containing all necessary data for execution.
        """
        # 1. Converteer het toplevel DTO naar een dictionary.
        nested_dict = routed_trade_plan.model_dump()

        # 2. Roep de recursieve functie aan om de dictionary plat te slaan.
        flat_data = self._flatten_recursively(nested_dict)

        # 3. Rename 'timestamp' from Signal to 'entry_time' for the directive
        if 'timestamp' in flat_data:
            flat_data['entry_time'] = flat_data.pop('timestamp')

        # 4. Creëer de uiteindelijke, platte DTO. Pydantic negeert
        #    automatisch alle overbodige velden (zoals de geneste objecten zelf).
        return ExecutionDirective(**flat_data)
