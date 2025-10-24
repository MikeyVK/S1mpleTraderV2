# Bijlage A: Terminologie

**Status:** Definitief  
**Versie:** 4.0

---

## Actieve Terminologie

### A

**AdapterConfig** - Configuratie object voor één EventAdapter, bevat subscriptions, handler_mapping en publication_config.

**AggregatedLedger** - Operation-breed singleton dat financiële staat over alle strategieën aggregeert.

### B

**BaseContextDTO** - Minimale context DTO met timestamp en current_price voor één tick.

**BuildSpecs** - Machine-leesbare specificatie gegenereerd door ConfigTranslator, bevat alle instructies voor factories.

### C

**ConfigTranslator** - Backend component die YAML configuratie vertaalt naar BuildSpecs.

**Custom Events** - Plugin-gedefinieerde events (bv. EMERGENCY_HALT_TRADING), gedeclareerd in manifest.publishes.

### D

**DependencyValidator** - Validator die checkt of data-afhankelijkheden consistent zijn met workflow.

**DispositionEnvelope** - Standaard return type van workers, bevat flow control (CONTINUE/PUBLISH/STOP).

**DTO Registry** - Centraal register van plugin-specifieke DTOs op `backend/dto_reg/<vendor>/<plugin>/<version>/`.

### E

**EventAdapter** - Generieke component die één worker of singleton verbindt met EventBus.

**EventBus** - Pure N-N broadcast bus zonder intelligentie.

**EventChainValidator** - Validator die event topologie analyseert tijdens bootstrap.

**EventDrivenWorker** - Basisklasse voor workers die autonoom op events reageren (geen process() methode).

**EventWiringFactory** - Factory die EventAdapters creëert en configureert uit wiring_specs.

### I

**ITradingContextProvider** - Interface voor toegang tot Tick Cache en basis context.

**IOhlcvProvider** - Interface voor historische OHLCV data (Point-in-Time).

**IStateProvider** - Interface voor persistent worker state.

**IJournalWriter** - Interface voor StrategyJournal logging.

**ILedgerProvider** - Interface voor financiële staat toegang.

### O

**OperationConfig** - Configuratie laag 2, bevat connectors, environments, schedule voor één operation.

**OperationService** - Hoofdservice die strategie levenscycli beheert (start/stop/restart).

**OpportunityID** - Causale UUID die reden voor trade opening vastlegt.

### P

**PlatformConfig** - Configuratie laag 1, bevat globale platform instellingen.

**Point-in-Time Principe** - Architecturaal principe dat data-lekkage uit toekomst voorkomt.

**Platform Providers** - Singleton services (IOhlcvProvider, IStateProvider, etc.) geïnjecteerd in workers.

**platform_wiring_map.yaml** - Bedradings configuratie voor operation-brede singletons.

### S

**StandardWorker** - Basisklasse voor workers in georkestreerde pipeline (vereist process() methode).

**StrategyConfig** - Configuratie laag 3, bevat blueprint en wiring_map voor één strategie.

**StrategyJournal** - Append-only logboek met causale geschiedenis van één strategie.

**StrategyLedger** - Operationele financiële staat van één strategie (alleen actueel).

**strategy_wiring_map.yaml** - UI-gegenereerde bedradings configuratie voor één strategie.

**System Events** - Interne flow-control events (bv. ema_fast_OUTPUT), niet zichtbaar voor plugin developer.

### T

**ThreatID** - Causale UUID die reden voor trade wijziging/sluiting vastlegt.

**Tick Cache** - Tijdelijke Dict[Type[BaseModel], BaseModel] die alleen tijdens één tick bestaat.

**TickCacheManager** - Singleton die Tick Cache levenscyclus beheert en flows initieert.

**TradeID** - Primaire identifier voor trade, gegenereerd door PlanningWorker.

**TradingContext** - Minimale context met alleen timestamp, price, strategy_link_id, asset_pair.

### W

**WiringRule** - Configuratie object dat één event-bedrading definieert (source → target).

**WorkerFactory** - Factory die workers bouwt uit workforce_spec met provider injecties.

---

## Deprecated Terminologie

### 🚫 VERVALLEN IN V4.0

**AnalysisOperator** ❌ - Operator die AnalysisWorkers beheerde. **Vervangen door**: Platgeslagen model zonder Operators.

**AnalysisWorker** ❌ - Worker type. **Vervangen door**: OpportunityWorker + PlanningWorker.

**BaseOperator** ❌ - Generieke operator klasse. **Vervallen**: Geen Operators meer.

**ContextOperator** ❌ - Operator voor ContextWorkers. **Vervallen**: Directe bedrading via adapters.

**enriched_df** ❌ - DataFrame in TradingContext. **Vervangen door**: DTOs in Tick Cache.

**ExecutionOperator** ❌ - Operator voor ExecutionWorkers. **Vervallen**: Event-driven via adapters.

**MonitorWorker** ❌ - Oude naam. **Vervangen door**: ThreatWorker (betere semantiek).

**operators.yaml** ❌ - Configuratie bestand. **Vervallen**: Geen operators meer.

**OpportunityOperator** ❌ - Operator voor OpportunityWorkers. **Vervallen**: Directe bedrading.

**PlanningOperator** ❌ - Operator voor PlanningWorkers. **Vervallen**: Sequentiële chain via wiring.

**ThreatOperator** ❌ - Operator voor ThreatWorkers. **Vervallen**: Event-driven via adapters.

**wiring_map.yaml** (globaal) ❌ - Globale bedrading. **Vervangen door**: platform_wiring_map.yaml + strategy_wiring_map.yaml.

### ⚠️ GEWIJZIGD IN V4.0

**EventAdapter** ⚠️ - **Was**: Per operator. **Nu**: Per component (worker/singleton).

**TradingContext** ⚠️ - **Was**: Bevatte enriched_df. **Nu**: Minimaal met alleen basis info.

**wiring_map.yaml** ⚠️ - **Was**: Statisch platform bestand. **Nu**: UI-gegenereerd per strategie.

---

## Afkortingen

- **DTO** - Data Transfer Object (Pydantic BaseModel)
- **SRP** - Single Responsibility Principle
- **DI** - Dependency Injection
- **CQRS** - Command Query Responsibility Segregation
- **MTF** - Multi-Timeframe
- **FVG** - Fair Value Gap
- **DCA** - Dollar Cost Averaging
- **UI** - User Interface (Strategy Builder)

---

**Einde Bijlage A**

Deze bijlage bevat alle actieve terminologie voor V4.0 architectuur en markeert deprecated terms uit eerdere versies.