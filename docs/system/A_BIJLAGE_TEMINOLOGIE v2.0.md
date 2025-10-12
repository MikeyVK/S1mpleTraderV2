# **Bijlage A: Terminologie**

**Versie:** 2.0 (Architectuur Blauwdruk v4) **Status:** Definitief

Dit document is een alfabetische legenda van de terminologie die wordt gebruikt in de S1mpleTrader V2-architectuurdocumentatie.

**9-Fasen Trechter/pijplijn** De fundamentele, sequentiële en procedurele workflow die een handelsidee stapsgewijs valideert en verrijkt. De logica hiervan is nu verdeeld over de `ContextWorker`\- en `AnalysisWorker`\-pijplijnen.

**AnalysisOperator** De manager van de `AnalysisWorkers`. Luistert naar `ContextReady`, orkestreert de executie van de analytische pijplijn, en publiceert het resultaat als `StrategyProposalReady`. Vervangt de `StrategyEngine` en deels de `StrategyOperator`.

**AnalysisWorker** De "Analist". Een type plugin dat de verrijkte context analyseert om **niet-deterministische, analytische handelsvoorstellen** te genereren. Vervangt de `StrategyWorker`.

**Assembly Team** De conceptuele naam voor de verzameling backend-componenten (`PluginRegistry`, `WorkerBuilder`, `ConnectorFactory`) die samen de technische orkestratie van plugins en connectoren verzorgen.

**Atomic Writes (Journaling)** Een robuust state-saving mechanisme dat dataverlies bij een crash voorkomt door eerst naar een tijdelijk `.journal`\-bestand te schrijven alvorens het originele state-bestand te overschrijven.

**Backend-for-Frontend (BFF)** Een gespecialiseerde API-laag in de architectuur die als enige doel heeft om data te leveren in het exacte formaat dat de Web UI nodig heeft, wat de frontend-code aanzienlijk versimpelt.

**Blueprint (`run_blueprint.yaml`)** Verouderde term. Nu vervangen door `strategy_blueprint.yaml`.

**Circuit Breaker** Een veiligheidsmechanisme, typisch binnen een `ExecutionEnvironment`, dat bij aanhoudende (netwerk)problemen de strategie in een veilige, passieve modus plaatst om verdere schade te voorkomen.

**Clock** De component binnen een `ExecutionEnvironment` die de "hartslag" (ticks) van het systeem genereert, ofwel gesimuleerd uit historische data (`Backtest`) of real-time (`Live`/`Paper`).

**Configuratie-gedreven** Het kernprincipe dat het gedrag van de applicatie volledig wordt bestuurd door `YAML`\-configuratiebestanden, niet door hardgecodeerde logica.

**`connectors.yaml`** Configuratiebestand dat de technische details (incl. secrets) voor verbindingen met externe, **live** partijen (bv. exchanges) definieert.

**Contract-gedreven** Het kernprincipe dat alle data-uitwisseling en configuratie wordt gevalideerd door strikte schema's (Pydantic, TypeScript-interfaces).

**ContextBuilder** Verouderde term. De functionaliteit is nu onderdeel van de `ContextOperator`.

**ContextOrchestrator** Verouderde term. De verantwoordelijkheden zijn overgenomen door de `ContextOperator`.

**ContextOperator** De manager van de `ContextWorkers`. Luistert naar `MarketDataReceived`, orkestreert de executie van de `ContextWorker`\-pijplijn, en publiceert het resultaat als `ContextReady`. Vervangt de `ContextOrchestrator`.

**ContextWorker** De "Voorbereider". Een type plugin dat ruwe marktdata verrijkt met analytische context (bv. het berekenen van indicatoren).

**Correlation ID** Een unieke identifier (UUID) die wordt toegewezen aan een initieel event om de volledige levenscyclus van een handelsidee traceerbaar te maken door alle logs heen.

**`data_sources.yaml`** Configuratiebestand dat de catalogus van alle beschikbare **lokale** historische datasets (bv. Parquet-archieven) op schijf registreert.

