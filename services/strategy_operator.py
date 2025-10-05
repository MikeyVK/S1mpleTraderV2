# services/strategy_operator.py
"""
Contains the StrategyOperator, the service responsible for orchestrating a
single, complete strategy run.

@layer: Service
@dependencies:
    - backend.config.schemas.app_schema: To receive the complete run configuration.
    - backend.assembly: To build all necessary components (plugins, engine).
    - backend.environments: To create the world the strategy runs in.
    - backend.core: To instantiate the portfolio and the engine itself.
@responsibilities:
    - Acts as the main "conductor" for a single backtest or trading session.
    - Initializes all necessary backend components based on an AppConfig.
    - Runs the main event loop by calling the StrategyEngine.
    - Delegates the results from the engine (Directives and Events) to the
      appropriate handlers.
"""
from typing import Optional
import pandas as pd

from backend.config.schemas.app_schema import AppConfig
from backend.utils.app_logger import LogEnricher

from backend.assembly import PluginRegistry, WorkerBuilder, ContextBuilder
from backend.assembly.engine_builder import EngineBuilder  # Import the new builder
from backend.core import Portfolio, ContextRecorder
from backend.core.interfaces import Tradable #pyright: ignore[reportUnusedImport], pylint: disable=unused-import
from backend.core.interfaces.execution import ExecutionHandler
from backend.environments.backtest_environment import BacktestEnvironment
from backend.dtos.state.trading_context import TradingContext

# Force Pydantic to resolve any forward-looking type references (like 'Tradable')
# This is crucial for models that use abstract base classes or protocols.
TradingContext.model_rebuild()

class StrategyOperator:  # pylint: disable=too-many-instance-attributes
    """Orchestrates a single, complete strategy run from setup to execution."""

    def __init__(self, app_config: AppConfig, logger: LogEnricher):
        """Initializes the StrategyOperator."""
        self._app_config = app_config
        self._logger = logger
        self._context_recorder = ContextRecorder()

        # Attributes to be initialized in _prepare_components
        self._engine_builder: Optional[EngineBuilder] = None
        self._context_builder: Optional[ContextBuilder] = None
        self._portfolio: Optional[Portfolio] = None
        self._environment: Optional[BacktestEnvironment] = None
        self._execution_handler: Optional[ExecutionHandler] = None

    def _prepare_components(self):
        """Phase 1: Prepares all long-lived components for the run."""
        self._logger.info("operator.setup_start")
        platform_conf = self._app_config.platform

        registry = PluginRegistry(platform_config=platform_conf, logger=self._logger)
        worker_builder = WorkerBuilder(plugin_registry=registry, logger=self._logger)

        # The EngineBuilder is now a dedicated specialist for engine assembly
        self._engine_builder = EngineBuilder(worker_builder=worker_builder)
        self._context_builder = ContextBuilder()

        self._portfolio = Portfolio(
            initial_capital=platform_conf.portfolio.initial_capital,
            fees_pct=platform_conf.portfolio.fees_pct,
            logger=self._logger,
            context_recorder=self._context_recorder
        )

        # TODO: MVP HACK - Environment should be injected by a factory.
        self._environment = BacktestEnvironment(app_config=self._app_config,
                                                tradable=self._portfolio)
        self._execution_handler = self._environment.handler

    def _prepare_data(self) -> pd.DataFrame:
        """Phase 2: Builds and runs the ContextBuilder to create enriched data."""
        assert self._engine_builder is not None, "Components not prepared"
        assert self._context_builder is not None, "Components not prepared"
        assert self._environment is not None, "Components not prepared"

        self._logger.info("operator.context_building_start")
        run_conf = self._app_config.run

        context_pipeline = self._engine_builder.build_context_pipeline(run_conf)

        enriched_df = self._context_builder.build(
            initial_df=self._environment.source.get_data(),
            context_pipeline=context_pipeline
        )
        self._logger.info("operator.context_building_complete")
        return enriched_df

    def _run_operational_cycle(self, enriched_df: pd.DataFrame):
        """Phase 3 & 4: Assembles the engine and runs the main event loop."""
        assert self._engine_builder is not None, "Components not prepared"
        assert self._portfolio is not None, "Components not prepared"
        assert self._environment is not None, "Components not prepared"
        assert self._execution_handler is not None, "Components not prepared"

        run_conf = self._app_config.run

        # --- Assemble Engine ---
        self._logger.info("operator.engine_assembly_start")
        engine = self._engine_builder.build_engine(run_conf)
        self._logger.info("operator.engine_assembly_complete")

        # --- Run Main Loop ---
        trading_context = TradingContext(
            enriched_df=enriched_df,
            portfolio=self._portfolio,
            context_recorder=self._context_recorder
        )
        self._logger.info("operator.engine_start")
        for result in engine.run(trading_context=trading_context, clock=self._environment.clock):
            if result.critical_events:
                # TODO: MVP HACK - Proper event handling belongs in a supervisor.
                self._logger.error("operator.critical_events_detected",
                                   values={'count': len(result.critical_events)})
                break

            if result.execution_directives:
                # TODO: ARCHITECTURE REFACTOR - Directive handling belongs in the caller.
                self._execution_handler.execute_plan(result.execution_directives)

    def run(self):
        """
        Executes the full workflow by composing the private helper methods.
        This method now only describes WHAT happens, not HOW.
        """
        self._logger.info("operator.run_start")

        self._prepare_components()
        enriched_df = self._prepare_data()
        self._run_operational_cycle(enriched_df)

        self._logger.info("operator.run_complete")
