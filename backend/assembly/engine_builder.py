# backend/assembly/engine_builder.py
"""
Contains the EngineBuilder, a specialist for assembling a StrategyEngine.
"""
from typing import Any, Dict, List

from backend.assembly.worker_builder import WorkerBuilder
from backend.config.schemas.run_schema import RunBlueprint, WorkerDefinition
from backend.core.enums import PipelinePhase
from backend.core.strategy_engine import StrategyEngine
from backend.core.interfaces.worker import ContextWorker

class EngineBuilder:
    """Assembles a StrategyEngine with all its required workers."""

    def __init__(self, worker_builder: WorkerBuilder):
        self._worker_builder = worker_builder

    def build_context_pipeline(
        self, run_conf: RunBlueprint
    ) -> List[ContextWorker]:
        """Builds the initial pipeline of context workers."""
        context_plugin_names: List[str] = run_conf.taskboard.root.get(
            PipelinePhase.STRUCTURAL_CONTEXT, []
        )

        built_workers = [
            self._worker_builder.build(
                name=name,
                user_params=run_conf.workforce.get(name, WorkerDefinition()).params
            ) for name in context_plugin_names if name
        ]
        # Filter out any workers that failed to build
        return [worker for worker in built_workers if worker is not None]

    def build_engine(self, run_conf: RunBlueprint) -> StrategyEngine:
        """Builds and returns a configured StrategyEngine."""
        active_workers: Dict[str, Any] = {}
        for phase, plugin_names in run_conf.taskboard.root.items():
            if phase != PipelinePhase.STRUCTURAL_CONTEXT:
                worker_list = [
                    self._worker_builder.build(
                        name=name,
                        user_params=run_conf.workforce.get(name, WorkerDefinition()).params
                    ) for name in plugin_names if name
                ]
                active_workers[phase.value] = [w for w in worker_list if w is not None]

        return StrategyEngine(active_workers=active_workers)