**DTO (Data Transfer Object)** Een Pydantic `BaseModel` (bv. `Signal`) dat dient als een strikt contract voor data die als payload op de EventBus wordt doorgegeven.

**Entrypoints** De gespecialiseerde starter-scripts om de applicatie te draaien, zoals `run_operation.py`.

**`environments.yaml`** Configuratiebestand dat de "werelden" (`ExecutionEnvironments`) definieert en ze koppelt aan een `connector_id` of `data_source_id`.

**EventAdapter** Een generieke component die als "vertaler" fungeert tussen de EventBus en de (bus-agnostische) `Operator`\-componenten, gedirigeerd door de `wiring_map.yaml`.

**`event_map.yaml`** Configuratiebestand dat elke toegestane event-naam definieert en koppelt aan zijn verplichte DTO-contract.

**EventWiringFactory** De "meester-assembler" die tijdens het opstarten de `wiring_map.yaml` leest om alle `EventAdapters` te creëren en te configureren.

**ExecutionEnvironment** De technische definitie van een "wereld" waarin een strategie kan draaien (`Backtest`, `Paper`, of `Live`).

**ExecutionHandler** Verouderde term. De verantwoordelijkheden zijn overgenomen door de `ExecutionOperator`.

**ExecutionOperator** De manager van de `ExecutionWorkers` en de verwerker van `ExecutionApproved`\-events. Geeft de definitieve opdracht aan de `ExecutionEnvironment`. Vervangt de `ExecutionHandler`.

**ExecutionWorker** De "Uitvoerder". Een type plugin dat luistert naar specifieke triggers om **deterministische, op regels gebaseerde acties** direct uit te voeren.

**Feedback Loop (Strategisch)** De door de gebruiker bestuurde "Bouwen \-\> Meten \-\> Leren" cyclus, gefaciliteerd door de Web UI.

**Feedback Loop (Technisch)** De real-time feedback *binnen* een run, waarbij de staat van de `StrategyLedger` de input kan zijn voor de volgende cyclus.

**Heartbeat** Een mechanisme in een live dataverbinding om de gezondheid van de connectie te monitoren door te controleren op periodieke signalen van de server.

**Manifest (`plugin_manifest.yaml`)** De "ID-kaart" van een plugin. Bevat alle metadata die de `PluginRegistry` nodig heeft om de plugin te ontdekken en te valideren.

**Meta Workflows (`Optimization`, `VariantTest`)** Hoog-niveau operaties die de kern-executielogica herhaaldelijk en systematisch aanroepen voor complexe kwantitatieve analyses.

**MonitorOperator** De manager van de `MonitorWorkers`. Zorgt ervoor dat de juiste monitors worden aangeroepen als reactie op de relevante events (`ContextReady` of `LedgerStateChanged`).

**MonitorWorker** De "Waakhond". Een type plugin dat de staat van de operatie observeert en informatieve, **strategische events** publiceert, maar **nooit** zelf handelt.

**Operation** Het hoogste strategische niveau, gedefinieerd in een `operation.yaml`. Een verzameling van actieve `Strategy Blueprints` gekoppeld aan `ExecutionEnvironments`. Vervangt het `Portfolio`\-concept.

**`operation.yaml`** Het centrale "draaiboek" van de quant. Koppelt `Strategy Blueprints` aan `ExecutionEnvironments`. Vervangt het `portfolio.yaml`\-bestand.

**OptimizationService** De service die een grote parameterruimte systematisch doorzoekt door duizenden backtests parallel uit te voeren.

**ParallelRunService** Een herbruikbare backend-component die het efficiënt managen van een `multiprocessing`\-pool voor parallelle backtests verzorgt, ter ondersteuning van `Meta Workflows`.

**Platform (Het "Quant Operating System")** De fundamentele visie van S1mpleTrader als een agnostisch **besturingssysteem** dat een flexibel framework biedt voor plugins.

