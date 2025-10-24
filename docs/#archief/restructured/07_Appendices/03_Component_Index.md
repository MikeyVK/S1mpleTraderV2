# Bijlage C: Component Index

**Versie:** 3.0
**Status:** Definitief

Dit document bevat een alfabetisch overzicht van alle componenten, interfaces, DTOs en configuratieschema's in het S1mpleTrader systeem.

---

## **Inhoudsopgave**

1. [Backend Assembly Componenten](#1-backend-assembly-componenten)
2. [Backend Core Componenten](#2-backend-core-componenten)
3. [Backend Data Componenten](#3-backend-data-componenten)
4. [Backend Environment Componenten](#4-backend-environment-componenten)
5. [Backend Utils Componenten](#5-backend-utils-componenten)
6. [Config Schema's](#6-config-schemas)
7. [DTO's (Data Transfer Objects)](#7-dtos-data-transfer-objects)
8. [Interface Contracten](#8-interface-contracten)
9. [Services](#9-services)
10. [Frontend Componenten](#10-frontend-componenten)
11. [Plugin Ecosystem](#11-plugin-ecosystem)
12. [Tools & Utilities](#12-tools--utilities)

---

## **1. Backend Assembly Componenten**

| Component | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----------|---------|-------|------|--------------|-------------|
| **ContextBuilder** | `backend/assembly/context_builder.py` | Backend (Assembly) | Builder/Orchestrator | Config schemas, factories | Orkestreert de volledige bootstrap fase van een operation |
| **EventChainValidator** | `backend/assembly/event_chain_validator.py` | Backend (Assembly) | Validator | Strategy blueprint schema | Valideert event chain integriteit tijdens bootstrap |
| **EventWiringFactory** | `backend/assembly/event_wiring_factory.py` | Backend (Assembly) | Factory | Wiring map schema, EventBus | Factory voor EventAdapters op basis van wiring_map.yaml |
| **OperatorFactory** | `backend/assembly/operator_factory.py` | Backend (Assembly) | Factory | Operators schema, BaseOperator | Factory voor BaseOperator instanties op basis van operators.yaml |
| **PersistorFactory** | `backend/assembly/persistor_factory.py` | Backend (Assembly) | Factory | Persistor interfaces | Factory voor gespecialiseerde persistors (Data, State, Journal) |
| **PluginEventAdapter** | `backend/assembly/plugin_event_adapter.py` | Backend (Assembly) | Adapter | EventHandler interface, EventBus | Adapter die bus-agnostische workers verbindt met EventBus |
| **PluginRegistry** | `backend/assembly/plugin_registry.py` | Backend (Assembly) | Registry | Plugin manifest schema | Ontdekt, valideert en registreert alle plugins |
| **WorkerBuilder** | `backend/assembly/worker_builder.py` | Backend (Assembly) | Builder | PluginRegistry, PersistorFactory | Assembleert workforce met dependency injection |

---

## **2. Backend Core Componenten**

| Component | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----------|---------|-------|------|--------------|-------------|
| **BaseEventAwareWorker** | `backend/core/base_worker.py` | Backend (Core) | Base Class | BaseWorker, IEventHandler | Base class voor event-gedreven workers |
| **BaseJournalingWorker** | `backend/core/base_worker.py` | Backend (Core) | Base Class | BaseWorker, IJournalPersistor | Base class voor journaling workers |
| **BaseOperator** | `backend/core/operators/base_operator.py` | Backend (Core) | Base Class | OperatorConfig, WorkerBuilder | Generieke, data-gedreven operator voor alle 5 worker types |
| **BaseStatefulWorker** | `backend/core/base_worker.py` | Backend (Core) | Base Class | BaseWorker, IStatePersistor | Base class voor stateful workers |
| **BaseWorker** | `backend/core/base_worker.py` | Backend (Core) | Base Class | ABC | Absolute basisklasse voor alle workers |
| **EventBus** | `backend/core/event_bus.py` | Backend (Core) | Infrastructure | Threading, typing | Centrale event distribution voor asynchrone communicatie |
| **Scheduler** | `backend/core/scheduler.py` | Backend (Core) | Infrastructure | Schedule library, EventBus | Tijd-gebaseerde event scheduling component |
| **StandardWorker** | `backend/core/base_worker.py` | Backend (Core) | Base Class | BaseWorker | Base class voor workers in georkestreerde pijplijn |
| **StrategyJournal** | `backend/core/strategy_journal.py` | Backend (Core) | Logging | IJournalPersistor, JournalEntry DTO | Append-only causaal logboek van alle gebeurtenissen |
| **StrategyLedger** | `backend/core/strategy_ledger.py` | Backend (Core) | State Management | LedgerState DTO | Operationeel grootboek voor snelle executie |

---

## **3. Backend Data Componenten**

| Component | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----------|---------|-------|------|--------------|-------------|
| **JsonPersistor** | `backend/data/persistors/json_persistor.py` | Backend (Data) | Persistor | JSON, pathlib, os | JSON persistor met atomic en append modes |
| **ParquetPersistor** | `backend/data/persistors/parquet_persistor.py` | Backend (Data) | Persistor | Pandas, PyArrow | Parquet persistor voor grote tijdreeksdata |

---

## **4. Backend Environment Componenten**

| Component | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----------|---------|-------|------|--------------|-------------|
| **BacktestEnvironment** | `backend/environments/backtest_environment.py` | Backend (Environments) | Implementation | BaseExecutionEnvironment | Execution environment voor historische backtesting |
| **BaseExecutionEnvironment** | `backend/environments/base_environment.py` | Backend (Environments) | Base Class | TradingContext, EventBus | Abstract base voor alle execution environments |
| **LiveEnvironment** | `backend/environments/live_environment.py` | Backend (Environments) | Implementation | BaseExecutionEnvironment | Execution environment voor live trading |
| **PaperEnvironment** | `backend/environments/paper_environment.py` | Backend (Environments) | Implementation | BaseExecutionEnvironment | Execution environment voor paper trading |

---

## **5. Backend Utils Componenten**

| Component | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----------|---------|-------|------|--------------|-------------|
| **AppLogger** | `backend/utils/app_logger.py` | Backend (Utils) | Utility | Logging | Application logging utility met i18n support |
| **DataUtils** | `backend/utils/data_utils.py` | Backend (Utils) | Utility | Pandas, NumPy | Data manipulation en analysis utilities |
| **DynamicLoader** | `backend/utils/dynamic_loader.py` | Backend (Utils) | Utility | Importlib | Dynamic plugin loading en class resolution |
| **Translator** | `backend/utils/translator.py` | Backend (Utils) | Utility | YAML, i18n | Internationalisatie en tekst vertaling |

---

## **6. Config Schema's**

| Schema | Bestand | Layer | Type | Dependencies | Beschrijving |
|--------|---------|-------|------|--------------|-------------|
| **EventDefinition** | `backend/config/schemas/event_map_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Definitie van toegestane events en DTO contracts |
| **EventMapConfig** | `backend/config/schemas/event_map_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor event_map.yaml validatie |
| **OperationConfig** | `backend/config/schemas/operation_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor operation.yaml validatie |
| **OperatorConfig** | `backend/config/schemas/operators_schema.py` | Backend (Config) | Pydantic Schema | Pydantic, Enums | Schema voor operator configuratie validatie |
| **OperatorSuiteConfig** | `backend/config/schemas/operators_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor alle operators configuratie |
| **PlatformConfig** | `backend/config/schemas/platform_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor platform.yaml validatie |
| **PluginEventConfig** | `backend/config/schemas/plugin_manifest_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor plugin event configuratie |
| **PluginIdentification** | `backend/config/schemas/plugin_manifest_schema.py` | Backend (Config) | Pydantic Schema | Pydantic, Enums | Schema voor plugin identification metadata |
| **PluginManifest** | `backend/config/schemas/plugin_manifest_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor complete plugin manifest validatie |
| **ScheduleConfig** | `backend/config/schemas/schedule_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor schedule configuratie |
| **ScheduleSuiteConfig** | `backend/config/schemas/schedule_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor alle schedules configuratie |
| **StrategyBlueprintConfig** | `backend/config/schemas/strategy_blueprint_schema.py` | Backend (Config) | Pydantic Schema | Pydantic, Enums | Schema voor strategy_blueprint.yaml validatie |
| **WiringDefinition** | `backend/config/schemas/wiring_map_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor event wiring definities |
| **WiringMapConfig** | `backend/config/schemas/wiring_map_schema.py` | Backend (Config) | Pydantic Schema | Pydantic | Schema voor wiring_map.yaml validatie |

---

## **7. DTO's (Data Transfer Objects)**

### **Config DTOs**
| DTO | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----|---------|-------|------|--------------|-------------|
| **EventDefinition** | `backend/dtos/config/event_definition.py` | Backend (DTO) | Pydantic Model | Pydantic | Runtime DTO voor event definities |
| **OperatorConfig** | `backend/dtos/config/operator_config.py` | Backend (DTO) | Pydantic Model | Pydantic, Enums | Runtime DTO voor operator configuratie |
| **ScheduleConfig** | `backend/dtos/config/schedule_config.py` | Backend (DTO) | Pydantic Model | Pydantic | Runtime DTO voor schedule configuratie |
| **WiringDefinition** | `backend/dtos/config/wiring_definition.py` | Backend (DTO) | Pydantic Model | Pydantic | Runtime DTO voor wiring definities |

### **State DTOs**
| DTO | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----|---------|-------|------|--------------|-------------|
| **BootstrapResult** | `backend/dtos/state/bootstrap_result.py` | Backend (DTO) | Pydantic Model | Pydantic | Resultaat van bootstrap fase |
| **JournalEntry** | `backend/dtos/state/journal_entry.py` | Backend (DTO) | Pydantic Model | Pydantic, UUID | Enkele entry in strategy journal |
| **LedgerState** | `backend/dtos/state/ledger_state.py` | Backend (DTO) | Pydantic Model | Pydantic, Decimal | Operationele ledger staat |
| **OperationParameters** | `backend/dtos/state/operation_parameters.py` | Backend (DTO) | Pydantic Model | Pydantic | Parameters voor operation startup |
| **ScheduledTick** | `backend/dtos/state/scheduled_tick.py` | Backend (DTO) | Pydantic Model | Pydantic, UUID | Scheduled event tick |
| **TradingContext** | `backend/dtos/state/trading_context.py` | Backend (DTO) | Pydantic Model | Pydantic, Pandas | Complete trading context voor één tick |

### **Pipeline DTOs**
| DTO | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----|---------|-------|------|--------------|-------------|
| **CriticalEvent** | `backend/dtos/execution/critical_event.py` | Backend (DTO) | Pydantic Model | Pydantic, UUID | Critical event met threat_id |
| **EntrySignal** | `backend/dtos/pipeline/entry_signal.py` | Backend (DTO) | Pydantic Model | Pydantic | Entry signal met entry price |
| **RiskDefinedSignal** | `backend/dtos/pipeline/risk_defined_signal.py` | Backend (DTO) | Pydantic Model | Pydantic | Signal met stop loss en take profit |
| **RoutedTradePlan** | `backend/dtos/pipeline/routed_trade_plan.py` | Backend (DTO) | Pydantic Model | Pydantic | Volledig trade plan met routing |
| **Signal** | `backend/dtos/pipeline/signal.py` | Backend (DTO) | Pydantic Model | Pydantic, UUID | Opportunity signal met opportunity_id |
| **TradePlan** | `backend/dtos/pipeline/trade_plan.py` | Backend (DTO) | Pydantic Model | Pydantic, UUID | Trade plan met entry/exit/sizing |

### **Market DTOs**
| DTO | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----|---------|-------|------|--------------|-------------|
| **DataCoverage** | `backend/dtos/market/data_coverage.py` | Backend (DTO) | Pydantic Model | Pydantic | Data coverage informatie |
| **TradeTick** | `backend/dtos/market/trade_tick.py` | Backend (DTO) | Pydantic Model | Pydantic | Individuele trade tick |

### **Execution DTOs**
| DTO | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----|---------|-------|------|--------------|-------------|
| **ExecutionDirective** | `backend/dtos/execution/execution_directive.py` | Backend (DTO) | Pydantic Model | Pydantic | Execution instructies |
| **ShutdownSignal** | `backend/dtos/execution/shutdown_signal.py` | Backend (DTO) | Pydantic Model | Pydantic | Shutdown signal |

---

## **8. Interface Contracten**

| Interface | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----------|---------|-------|------|--------------|-------------|
| **IAPIConnector** | `backend/core/interfaces/connectors.py` | Backend (Core) | Protocol | Typing | Interface voor API connectors |
| **IDataPersistor** | `backend/core/interfaces/persistors.py` | Backend (Core) | Protocol | Typing, Pandas | Interface voor market data persistentie |
| **IEventHandler** | `backend/core/interfaces/event_handler.py` | Backend (Core) | Protocol | Typing, Pydantic | Interface voor event publicatie |
| **IExecutionEnvironment** | `backend/core/interfaces/environment.py` | Backend (Core) | Protocol | Typing | Interface voor execution environments |
| **IExecutionHandler** | `backend/core/interfaces/execution.py` | Backend (Core) | Protocol | Typing | Interface voor trade execution |
| **IJournalPersistor** | `backend/core/interfaces/persistors.py` | Backend (Core) | Protocol | Typing | Interface voor journal persistentie |
| **IOperator** | `backend/core/interfaces/operator.py` | Backend (Core) | Protocol | Typing | Interface voor operators |
| **IStatePersistor** | `backend/core/interfaces/persistors.py` | Backend (Core) | Protocol | Typing | Interface voor state persistentie |
| **ITradingContextProvider** | `backend/core/interfaces/environment.py` | Backend (Core) | Protocol | Typing | Interface voor trading context provider |
| **IWorker** | `backend/core/interfaces/worker.py` | Backend (Core) | Protocol | Typing | Base interface voor alle workers |

---

## **9. Services**

| Service | Bestand | Layer | Type | Dependencies | Beschrijving |
|---------|---------|-------|------|--------------|-------------|
| **DataCommandService** | `services/data_services/data_command_service.py` | Service | Service | IDataPersistor | Service voor data management commands |
| **DataQueryService** | `services/data_services/data_query_service.py` | Service | Service | IDataPersistor | Service voor data queries |
| **OperationService** | `services/operation_service.py` | Service | Orchestrator | ContextBuilder, Config | Hoofdservice voor operation execution |
| **ParallelRunService** | `services/meta_workflows/parallel_run_service.py` | Service | Service | Multiprocessing | Parallel execution voor meta workflows |
| **SchedulerService** | `services/scheduler_service.py` | Service | Service | Scheduler, EventBus | Service wrapper voor scheduler |
| **VariantTestService** | `services/meta_workflows/variant_test_service.py` | Service | Service | ParallelRunService | Service voor variant testing |
| **OptimizationService** | `services/meta_workflows/optimization_service.py` | Service | Service | ParallelRunService | Service voor parameter optimization |

---

## **10. Frontend Componenten**

| Component | Bestand | Layer | Type | Dependencies | Beschrijving |
|-----------|---------|-------|------|--------------|-------------|
| **CLIReporter** | `frontends/cli/reporters/cli_reporter.py` | Frontend | Reporter | Typing | CLI output formatting |
| **OptimizationPresenter** | `frontends/cli/presenters/optimization_presenter.py` | Frontend | Presenter | Typing | CLI presentation voor optimization results |
| **RunOperationEntrypoint** | `frontends/cli/run_operation_entrypoint.py` | Frontend | Entrypoint | Argparse, Services | CLI entrypoint voor operation execution |

---

## **11. Plugin Ecosystem**

### **Plugin Structure**
```
plugins/
├── context_workers/           # ContextType plugins
├── opportunity_workers/       # OpportunityType plugins
├── threat_workers/           # ThreatType plugins
├── planning_workers/         # PlanningPhase plugins
└── execution_workers/        # ExecutionType plugins
```

### **Plugin Components**
| Component | Type | Beschrijving |
|-----------|------|-------------|
| **manifest.yaml** | YAML Config | Plugin identification, dependencies, capabilities |
| **worker.py** | Python Class | Business logic implementation |
| **schema.py** | Pydantic Schema | Parameter validation schema |
| **context_schema.py** | Pydantic Schema | Visual context schema |
| **tests/test_worker.py** | Python Tests | Unit tests (100% coverage required) |
| **dtos/** | Python DTOs | Custom event DTOs (optioneel) |

### **Worker Base Classes**
| Base Class | Inheritance | Beschrijving |
|------------|-------------|-------------|
| **BaseWorker** | ABC | Absolute basis voor alle workers |
| **StandardWorker** | BaseWorker | Voor georkestreerde pijplijn (process method) |
| **EventDrivenWorker** | BaseWorker | Voor autonome, event-based workers |
| **BaseStatefulWorker** | StandardWorker | Voor stateful standard workers |
| **BaseEventAwareWorker** | StandardWorker | Voor event-aware standard workers |
| **BaseJournalingWorker** | StandardWorker | Voor journaling standard workers |

---

## **12. Tools & Utilities**

| Tool | Bestand | Type | Beschrijving |
|------|---------|------|-------------|
| **ValidateEventChains** | `tools/validate_event_chains.py` | Standalone Tool | Event chain validation utility |
| **GeneratePluginScaffold** | `tools/generate_plugin_scaffold.py` | Generator | Plugin boilerplate generator |

---

## **Dependencies Matrix**

### **Component Dependencies**
- **ContextBuilder** → OperatorFactory, EventWiringFactory, EventChainValidator
- **OperatorFactory** → WorkerBuilder, PersistorFactory, EventBus
- **WorkerBuilder** → PluginRegistry, PersistorFactory, EventAdapterFactory
- **PluginEventAdapter** → EventBus, IWorker
- **EventWiringFactory** → EventBus, Component Registry

### **Layer Dependencies**
- **Frontend** → Service Layer (via API)
- **Service** → Backend Assembly (via ContextBuilder)
- **Backend Assembly** → Backend Core (via interfaces)
- **Backend Core** → Backend Data (via persistors)

---

## **Naming Conventions**

### **Files & Classes**
- **Interfaces:** `I` prefix (e.g., `IEventHandler`)
- **Base Classes:** `Base` prefix (e.g., `BaseWorker`)
- **Factories:** `Factory` suffix (e.g., `OperatorFactory`)
- **Services:** `Service` suffix (e.g., `OperationService`)
- **DTOs:** Descriptive names (e.g., `Signal`, `TradePlan`)
- **Schemas:** `Config` suffix (e.g., `OperatorConfig`)

### **Private Members**
- **Internal:** `_` prefix (e.g., `_event_bus`, `_logger`)
- **Not part of public API**

---

## **Referenties**

- **[Architecture Overview](01_Architecture_Overview.md)** - Top-level systeem overzicht
- **[Component Architecture](04_System_Architecture/01_Component_Architecture.md)** - Backend/frontend/services lagen
- **[Data Architecture](04_System_Architecture/02_Data_Architecture.md)** - DTOs en persistence
- **[Integration Architecture](04_System_Architecture/03_Integration_Architecture.md)** - Event wiring en operators
- **[Coding Standards](05_Implementation/01_Coding_Standards.md)** - Naming conventions en patterns

---

**Einde Document**

*"Van componenten naar systeem - waar elke bouwsteen zijn plaats heeft in het grote geheel."*