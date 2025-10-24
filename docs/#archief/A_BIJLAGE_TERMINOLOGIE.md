# **Bijlage A: Terminologie**

**Versie:** 3.0
**Status:** Definitief
Dit document is een alfabetische legenda van de terminologie die wordt gebruikt in de S1mpleTrader-architectuurdocumentatie.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Alfabetische Terminologie](#alfabetische-terminologie)
3. [Architectuur: Kernconcepten](#architectuur-kernconcepten)

---

## **Executive Summary**

Dit document dient als een centrale verklarende woordenlijst voor alle terminologie die wordt gebruikt in de S1mpleTrader architectuur. Het doel is om een eenduidig en consistent begrip van de kernconcepten te garanderen.

### **🎯 Kernconcepten**

**1. 5-Worker Taxonomie**
-   Het systeem gebruikt 5 gespecialiseerde rollen: `ContextWorker`, `OpportunityWorker`, `ThreatWorker`, `PlanningWorker`, en `ExecutionWorker`.

**2. ROL vs. CAPABILITIES**
-   De **ROL** van een worker (zijn architecturale doel) wordt bepaald door de basisklasse (`StandardWorker` of `EventDrivenWorker`).
-   De **CAPABILITIES** (extra vaardigheden zoals `state` en `events`) worden expliciet aangevraagd in het `manifest.yaml`.

**3. Data-Gedreven Operators**
-   Het gedrag van de 5 core operators wordt in `operators.yaml` gedefinieerd via `execution_strategy` en `aggregation_strategy`.

**4. Causaal ID Framework**
-   Een rijk systeem van getypeerde IDs (`OpportunityID`, `ThreatID`, `TradeID`) maakt volledige "waarom"-analyse mogelijk.

**5. Unified Persistence Suite**
-   Een formele, interface-gedreven architectuur voor data-persistentie (`IDataPersistor`, `IStatePersistor`, `IJournalPersistor`).

Dit document biedt gedetailleerde definities voor al deze termen om een helder begrip van de architectuur te faciliteren.

---

## **Alfabetische Terminologie**

**9-Fasen Trechter/pijplijn** 🚫 **DEPRECATED.** De fundamentele, sequentiële en procedurele workflow die een handelsidee stapsgewijs valideert en verrijkt. Deze is vervangen door de **5-Categorie Worker Taxonomie** (ContextWorker, OpportunityWorker, ThreatWorker, PlanningWorker, ExecutionWorker).

**AggregationStrategy** Een enum die bepaalt hoe een [`BaseOperator`](backend/core/operators/base_operator.py) de resultaten van meerdere workers combineert. Opties: `COLLECT_ALL` (verzamel alle resultaten), `CHAIN_THROUGH` (output wordt input voor volgende), `NONE` (geen aggregatie).

**AnalysisOperator** 🚫 **DEPRECATED.** De manager van de `AnalysisWorkers`. Opgesplitst in [`OpportunityOperator`](#opportunityoperator) (voor signal detection) en [`PlanningOperator`](#planningoperator) (voor trade planning).

**AnalysisPhase** 🚫 **DEPRECATED.** Enum voor analytische fasen. Vervangen door [`OpportunityType`](#opportunitytype) (voor signals) en [`PlanningPhase`](#planningphase) (voor planning).

**AnalysisWorker** 🚫 **DEPRECATED.** Een type plugin dat analytische handelsvoorstellen genereerde. Opgesplitst in [`OpportunityWorker`](#opportunityworker) (detecteert kansen) en [`PlanningWorker`](#planningworker) (maakt plannen).

**Assembly Team** De conceptuele naam voor de verzameling backend-componenten ([`PluginRegistry`](backend/assembly/plugin_registry.py), [`WorkerBuilder`](backend/assembly/worker_builder.py), [`ConnectorFactory`](backend/assembly/connector_factory.py), [`OperatorFactory`](#operatorfactory), [`PersistorFactory`](#persistorfactory)) die samen de technische orkestratie van plugins, connectoren, operators en persistors verzorgen.

**Atomic Writes (Journaling)** Een robuust state-saving mechanisme dat dataverlies bij een crash voorkomt door eerst naar een tijdelijk `.journal`-bestand te schrijven alvorens het originele state-bestand te overschrijven. Geïmplementeerd in de [`IStatePersistor`](#istatepersistor) en [`IJournalPersistor`](#ijournalpersistor) interfaces.

**Backend-for-Frontend (BFF)** Een gespecialiseerde API-laag in de architectuur die als enige doel heeft om data te leveren in het exacte formaat dat de Web UI nodig heeft, wat de frontend-code aanzienlijk versimpelt.

**BaseEventAwareWorker** 🚫 **DEPRECATED.** Verouderd concept. De vaardigheid om met events te werken is nu een **Capability** die wordt geconfigureerd in het `manifest.yaml`, niet langer een basisklasse waarvan geërfd wordt. Zie **Manifest-Gedreven Capability Model**.

**BaseJournalingWorker** 🚫 **DEPRECATED.** Verouderd concept. De vaardigheid om te loggen naar het journal is nu een **Capability** die wordt geconfigureerd in het `manifest.yaml`, niet langer een basisklasse waarvan geërfd wordt.

**BaseOperator** De generieke, data-gedreven operator-klasse. Een enkele klasse die alle orkestratie-verantwoordelijkheden kan overnemen, waarbij het gedrag volledig wordt bepaald door de [`operators.yaml`](#operatorsyaml) configuratie. Ontvangt een voorbereide lijst van `StandardWorkers` van de `OperatorFactory`.

**BaseStatefulWorker** 🚫 **DEPRECATED.** Verouderd concept. De vaardigheid om state bij te houden is nu een **Capability** die wordt geconfigureerd in het `manifest.yaml`, niet langer een basisklasse waarvan geërfd wordt.

**BaseWorker** De absolute, abstracte basisklasse voor alle workers. Definieert alleen de `__init__`. Een ontwikkelaar erft hier nooit direct van, maar kiest altijd een van de twee ROL-definiërende kinderen: [`StandardWorker`](#standardworker) of [`EventDrivenWorker`](#eventdrivenworker).

**Capability (Worker Capability)** Een extra vaardigheid die een worker kan bezitten, onafhankelijk van zijn ROL. Capabilities (zoals state, events, journaling) worden uitsluitend gedeclareerd in de `capabilities`-sectie van het `manifest.yaml`.

**EventAdapterFactory** De gespecialiseerde, centrale factory die als **enige** de verantwoordelijkheid heeft voor het creëren en configureren van `IEventHandler` (EventAdapter) instanties. Componenten zoals de `WorkerBuilder` zijn "klanten" van deze factory.

**ROL (Worker Rol)** De fundamentele, architecturale rol van een worker, die bepaalt *hoe* de worker wordt aangeroepen. Een ontwikkelaar kiest de ROL door te erven van [`StandardWorker`](#standardworker) (voor de georkestreerde pijplijn) of [`EventDrivenWorker`](#eventdrivenworker) (voor autonome, event-based acties).

**StandardWorker** Een abstracte basisklasse die de **ROL** definieert van een worker die deelneemt aan de georkestreerde, "top-down" pijplijn. Dwingt de implementatie van een `process()`-methode af.

**EventDrivenWorker** Een abstracte basisklasse die de **ROL** definieert van een worker die autonoom en "bottom-up" reageert op events van de EventBus. Heeft bewust geen `process()`-methode.

**Workforce DTO** Een Data Transfer Object dat de output is van de `WorkerBuilder`. Het bevat twee gescheiden lijsten: `standard_workers` en `event_driven_workers`. Dit is de kern van het "Geprepareerde Workforce Model", dat setup- en runtime-logica scheidt.
**Blueprint (`run_blueprint.yaml`)** 🚫 **DEPRECATED.** Verouderde term. Nu vervangen door [`strategy_blueprint.yaml`](#strategy_blueprintyaml).

**Causaal ID Framework** Het traceability systeem dat [`CorrelationID`](#correlationid) vervangt. Gebruikt getypeerde, semantische IDs ([`TradeID`](#tradeid), [`OpportunityID`](#opportunityid), [`ThreatID`](#threatid), [`ScheduledID`](#scheduledid)) om volledige causale reconstructie mogelijk te maken: "Waarom is deze trade geopend/gesloten?"

**Circuit Breaker** Een veiligheidsmechanisme, typisch binnen een [`ExecutionEnvironment`](backend/environments/), dat bij aanhoudende (netwerk)problemen de strategie in een veilige, passieve modus plaatst om verdere schade te voorkomen.

**Clock** De component binnen een [`ExecutionEnvironment`](backend/environments/) die de "hartslag" (ticks) van het systeem genereert, ofwel gesimuleerd uit historische data (`Backtest`) of real-time (`Live`/`Paper`).

**Configuratie-gedreven** Het kernprincipe dat het gedrag van de applicatie volledig wordt bestuurd door YAML-configuratiebestanden, niet door hardgecodeerde logica. Dit is uitgebreid met [`operators.yaml`](#operatorsyaml) voor operator-gedrag.

**`connectors.yaml`** Configuratiebestand dat de technische details (incl. secrets) voor verbindingen met externe, **live** partijen (bv. exchanges) definieert.

**Contract-gedreven** Het kernprincipe dat alle data-uitwisseling en configuratie wordt gevalideerd door strikte schema's (Pydantic, TypeScript-interfaces).

**ContextBuilder** 🚫 **DEPRECATED.** Verouderde term. De functionaliteit is nu onderdeel van de [`ContextOperator`](#contextoperator).

**ContextOperator** De operator (een instantie van [`BaseOperator`](backend/core/operators/base_operator.py)) die de `ContextWorkers` beheert. Luistert naar `MarketDataReceived`, orkestreert de executie van de context-verrijking, en publiceert het resultaat als `ContextReady`.

**ContextOrchestrator** 🚫 **DEPRECATED.** Verouderde term. De verantwoordelijkheden zijn overgenomen door de [`ContextOperator`](#contextoperator).

**ContextType** Enum met 7 sub-categorieën voor [`ContextWorker`](#contextworker) plugins: `REGIME_CLASSIFICATION`, `STRUCTURAL_ANALYSIS`, `INDICATOR_CALCULATION`, `MICROSTRUCTURE_ANALYSIS`, `TEMPORAL_CONTEXT`, `SENTIMENT_ENRICHMENT`, `FUNDAMENTAL_ENRICHMENT`. Georganiseerd naar type data-verrijking.

**ContextWorker** De "Cartograaf". Een type plugin dat ruwe marktdata verrijkt met analytische context (bv. het berekenen van indicatoren). Produceert een verrijkte [`TradingContext`](backend/dtos/state/trading_context.py).

**Correlation ID** 🚫 **DEPRECATED.** Een unieke identifier (UUID) voor simpele tracking. Vervangen door het [`Causaal ID Framework`](#causaal-id-framework) met getypeerde IDs voor volledige causale reconstructie.

**`data_sources.yaml`** Configuratiebestand dat de catalogus van alle beschikbare **lokale** historische datasets (bv. Parquet-archieven) op schijf registreert.

**DTO (Data Transfer Object)** Een Pydantic [`BaseModel`](backend/dtos/) (bv. [`Signal`](backend/dtos/pipeline/signal.py)) dat dient als een strikt contract voor data die als payload op de EventBus wordt doorgegeven.

**Entrypoints** De gespecialiseerde starter-scripts om de applicatie te draaien, zoals `run_operation.py`.

**`environments.yaml`** Configuratiebestand dat de "werelden" ([`ExecutionEnvironments`](backend/environments/)) definieert en ze koppelt aan een `connector_id` of `data_source_id`.

**EventAdapter** Een generieke component die als "vertaler" fungeert tussen de EventBus en de (bus-agnostische) [`Operator`](#baseoperator)-componenten, gedirigeerd door de `wiring_map.yaml`.

**Event Chain Validatie** Mechanisme dat automatisch valideert of alle event triggers een publisher hebben en vice versa. Voorkomt circular dependencies en waarschuwt voor "dode" events. Onderdeel van de **Event Architecture**.

**`event_map.yaml`** Configuratiebestand dat elke toegestane event-naam definieert en koppelt aan zijn verplichte DTO-contract.

**Event Topology** De term voor de volledige grafiek van event-producenten, -consumenten en hun onderlinge relaties. Kan automatisch worden gegenereerd (impliciete pijplijnen) of expliciet worden gedefinieerd (custom event chains).

**EventWiringFactory** De component die tijdens het opstarten de `wiring_map.yaml` leest. In het Gecentraliseerde Factory Model bevat deze factory zelf geen bouwlogica meer, maar is hij een "klant" van de [`EventAdapterFactory`](#eventadapterfactory). Zijn taak is gereduceerd tot het vertalen van de `wiring_map.yaml` en het aanroepen van de specialist.

**ExecutionEnvironment** De technische definitie van een "wereld" waarin een strategie kan draaien ([`Backtest`](backend/environments/backtest_environment.py), [`Paper`](backend/environments/paper_environment.py), of [`Live`](backend/environments/live_environment.py)). Verantwoordelijk voor het creëren van [`TradingContext`](backend/dtos/state/trading_context.py) inclusief `strategy_link_id`.

**ExecutionHandler** 🚫 **DEPRECATED.** Verouderde term. De verantwoordelijkheden zijn overgenomen door de [`ExecutionOperator`](#executionoperator).

**ExecutionOperator** De operator (een instantie van [`BaseOperator`](backend/core/operators/base_operator.py)) die de `ExecutionWorkers` beheert en `ExecutionApproved`-events verwerkt. Geeft de definitieve opdracht aan de [`ExecutionEnvironment`](backend/environments/).

**ExecutionStrategy** Een enum die bepaalt hoe een [`BaseOperator`](backend/core/operators/base_operator.py) zijn workers uitvoert. Opties: `SEQUENTIAL` (één voor één), `PARALLEL` (tegelijkertijd), `EVENT_DRIVEN` (op basis van events).

**ExecutionType** Enum met 4 sub-categorieën voor [`ExecutionWorker`](#executionworker) plugins: `TRADE_INITIATION`, `POSITION_MANAGEMENT`, `RISK_SAFETY`, `OPERATIONAL`. Georganiseerd naar type actie.

**ExecutionWorker** De "Uitvoerder". Een type plugin dat luistert naar specifieke triggers om **deterministische, op regels gebaseerde acties** direct uit te voeren. Voert plannen uit en beheert actieve posities.

**Feedback Loop (Strategisch)** De door de gebruiker bestuurde "Bouwen -> Meten -> Leren" cyclus, gefaciliteerd door de Web UI.

**Feedback Loop (Technisch)** De real-time feedback *binnen* een run, waarbij de staat van de [`StrategyLedger`](#strategyledger) de input kan zijn voor de volgende cyclus.

**Heartbeat** Een mechanisme in een live dataverbinding om de gezondheid van de connectie te monitoren door te controleren op periodieke signalen van de server.

**IDataPersistor** Protocol interface voor marktdata persistentie. Geoptimaliseerd voor grote volumes kolom-georiënteerde tijdreeksdata. Geïmplementeerd door [`ParquetPersistor`](backend/data/persistors/parquet_persistor.py). Onderdeel van de **Persistence Suite**.

**IEventHandler** Protocol interface voor event publicatie. Workers gebruiken deze abstractie in plaats van directe EventBus koppeling. Maakt workers testbaar en herbruikbaar. Onderdeel van de **Gelaagde Plugin Capaciteiten** architectuur.

**IJournalPersistor** Protocol interface voor strategy journal persistentie. Append-only, semi-gestructureerde historische logdata. Onderdeel van de **Persistence Suite**.

**Impliciete Pijplijnen** Event niveau waarbij het systeem automatisch de event chain genereert op basis van de workforce definitie. Voor 95% van standaard strategieën. **Geen event management nodig** voor de quant.

**IStatePersistor** Protocol interface voor plugin state persistentie. Kleine, transactionele, read-write data met atomische consistentie via journaling. Onderdeel van de **Persistence Suite**.

**Manifest (`plugin_manifest.yaml`)** De "ID-kaart" van een plugin. Bevat alle metadata die de [`PluginRegistry`](#pluginregistry) nodig heeft. Dit is de **Single Source of Truth** voor de **Capabilities** van een worker, gedefinieerd in een centrale `capabilities`-sectie (bv. voor state, events, journaling).

**Meta Workflows (`Optimization`, `VariantTest`)** Hoog-niveau operaties die de kern-executielogica herhaaldelijk en systematisch aanroepen voor complexe kwantitatieve analyses.

**MonitorOperator** 🚫 **DEPRECATED.** De manager van de `MonitorWorkers`. Nu hernoemd naar [`ThreatOperator`](#threatoperator) voor betere dualiteit met OpportunityOperator.

**MonitorWorker** 🚫 **DEPRECATED.** Verouderde naam voor [`ThreatWorker`](#threatworker). Hernoemd voor betere semantiek en duidelijkere verantwoordelijkheid.

**Operation** Het hoogste strategische niveau, gedefinieerd in een `operation.yaml`. Een verzameling van actieve Strategy Blueprints gekoppeld aan [`ExecutionEnvironments`](backend/environments/).

**`operation.yaml`** Het centrale "draaiboek" van de quant. Koppelt Strategy Blueprints aan [`ExecutionEnvironments`](backend/environments/).

**OperatorConfig** Pydantic schema dat een enkele operator-configuratie valideert vanuit [`operators.yaml`](#operatorsyaml). Definieert `operator_id`, `manages_worker_type`, `execution_strategy` en `aggregation_strategy`.

**OperatorFactory** De Assembly Team component die [`BaseOperator`](backend/core/operators/base_operator.py) instanties creëert op basis van de [`operators.yaml`](#operatorsyaml) configuratie. De "hoofdaannemer" voor operator-creatie.

**`operators.yaml`** Centraal configuratiebestand dat het gedrag van elke operator definieert (execution strategy, aggregation strategy). Het "configuratie-hart" dat hard-coded orkestratie vervangt.

**Opt-in Complexiteit** De filosofie waarbij de complexiteit van een worker wordt bepaald door expliciete keuzes:
1.  **ROL:** De ontwikkelaar kiest een `StandardWorker` of `EventDrivenWorker` basisklasse, waarmee de fundamentele rol wordt vastgelegd.
2.  **CAPABILITIES:** Extra vaardigheden (state, events, etc.) worden expliciet "aangezet" in de `capabilities`-sectie van het `manifest.yaml`.
Een worker zonder `capabilities`-sectie is 100% sandboxed en stateless.

**OptimizationService** De service die een grote parameterruimte systematisch doorzoekt door duizenden backtests parallel uit te voeren.

**OpportunityID** Getypeerde ID die de reden voor trade opening vastlegt. Gegenereerd door [`OpportunityWorker`](#opportunityworker). Beantwoordt de vraag: "Waarom is deze trade geopend?" Onderdeel van het [`Causaal ID Framework`](#causaal-id-framework).

**OpportunityOperator** De operator (een instantie van [`BaseOperator`](backend/core/operators/base_operator.py)) die de `OpportunityWorkers` beheert. Detecteert handelskansen en publiceert [`OpportunitySignal`](#opportunitysignal) events.

**OpportunitySignal** DTO voor opportunity signals. Bevat [`OpportunityID`](#opportunityid) in plaats van generieke `correlation_id`. Getypeerde signal met causale metadata.

**OpportunityType** Enum met 7 sub-categorieën voor [`OpportunityWorker`](#opportunityworker) plugins: `TECHNICAL_PATTERN`, `MOMENTUM_SIGNAL`, `MEAN_REVERSION`, `STATISTICAL_ARBITRAGE`, `EVENT_DRIVEN`, `SENTIMENT_SIGNAL`, `ML_PREDICTION`. Georganiseerd naar strategische benadering.

**OpportunityWorker** De "Verkenner". Een type plugin dat de verrijkte context analyseert om handelskansen te detecteren. Herkent patronen en genereert "handelsideeën" zonder concrete plannen. Vervangt de signal detection rol van `AnalysisWorker`.

**ParallelRunService** Een herbruikbare backend-component die het efficiënt managen van een `multiprocessing`-pool voor parallelle backtests verzorgt, ter ondersteuning van Meta Workflows.

**PersistorFactory** De Assembly Team component die alle persistor-instanties creëert en beheert. De "hoofdaannemer" voor de **Persistence Suite**. Creëert [`IDataPersistor`](#idatapersistor), [`IStatePersistor`](#istatepersistor) en [`IJournalPersistor`](#ijournalpersistor) implementaties.

**Platform (Het "Quant Operating System")** De fundamentele visie van S1mpleTrader als een agnostisch **besturingssysteem** dat een flexibel framework biedt voor plugins.

**`platform.yaml`** Configuratiebestand met globale, niet-strategische platforminstellingen.

**PlanningOperator** De operator (een instantie van [`BaseOperator`](backend/core/operators/base_operator.py)) die de `PlanningWorkers` beheert. Transformeert opportunity signals naar concrete, uitvoerbare plannen.

**PlanningPhase** Enum met 4 sub-categorieën voor [`PlanningWorker`](#planningworker) plugins: `ENTRY_PLANNING`, `EXIT_PLANNING`, `SIZE_PLANNING`, `ORDER_ROUTING`. Georganiseerd naar planningsfase in trade lifecycle.

**PlanningWorker** De "Strateeg". Een type plugin dat handelskansen transformeert naar concrete, uitvoerbare plannen. Bepaalt entry, exit, size en routing. Vervangt de planning rol van `AnalysisWorker`.

**Plugin** De fundamentele, zelfstandige en testbare eenheid van businesslogica in het systeem, behorend tot een van de vijf Worker-categorieën.

**Plugin-First** De filosofie dat alle businesslogica wordt geïmplementeerd in de vorm van onafhankelijke, herbruikbare en testbare plugins.

**PluginEventAdapter** Component die als "vertaler" fungeert tussen [`BaseEventAwareWorker`](#baseeventawareworker) en de EventBus. Leest event configuratie uit het plugin manifest en beheert subscriptions. Onderdeel van de **Plugin Event Architectuur**.

**PluginRegistry** De specialistische klasse binnen het Assembly Team die verantwoordelijk is voor het scannen van de `plugins/`-map en het valideren van alle manifesten.

**Portfolio** 🚫 **DEPRECATED.** Verouderde term. De strategische rol is overgenomen door **[`Operation`](#operation)**, de financiële rol door **[`StrategyLedger`](#strategyledger)**.

**Portfolio Blueprint** 🚫 **DEPRECATED.** Verouderde term. Nu vervangen door `operation.yaml`.

**PortfolioSupervisor** 🚫 **DEPRECATED.** Verouderde term. De verantwoordelijkheden zijn nu verdeeld over het [`Operation`](#operation)-concept en de verschillende Operators.

**Predefined Triggers** Event niveau met voorgedefinieerde trigger namen voor common use cases: `on_context_ready`, `on_signal_generated`, `on_ledger_update`, `on_position_opened`, `on_position_closed`, `on_schedule`. Voor meer controle zonder custom events.

**Pydantic** De Python-bibliotheek die wordt gebruikt voor datavalidatie en het definiëren van de data-contracten (DTO's, configuratie-schema's).

**RoutedTradePlan** DTO voor een volledig uitgewerkt trade plan. Output van [`PlanningWorker`](#planningworker), bevat entry, exit, size en routing details. Klaar voor executie door [`ExecutionWorker`](#executionworker).

**RunOrchestrator** 🚫 **DEPRECATED.** Verouderde term. Het opstartproces wordt nu direct gedreven door het uitvoeren van een [`Operation`](#operation).

**`schedule.yaml`** Configuratiebestand dat de Scheduler configureert om op gezette tijden (interval of cron) specifieke, tijd-gebaseerde events te publiceren. Creëert [`ScheduledID`](#scheduledid) voor traceability.

**ScheduledID** Getypeerde ID voor tijd-gedreven acties. Gegenereerd door de Scheduler. Beantwoordt de vraag: "Waarom is deze actie nu uitgevoerd?" Onderdeel van het [`Causaal ID Framework`](#causaal-id-framework).

**Schema (`schema.py`)** Het bestand binnen een plugin dat het Pydantic-model bevat dat de configuratieparameters van die specifieke plugin definieert en valideert.

**State Reconciliation** Het "pull"-proces voor live-omgevingen waarbij de interne [`StrategyLedger`](#strategyledger)-staat periodiek wordt gevalideerd en gecorrigeerd tegen de "enige bron van waarheid": de exchange.

**Strategy Builder** De specifieke "werkruimte" in de Web UI waar een gebruiker visueel een [`strategy_blueprint.yaml`](#strategy_blueprintyaml) kan samenstellen.

**`strategy_blueprint.yaml`** De gedetailleerde "receptenkaart". Beschrijft de volledige configuratie van plugins (`workforce`) en parameters voor één strategie. Uitgebreid met 5 worker categorieën en sub-structuur.

**StrategyEngine** 🚫 **DEPRECATED.** Verouderde term. De analytische logica is nu de verantwoordelijkheid van de [`OpportunityOperator`](#opportunityoperator), [`PlanningOperator`](#planningoperator) en hun workers.

**StrategyJournal** Het append-only, historische logbestand dat de volledige causale geschiedenis van een strategie-run vastlegt. Bevat opportunity detections, rejected opportunities (met [`ThreatID`](#threatid)), trade executions en alle causale links. Gescheiden van [`StrategyLedger`](#strategyledger) voor performance en analyserbaarheid.

**StrategyLedger** Het "domme grootboek". Een backend-component dat de financiële staat (kapitaal, posities, PnL) bijhoudt voor **één enkele, geïsoleerde strategie-run**. **Alleen operationele state**, geen historie (historie is in [`StrategyJournal`](#strategyjournal)).

**StrategyOperator** 🚫 **DEPRECATED.** Verouderde term. De generieke rol is opgesplitst in de vijf specifieke en functionele Operators: [`ContextOperator`](#contextoperator), [`OpportunityOperator`](#opportunityoperator), [`ThreatOperator`](#threatoperator), [`PlanningOperator`](#planningoperator), [`ExecutionOperator`](#executionoperator).

**StrategyWorker** 🚫 **DEPRECATED.** Verouderde term. Nu vervangen door [`OpportunityWorker`](#opportunityworker).

**Supervisor Model** Het crash-recovery mechanisme voor live trading, waarbij een extern "watchdog"-proces de hoofdapplicatie monitort en indien nodig herstart.

**ThreatID** Getypeerde ID die de reden voor ingreep vastlegt. Gegenereerd door [`ThreatWorker`](#threatworker). Beantwoordt de vraag: "Waarom is deze trade gesloten/aangepast?" Onderdeel van het [`Causaal ID Framework`](#causaal-id-framework).

**ThreatOperator** De operator (een instantie van [`BaseOperator`](backend/core/operators/base_operator.py)) die de `ThreatWorkers` beheert. Detecteert risico's en bedreigingen, publiceert strategische events. Hernoemd van `MonitorOperator` voor betere dualiteit met [`OpportunityOperator`](#opportunityoperator).

**ThreatSignal** DTO voor threat/risk signals. Bevat [`ThreatID`](#threatid) voor causale traceability. Getypeerde signal met threat metadata.

**ThreatType** Enum met 5 sub-categorieën voor [`ThreatWorker`](#threatworker) plugins: `PORTFOLIO_RISK`, `MARKET_RISK`, `SYSTEM_HEALTH`, `STRATEGY_PERFORMANCE`, `EXTERNAL_EVENT`. Georganiseerd naar domein van risico.

**ThreatWorker** De "Waakhond". Een type plugin dat de staat van de operatie observeert en informatieve, **strategische events** publiceert, maar **nooit** zelf handelt. Detecteert risico's en bedreigingen. Betere semantiek en dualiteit met [`OpportunityWorker`](#opportunityworker).

**Trade Explorer** De specifieke "werkruimte" in de Web UI die een diepgaande visuele analyse van de trades en de context van een voltooide run mogelijk maakt. Verrijkt met causale reconstructie via het [`Causaal ID Framework`](#causaal-id-framework).

**TradeID** Getypeerde ID als ankerpunt voor trade lifecycle. Gegenereerd door [`PlanningWorker`](backend/core/base_worker.py) of [`ExecutionWorker`](backend/core/base_worker.py). Primaire sleutel in [`StrategyJournal`](#strategyjournal). Onderdeel van het [`Causaal ID Framework`](#causaal-id-framework).

**TradingContext** DTO dat de volledige trading context bevat. Het wordt **direct gecreëerd door de ExecutionEnvironment** (inclusief `strategy_link_id`). Bevat OHLCV data, verrijkte context en metadata.

**TypeScript** De programmeertaal die voor de frontend wordt gebruikt om een type-veilig contract met de Pydantic-backend te garanderen via automatisch gegenereerde interfaces.

**VariantTestService** De service die een klein, gedefinieerd aantal strategie-varianten "head-to-head" met elkaar vergelijkt onder identieke marktomstandigheden.

**Worker (`worker.py`)** Het bestand binnen een plugin dat de Python-klasse met de daadwerkelijke businesslogica bevat.

**WorkerBuilder** De specialistische klasse binnen het Assembly Team die de volledige "workforce" voor een operator bouwt. Deze klasse heeft drie hoofdtaken:
1.  **Classificeren:** Leest de manifesten en classificeert workers om een [`Workforce DTO`](#workforcedto) te produceren.
2.  **Valideren:** Controleert of de ROL in de code (bv. `StandardWorker`) overeenkomt met de intentie in het manifest.
3.  **Assembleren:** Fungeert als "klant" van gespecialiseerde factories (zoals [`PersistorFactory`](#persistorfactory) en [`EventAdapterFactory`](#eventadapterfactory)) om de benodigde capabilities te injecteren in de worker-instanties.

**`wiring_map.yaml`** De "bouwtekening" van de dataflow. Beschrijft expliciet welke methode op welk component wordt aangeroepen als reactie op een specifiek event.

---

## **Architectuur: Kernconcepten**

### **Worker Taxonomie (5 Categorieën)**
De fundamentele organisatie van businesslogica:
1.  **[`ContextWorker`](#contextworker)** - "De Cartograaf" (verrijkt data)
2.  **[`OpportunityWorker`](#opportunityworker)** - "De Verkenner" (detecteert kansen)
3.  **[`ThreatWorker`](#threatworker)** - "De Waakhond" (detecteert risico's)
4.  **[`PlanningWorker`](#planningworker)** - "De Strateeg" (maakt plannen)
5.  **[`ExecutionWorker`](#executionworker)** - "De Uitvoerder" (voert uit & beheert)

### **Data-Gedreven Operators**
Eén generieke [`BaseOperator`](#baseoperator) klasse in plaats van vijf aparte classes. Gedrag bepaald door [`operators.yaml`](#operatorsyaml) configuratie. Definieert [`ExecutionStrategy`](#executionstrategy) en [`AggregationStrategy`](#aggregationstrategy).

### **Persistence Suite**
Uniform interface-driven model met drie gespecialiseerde interfaces:
-   [`IDataPersistor`](#idatapersistor) - Marktdata (Parquet)
-   [`IStatePersistor`](#istatepersistor) - Plugin state (JSON met journaling)
-   [`IJournalPersistor`](#ijournalpersistor) - Strategy journal (JSON append-only)

Beheerd door [`PersistorFactory`](#persistorfactory).

### **Manifest-Gedreven Capability Model**
De architectuur scheidt de **ROL** van een worker van zijn **CAPABILITIES**:
-   **ROL (via Klasse):** De ontwikkelaar kiest een basisklasse die de rol definieert.
    -   [`StandardWorker`](#standardworker): Voor de georkestreerde pijplijn (`process()`-methode).
    -   [`EventDrivenWorker`](#eventdrivenworker): Voor autonome, event-gedreven logica.
-   **CAPABILITIES (via Manifest):** Extra vaardigheden worden aangevraagd in `manifest.yaml`.
    -   `capabilities.state: { enabled: true }`
    -   `capabilities.events: { enabled: true }`
    -   `capabilities.journaling: { enabled: true }`
De `WorkerBuilder` leest dit contract en injecteert de benodigde dependencies.

### **Causale Traceability**
Het [`Causaal ID Framework`](#causaal-id-framework) gebruikt getypeerde IDs:
-   [`TradeID`](#tradeid) - Ankerpunt van trade
-   [`OpportunityID`](#opportunityid) - Waarom geopend?
-   [`ThreatID`](#threatid) - Waarom gesloten/aangepast?
-   [`ScheduledID`](#scheduledid) - Waarom nu?

### **Event Architectuur (3 Niveaus)**
1.  **[`Impliciete Pijplijnen`](#impliciete-pijplijnen)** - Automatisch gegenereerd (95% gebruik)
2.  **[`Predefined Triggers`](#predefined-triggers)** - Voorgedefinieerde trigger namen
3.  **Custom Event Chains** - Volledige controle voor experts

Gevalideerd door [`Event Chain Validatie`](#event-chain-validatie).

---

---