**`platform.yaml`** Configuratiebestand met globale, niet-strategische platforminstellingen.

**Plugin** De fundamentele, zelfstandige en testbare eenheid van businesslogica in het systeem, behorend tot een van de vier `Worker`\-categorieën.

**Plugin-First** De filosofie dat alle businesslogica wordt geïmplementeerd in de vorm van onafhankelijke, herbruikbare en testbare plugins.

**PluginRegistry** De specialistische klasse binnen het `Assembly Team` die verantwoordelijk is voor het scannen van de `plugins/`\-map en het valideren van alle manifesten.

**Portfolio** Verouderde term. De strategische rol is overgenomen door **`Operation`**, de financiële rol door **`StrategyLedger`**.

**Portfolio Blueprint** Verouderde term. Nu vervangen door `operation.yaml`.

**PortfolioSupervisor** Verouderde term. De verantwoordelijkheden zijn nu verdeeld over het `Operation`\-concept en de verschillende `Operators`.

**Pydantic** De Python-bibliotheek die wordt gebruikt voor datavalidatie en het definiëren van de data-contracten (DTO's, configuratie-schema's).

**RunOrchestrator** Verouderde term. Het opstartproces wordt nu direct gedreven door het uitvoeren van een `Operation`.

**`schedule.yaml`** Configuratiebestand dat de `Scheduler` configureert om op gezette tijden (interval of cron) specifieke, tijd-gebaseerde events te publiceren.

**Schema (`schema.py`)** Het bestand binnen een plugin dat het Pydantic-model bevat dat de configuratieparameters van die specifieke plugin definieert en valideert.

**State Reconciliation** Het "pull"-proces voor live-omgevingen waarbij de interne `StrategyLedger`\-staat periodiek wordt gevalideerd en gecorrigeerd tegen de "enige bron van waarheid": de exchange.

**Strategy Builder** De specifieke "werkruimte" in de Web UI waar een gebruiker visueel een `strategy_blueprint.yaml` kan samenstellen.

**`strategy_blueprint.yaml`** De gedetailleerde "receptenkaart". Beschrijft de volledige configuratie van plugins (`workforce`) en parameters voor één strategie. Vervangt het `run_blueprint.yaml`\-bestand.

**StrategyEngine** Verouderde term. De analytische logica is nu de verantwoordelijkheid van de `AnalysisOperator` en `AnalysisWorkers`.

**StrategyLedger** Het "domme grootboek". Een backend-component dat de financiële staat (kapitaal, posities, PnL) bijhoudt voor **één enkele, geïsoleerde strategie-run**.

**StrategyOperator** Verouderde term. De generieke rol is opgesplitst in de vier specifieke en functionele `Operators` (Context, Analysis, Monitor, Execution).

**StrategyWorker** Verouderde term. Nu vervangen door `AnalysisWorker`.

**Supervisor Model** Het crash-recovery mechanisme voor live trading, waarbij een extern "watchdog"-proces de hoofdapplicatie monitort en indien nodig herstart.

**Trade Explorer** De specifieke "werkruimte" in de Web UI die een diepgaande visuele analyse van de trades en de context van een voltooide run mogelijk maakt.

**TypeScript** De programmeertaal die voor de frontend wordt gebruikt om een type-veilig contract met de Pydantic-backend te garanderen via automatisch gegenereerde interfaces.

**VariantTestService** De service die een klein, gedefinieerd aantal strategie-varianten "head-to-head" met elkaar vergelijkt onder identieke marktomstandigheden.

**Worker (`worker.py`)** Het bestand binnen een plugin dat de Python-klasse met de daadwerkelijke businesslogica bevat.

**WorkerBuilder** De specialistische klasse binnen het `Assembly Team` die op aanvraag een geïnstantieerd en gevalideerd `worker`\-object bouwt.

**`wiring_map.yaml`** De "bouwtekening" van de dataflow. Beschrijft expliciet welke methode op welk component wordt aangeroepen als reactie op een specifiek event.

