# Bijlage A: Terminologie

Dit document dient als een uitgebreid naslagwerk voor alle kerntbegrippen, componenten en patronen binnen de S1mpleTrader V2-architectuur.

**9-Fasen Trechter/pijplijn:** De fundamentele, sequentiële en procedurele workflow binnen de ContextBuilder (fase 1-2) en StrategyEngine (fase 3-9).die een handelsidee stapsgewijs valideert en verrijkt, van `RegimeContext` tot `CriticalEventDetection`.
**Assembly Team:** De conceptuele naam voor de verzameling backend-componenten (`PluginRegistry`, `WorkerBuilder`, `ContextPipelineRunner`) die samen de technische orkestratie van plugins verzorgen.
**Atomic Writes (Journaling):** Het robuuste state-saving mechanisme dat dataverlies bij een crash voorkomt door eerst naar een tijdelijk `.journal`-bestand te schrijven.
**Backend-for-Frontend (BFF):** Een gespecialiseerde API-laag die data levert in het exacte formaat dat de Web UI nodig heeft, wat de frontend-code versimpelt.
**Blueprint (`run_blueprint.yaml`):** Een door de gebruiker gedefinieerd `YAML`-bestand dat een complete strategie-configuratie beschrijft, inclusief alle geselecteerde plugins en hun parameters.
**Circuit Breaker:** Een veiligheidsmechanisme in de `LiveEnvironment` dat, bij aanhoudende netwerkproblemen, de strategie in een veilige modus plaatst.
**Clock:** De component binnen een `ExecutionEnvironment` die de "hartslag" van het systeem genereert, ofwel gesimuleerd (voor backtests) of real-time.
**Configuratie-gedreven:** Het kernprincipe dat het gedrag van de applicatie wordt bestuurd door `YAML`-configuratiebestanden, niet door hardgecodeerde logica.
**Contract-gedreven:** Het kernprincipe dat alle data-uitwisseling wordt gevalideerd door strikte schema's (Pydantic voor de backend, TypeScript voor de frontend).
**ContextOrchestrator:** Het "stateful hart" van een actieve run in de Service-laag. Het beheert de "levende" `TradingContext` door marktdata te verrijken met de Fase 1-2 `ContextWorker`-plugins en publiceert een `ContextReady`-event voor elke tick.
**ContextBuilder:** De door de `ContextPipelineRunner` beheerde executie van `ContextWorker`-plugins (Fase 1 & 2), die de ruwe marktdata verrijkt tot een `enriched_df`.
**ContextWorker:** Een type plugin dat als doel heeft data of context toe te voegen aan de `DataFrame` (bv. het berekenen van een indicator zoals RSI of ADX).
**Correlation ID:** Een unieke identifier (UUID) die wordt toegewezen aan een `Signal` DTO om de volledige levenscyclus van een trade traceerbaar te maken door alle logs heen.
**DTO (Data Transfer Object):** Een Pydantic `BaseModel` (bv. `Signal`, `Trade`, `ClosedTrade`) dat dient als een strikt contract voor data die tussen componenten wordt doorgegeven.
**Entrypoints:** De drie gespecialiseerde starter-scripts: `run_web.py` (voor de UI), `run_supervisor.py` (voor live trading), en `run_backtest_cli.py` (voor automatisering).
**ExecutionEnvironment:** De backend-laag die de "wereld" definieert waarin een strategie draait (`Backtest`, `Paper`, of `Live`).
**ExecutionHandler:** De component binnen een `ExecutionEnvironment` die verantwoordelijk is voor het daadwerkelijk uitvoeren van `Trade` DTO's (gesimuleerd of via een echte broker).
**Feedback Loop (Strategisch):** De door de gebruiker bestuurde "Bouwen -> Meten -> Leren" cyclus, gefaciliteerd door de Web UI.
**Feedback Loop (Technisch):** De real-time feedback *binnen* een run, waarbij de staat van het `Portfolio` wordt gebruikt als input voor de `Portfolio Overlay`-plugins.
**Heartbeat:** Een mechanisme in de `LiveDataSource` om de gezondheid van een live dataverbinding te monitoren door te controleren op periodieke signalen van de server.
**Manifest (`plugin_manifest.yaml`):** De "ID-kaart" van een plugin. Dit `YAML`-bestand bevat alle metadata die de `PluginRegistry` nodig heeft om de plugin te ontdekken en te begrijpen.
**Meta Workflows:** Hoog-niveau services (`OptimizationService`, `VariantTestService`) die de `StrategyOperator` herhaaldelijk aanroepen voor complexe analyses.
**OptimizationService:** De service die een grote parameterruimte systematisch doorzoekt door duizenden backtests parallel uit te voeren.
**ParallelRunService:** Een herbruikbare backend-component die het efficiënt managen van een `multiprocessing`-pool voor parallelle backtests verzorgt.
**Plugin:** De fundamentele, zelfstandige en testbare eenheid van logica in het systeem, bestaande uit een `manifest`, `worker` en `schema`.
**PluginRegistry:** De specialistische klasse binnen het `Assembly Team` die verantwoordelijk is voor het scannen van de `plugins/`-map en het valideren van alle manifesten.
**Portfolio:** De backend-component die fungeert als het "domme grootboek" en de financiële staat van het systeem (kapitaal, posities, orders) bijhoudt.
**PortfolioSupervisor:** De "operationeel manager" in de Service-laag. Dit is de eigenaar van de levenscyclus van alle actieve strategieën en agenten en de hoogste risicomanager die handelsvoorstellen goed- of afkeurt.
**Pydantic:** De Python-bibliotheek die wordt gebruikt voor datavalidatie en het definiëren van de data-contracten via `BaseModel`-klassen.
**RunOrchestrator:** Een lichtgewicht "facilitator" in de Service-laag, geïnstantieerd per strategie. Zijn enige taak is het opzetten van de benodigde specialisten voor één run en het publiceren van de initiële `RunStarted`-event.
**Schema (`schema.py`):** Het bestand binnen een plugin dat het Pydantic-model bevat dat de configuratieparameters van die specifieke plugin definieert en valideert.
**State Reconciliation:** Het cruciale proces na een netwerk-reconnect waarbij de interne `Portfolio`-staat wordt gesynchroniseerd met de 'single source of truth': de exchange.
**Strategy Builder:** De "werkruimte" in de Web UI waar een gebruiker visueel een strategie kan samenstellen door plugins te selecteren en te configureren.
**StrategyEngine:** De stateless "analytische motor" in de Backend-laag. Voert het analytische gedeelte van de 9-fasen trechter uit (Fase 3-9) in reactie op een aanroep en produceert een `EngineCycleResult` (een analytisch voorstel) zonder kennis van de EventBus.
**StrategyOperator:** Een "analytische specialist" en schone brug in de Service-laag. Het abonneert zich op ContextReady, roept procedureel de StrategyEngine (uit de Backend-laag) aan, en publiceert het resultaat als een StrategyProposalReady-event.
**StrategyWorker:** Een type plugin dat wordt gebruikt in de besluitvormingsfases (3-6) van de trechter en die opereert op DTO's in plaats van de `DataFrame`.
**Supervisor Model:** Het crash-recovery mechanisme voor live trading, waarbij een lichtgewicht "watchdog"-proces de `StrategyOperator` monitort en herstart.
**Trade Explorer:** De "werkruimte" in de Web UI die een diepgaande visuele analyse van de trades en de context van een enkele backtest-run mogelijk maakt.
**TypeScript:** De programmeertaal die voor de frontend wordt gebruikt om een type-veilig contract met de Pydantic-backend te garanderen via automatisch gegenereerde interfaces.
**VariantTestService:** De service die een klein, gedefinieerd aantal strategie-varianten "head-to-head" met elkaar vergelijkt onder identieke marktomstandigheden.
**Worker (`worker.py`):** Het bestand binnen een plugin dat de Python-klasse met de daadwerkelijke businesslogica bevat.
**WorkerBuilder:** De specialistische klasse binnen het `Assembly Team` die op aanvraag een geïnstantieerd en gevalideerd `worker`-object bouwt.