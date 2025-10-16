# 0_S1MPLETRADER_V2_DEVELOPMENT.md

# **S1mpleTrader V2 Development: Architectonische Blauwdruk**

Versie: 2.0 (Architectuur Blauwdruk v4)  
Status: Definitief

## **Voorwoord: Kernfilosofie - Het Platform als Framework**

Welkom bij de architectonische blauwdruk voor S1mpleTrader V2. Dit document dient als de centrale gids voor een systeem dat is geëvolueerd van een applicatie naar een agnostisch **besturingssysteem** voor kwantitatieve strategen.

De kernvisie is dat het platform zelf geen specifieke manier van handelen afdwingt. Zijn enige doel is het bieden van een extreem robuust, flexibel en schaalbaar **framework**. Binnen dit framework kan een quant alle mogelijke kwantitatieve en operationele functionaliteit implementeren via zelfstandige, specialistische plugins. De configuratie is het draaiboek; de plugins zijn de acteurs; het platform is het podium.

Deze documentatie beschrijft de architectuur die deze visie mogelijk maakt.

## **De Architectuur in Hoofdstukken**

### **Hoofdstuk 1: De Communicatie Architectuur**

De kern van de V2-architectuur is de radicale scheiding tussen business- en communicatielogica. Dit hoofdstuk beschrijft het EventAdapter-patroon en de rol van de wiring_map.yaml, die samen het "zenuwstelsel" van het platform vormen.

**→ Lees de volledige uitwerking in: system/1_BUS_COMMUNICATION_ARCHITECTURE.md**

### **Hoofdstuk 2: Architectuur & Componenten**

Dit hoofdstuk beschrijft de strikt gelaagde opbouw (Backend, Service, Frontend) en introduceert de vier functionele pijlers die de basis vormen van alle logica: Context, Analysis, Monitor, en Execution.

**→ Lees de volledige uitwerking in: system/2_ARCHITECTURE.md**

### **Hoofdstuk 3: De Configuratie Trein**

Configuratie is koning in V2. Dit document is een gedetailleerde gids voor de volledige hiërarchie van YAML-bestanden, van platform.yaml tot plugin_manifest.yaml, die samen een volledige Operation definiëren.

**→ Lees de volledige uitwerking in: system/3_DE_CONFIGURATIE_TREIN.md**

### **Hoofdstuk 4: De Anatomie van een Plugin**

Een plugin is de fundamentele, zelfstandige en testbare eenheid van logica. Dit hoofdstuk beschrijft de mappenstructuur, het manifest.yaml, het schema.py en de vier verschillende types plugins (ContextWorker, AnalysisWorker, etc.).

**→ Lees de volledige uitwerking in: system/4_DE_PLUGIN_ANATOMIE.md**

### **Hoofdstuk 5: De Analytische Pijplijn**

De kern van elke analytische strategie is de pijplijn die een idee stapsgewijs valideert. Dit hoofdstuk beschrijft de interne, procedurele 9-fasen trechter die wordt uitgevoerd door de ContextOperator en AnalysisOperator.

**→ Lees de volledige uitwerking in: system/5_DE_ANALYTISCHE_PIJPLIJN.md**

### **Hoofdstuk 6: Robuustheid & Operationele Betrouwbaarheid**

Een live trading-systeem moet veerkrachtig zijn. Dit hoofdstuk beschrijft de verdedigingslinies: atomische schrijfacties (journaling), protocollen voor netwerkveerkracht, en het Supervisor-model voor crash recovery.

**→ Lees de volledige uitwerking in: system/6_RESILIENCE_AND_OPERATIONS.md**

### **Hoofdstuk 7: Ontwikkelstrategie & Tooling**

Dit document beschrijft de workflow en tooling, van de visuele 'Strategy Builder' tot de 'Trade Explorer' en de cruciale rol van de Correlation ID voor traceerbaarheid.

**→ Lees de volledige uitwerking in: system/7_DEVELOPMENT_STRATEGY.md**

### **Hoofdstuk 8: Meta Workflows**

Bovenop de executie van een enkele strategie draaien "Meta Workflows" om geavanceerde analyses uit te voeren. Dit hoofdstuk beschrijft de OptimizationService en VariantTestService.

**→ Lees de volledige uitwerking in: system/8_META_WORKFLOWS.md**

### **Hoofdstuk 9: Coding Standaarden & Design Principles**

Een consistente codebase is essentieel. Dit hoofdstuk beschrijft de verplichte standaarden (PEP 8, Type Hinting) en de kern design principles (SOLID, Factory Pattern, DTO's).

**→ Lees de volledige uitwerking in: system/9_CODING_STANDAARDS_DESIGN_PRINCIPLES.md**

## **Bijlages**

* **Bijlage A: Terminologie**: Een uitgebreid, alfabetisch naslagwerk met beschrijvingen van alle belangrijke concepten en componenten.  
* **Bijlage B: Openstaande Vraagstukken**: Een overzicht van bekende "onbekenden" die tijdens de implementatie verder onderzocht moeten worden.  
* **Bijlage C: MVP**: De scope en componenten van het Minimum Viable Product.  
* **Bijlage D: Plugin IDE**: De architectuur en UX voor de web-based IDE voor plugins.

---

# 1_BUS_COMMUNICATION_ARCHITECTURE v2.md

# **1. S1mpleTrader V2: De Communicatie Architectuur**

Versie: 2.1 (Gecorrigeerd & Aangevuld)  
Status: Definitief

## **1.1. Visie & Filosofie: Scheiding van Logica**

### **1.1.1. Inleiding & Doel**

Dit document beschrijft de communicatie-architectuur van S1mpleTrader V2. De kern van dit ontwerp is niet simpelweg het gebruik van een event-gedreven model, maar de **radicale scheiding tussen businesslogica en communicatielogica**.

Het doel is een systeem te creëren waarin de componenten die de daadwerkelijke strategie- en businesslogica bevatten (Operators) volledig puur, agnostisch en onwetend zijn van het communicatiemechanisme (de EventBus).

### **1.1.2. De Filosofie: Bus-Agnostische Componenten**

In deze architectuur is een Operator (bv. de AnalysisOperator) een pure Python-klasse. Zijn taak is het uitvoeren van een specifieke business-taak: hij accepteert een DTO (Data Transfer Object) als input en retourneert een DTO als output. Hij weet niets van "subscriben" of "publishen".

De volledige verantwoordelijkheid voor de communicatie met de EventBus wordt gedelegeerd aan een generieke tussenlaag: het **EventAdapter Patroon**.

## **1.2. De Architectuur: Het EventAdapter Patroon**

### **1.2.1. De EventAdapter als Vertaler**

De EventAdapter is een generieke, herbruikbare "vertaler" wiens enige taak het is om een brug te slaan tussen de EventBus en een pure business-component (Operator). Zijn gedrag wordt niet in code, maar in configuratie gedefinieerd via de wiring_map.yaml.

**Voorbeeld van een wiring_map.yaml-regel:**

# wiring_map.yaml  
- adapter_id: "AnalysisPipelineAdapter"  
  listens_to: "ContextReady"  
  invokes:  
    component: "AnalysisOperator"  
    method: "run_pipeline"  
  publishes_result_as: "StrategyProposalReady"

Deze regel instrueert het systeem om:

1. Een EventAdapter te creëren.  
2. Deze adapter te laten luisteren naar het ContextReady-event.  
3. Wanneer dat event binnenkomt, de run_pipeline()-methode van de AnalysisOperator aan te roepen met de event-payload.  
4. Als de methode een resultaat teruggeeft, dit resultaat te publiceren op de bus onder de naam StrategyProposalReady.

### **1.2.2. De Rol van de EventWiringFactory**

Tijdens het opstarten van de applicatie leest de EventWiringFactory de volledige wiring_map.yaml. Voor elke regel in de map creëert en configureert het een EventAdapter-instantie en abonneert deze op de EventBus.

## **1.3. De Levenscyclus in de Praktijk**

### **1.3.1. De Bootstrap Fase (Het "Bedraden" van het Systeem)**

1. De gebruiker start een Operation via een entrypoint.  
2. De applicatie laadt de volledige "Configuratie Trein".  
3. De **ComponentBuilder** (onderdeel van het Assembly Team) instantieert alle benodigde, pure business-componenten (Operators en Workers).  
4. De **ContextBootstrapper** zorgt voor het vullen van de initiële, rijke context *voordat* de Operation live gaat.  
5. De **EventWiringFactory** leest de wiring_map.yaml en creëert de EventAdapters, die zich abonneren op de EventBus.  
6. Het OperationStarted-event wordt gepubliceerd. Het systeem is nu "live".

### **1.3.2. Een Runtime Voorbeeld (De Tick-Loop)**

1. Een ExecutionEnvironment publiceert een MarketDataReceived-event.  
2. De **EventAdapter** voor de ContextOperator wordt geactiveerd.  
3. De adapter roept de run_pipeline()-methode van de ContextOperator aan.  
4. De ContextOperator retourneert een TradingContext DTO.  
5. De adapter publiceert dit resultaat als een ContextReady-event.  
6. **Parallel** worden nu alle adapters wakker die luisteren naar ContextReady (voor de AnalysisOperator, MonitorWorker, etc.), en de cyclus herhaalt zich.

## **1.4. De Event Map: De Grondwet van de Communicatie**

De event_map.yaml definieert alle toegestane events en hun contracten.

| Event Naam | Payload (DTO Contract) | Mogelijke Publisher(s) | Mogelijke Subscriber(s) |
| :---- | :---- | :---- | :---- |
| **Operation Lifecycle** |  |  |  |
| OperationStarted | OperationParameters | Operations | EventAdapter (voor ContextOperator), ContextBootstrapper |
| BootstrapComplete | BootstrapResult | ContextBootstrapper | ExecutionEnvironment |
| ShutdownRequested | ShutdownSignal | UI, EventAdapter (van MonitorWorker) | Operations |
| OperationFinished | OperationSummary | Operations | ResultLogger, UI |
| --- | --- | --- | --- |
| **Tick Lifecycle** |  |  |  |
| MarketDataReceived | MarketSnapshot | ExecutionEnvironment | EventAdapter (voor ContextOperator) |
| ContextReady | TradingContext | EventAdapter (van ContextOperator) | EventAdapter (voor AnalysisOperator, MonitorWorker, ExecutionWorker) |
| StrategyProposalReady | EngineCycleResult | EventAdapter (van AnalysisOperator) | EventAdapter (voor ExecutionOperator) |
| ExecutionApproved | List[ExecutionDirective] | EventAdapter (van ExecutionOperator) | ExecutionEnvironment |
| --- | --- | --- | --- |
| **State & Monitoring Lifecycle** |  |  |  |
| LedgerStateChanged | LedgerState | ExecutionEnvironment | EventAdapter (voor MonitorWorker) |
| AggregatePortfolioUpdated | AggregateMetrics | EventAdapter (van MonitorWorker) | EventAdapter (voor ExecutionWorker), UI |
| --- | --- | --- | --- |
| **Analyse Lifecycle** |  |  |  |
| BacktestCompleted | BacktestResult | Operations | ResultLogger, UI |



---

# 2_ARCHITECTURE v2.md

# **2. Architectuur & Componenten**

Versie: 2.1 (Gecorrigeerd & Aangevuld)  
Status: Definitief

## **2.1. De Configuratie: De Bron van Waarheid**

De S1mpleTrader V2 architectuur is fundamenteel **configuratie-gedreven**. De YAML-bestanden zijn niet slechts instellingen; ze vormen het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft.

Een gedetailleerde gids over de hiërarchie, de rol van elk bestand en hun onderlinge samenhang is vastgelegd in een apart document om dit hoofdstuk gefocust te houden op de softwarecomponenten.

**→ Lees de volledige uitwerking in: system/3_DE_CONFIGURATIE_TREIN.md**

## **2.2. De Gelaagde Architectuur: Een Strikte Scheiding**

De applicatie is opgebouwd uit drie strikt gescheiden lagen die een **eenrichtingsverkeer** van afhankelijkheden afdwingen.

* **Backend Laag (/backend)**: De **"Motor & Gereedschapskist"**. Bevat alle herbruikbare, agnostische en pure businesslogica (klassen, DTO's, interfaces). Deze laag is volledig onafhankelijk en heeft geen kennis van de Service Laag of de EventBus. Het is een pure, importeerbare library.  
* **Service Laag (/services)**: De **"Orkestratielaag"**. Dit is de enige laag die de EventBus kent en beheert via de EventAdapters. Componenten hier orkestreren complete business workflows door de "gereedschappen" uit de Backend-laag aan te roepen in reactie op events.  
* **Frontend Laag (/frontends)**: De **"Gebruikersinterface"**. Verantwoordelijk voor alle gebruikersinteractie en communiceert uitsluitend met de Service Laag via een BFF (Backend-for-Frontend) API.

## **2.3. De Functionele Pijlers: De Vier Rollen**

Alle businesslogica in het systeem is ondergebracht in vier duidelijk gescheiden, functionele categorieën. Elke categorie bestaat uit een **Worker** (de plugin met de daadwerkelijke logica) en een **Operator** (de manager in de Service Laag die de workers aanstuurt).

| Quant's Doel | Hoofdverantwoordelijkheid | Plugin Categorie (De "Worker") | De Manager (De "Operator") |
| :---- | :---- | :---- | :---- |
| "Ik wil mijn data voorbereiden" | **Contextualiseren** | ContextWorker | ContextOperator |
| "Ik wil een handelsidee ontwikkelen" | **Analyseren** | AnalysisWorker | AnalysisOperator |
| "Ik wil de situatie in de gaten houden" | **Monitoren** | MonitorWorker | MonitorOperator |
| "Ik wil een regel direct laten uitvoeren" | **Executeren** | ExecutionWorker | ExecutionOperator |

## **2.4. Componenten in Detail**

### **Context Pijler (Voorbereiden)**

* **ContextWorker (Plugin, Backend)**: Verrijkt ruwe marktdata met analytische context (indicatoren, marktstructuur, etc.).  
* **ContextOperator (Service Laag)**: Orkestreert de executie van de ContextWorker-pijplijn.

### **Analysis Pijler (Analyseren)**

* **AnalysisWorker (Plugin, Backend)**: Genereert **niet-deterministische, analytische handelsvoorstellen**.  
* **AnalysisOperator (Service Laag)**: Orkestreert de AnalysisWorker-pijplijn.

### **Monitor Pijler (Monitoren)**

* **MonitorWorker (Plugin, Backend)**: Observeert de operatie en publiceert informatieve, **strategische events**. Handelt **nooit** zelf.  
* **MonitorOperator (Service Laag)**: Zorgt ervoor dat de juiste MonitorWorkers worden aangeroepen.

### **Execution Pijler (Executeren)**

* **ExecutionWorker (Plugin, Backend)**: Voert **deterministische, op regels gebaseerde acties** uit.  
* **ExecutionOperator (Service Laag)**: Keurt voorstellen goed en geeft de definitieve opdracht aan de ExecutionEnvironment.

### **Ondersteunende Componenten**

* **ComponentBuilder (Backend Laag)**: Een specialist binnen het Assembly Team. Verantwoordelijk voor het lezen van de strategy_blueprint.yaml en het daadwerkelijk assembleren en instantiëren van alle benodigde Operator- en Worker-componenten voor een specifieke strategy_link. Dit is de opvolger van de RunOrchestrator.  
* **ContextBootstrapper (Backend Laag)**: Een essentieel component dat ervoor zorgt dat de ContextOperator een compleet en historisch correct "rollend venster" van data heeft *voordat* de eerste live tick wordt verwerkt. Dit voorkomt beslissingen op basis van onvolledige data.  
* **ExecutionEnvironment (Backend Laag)**: De technische "wereld" waarin een strategie draait (Backtest, Paper, of Live). Verantwoordelijk voor marktdata en het uitvoeren van trades.  
* **StrategyLedger (Backend Laag)**: Het "domme" financiële grootboek dat de staat (kapitaal, posities, PnL) bijhoudt voor één enkele, geïsoleerde strategie-run.  
* **Assembly Team (Backend Laag)**: De verzameling componenten (PluginRegistry, WorkerBuilder, ComponentBuilder) die verantwoordelijk is voor het ontdekken, valideren en bouwen van alle plugins en componenten.

---

# 3_DE_CONFIGURATIE_TREIN v1.3.md

# **3. De Configuratie Trein: Een Gids voor S1mpleTrader V2 YAML-bestanden**

Versie: 1.3 (Detailniveau Hersteld)  
Status: Definitief

## **3.1. Voorwoord: De Bron van Waarheid**

In de S1mpleTrader V2 architectuur is de configuratie koning. De YAML-bestanden zijn niet slechts instellingen; ze zijn het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft. Het platform zelf is een agnostische uitvoerder die tot leven komt op basis van deze bestanden.

Dit document beschrijft de "configuratie trein": de logische hiërarchie en samenhang van de verschillende YAML-bestanden die samen een volledige, gevalideerde en uitvoerbare operatie definiëren. We volgen de stroom van de meest stabiele, platform-brede bestanden tot de meest specifieke, gedetailleerde plugin-parameters.

## **3.2. Het Landschap van de Configuratie**

De configuratie is opgedeeld in een reeks van gespecialiseerde bestanden. Elk bestand heeft een duidelijke Single Responsibility (SRP).

**De Hiërarchie (van Stabiel naar Dynamisch):**

1. **platform.yaml**: De fundering van het hele platform.  
2. **connectors.yaml**: De technische "stekkerdoos" voor **live** verbindingen.  
3. **data_sources.yaml**: De catalogus van **lokale** historische datasets.  
4. **environments.yaml**: De definitie van de abstracte "werelden".  
5. **event_map.yaml**: De grondwet van de interne communicatie.  
6. **wiring_map.yaml**: De bouwtekening van de dataflow.  
7. **schedule.yaml**: De agnostische "metronoom" van het systeem.  
8. **operation.yaml**: Het centrale "draaiboek" van de quant.  
9. **strategy_blueprint.yaml**: De gedetailleerde "receptenkaart".  
10. **plugin_manifest.yaml**: De "ID-kaart" van elke individuele plugin.

## **3.3. De Platform- & Systeemarchitectuur**

Deze bestanden vormen de stabiele basis. Ze worden doorgaans één keer opgezet en veranderen zelden.

### **3.3.1. platform.yaml - De Fundering**

* **Doel**: Definieert globale, niet-strategische instellingen voor het hele platform. Dit is het domein van de platformbeheerder, niet van de quant.  
* **Inhoud**:  
  * **Logging-profielen**: Definieert welke log-niveaus worden getoond (developer, analysis).  
  * **Taalinstellingen**: Bepaalt de standaardtaal voor de UI en logs.  
  * **Archiveringsformaat**: Bepaalt of resultaten worden opgeslagen als csv, parquet, etc.  
  * **Bestandspaden**: Definieert de root-locatie van de plugins-map.  
* **Voorbeeld (Conceptueel)**:  
  # config/platform.yaml  
  language: "nl"  
  logging:  
    profile: "analysis"  
    profiles:  
      developer: [INFO, WARNING, ERROR]  
      analysis: [DEBUG, INFO, SETUP, MATCH, FILTER, RESULT, TRADE, ERROR]  
  archiving:  
    format: "parquet"  
  plugins_root_path: "plugins"

### **3.3.2. connectors.yaml - De Stekkerdoos**

* **Doel**: Centraliseert de technische configuratie van **alle** mogelijke verbindingen met externe, **live** partijen (exchanges).  
* **Inhoud**: Een lijst van benoemde connector-instanties. Elke instantie heeft een unieke naam (de *identifier*), een type (die de ConnectorFactory vertelt welke Python-klasse hij moet gebruiken), en de benodigde credentials en API-eindpunten.  
* **Voorbeeld (Conceptueel)**:  
  # config/connectors.yaml  
  kraken_live_eur_account:  
    type: "kraken_private"  
    api_key: "${KRAKEN_API_KEY}"  
    api_secret: "${KRAKEN_API_SECRET}"

  binance_paper_trading:  
    type: "binance_public"  
    base_url: "[https://testnet.binance.vision/api](https://testnet.binance.vision/api)"

### **3.3.3. data_sources.yaml - De Archievenkast**

* **Doel**: Centraliseert de definitie van alle beschikbare, op schijf opgeslagen, **historische datasets** (archieven). Dit creëert een register van alle "backtest-werelden".  
* **Inhoud**: Een lijst van benoemde data sources. Elke data source heeft een unieke naam (de *identifier*) en specificaties over de fysieke locatie en het type data.  
* **Voorbeeld (Conceptueel)**:  
  # config/data_sources.yaml  
  btc_eur_15m_archive:  
    type: "parquet_archive"  
    path: "source_data/BTC_EUR_15m/"  
    asset_pair: "BTC/EUR"  
    timeframe: "15m"

### **3.3.4. environments.yaml - De Werelden**

* **Doel**: Definieert de operationele "werelden" (live, paper, backtest) en koppelt ze aan een technische bron.  
* **Inhoud**: Een lijst van benoemde omgevingen met een unieke naam, een type, en een verwijzing naar ofwel een connector_id ofwel een data_source_id.  
* **Voorbeeld (Conceptueel)**:  
  # config/environments.yaml  
  live_kraken_main:  
    type: "live"  
    connector_id: "kraken_live_eur_account" # VERWIJST NAAR connectors.yaml

  backtest_2020_2024_btc:  
    type: "backtest"  
    data_source_id: "btc_eur_15m_archive" # VERWIJST NAAR data_sources.yaml

### **3.3.5. event_map.yaml - De Grondwet van de Communicatie**

* **Doel**: Functioneert als de strikte "Grondwet" voor alle communicatie op de EventBus. Het definieert welke events mogen bestaan en wat hun exacte data-contract is.  
* **Inhoud**: Een lijst van alle toegestane event-namen met hun verplichte payload_dto-contract.  
* **Voorbeeld (Conceptueel)**:  
  # config/event_map.yaml  
  - event_name: "OperationStarted"  
    payload_dto: "OperationParameters"  
  - event_name: "ContextReady"  
    payload_dto: "TradingContext"

### **3.3.6. wiring_map.yaml - De Bouwtekening van de Dataflow**

* **Doel**: De "bouwtekening" die beschrijft hoe Operators via EventAdapters op de EventBus worden aangesloten. Het definieert de dataflow: welk event triggert welke actie?  
* **Inhoud**: Een lijst van "wiring"-regels die een component en method koppelen aan een listens_to event, en specificeren hoe het resultaat gepubliceerd wordt (publishes_result_as).  
* **Voorbeeld (Conceptueel)**:  
  # config/wiring_map.yaml  
  - adapter_id: "ContextPipelineAdapter"  
    listens_to: "MarketDataReceived"  
    invokes:  
      component: "ContextOperator"  
      method: "run_pipeline"  
    publishes_result_as: "ContextReady"

### **3.3.7. schedule.yaml - De Metronoom**

* **Doel**: Configureert de Scheduler service voor alle tijd-gebaseerde events.  
* **Inhoud**: Een lijst van event-definities, elk met een event_name en een type (interval of cron).  
* **Voorbeeld (Conceptueel)**:  
  # config/schedule.yaml  
  schedule:  
    - event_name: "five_minute_reconciliation_tick"  
      type: "interval"  
      value: "5m"  
    - event_name: "daily_dca_buy_signal"  
      type: "cron"  
      value: "0 9 * * *"  
      timezone: "Europe/Amsterdam"

## **3.4. De Operationele Configuratie**

Deze bestanden beschrijven de **strategische en operationele intentie** van de quant.

### **3.4.1. operation.yaml - Het Centrale Draaiboek**

* **Doel**: Het **hoofdbestand** dat een volledige operatie definieert door strategy_links te creëren die blueprints aan environments koppelen.  
* **Inhoud**: Een display_name, description, en een lijst van strategy_links, elk met een strategy_blueprint_id en een execution_environment_id.  
* **Voorbeeld (Conceptueel)**:  
  # config/operations/my_btc_operation.yaml  
  display_name: "Mijn BTC Operatie (Live & Backtest)"  
  description: "Draait een FVG-strategie live en backtest een nieuwe mean-reversion strategie."  
  strategy_links:  
    - strategy_blueprint_id: "live_fvg_strategy"  
      execution_environment_id: "live_kraken_main"  
      is_active: true

    - strategy_blueprint_id: "experimental_mean_reversion"  
      execution_environment_id: "backtest_2020_2024_btc"  
      is_active: true

### **3.4.2. strategy_blueprint.yaml - Het Gedetailleerde Recept**

* **Doel**: Bevat de **volledige configuratie van alle plugins** (workforce) voor één strategy_link.  
* **Inhoud**: Een workforce-sectie die, gegroepeerd per plugin-categorie, de parameters voor elke individuele plugin definieert.  
* **Voorbeeld (Conceptueel)**:  
  # config/strategy_blueprints/live_fvg_strategy.yaml  
  display_name: "Live FVG Entry Strategy"  
  workforce:  
    context_workers:  
      ema_detector_fast: { plugin_name: "ema_detector", params: { period: 50 } }  
    analysis_workers:  
      fvg_entry: { plugin_name: "fvg_entry_detector", params: { fvg_min_size_pct: 0.1 } }  
    monitor_workers:  
      daily_drawdown: { plugin_name: "max_drawdown_monitor", params: { max_drawdown_pct: 5.0 } }  
    execution_workers:  
      emergency_exit: { plugin_name: "emergency_exit_agent", params: { listens_to_event: "MAX_DRAWDOWN_BREACHED" } }

## **3.5. De Plugin-Configuratie**

Deze bestanden zijn onderdeel van de plugin zelf en maken hem vindbaar en configureerbaar.
### **3.5.1. plugin_manifest.yaml - De ID-kaart**

* **Doel**: Maakt een plugin **ontdekbaar en begrijpelijk** voor het Assembly Team.  
* **Inhoud**: identification (incl. type), dependencies, en produces_events voor MonitorWorkers.  
* **Voorbeeld (Conceptueel)**:  
  # plugins/monitor_workers/max_drawdown_monitor/manifest.yaml  
  identification:  
    name: "max_drawdown_monitor"  
    type: "monitor_worker"  
  dependencies:  
    produces_events:  
      - "MAX_DRAWDOWN_BREACHED"

## **3.6. De Onderlinge Samenhang - De "Configuratie Trein" in Actie**

De magie van het systeem zit in hoe Operations deze bestanden aan elkaar koppelt tijdens de bootstrap-fase.

1. **Startpunt**: De gebruiker start de applicatie met de opdracht: run my_btc_operation.  
2. **Operations leest operation.yaml**: Hij vindt de strategy_link voor experimental_mean_reversion.  
3. **Analyse van de Link**:  
   * Operations kijkt naar de execution_environment_id: backtest_2020_2024_btc.  
   * Hij zoekt in **environments.yaml** en vindt backtest_2020_2024_btc. Hij ziet dat dit een backtest-omgeving is die data_source_id: btc_eur_15m_archive vereist.  
   * Hij zoekt nu in **data_sources.yaml** en vindt btc_eur_15m_archive. Hij heeft nu alle technische details (pad, type) om de BacktestEnvironment en zijn DataSource te bouwen.  
   * Vervolgens kijkt Operations naar de strategy_blueprint_id: experimental_mean_reversion.  
   * Hij laadt **strategy_blueprints/experimental_mean_reversion.yaml** en ziet de volledige workforce.  
   * Voor elke plugin in de workforce, gebruikt het Assembly Team de **manifest.yaml** van die plugin om de code te vinden en de params uit de blueprint te valideren tegen de schema.py.  
4. **Herhaling**: Operations herhaalt dit proces voor de live_fvg_strategy-link, maar volgt nu het pad via environments.yaml naar **connectors.yaml** om de LiveEnvironment te bouwen.  
5. **Afronding**: Operations laadt tot slot schedule.yaml, event_map.yaml en wiring_map.yaml om de Scheduler en de volledige "bedrading" van de EventBus te configureren.

Het resultaat is een volledig geassembleerd, gevalideerd en onderling verbonden ecosysteem van plugins, klaar om van start te gaan, puur en alleen op basis van de declaratieve YAML-bestanden.

---

# 4_DE_PLUGIN_ANATOMIE.md

# **4. De Anatomie van een Plugin**

Versie: 2.2 (Details Hersteld & Aangevuld)  
Status: Definitief  
Dit document beschrijft de gedetailleerde structuur en de technische keuzes achter de plugins in de S1mpleTrader V2 architectuur. Plugins zijn de specialistische, onafhankelijke en testbare bouwstenen van elke Operation.

## **4.1. Fundamentele Mappenstructuur**

Elke plugin is een opzichzelfstaande Python package. Deze structuur garandeert dat logica, contracten en metadata altijd bij elkaar blijven, wat essentieel is voor het "Plugin First" principe.

plugins/[plugin_naam]/  
├── manifest.yaml         # De ID-kaart (wie ben ik?)  
├── worker.py             # De Logica (wat doe ik?)  
├── schema.py             # Het Contract (wat heb ik nodig?)  
├── context_schema.py     # Het visuele contract (wat kan ik laten zien?)  
└── test/test_worker.py   # De Kwaliteitscontrole (werk ik correct?)

* **manifest.yaml**: De "ID-kaart" van de plugin. Dit bestand maakt de plugin vindbaar en begrijpelijk voor het Assembly Team.  
* **worker.py**: Bevat de Python-klasse met de daadwerkelijke businesslogica van de plugin.  
* **schema.py**: Bevat het Pydantic-model dat de structuur en validatieregels voor de configuratieparameters (params) van de plugin definieert.  
* **context_schema.py**: Bevat het concrete context model voor de visualisatie van gegevens die de plugin produceert. Dit is cruciaal voor de "Trade Explorer" in de frontend.  
* **test/test_worker.py**: Dit bestand bevat de verplichte unit tests voor het valideren van de werking van de plugin. Een 100% score als uitkomst van pytest is noodzakelijk voor de succesvolle "enrollment" van een nieuwe plugin.

## **4.2. Formaat Keuzes: YAML vs. JSON**

De keuze voor een dataformaat hangt af van de primaire gebruiker: **een mens of een machine**. We hanteren daarom een hybride model om zowel leesbaarheid als betrouwbaarheid te maximaliseren.

* **YAML voor Menselijke Configuratie**  
  * **Toepassing:** manifest.yaml en alle door de gebruiker geschreven strategy_blueprint.yaml en operation.yaml-bestanden.  
  * **Waarom:** De superieure leesbaarheid, de mogelijkheid om commentaar toe te voegen, en de flexibelere syntax zijn essentieel voor ontwikkelaars en strategen die deze bestanden handmatig schrijven en onderhouden.  
* **JSON voor Machine-Data**  
  * **Toepassing:** Alle machine-gegenereerde data, zoals API-responses, state-bestanden, en gestructureerde logs.  
  * **Waarom:** De strikte syntax en universele portabiliteit maken JSON de betrouwbare standaard voor communicatie tussen systemen en voor het opslaan van gestructureerde data waar absolute betrouwbaarheid vereist is.

## **4.3. Het Manifest: De Zelfbeschrijvende ID-kaart**

Het manifest.yaml is de kern van het "plugin discovery" mechanisme. Het stelt het Assembly Team in staat om een plugin volledig te begrijpen **zonder de Python-code te hoeven inspecteren**. Dit manifest is een strikt contract dat alle cruciale metadata van een plugin vastlegt.

### **4.3.1. Identification**

De identification-sectie bevat alle beschrijvende metadata.

* **name**: De unieke, machine-leesbare naam (bv. market_structure_detector).  
* **display_name**: De naam zoals deze in de UI wordt getoond.  
* **type**: De **cruciale** categorie die bepaalt tot welke van de vier functionele pijlers de plugin behoort. Toegestane waarden zijn:  
  * context_worker  
  * analysis_worker  
  * monitor_worker  
  * execution_worker  
* **version**: De semantische versie van de plugin (bv. 1.0.1).  
* **description**: Een korte, duidelijke beschrijving van de functionaliteit.  
* **author**: De naam van de ontwikkelaar.

### **4.3.2. Dependencies (Het Data Contract)**

De dependencies-sectie is het formele contract dat definieert welke data een plugin nodig heeft om te functioneren en wat het produceert. Dit is de kern van de "context-bewuste" UI en validatie.

* **requires (Verplichte DataFrame Kolommen)**: Een lijst van datakolommen die een ContextWorker als **harde eis** verwacht in de DataFrame (bv. ['high', 'low', 'close']). Het Assembly Team controleert of aan deze vereisten wordt voldaan.  
* **provides (Geproduceerde DataFrame Kolommen)**: Een lijst van nieuwe datakolommen die een ContextWorker als **output** toevoegt aan de DataFrame (bv. ['is_swing_high']).  
* **requires_context (Verplichte Rijke Data)**: Een lijst van **niet-DataFrame** data-objecten die de plugin als **harde eis** verwacht in de TradingContext. Als deze data niet beschikbaar is, zal de plugin in de UI **uitgeschakeld** zijn en zal de ComponentBuilder een fout genereren bij de bootstrap.  
  * *Voorbeeld*: ['orderbook_snapshot'].  
* **uses (Optionele Rijke Data)**: Een lijst van **niet-DataFrame** data-objecten die de plugin kan gebruiken voor een **verbeterde analyse**, maar die **niet verplicht** zijn. Als deze data niet beschikbaar is, zal de plugin in een "fallback-modus" werken.  
  * *Voorbeeld*: ['tick_by_tick_volume'].  
* **produces_events (Gepubliceerde Events)**: **Specifiek voor MonitorWorker-plugins**. Dit is een lijst van de unieke event-namen die deze monitor kan publiceren op de EventBus. De EventWiringFactory valideert dit tegen de event_map.yaml.

### **4.3.3. Permissions (Optioneel)**

De permissions-sectie fungeert als een beveiligingscontract. Standaard heeft een plugin geen toegang tot externe bronnen.

* **network_access**: Een 'allowlist' van netwerkbestemmingen.  
* **filesystem_access**: Een 'allowlist' van bestanden of mappen.

## **4.4. De Worker & het BaseWorker Raamwerk**

De worker.py bevat de daadwerkelijke logica. Om de ontwikkeling te versnellen en te standaardiseren, biedt de architectuur een set aan basisklassen (BaseWorker) in de backend.

* **Doel:** Het automatiseren van de complexe, geneste DTO-creatie die veel voorkomt in de AnalysisWorker-pijplijn en het consistent doorgeven van de correlation_id.  
* **Voorbeeld (BaseEntryPlanner binnen de AnalysisWorker-pijplijn):**

Een ontwikkelaar die een EntryPlanner-plugin schrijft, hoeft niet zelf de volledige EntrySignal DTO te construeren. Hij kan erven van een BaseEntryPlanner.

# Voorbeeld van een simpele Entry Planner plugin  
class MySimpleEntryPlanner(BaseEntryPlanner):  
    def _process(self, input_dto: Signal, correlation_id: UUID, context: TradingContext) -> Optional[Dict[str, Any]]:  
        # De ontwikkelaar focust zich puur op de kernlogica:  
        # het berekenen van de entry-prijs.  
        entry_price = context.get_last_price('close') * 0.99  
          
        # Hij retourneert alleen de *nieuwe* data.  
        return {"entry_price": entry_price}

De BaseEntryPlanner-klasse handelt op de achtergrond automatisch de creatie van de EntrySignal DTO af, nest de oorspronkelijke Signal erin, en zorgt dat de correlation_id correct wordt doorgegeven. Dit maakt de plugin-code extreem schoon, gefocust en minder foutgevoelig.

---

# 5_DE_ANALYTISCHE_PIJPLIJN.md

# **5. De Analytische Pijplijn**

Versie: 2.2 (Gecorrigeerd & Aangevuld)  
Status: Definitief

## **5.1. Introductie: Een Gescheiden Pijplijn**

Dit document beschrijft de volledige workflow van data-analyse tot handelsvoorstel. Deze workflow is bewust opgesplitst in twee conceptueel verschillende, opeenvolgende processen die worden beheerd door gespecialiseerde Operators:

1. **De Context Pijplijn (Fase 1-2):** De eerste twee fasen zijn de verantwoordelijkheid van de **ContextOperator**. Deze fasen verrijken de ruwe marktdata en bereiden de complete, state-bewuste TradingContext voor. Dit proces eindigt met het publiceren van een ContextReady-event.  
2. **De Analytische Pijplijn (Fase 3-8):** De daaropvolgende fasen vormen de kern van de **AnalysisOperator**. In reactie op de ContextReady-event, voert de AnalysisOperator zijn interne, stateless en procedurele trechter uit om een *analytisch voorstel* (EngineCycleResult) te produceren. Dit voorstel wordt gepubliceerd als een StrategyProposalReady-event.

## **5.2. De Pijplijn: Een Praktijkvoorbeeld**

We volgen een concreet voorbeeld: een **"Market Structure Shift + FVG Entry"** strategie.

   ┌───────────────────────────────────────────┐  
   │        RUWE DATAFRAME (OHLCV)             │  
   └────────────────────┬──────────────────────┘  
                        │ (Beheerd door ContextOperator)  
                        v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 1: REGIME CONTEXT (De "Weerman")                            │  
│ Plugin: ContextWorker                                            │  
└────────────────────┬─────────────────────────────────────────────┘  
                        v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 2: STRUCTURELE CONTEXT (De "Cartograaf")                    │  
│ Plugin: ContextWorker                                            │  
└────────────────────┬─────────────────────────────────────────────┘  
                        │  
                        v (Publiceert ContextReady event)  
   ┌───────────────────────────────────────────┐  
   │ FINALE TRADING CONTEXT (met enriched_df)  │  
   └────────────────────┬──────────────────────┘  
                        │ (Start AnalysisOperator Pijplijn)  
                        v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 3: SIGNAAL GENERATIE (De "Verkenner")                       │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: Signal  
│ -------------------------------  
│ { correlation_id, timestamp, asset,  
│   direction, signal_type }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 4: SIGNAAL VERFIJNING (De "Kwaliteitscontroleur")           │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: Signal (of None)  
│ -------------------------------  
│ { ... (inhoud blijft gelijk) }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 5: ENTRY PLANNING (De "Timing Expert")                      │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: EntrySignal  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│   signal: Signal (genest),  
│   + entry_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 6: EXIT PLANNING (De "Strateeg")                            │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: RiskDefinedSignal  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│   entry_signal: EntrySignal (genest),  
│   + sl_price, tp_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 7: SIZE PLANNING (De "Logistiek Manager")                   │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: TradePlan  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│   risk_defined_signal: RiskDefinedSignal (genest),  
│   + position_value_quote, position_size_asset }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 8: ORDER ROUTING (De "Verkeersleider")                      │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: RoutedTradePlan  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│   trade_plan: TradePlan (genest),  
│   + order_type, time_in_force, ... }  
│  
v  
   ┌─────────────────────────────────────────────┐  
   │ FINAAL EngineCycleResult DTO                │  
   │ { routed_trade_plans?, ... }                │  
   └────────────────────┬────────────────────────┘  
                        │  
                        v (Publiceert StrategyProposalReady Event)

*Opmerking: Fase 9 (CriticalEventDetection) is in de V4-architectuur verplaatst naar een aparte MonitorWorker en maakt geen deel meer uit van deze lineaire, analytische pijplijn.*

### **5.2.1. Gedetailleerde Fasen**

#### **Fase 1: Regime Context (De "Weerman")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** Wat is de algemene "weersverwachting" van de markt? Deze fase classificeert de marktomstandigheid zonder data weg te gooien.  
* **Input:** De ruwe DataFrame met OHLCV-data uit de TradingContext.  
* **Proces (voorbeeld):** Een ADXContext-plugin berekent de ADX-indicator en voegt een nieuwe kolom regime toe aan de DataFrame. Deze kolom krijgt de waarde 'trending' als ADX > 25 en 'ranging' als ADX < 25.  
* **Output:** Een verrijkte DataFrame. Er wordt geen data verwijderd; er wordt alleen een contextuele "tag" toegevoegd aan elke rij.

#### **Fase 2: Structurele Context (De "Cartograaf")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?  
* **Input:** De verrijkte DataFrame uit Fase 1.  
* **Proces (voorbeeld):** Een MarketStructureDetector-plugin analyseert de prijs en voegt twee nieuwe kolommen toe: trend_direction (met waarden als bullish of bearish) en is_mss (een True/False vlag op de candle waar een Market Structure Shift plaatsvindt).  
* **Output:** De finale enriched_df. We hebben nu "slimme" data met meerdere lagen context, klaar voor de AnalysisOperator.

***Controle wordt via een ContextReady-event overgedragen.***

#### **Fase 3: Signaal Generatie (De "Verkenner")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Waar is de precieze, actiegerichte trigger? We zoeken naar een Fair Value Gap (FVG) ná een Market Structure Shift.  
* **Input:** De enriched_df (via het TradingContext object).  
* **Proces (voorbeeld):** Een FVGEntryDetector-plugin scant de data. Wanneer het een rij tegenkomt waar is_mss True is, begint het te zoeken naar een FVG. Als het er een vindt, genereert het een signaal.  
* **Output:** Een **Signal DTO**. Dit object krijgt een unieke correlation_id (UUID) en bevat de essentie: {asset: 'BTC/EUR', timestamp: '...', direction: 'long', signal_type: 'fvg_entry'}.

#### **Fase 4: Signaal Verfijning (De "Kwaliteitscontroleur")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Is er bevestiging voor het signaal? We willen volume zien bij de FVG-entry.  
* **Input:** Het Signal DTO en het TradingContext.  
* **Proces (voorbeeld):** Een VolumeSpikeRefiner-plugin controleert het volume op de timestamp van het Signal. Als het volume te laag is, wordt het signaal afgekeurd.  
* **Output:** Het **gevalideerde Signal DTO** of None. De correlation_id blijft behouden.

#### **Fase 5: Entry Planning (De "Timing Expert")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Wat is de precieze entry-prijs voor ons goedgekeurde signaal?  
* **Input:** Het gevalideerde Signal DTO.  
* **Proces (voorbeeld):** Een LimitEntryPlanner-plugin bepaalt dat de entry een limietorder moet zijn op de 50% retracement van de FVG.  
* **Output:** Een **EntrySignal DTO**. Dit DTO *nest* het originele Signal en verrijkt het met { entry_price: 34500.50 }. De correlation_id wordt gepromoot naar het top-level.

#### **Fase 6: Exit Planning (De "Strateeg")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Wat is het initiële plan voor risico- en winstmanagement?  
* **Input:** Het EntrySignal DTO.  
* **Proces (voorbeeld):** Een LiquidityTargetExit-plugin plaatst de stop-loss onder de laatste swing low en de take-profit op de volgende major liquidity high.  
* **Output:** Een **RiskDefinedSignal DTO**. Nest het EntrySignal en voegt { sl_price: 34200.0, tp_price: 35100.0 } toe.

#### **Fase 7: Size Planning (De "Logistiek Manager")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Wat is de definitieve positiegrootte, gegeven ons risicoplan en kapitaal?  
* **Input:** Het RiskDefinedSignal DTO en de StrategyLedger (via de TradingContext).  
* **Proces (voorbeeld):** Een FixedRiskSizer-plugin berekent de positiegrote zodat het risico (entry_price - sl_price) exact 1% van de totale equity van de StrategyLedger is.  
* **Output:** Een **TradePlan DTO**. Nest het RiskDefinedSignal en bevat de finale, berekende { position_value_quote: 1000.0, position_size_asset: 0.0289 }.

#### **Fase 8: Order Routing (De "Verkeersleider")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Hoe moet dit strategische plan *technisch* worden uitgevoerd?  
* **Input:** Het TradePlan DTO.  
* **Proces (voorbeeld):** Een DefaultRouter-plugin vertaalt het plan naar concrete order-instructies.  
* **Output:** Een **RoutedTradePlan DTO**. Nest het TradePlan en voegt de *tactische* executie-instructies toe, zoals { order_type: 'limit', time_in_force: 'GTC' }.

## **5.3. Rolverdeling in de Architectuur**

* **ContextOperator (De Voorbereider)**: Verantwoordelijk voor Fase 1 & 2. Abonneert (via zijn adapter) op MarketDataReceived, roept de ContextWorker-plugins aan, en publiceert de ContextReady-event.  
* **AnalysisOperator (De Analist)**: Verantwoordelijk voor Fase 3 t/m 8. Abonneert (via zijn adapter) op ContextReady. Na ontvangst doorloopt het de procedurele DTO-trechter en publiceert het eindresultaat als een StrategyProposalReady-event.  
* **MonitorOperator (De Waakhond)**: Draait **parallel** aan de AnalysisOperator. Abonneert (via zijn adapter) op events zoals ContextReady en LedgerStateChanged om de algehele staat van de operatie te bewaken. Het publiceert informatieve of waarschuwende events (bv. MAX_DRAWDOWN_BREACHED) maar handelt nooit zelf.  
* **ExecutionOperator (De Poortwachter)**: Abonneert (via zijn adapter) op StrategyProposalReady-events (van de AnalysisOperator) en eventuele events van MonitorWorkers. Het ontvangt de voorstellen, toetst deze aan overkoepelende regels, en beslist of de trades daadwerkelijk uitgevoerd mogen worden door een ExecutionApproved-event te publiceren.

## **5.4. De Feedback Loops**

1. **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** een Operation, via de EventBus. Een LedgerStateChanged-event, gepubliceerd door de ExecutionEnvironment, wordt opgenomen in de volgende TradingContext. Hierdoor heeft de AnalysisOperator bij de volgende tick altijd de meest actuele financiële staat beschikbaar voor zijn berekeningen.  
2. **De Strategische Feedback Loop (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** de Operations, volgens het **"Bouwen -> Meten -> Leren"** principe. Je analyseert de resultaten, past de strategy_blueprint.yaml aan en start een nieuwe Operation.

---

# 6_RESILIENCE_AND_OPERATIONS v2.md

# **6. Robuustheid & Operationele Betrouwbaarheid**

Versie: 2.0 (Architectuur Blauwdruk v4)  
Status: Definitief  
Dit document beschrijft de strategieën en architectonische patronen die S1mpleTrader V2 veerkrachtig maken tegen technische fouten. Deze principes zijn essentieel voor de betrouwbaarheid van het systeem, met name in een live trading-omgeving waar kapitaal op het spel staat.

## **6.1. Integriteit van de Staat: Atomiciteit en Persistentie**

Een trading-systeem is inherent 'stateful'. De huidige staat (open posities, kapitaal, de interne staat van een stateful plugin) is de basis voor toekomstige beslissingen. Het corrumperen van deze staat is catastrofaal.

### **6.1.1. Atomische Schrijfacties (Journaling)**

* **Probleem:** Een applicatiecrash of stroomuitval tijdens het schrijven van een state-bestand (bv. state.json voor een stateful ExecutionWorker) kan leiden tot een half geschreven, corrupt bestand, met permanent dataverlies tot gevolg.  
* **Architectonische Oplossing:** We implementeren een **Write-Ahead Log (WAL)** of **Journaling**-patroon, een techniek die door professionele databases wordt gebruikt.  
* **Gedetailleerde Workflow:**  
  1. **Schrijf naar Journaal:** De save_state()-methode van een stateful plugin schrijft de nieuwe staat **nooit** direct naar state.json. Het serialiseert de data naar een tijdelijk bestand: state.json.journal.  
  2. **Forceer Sync naar Schijf:** Na het schrijven roept de methode os.fsync() aan op het .journal-bestands-handle. Dit is een cruciale, expliciete instructie aan het besturingssysteem om alle databuffers onmiddellijk naar de fysieke schijf te schrijven.  
  3. **Atomische Hernoeming:** Alleen als de sync succesvol is, wordt de os.rename()-operatie uitgevoerd om state.json.journal te hernoemen naar state.json. Deze rename-operatie is op de meeste moderne bestandssystemen een **atomische handeling**: het slaagt in zijn geheel, of het faalt in zijn geheel.  
  4. **Herstel-Logica:** De load_state()-methode van de plugin bevat de herstel-logica. Bij het opstarten controleert het: "Bestaat er een .journal-bestand?". Zo ja, dan weet het dat de applicatie is gecrasht na stap 2 maar vóór stap 3. De herstelprocedure is dan het voltooien van de rename-operatie.

## **6.2. Netwerkveerkracht en Staatssynchronisatie**

Een live-systeem is afhankelijk van een stabiele verbinding en moet kunnen omgaan met de onvermijdelijke instabiliteit van het internet. De kernfilosofie is: **de exchange is de enige bron van waarheid.** Ons platform onderhoudt slechts een real-time cache van die waarheid.

* **Architectonische Oplossing:** De verantwoordelijkheid voor het managen van de verbinding en de staatssynchronisatie ligt bij de **LiveEnvironment** en wordt aangestuurd door gespecialiseerde MonitorWorkers en ExecutionWorkers. We gebruiken een tweeledige strategie van "push" en "pull".

### **6.2.1. Mechanisme 1: Real-time Synchronisatie via 'Push' (WebSocket)**

* **Doel:** De interne staat (StrategyLedgers) met minimale latency synchroon houden tijdens de normale operatie.  
* **Componenten:** De LiveEnvironment en zijn IAPIConnector.  
* **Proces:**  
  1. De LiveEnvironment zet via de IAPIConnector een **private WebSocket-verbinding** (start_user_data_stream()) op.  
  2. Wanneer een door S1mpleTrader geplaatste order wordt gevuld, *pusht* de exchange onmiddellijk een TradeExecuted-bericht.  
  3. De IAPIConnector vangt dit bericht op en vertaalt het naar een intern LedgerStateChanged-event.  
  4. Een MonitorWorker die de LedgerState observeert, wordt geactiveerd door dit event en kan indien nodig andere componenten informeren.

### **6.2.2. Mechanisme 2: Herstel & Verificatie via 'Pull' (State Reconciliation)**

* **Doel:** Het cruciale veiligheidsnet voor periodieke verificatie en, belangrijker nog, voor **herstel na een crash** of netwerkonderbreking.  
* **Componenten:** Een ReconciliationMonitor (een MonitorWorker) en de LiveEnvironment.  
* **Proces:**  
  1. **Trigger**: De Scheduler publiceert een periodiek event (bv. five_minute_reconciliation_tick) zoals gedefinieerd in schedule.yaml.  
  2. De ReconciliationMonitor luistert naar dit event en start de reconcile_state()-procedure. Dit gebeurt **altijd** bij het opstarten van een live Operation.  
  3. **Pull**: De monitor instrueert de LiveEnvironment om via de IAPIConnector de REST API van de exchange aan te roepen (get_open_orders(), get_open_positions()) om de "absolute waarheid" op te halen.  
  4. **Vergelijk**: Het vergelijkt deze lijst van "echte" posities en orders met de staat van de StrategyLedgers die het beheert.  
  5. **Corrigeer**: Bij discrepanties wordt de StrategyLedger geforceerd gecorrigeerd om de staat van de exchange te weerspiegelen, en wordt een CRITICAL-waarschuwing gelogd.

### **6.2.3. Verbindingsbeheer & Circuit Breaker**

* **Componenten:** Een ConnectionMonitor (MonitorWorker), een CircuitBreakerWorker (ExecutionWorker), en de LiveEnvironment's DataSource.  
* **Proces:**  
  1. **Heartbeat & Reconnect**: De DataSource monitort de verbinding. Bij een onderbreking start het een automatisch reconnect-protocol met een **exponential backoff**-algoritme.  
  2. **Event Publicatie**: Als de DataSource na een configureerbaar aantal pogingen geen verbinding kan herstellen, publiceert het een CONNECTION_LOST-event.  
  3. De **ConnectionMonitor** vangt dit event op en publiceert een strategisch event, bijvoorbeeld CONNECTION_UNSTABLE_DETECTED.  
  4. De **CircuitBreakerWorker** luistert naar CONNECTION_UNSTABLE_DETECTED en activeert de **Circuit Breaker**:  
     * Het publiceert een HALT_NEW_SIGNALS-event.  
     * Het stuurt een kritieke alert naar de gebruiker.  
     * Het kan (optioneel) proberen alle open posities die door S1mpleTrader worden beheerd, te sluiten door een EXECUTE_EMERGENCY_EXIT-event te publiceren.

## **6.3. Applicatie Crash Recovery (Supervisor Model)**

* **Probleem:** Het hoofdproces van het platform (de Operations-service) kan crashen door een onverwachte bug.  
* **Architectonische Oplossing:** We scheiden het *starten* van de applicatie van de *applicatie zelf* door middel of een **Supervisor (Watchdog)**-proces, aangestuurd door run_supervisor.py.  
* **Gedetailleerde Workflow:**  
  1. **Entrypoint run_supervisor.py:** Dit is het enige script dat je handmatig start in een live-omgeving.  
  2. **Supervisor Proces:** Dit script start een lichtgewicht "supervisor"-proces dat een *kind-proces* voor de daadwerkelijke Operations-service start en monitort.  
  3. **Herstart & Herstel Cyclus:**  
     * Als het Operations-proces onverwacht stopt, detecteert de Supervisor dit.  
     * De Supervisor start de Operations-service opnieuw.  
     * De *nieuwe* Operations-instantie start in een **"herstelmodus"**:  
       * **Stap A (Plugin State Herstel):** Via de ComponentBuilder worden alle stateful plugins geladen met hun load_state()-methodes, die de journaling-logica (zie 6.1) gebruiken om een consistente staat te herstellen.  
       * **Stap B (Ledger Herstel):** De **State Reconciliation**-procedure (zie 6.2.2) wordt onmiddellijk uitgevoerd om alle StrategyLedgers te synchroniseren met de exchange.  
       * **Stap C (Hervatting):** Alleen als beide stappen succesvol zijn, gaat de Operation verder met de normale-tick verwerking.

---

# 7_DEVELOPMENT_STRATEGY v2.md

# **7. Ontwikkelstrategie & Tooling**

Versie: 2.0 (Architectuur Blauwdruk v4)  
Status: Definitief

Dit document beschrijft de methodiek, de workflow en de tooling voor het ontwikkelen, testen en debuggen van het S1mpleTrader V2 ecosysteem. Het is de blauwdruk voor een snelle, efficiënte en data-gedreven ontwikkelomgeving.

## **7.1. Filosofie: Rapid, Lean & User-Centered**

We stappen af van een traditionele, op de CLI gerichte workflow. De nieuwe filosofie is gebaseerd op een combinatie van **Lean UX** en **User-Centered Design (UCD)**, met als doel een "supercharged" ontwikkelcyclus te creëren.

* **De Gebruiker staat Centraal:** De primaire gebruiker ("De Kwantitatieve Strateeg") en diens workflow bepalen wat we bouwen en in welke volgorde. De Web UI is het centrale instrument.  
* **Compact Ontwikkelen:** We bouwen in de kleinst mogelijke, onafhankelijke eenheden (een plugin) en testen deze geïsoleerd.  
* **Direct Testen:** Elke plugin wordt vergezeld van unit tests. Geen enkele component wordt als "klaar" beschouwd zonder succesvolle, geautomatiseerde tests.  
* **Snelle Feedback Loop (Bouwen -> Meten -> Leren):** De tijd tussen een idee, een codewijziging en het zien van het visuele resultaat moet minimaal zijn. De Web UI is de motor van deze cyclus.

## **7.2. De "Supercharged" Ontwikkelcyclus in de Praktijk**

De gehele workflow, van het bouwen van een strategie tot het analyseren van de resultaten, vindt plaats binnen de naadloze, visuele webapplicatie.

### **7.2.1. Fase 1: Visuele Strategie Constructie (De "Strategy Builder")**

* **Doel:** Snel en foutloos een nieuwe strategie (strategy_blueprint.yaml) samenstellen.  
* **Proces:**  
  1. De gebruiker opent de "Strategy Builder" in de Web UI.  
  2. In een zijbalk verschijnen alle beschikbare plugins, opgehaald via een API en gegroepeerd per type (bv. analysis_worker).  
  3. De gebruiker sleept plugins naar de "slots" in een visuele weergave van de workforce.  
  4. Voor elke geplaatste plugin genereert de UI automatisch een configuratieformulier op basis van de schema.py van de plugin. Input wordt direct in de browser gevalideerd.  
  5. Bij het opslaan wordt de configuratie als YAML op de server aangemaakt.

### **7.2.2. Fase 2: Interactieve Analyse (De "Backtesting Hub")**

* **Doel:** De gebouwde strategieën rigoureus testen en de resultaten diepgaand analyseren.  
* **Proces:**  
  1. **Run Launcher:** Vanuit de UI start de gebruiker een backtest of optimalisatie voor een specifieke Operation.  
  2. **Live Progress:** Een dashboard toont de live voortgang.  
  3. **Resultaten Analyse:**  
     * **Optimalisatie:** Resultaten verschijnen in een interactieve tabel (sorteren, filteren).  
     * **Diepgaande Analyse (Trade Explorer):** De gebruiker kan doorklikken naar een enkele run en door individuele trades bladeren, waarbij een interactieve grafiek alle contextuele data (marktstructuur, indicatoren, etc.) toont op het moment van de trade.

### **7.2.3. Fase 3: De Feedback Loop**

* **Doel:** Een inzicht uit de analysefase direct omzetten in een verbetering.  
* **Proces:** Vanuit de "Trade Explorer" klikt de gebruiker op "Bewerk Strategie". Hij wordt direct teruggebracht naar de "Strategy Builder" met de volledige strategy_blueprint.yaml al ingeladen, klaar om een aanpassing te doen. De cyclus begint opnieuw.

## **7.3. De Tooling in Detail**

### **7.3.1. Gespecialiseerde Entrypoints**

De applicatie kent drie manieren om gestart te worden, elk met een eigen doel:

* **run_web.py (De IDE):** Het primaire entrypoint voor de ontwikkelaar. Start de FastAPI-server die de Web UI en de bijbehorende API's serveert.  
* **run_operation.py (De Robot):** De "headless" entrypoint voor het uitvoeren van een Operation, ideaal voor automatisering, zoals regressietesten en Continuous Integration (CI/CD) workflows.  
* **run_supervisor.py (De Productie-schakelaar):** De minimalistische, robuuste starter voor de live trading-omgeving, die het Operations-proces monitort.

### **7.3.2. Testen als Integraal Onderdeel**

* **Unit Tests per Plugin:** Elke plugin-map krijgt een tests/test_worker.py. Deze test laadt een stukje voorbeeld-data, draait de worker.py erop, en valideert of de output (bv. de nieuwe kolom of de Signal DTO) correct is. Dit gebeurt volledig geïsoleerd.  
* **Integratietests:** Testen de samenwerking tussen de service laag componenten en het AssemblyTeam.  
* **End-to-End Tests:** Een klein aantal tests die via run_operation.py een volledige Operation draaien op een vaste dataset en controleren of het eindresultaat (de PnL) exact overeenkomt met een vooraf berekende waarde.

### **7.3.3. Gelaagde Logging & Debugging**

Logging is een multi-inzetbare tool, geen eenheidsworst. We onderscheiden drie lagen:

1. **Laag 1: stdio (De Console)**  
   * **Doel:** Alleen voor *initiële, basic development* van een geïsoleerde plugin. Gebruik print() voor de snelle, "vuile" check. Dit is vluchtig en wordt niet bewaard.  
2. **Laag 2: Gestructureerde Logs (JSON)**  
   * **Doel:** De primaire output voor **backtests en paper trading**. Dit is de *databron* voor analyse.  
   * **Implementatie:** Een logging.FileHandler die log-records als gestructureerde JSON-objecten wegschrijft naar een logbestand.  
   * **Principe:** De console blijft schoon. De *echte* output is het log-bestand.  
3. **Laag 3: De "Log Explorer" (Web UI)**  
   * **Doel:** De primaire interface voor **analyse en debugging**.  
   * **Implementatie:** Een tool in de frontend die het JSON-logbestand inleest en interactief presenteert, waardoor je kunt filteren op plugin_name of een Correlation ID.

#### **Traceability met de Correlation ID**

Elk Signal DTO dat wordt gecreëerd, krijgt een unieke ID (bv. een UUID). Elke plugin die dit signaal (of een afgeleid object zoals een Trade DTO) verwerkt, voegt deze Correlation ID toe aan zijn log-berichten. Door in de "Log Explorer" op deze ID te filteren, kan de gebruiker de volledige levenscyclus en beslissingsketen van één specifieke trade volgen, door alle fasen en parallelle processen heen.

---

# 8_META_WORKFLOWS v2.md

# **8. Meta Workflows: Van Analyse tot Inzicht**

Versie: 2.0 (Architectuur Blauwdruk v4)  
Status: Definitief  
Dit document beschrijft de architectuur en de rol van de "Meta Workflows". Dit zijn hoog-niveau services die bovenop de kern-executielogica draaien om geavanceerde analyses, optimalisaties en automatisering mogelijk te maken.

## **8.1. Concept: De Operations-service als Motor**

De Operations-service, aangestuurd via het run_operation.py entrypoint, is de motor die in staat is om **één enkele, volledig gedefinieerde Operation** uit te voeren. Meta Workflows zijn services in de Service-laag die deze motor herhaaldelijk en systematisch aanroepen, met steeds een andere configuratie, om complexe, kwantitatieve vragen te beantwoorden.

Ze fungeren als "onderzoekleiders" die de Operations-service als een "black box"-motor gebruiken. Ze leunen zwaar op een ParallelRunService om duizenden backtests efficiënt en parallel uit te voeren. Waar optimalisatie in V1 een ad-hoc script was, wordt het in V2 een **"eerste klas burger"** van de architectuur.

## **8.2. De OptimizationService (Het Onderzoekslab)**

* **Doel:** Het systematisch doorzoeken van een grote parameterruimte om de meest performante combinaties voor een strategie te vinden.  
* **Analogie:** Een farmaceutisch lab dat duizenden moleculaire variaties test om het meest effectieve medicijn te vinden.

#### **Gedetailleerde Workflow:**

1. **Input (Het Onderzoeksplan):** De service vereist een **basis operation.yaml** die de te testen strategy_link bevat, en een **optimization.yaml** die de onderzoeksvraag definieert: welke parameters (start, end, step) in de gelinkte strategy_blueprint.yaml moeten worden gevarieerd.  
2. **Proces (De Experimenten):**  
   * De OptimizationService genereert een volledige lijst van alle mogelijke parameter-combinaties.  
   * Voor elke combinatie creëert het:  
     1. Een unieke, **tijdelijke strategy_blueprint.yaml** waarin de parameters zijn aangepast.  
     2. Een unieke, **tijdelijke en uitgeklede operation.yaml** die slechts één strategy_link bevat: die naar de zojuist gecreëerde tijdelijke blueprint en de relevante backtest-omgeving.  
   * Het delegeert de volledige lijst van paden naar deze tijdelijke operation.yaml-bestanden aan de ParallelRunService.  
3. **Executie (Het Robotleger):**  
   * De ParallelRunService start een pool van workers (één per CPU-kern).  
   * Elke worker ontvangt een pad naar een unieke operation.yaml, roept de Operations-service aan via run_operation.py en voert een volledige backtest uit.  
4. **Output (De Analyse):**  
   * De OptimizationService verzamelt alle BacktestResult-objecten.  
   * Het creëert een pandas DataFrame met de geteste parameters en de resulterende performance-metrieken.  
   * Deze data wordt naar de Web UI gestuurd voor presentatie in een interactieve, sorteerbare tabel.

## **8.3. De VariantTestService (De Vergelijkings-Arena)**

* **Doel:** Het direct vergelijken van een klein aantal discrete strategie-varianten onder exact dezelfde marktomstandigheden om de robuustheid en de impact van specifieke keuzes te valideren.  
* **Analogie:** Een "head-to-head" race tussen een paar topatleten om te zien wie de beste allrounder is.

#### **Gedetailleerde Workflow:**

1. **Input (De Deelnemers):** De service vereist een **basis operation.yaml** en een **variant.yaml** die de "deelnemers" definieert door middel van "overrides" op de gelinkte strategy_blueprint.yaml.  
   * **Voorbeeld:**  
     * **Variant A ("Baseline"):** De basisconfiguratie.  
     * **Variant B ("Hoge RR"):** Overschrijft alleen de risk_reward_ratio parameter in een specifieke plugin.  
     * **Variant C ("Andere Exit"):** Vervangt de ATR exit-plugin door een FixedPercentage exit-plugin.  
2. **Proces (De Race-Opzet):**  
   * De VariantTestService past voor elke gedefinieerde variant de "overrides" toe op de basis-blueprint om unieke, **tijdelijke strategy_blueprint.yaml**-bestanden te creëren.  
   * Vervolgens creëert het voor elke variant een **tijdelijke, uitgeklede operation.yaml** die naar de juiste tijdelijke blueprint linkt.  
   * Het delegeert de lijst van paden naar deze operation.yaml-bestanden aan de ParallelRunService.  
3. **Executie (Het Startschot):**  
   * De ParallelRunService voert voor elke variant een volledige backtest uit door de Operations-service aan te roepen met het juiste operation.yaml-bestand.  
4. **Output (De Finishfoto):**  
   * De VariantTestService verzamelt de BacktestResult-objecten.  
   * Deze data wordt naar de Web UI gestuurd voor een directe, visuele vergelijking, bijvoorbeeld door de equity curves van alle varianten in één grafiek te plotten.

## **8.4. De Rol van ParallelRunService**

Deze service is een cruciale, herbruikbare Backend-component. Zowel de OptimizationService als de VariantTestService zijn "klanten" van deze service. Zijn enige verantwoordelijkheid is het efficiënt managen van de multiprocessing-pool, het tonen van de voortgang en het netjes aggregeren van resultaten. Dit is een perfect voorbeeld van het **Single Responsibility Principle**.

---

# 9_CODING_STANDAARDS_DESIGN_PRINCIPLES v2.5.md

# **9. Coding Standaarden & Design Principles**

Versie: 2.5 (Scope Details Hersteld)  
Status: Definitief  
Dit document beschrijft de verplichte standaarden en best practices voor het schrijven van alle code binnen het S1mpleTrader V2 project. Het doel is een consistente, leesbare, onderhoudbare en robuuste codebase. Het naleven van deze standaarden is niet optioneel.

## **9.1. Code Kwaliteit & Stijl**

### **9.1.1. Fundamenten**

* **PEP 8 Compliant:** Alle Python-code moet strikt voldoen aan de [PEP 8](https://peps.python.org/pep-0008/) stijlgids. Een linter wordt gebruikt om dit te handhaven.  
  * **Regellengte:** Maximaal 100 tekens.  
  * **Naamgeving:** snake_case voor variabelen, functies en modules; PascalCase voor klassen.  
* **Volledige Type Hinting:** Alle functies, methodes, en variabelen moeten volledig en correct getypeerd zijn. We streven naar een 100% getypeerde codebase om runtime-fouten te minimaliseren.  
* **Commentaar in het Engels:** Al het commentaar in de code (# ...) en docstrings moeten in het Engels zijn voor universele leesbaarheid en onderhoudbaarheid.

### **9.1.2. Gestructureerde Docstrings**

Elk bestand, elke klasse en elke functie moet een duidelijke docstring hebben.

* **Bestands-Header Docstring:** Elk .py-bestand begint met een gestandaardiseerde header die de inhoud en de plaats in de architectuur beschrijft.  
  # backend/assembly/component_builder.py  
  """  
  Contains the ComponentBuilder, responsible for assembling and instantiating  
  all required Operator and Worker components for a given strategy_link.

  @layer: Backend (Assembly)  
  @dependencies: [PyYAML, Pydantic]  
  @responsibilities:  
      - Reads the strategy_blueprint.yaml.  
      - Validates the workforce configuration.  
      - Instantiates all required plugin workers and operators.  
  """

* **Imports:** Alle imports staan bovenaan het bestand. Het is van belang dat deze in de juiste volgorde staan. We zullen hiervoor ten alle tijden een onderverdeling gebruiken in de volgende drie groepen en volgorde:  
  * **1. Standard Library Imports**  
  * **2. Third-Party Imports**  
  * 3. Our Application Imports  
    Alle imports zullen absoluut zijn en opbouwen vanaf de project root.

Indien mogelijk worden imports gegroepeerd om lange regels te voorkomen en te blijven voldoen aan de PEP 8.

* **Functie & Methode Docstrings (Google Style):** Voor alle functies en methodes hanteren we de **Google Style Python Docstrings**. Dit is een leesbare en gestructureerde manier om parameters, return-waarden en voorbeelden te documenteren.  
  def process_data(df: pd.DataFrame, length: int = 14) -> pd.DataFrame:  
      """Calculates an indicator and adds it as a new column.

      Args:  
          df (pd.DataFrame): The input DataFrame with OHLCV data.  
          length (int, optional): The lookback period for the indicator.  
              Defaults to 14.

      Returns:  
          pd.DataFrame: The DataFrame with the new indicator column added.  
      """  
      # ... function logic ...  
      return df

### **9.1.3. Naamgevingsconventies**

Naast de algemene [PEP 8]-richtlijnen hanteren we een aantal strikte, aanvullende conventies om de leesbaarheid en de architectonische zuiverheid van de code te vergroten.

* **Interfaces (Contracten):**  
  * **Principe:** Elke abstracte klasse (ABC) of Protocol die een contract definieert, moet worden voorafgegaan door een hoofdletter I.  
  * **Doel:** Dit maakt een onmiddellijk en ondubbelzinnig onderscheid tussen een abstract contract en een concrete implementatie.  
  * Voorbeeld:  
    ```Python  
    # Het contract (de abstractie)  
    class IAPIConnector(Protocol):  
    ...  
    # De concrete implementatie  
    class KrakenAPIConnector(IAPIConnector):  
        ...  
    ```

* **Interne Attributen en Methodes:**  
  * **Principe:** Attributen of methodes die niet bedoeld zijn voor gebruik buiten de klasse, moeten worden voorafgegaan door een enkele underscore (_).  
  * **Doel:** Dit communiceert duidelijk de publieke API van een klasse.  
  * Voorbeeld:  
    ```Python  
    class AnalysisOperator:  
    def init(self):  
    self._app_config = ... # Intern  
        def run_pipeline(self): # Publiek  
            self._prepare_workers() # Intern

        def _prepare_workers(self):  
            ...  
    ```

## **9.2. Contract-Gedreven Ontwikkeling**

### **9.2.1. Pydantic voor alle Data-Structuren**

* **Principe:** Alle data die tussen componenten wordt doorgegeven, moet worden ingekapseld in een **Pydantic BaseModel**. Dit geldt voor DTO's, configuraties en plugin-parameters.  
* **Voordeel:** Dit garandeert dat data van het juiste type en de juiste structuur is *voordat* het wordt verwerkt.

### **9.2.2. Abstracte Basisklassen (Interfaces)**

* **Principe:** Componenten die uitwisselbaar moeten zijn (zoals plugins), moeten erven van een gemeenschappelijke abstracte basisklasse (ABC) die een consistent contract afdwingt.

## **9.3. Gelaagde Logging & Traceability**

### **9.3.1. Drie Lagen van Logging**

1. **Laag 1: stdio (Console via print()):** Uitsluitend voor snelle, lokale, vluchtige debugging. Mag nooit gecommit worden.  
2. **Laag 2: Gestructureerde JSON-logs:** De standaard output voor alle runs, bedoeld voor analyse.  
3. **Laag 3: De Web UI (Log Explorer):** De primaire interface voor het analyseren en debuggen van runs.

### **9.3.2. Traceability via Correlation ID**

* **Principe:** Elk Signal DTO krijgt een unieke UUID. Elke volgende plugin die dit signaal verwerkt, neemt deze correlation_id over in zijn log-berichten. Dit maakt de volledige levenscyclus van een trade traceerbaar.

## **9.4. Testen als Voorwaarde**

* **Principe:** Code zonder tests wordt beschouwd als onvolledig.  
* **Implementatie:** Elke plugin is **verplicht** om een tests/test_worker.py-bestand te bevatten. Continue Integratie (CI) voert alle tests automatisch uit na elke push.

## **9.5. Overige Standaarden**

* **Internationalisatie (i18n):**  
  * **Principe:** *Alle* tekst die direct of indirect aan een gebruiker kan worden getoond, moet via de internationalisatie-laag lopen. Hardgecodeerde, gebruikersgerichte strings in de Python-code zijn niet toegestaan.  
  * **Implementatie:** Een centrale Translator-klasse laadt YAML-bestanden uit de /locales map. Code gebruikt vertaalsleutels in "dot-notation" (bv. log.backtest.complete).  
  * **Scope van de Regel:** Deze regel is van toepassing op, maar niet beperkt tot, de volgende onderdelen:  
    1. Log Berichten: Alle log-berichten die bedoeld zijn om de gebruiker te informeren over de voortgang of status van de applicatie (voornamelijk INFO-niveau en hoger). Foutmeldingen voor ontwikkelaars (DEBUG-niveau) mogen wel hardcoded zijn.  
       Correct: logger.info('run.starting', pair=pair_name)  
       Incorrect: logger.info(f'Starting run for {pair_name}...')  
    2. Pydantic Veldbeschrijvingen: Alle description velden binnen Pydantic-modellen (DTO's, configuratie-schema's). Deze beschrijvingen kunnen direct in de UI of in documentatie worden getoond.  
       Correct: equity: float = Field(..., description="ledger_state.equity.desc")  
       Incorrect: equity: float = Field(..., description="The total current value...")  
    3. **Plugin Manifesten:** Alle beschrijvende velden in een plugin_manifest.yaml, zoals description en display_name. Een PluginQueryService moet deze velden door de Translator halen voordat ze naar de frontend worden gestuurd.  
  * **Interactie met Logger:** De Translator wordt één keer geïnitialiseerd en geïnjecteerd in de LogFormatter. De formatter is de enige component binnen het logsysteem die sleutels vertaalt naar leesbare berichten. Componenten die direct output genereren (zoals UI Presenters) krijgen de Translator ook apart geïnjecteerd.

### **9.5.1. Structuur van i18n Dotted Labels**

Om de locales/*.yaml bestanden georganiseerd en onderhoudbaar te houden, hanteren we een strikte, hiërarchische structuur voor alle vertaalsleutels. De structuur volgt over het algemeen het pad van de component of het datamodel waar de tekst wordt gebruikt.

* **Principe:** component_of_laag.specifieke_context.naam_van_de_tekst

**Voorbeelden van de Structuur:**

1. Log Berichten:  
   De sleutel begint met de naam van de module of de belangrijkste klasse waarin de log wordt aangeroepen.  
   **Structuur:** component_name.actie_of_gebeurtenis  
   **Voorbeelden:**  
   # Voor backend/assembly/plugin_registry.py  
   plugin_registry:  
     scan_start: "Scanning for plugins in '{path}'..."  
     scan_complete: "Scan complete. Found {count} valid plugins."

   # Voor services/operators/analysis_operator.py  
   analysis_operator:  
     run_start: "AnalysisOperator run starting..."  
     critical_event: "Critical event detected: {event_type}"

2. Pydantic Veldbeschrijvingen (description):  
   De sleutel weerspiegelt het pad naar het veld binnen het DTO of schema. De sleutel eindigt altijd op .desc om aan te geven dat het een beschrijving is.  
   **Structuur:** schema_naam.veld_naam.desc  
   **Voorbeelden:**  
   # Voor backend/dtos/ledger_state.py  
   ledger_state:  
     equity:  
       desc: "The total current value of the ledger."  
     available_cash:  
       desc: "The amount of cash available for new positions."

   # Voor een plugin's schema.py  
   ema_detector_params:  
     period:  
       desc: "The lookback period for the EMA calculation."

3. Plugin Manifesten (plugin_manifest.yaml):  
   Voor de beschrijvende velden van een plugin gebruiken we een structuur die de plugin uniek identificeert.  
   **Structuur:** plugins.plugin_naam.veld_naam  
   **Voorbeelden:**  
   plugins:  
     ema_detector:  
       display_name: "EMA Detector"  
       description: "Calculates and adds an Exponential Moving Average."  
     fvg_detector:  
       display_name: "FVG Detector"  
       description: "Detects a Fair Value Gap after a Market Structure Shift."

* **Configuratie Formaat:** YAML is de standaard voor alle door mensen geschreven configuratie. JSON wordt gebruikt voor machine-naar-machine data-uitwisseling.

## **9.6. Design Principles & Kernconcepten**

De architectuur is gebouwd op de **SOLID**-principes en een aantal kern-ontwerppatronen die de vier kernprincipes (Plugin First, Scheiding van Zorgen, Configuratie-gedreven, Contract-gedreven) tot leven brengen.

### **9.6.1. De Synergie: Configuratie- & Contract-gedreven Executie**

Het meest krachtige concept van V2 is de combinatie van configuratie- en contract-gedreven werken. De code is de motor; **de configuratie is de bestuurder, en de contracten zijn de verkeersregels die zorgen dat de bestuurder binnen de lijntjes blijft.**

* **Configuratie-gedreven:** De *volledige samenstelling* van een strategie (welke plugins, in welke volgorde, met welke parameters) wordt gedefinieerd in een strategy_blueprint.yaml. Dit maakt het mogelijk om strategieën drastisch te wijzigen zonder één regel code aan te passen.  
* **Contract-gedreven:** Elk stukje configuratie en data wordt gevalideerd door een strikt **Pydantic-schema**. Dit werkt op twee niveaus:  
  1. **Algemene Schema's:** De hoofdstructuur van een operation.yaml wordt gevalideerd door een algemeen schema. Dit contract dwingt af dat er bijvoorbeeld altijd een strategy_links sectie aanwezig is.  
  2. **Plugin-Specifieke Schema's:** De parameters voor een specifieke plugin (bv. de length van een EMA-indicator) worden gevalideerd door de Pydantic-klasse in de schema.py van *die ene plugin*.

Bij het starten van een Operation, leest de applicatie de YAML-bestanden en bouwt een set gevalideerde configuratie-objecten. Als een parameter ontbreekt, een verkeerd type heeft, of een plugin wordt aangeroepen die niet bestaat, faalt de applicatie *onmiddellijk* met een duidelijke foutmelding. Dit voorkomt onvoorspelbare runtime-fouten en maakt het systeem extreem robuust en voorspelbaar.

### **9.6.2. SOLID in de Praktijk**

* **SRP (Single Responsibility Principle):** Elke klasse heeft één duidelijke taak.  
  * ***V2 voorbeeld:*** Een FvgDetector-plugin (AnalysisWorker) detecteert alleen Fair Value Gaps. Het bepalen van de positiegrootte gebeurt in een aparte PositionSizer (AnalysisWorker).  
* **OCP (Open/Closed Principle):** Uitbreidbaar zonder bestaande code te wijzigen.  
  * ***V2 voorbeeld:*** Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe exit_planner-plugin (AnalysisWorker); de AnalysisOperator hoeft hiervoor niet aangepast te worden.  
* **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.  
  * ***V2 voorbeeld:*** De Operations-service hangt af van de IAPIConnector-interface, niet van de specifieke KrakenAPIConnector. Hierdoor kan de connector_id in de configuratie eenvoudig worden gewisseld.

### **9.6.3. Kernpatronen**

* **Factory Pattern:** Het Assembly Team (met ComponentBuilder) centraliseert het ontdekken, valideren en creëren van alle plugins.  
* **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.  
* **DTO’s (Data Transfer Objects):** Pydantic-modellen (Signal, TradePlan, ClosedTrade) zorgen voor een voorspelbare en type-veilige dataflow tussen alle componenten.

### **9.6.4. CQRS (Command Query Responsibility Segregation)**

* **Principe:** We hanteren een strikte scheiding tussen operaties die data lezen (Queries) en operaties die de staat van de applicatie veranderen (Commands). Een methode mag óf data retourneren, óf data wijzigen, maar nooit beide tegelijk. Dit principe voorkomt onverwachte bijeffecten en maakt het gedrag van het systeem glashelder en voorspelbaar.  
* **Implementatie in de Service Laag:** Dit principe is het meest expliciet doorgevoerd in de architectuur van onze data-services, waar we een duidelijke scheiding hebben tussen *lezers* en *schrijvers*:  
  1. **Query Services (Lezers):**  
     * **Naamgeving:** Services die uitsluitend data lezen, krijgen de QueryService-suffix (bv. PluginQueryService).  
     * **Methodes:** Alle publieke methodes in een Query Service zijn "vragen" en beginnen met het get_ prefix (bv. get_coverage).  
     * **Contract:** De DTO's die deze methodes accepteren, krijgen de Query-suffix (bv. CoverageQuery).  
  2. **Command Services (Schrijvers):**  
     * **Naamgeving:** Services die de staat van de data veranderen, krijgen de CommandService-suffix (bv. DataCommandService).  
     * **Methodes:** Alle publieke methodes in een Command Service zijn "opdrachten" en hebben een actieve, werkwoordelijke naam die de actie beschrijft (bv. synchronize, fetch_period).  
     * **Contract:** De DTO's die deze methodes accepteren, krijgen de Command-suffix (bv. SynchronizationCommand).  
* **Scope:** Deze CQRS-naamgevingsconventie is de standaard voor alle services binnen de Service-laag die direct interacteren met de staat van data of het systeem. Het naleven van deze conventie is verplicht om de voorspelbaarheid en onderhoudbaarheid van de codebase te garanderen.

---

# A_BIJLAGE_TEMINOLOGIE v2.0.md

# **Bijlage A: Terminologie**

**Versie:** 2.0 (Architectuur Blauwdruk v4) **Status:** Definitief

Dit document is een alfabetische legenda van de terminologie die wordt gebruikt in de S1mpleTrader V2-architectuurdocumentatie.

**9-Fasen Trechter/pijplijn** De fundamentele, sequentiële en procedurele workflow die een handelsidee stapsgewijs valideert en verrijkt. De logica hiervan is nu verdeeld over de `ContextWorker`- en `AnalysisWorker`-pijplijnen.

**AnalysisOperator** De manager van de `AnalysisWorkers`. Luistert naar `ContextReady`, orkestreert de executie van de analytische pijplijn, en publiceert het resultaat als `StrategyProposalReady`. Vervangt de `StrategyEngine` en deels de `StrategyOperator`.

**AnalysisWorker** De "Analist". Een type plugin dat de verrijkte context analyseert om **niet-deterministische, analytische handelsvoorstellen** te genereren. Vervangt de `StrategyWorker`.

**Assembly Team** De conceptuele naam voor de verzameling backend-componenten (`PluginRegistry`, `WorkerBuilder`, `ConnectorFactory`) die samen de technische orkestratie van plugins en connectoren verzorgen.

**Atomic Writes (Journaling)** Een robuust state-saving mechanisme dat dataverlies bij een crash voorkomt door eerst naar een tijdelijk `.journal`-bestand te schrijven alvorens het originele state-bestand te overschrijven.

**Backend-for-Frontend (BFF)** Een gespecialiseerde API-laag in de architectuur die als enige doel heeft om data te leveren in het exacte formaat dat de Web UI nodig heeft, wat de frontend-code aanzienlijk versimpelt.

**Blueprint (`run_blueprint.yaml`)** Verouderde term. Nu vervangen door `strategy_blueprint.yaml`.

**Circuit Breaker** Een veiligheidsmechanisme, typisch binnen een `ExecutionEnvironment`, dat bij aanhoudende (netwerk)problemen de strategie in een veilige, passieve modus plaatst om verdere schade te voorkomen.

**Clock** De component binnen een `ExecutionEnvironment` die de "hartslag" (ticks) van het systeem genereert, ofwel gesimuleerd uit historische data (`Backtest`) of real-time (`Live`/`Paper`).

**Configuratie-gedreven** Het kernprincipe dat het gedrag van de applicatie volledig wordt bestuurd door `YAML`-configuratiebestanden, niet door hardgecodeerde logica.

**`connectors.yaml`** Configuratiebestand dat de technische details (incl. secrets) voor verbindingen met externe, **live** partijen (bv. exchanges) definieert.

**Contract-gedreven** Het kernprincipe dat alle data-uitwisseling en configuratie wordt gevalideerd door strikte schema's (Pydantic, TypeScript-interfaces).

**ContextBuilder** Verouderde term. De functionaliteit is nu onderdeel van de `ContextOperator`.

**ContextOrchestrator** Verouderde term. De verantwoordelijkheden zijn overgenomen door de `ContextOperator`.

**ContextOperator** De manager van de `ContextWorkers`. Luistert naar `MarketDataReceived`, orkestreert de executie van de `ContextWorker`-pijplijn, en publiceert het resultaat als `ContextReady`. Vervangt de `ContextOrchestrator`.

**ContextWorker** De "Voorbereider". Een type plugin dat ruwe marktdata verrijkt met analytische context (bv. het berekenen van indicatoren).

**Correlation ID** Een unieke identifier (UUID) die wordt toegewezen aan een initieel event om de volledige levenscyclus van een handelsidee traceerbaar te maken door alle logs heen.

**`data_sources.yaml`** Configuratiebestand dat de catalogus van alle beschikbare **lokale** historische datasets (bv. Parquet-archieven) op schijf registreert.

**DTO (Data Transfer Object)** Een Pydantic `BaseModel` (bv. `Signal`) dat dient als een strikt contract voor data die als payload op de EventBus wordt doorgegeven.

**Entrypoints** De gespecialiseerde starter-scripts om de applicatie te draaien, zoals `run_operation.py`.

**`environments.yaml`** Configuratiebestand dat de "werelden" (`ExecutionEnvironments`) definieert en ze koppelt aan een `connector_id` of `data_source_id`.

**EventAdapter** Een generieke component die als "vertaler" fungeert tussen de EventBus en de (bus-agnostische) `Operator`-componenten, gedirigeerd door de `wiring_map.yaml`.

**`event_map.yaml`** Configuratiebestand dat elke toegestane event-naam definieert en koppelt aan zijn verplichte DTO-contract.

**EventWiringFactory** De "meester-assembler" die tijdens het opstarten de `wiring_map.yaml` leest om alle `EventAdapters` te creëren en te configureren.

**ExecutionEnvironment** De technische definitie van een "wereld" waarin een strategie kan draaien (`Backtest`, `Paper`, of `Live`).

**ExecutionHandler** Verouderde term. De verantwoordelijkheden zijn overgenomen door de `ExecutionOperator`.

**ExecutionOperator** De manager van de `ExecutionWorkers` en de verwerker van `ExecutionApproved`-events. Geeft de definitieve opdracht aan de `ExecutionEnvironment`. Vervangt de `ExecutionHandler`.

**ExecutionWorker** De "Uitvoerder". Een type plugin dat luistert naar specifieke triggers om **deterministische, op regels gebaseerde acties** direct uit te voeren.

**Feedback Loop (Strategisch)** De door de gebruiker bestuurde "Bouwen -> Meten -> Leren" cyclus, gefaciliteerd door de Web UI.

**Feedback Loop (Technisch)** De real-time feedback *binnen* een run, waarbij de staat van de `StrategyLedger` de input kan zijn voor de volgende cyclus.

**Heartbeat** Een mechanisme in een live dataverbinding om de gezondheid van de connectie te monitoren door te controleren op periodieke signalen van de server.

**Manifest (`plugin_manifest.yaml`)** De "ID-kaart" van een plugin. Bevat alle metadata die de `PluginRegistry` nodig heeft om de plugin te ontdekken en te valideren.

**Meta Workflows (`Optimization`, `VariantTest`)** Hoog-niveau operaties die de kern-executielogica herhaaldelijk en systematisch aanroepen voor complexe kwantitatieve analyses.

**MonitorOperator** De manager van de `MonitorWorkers`. Zorgt ervoor dat de juiste monitors worden aangeroepen als reactie op de relevante events (`ContextReady` of `LedgerStateChanged`).

**MonitorWorker** De "Waakhond". Een type plugin dat de staat van de operatie observeert en informatieve, **strategische events** publiceert, maar **nooit** zelf handelt.

**Operation** Het hoogste strategische niveau, gedefinieerd in een `operation.yaml`. Een verzameling van actieve `Strategy Blueprints` gekoppeld aan `ExecutionEnvironments`. Vervangt het `Portfolio`-concept.

**`operation.yaml`** Het centrale "draaiboek" van de quant. Koppelt `Strategy Blueprints` aan `ExecutionEnvironments`. Vervangt het `portfolio.yaml`-bestand.

**OptimizationService** De service die een grote parameterruimte systematisch doorzoekt door duizenden backtests parallel uit te voeren.

**ParallelRunService** Een herbruikbare backend-component die het efficiënt managen van een `multiprocessing`-pool voor parallelle backtests verzorgt, ter ondersteuning van `Meta Workflows`.

**Platform (Het "Quant Operating System")** De fundamentele visie van S1mpleTrader als een agnostisch **besturingssysteem** dat een flexibel framework biedt voor plugins.

**`platform.yaml`** Configuratiebestand met globale, niet-strategische platforminstellingen.

**Plugin** De fundamentele, zelfstandige en testbare eenheid van businesslogica in het systeem, behorend tot een van de vier `Worker`-categorieën.

**Plugin-First** De filosofie dat alle businesslogica wordt geïmplementeerd in de vorm van onafhankelijke, herbruikbare en testbare plugins.

**PluginRegistry** De specialistische klasse binnen het `Assembly Team` die verantwoordelijk is voor het scannen van de `plugins/`-map en het valideren van alle manifesten.

**Portfolio** Verouderde term. De strategische rol is overgenomen door **`Operation`**, de financiële rol door **`StrategyLedger`**.

**Portfolio Blueprint** Verouderde term. Nu vervangen door `operation.yaml`.

**PortfolioSupervisor** Verouderde term. De verantwoordelijkheden zijn nu verdeeld over het `Operation`-concept en de verschillende `Operators`.

**Pydantic** De Python-bibliotheek die wordt gebruikt voor datavalidatie en het definiëren van de data-contracten (DTO's, configuratie-schema's).

**RunOrchestrator** Verouderde term. Het opstartproces wordt nu direct gedreven door het uitvoeren van een `Operation`.

**`schedule.yaml`** Configuratiebestand dat de `Scheduler` configureert om op gezette tijden (interval of cron) specifieke, tijd-gebaseerde events te publiceren.

**Schema (`schema.py`)** Het bestand binnen een plugin dat het Pydantic-model bevat dat de configuratieparameters van die specifieke plugin definieert en valideert.

**State Reconciliation** Het "pull"-proces voor live-omgevingen waarbij de interne `StrategyLedger`-staat periodiek wordt gevalideerd en gecorrigeerd tegen de "enige bron van waarheid": de exchange.

**Strategy Builder** De specifieke "werkruimte" in de Web UI waar een gebruiker visueel een `strategy_blueprint.yaml` kan samenstellen.

**`strategy_blueprint.yaml`** De gedetailleerde "receptenkaart". Beschrijft de volledige configuratie van plugins (`workforce`) en parameters voor één strategie. Vervangt het `run_blueprint.yaml`-bestand.

**StrategyEngine** Verouderde term. De analytische logica is nu de verantwoordelijkheid van de `AnalysisOperator` en `AnalysisWorkers`.

**StrategyLedger** Het "domme grootboek". Een backend-component dat de financiële staat (kapitaal, posities, PnL) bijhoudt voor **één enkele, geïsoleerde strategie-run**.

**StrategyOperator** Verouderde term. De generieke rol is opgesplitst in de vier specifieke en functionele `Operators` (Context, Analysis, Monitor, Execution).

**StrategyWorker** Verouderde term. Nu vervangen door `AnalysisWorker`.

**Supervisor Model** Het crash-recovery mechanisme voor live trading, waarbij een extern "watchdog"-proces de hoofdapplicatie monitort en indien nodig herstart.

**Trade Explorer** De specifieke "werkruimte" in de Web UI die een diepgaande visuele analyse van de trades en de context van een voltooide run mogelijk maakt.

**TypeScript** De programmeertaal die voor de frontend wordt gebruikt om een type-veilig contract met de Pydantic-backend te garanderen via automatisch gegenereerde interfaces.

**VariantTestService** De service die een klein, gedefinieerd aantal strategie-varianten "head-to-head" met elkaar vergelijkt onder identieke marktomstandigheden.

**Worker (`worker.py`)** Het bestand binnen een plugin dat de Python-klasse met de daadwerkelijke businesslogica bevat.

**WorkerBuilder** De specialistische klasse binnen het `Assembly Team` die op aanvraag een geïnstantieerd en gevalideerd `worker`-object bouwt.

**`wiring_map.yaml`** De "bouwtekening" van de dataflow. Beschrijft expliciet welke methode op welk component wordt aangeroepen als reactie op een specifiek event.



---

# B_BIJLAGE_OPENSTAANDE_VRAAGSTUKKEN.md

Bijlage B: Openstaande Vraagstukken & Onderzoekspunten
Dit document bevat een lijst van bekende "onbekenden" en complexe vraagstukken die tijdens de detailimplementatie van de V2-architectuur verder onderzocht en opgelost moeten worden. Ze worden hier vastgelegd om te verzekeren dat ze niet vergeten worden.

B.1. State Management voor Stateful Plugins (Status: Gedeeltelijk ontworpen)

Vraagstuk: Hoe persisteren, beheren en herstellen we de staat van stateful plugins (bv. een Grid Trading-strategie die zijn openstaande grid-levels moet onthouden) op een robuuste manier, met name na een applicatiecrash?

Zie ook: docs/system/6_RESILIENCE_AND_OPERATIONS.md (paragraaf 6.1.1)

B.2. Data Synchronisatie in Live Omgevingen

Vraagstuk: Hoe gaat de LiveEnvironment om met asynchrone prijs-ticks die voor verschillende assets op verschillende momenten binnenkomen? Moet de orkestratie tick-gedreven zijn (complexer, maar nauwkeuriger) of bar-gedreven (eenvoudiger, maar met mogelijke vertraging)?

B.3. Performance en Geheugengebruik

Vraagstuk: Wat is de meest efficiënte strategie voor het beheren van geheugen bij grootschalige Multi-Time-Frame (MTF) analyses, met name wanneer dit over meerdere assets parallel gebeurt? Hoe voorkomen we onnodige duplicatie van data in het geheugen?

B.4. Debugging en Traceability (Status: Ontworpen)

Vraagstuk: Welke tools of modi moeten we ontwikkelen om het debuggen van complexe, parallelle runs te faciliteren? Hoe kan een ontwikkelaar eenvoudig de volledige levenscyclus van één specifieke trade volgen (traceability) door alle lagen en plugins heen?

Zie ook: docs/system/7_DEVELOPMENT_STRATEGY.md (paragraaf 9.3.2)

---

# D_BIJLAGE_PLUGIN_IDE.md

# **Bijlage D: De Plugin Development Experience & IDE**

**Versie:** 1.0 · **Status:** Concept

Dit document beschrijft de architectuur en de gebruikerservaring (UX) voor de web-based Integrated Development Environment (IDE) voor plugins binnen S1mpleTrader V2. Het doel van deze IDE is om het ontwikkelen van plugins te transformeren van een puur technische taak naar een laagdrempelige, creatieve en domein-specifieke functie voor kwantitatieve analisten ("quants").

---

## **F.1. Kernfilosofie: Abstractie & Glijdende Schaal**

De fundamentele uitdaging van elk plugin-systeem is de balans tussen gebruiksgemak en de kracht van code. Om dit op te lossen, hanteren we twee kernprincipes:

1. **Abstractie van Complexiteit**: De quant wordt volledig ontlast van de onderliggende technische en beveiligingscomplexiteit van het platform. Concepten als `Protocols`, `sandboxing`, `Pydantic-validatie` en `code signing` zijn de verantwoordelijkheid van het platform en worden onzichtbaar op de achtergrond afgehandeld.  
2. **Glijdende Schaal van Abstractie**: De IDE is geen "one-size-fits-all" oplossing. Het biedt een gelaagd model met verschillende abstractieniveaus. De quant kan zelf kiezen hoe diep hij in de code wil duiken, afhankelijk van zijn vaardigheden en de complexiteit van de strategie die hij wil bouwen.

---

## **F.2. De MVP: De "Slimme Boilerplate Generator"**

De eerste, meest cruciale stap is het bouwen van een Minimum Viable Product (MVP) dat het grootste pijnpunt voor de ontwikkelaar oplost: het handmatig aanmaken van de repetitieve boilerplate-code.

### **F.2.1. De "Nieuwe Plugin" Wizard**

Het hart van de MVP is een eenvoudig, gebruiksvriendelijk formulier in de Web IDE dat de ontwikkelaar door de creatie van een nieuwe plugin leidt. De focus ligt op de *intentie* van de plugin, niet op de technische implementatie.

**Velden in het Formulier:**

* **Display Naam**  
  * **UI Element**: Tekstveld.  
  * **Doel**: De mens-leesbare naam van de plugin zoals deze overal in de UI (strategie-bouwer, rapporten, grafieken) zal verschijnen.  
  * **Voorbeeld**: `Snelle EMA Crossover`  
* **Technische Naam**  
  * **UI Element**: *Read-only* tekstveld dat dynamisch wordt bijgewerkt.  
  * **Doel**: De `snake_case` identifier die intern wordt gebruikt voor map- en bestandsnamen. Dit veld wordt automatisch afgeleid van de Display Naam, waardoor de quant `snake_case` niet hoeft te kennen.  
  * **Voorbeeld**: `snelle_ema_crossover`  
* **Plugin Type**  
  * **UI Element**: Dropdown-menu.  
  * **Doel**: Bepaalt de rol van de plugin in de strategie-pijplijn.  
  * **Abstractie**: De opties in de dropdown zijn mensvriendelijke, vertaalde beschrijvingen (bv. "Signaal Generator (De Verkenner)"), niet de technische `enum`-waarden (`signal_generator`). Het platform vertaalt de keuze van de gebruiker op de achtergrond naar de juiste technische waarde.  
* **Beschrijving & Auteur (Optioneel)**  
  * **UI Element**: Tekstvelden.  
  * **Doel**: Verrijken de `plugin_manifest.yaml` en de docstrings direct bij de creatie.

### **F.2.2. De Template-gedreven `PluginCreator`**

Op de backend wordt een `PluginCreator` in de `assembly` module verantwoordelijk voor het genereren van de bestanden. Deze service gebruikt een set van template-bestanden (`.tpl`) die de volledige, correcte en linter-vriendelijke boilerplate bevatten, inclusief:

* Een `plugin_manifest.yaml` met een standaard restrictief `permissions` blok.  
* Een `worker.py` met de correcte klasse-definitie en interface.  
* Lege `schema.py` en `context_schema.py` bestanden.  
* Een `tests/test_worker.py` met een placeholder-test.

Voor de MVP stopt de verantwoordelijkheid van de IDE hier. De ontwikkelaar opent de gegenereerde bestanden in zijn favoriete lokale IDE (bv. VS Code) om de daadwerkelijke logica te schrijven en de tests uit te voeren via de command-line.

---

## **F.3. De Toekomstvisie: Een Gelaagde Web IDE**

Na de MVP wordt de Web IDE uitgebreid tot een volwaardige ontwikkelomgeving door de volgende drie lagen van abstractie aan te bieden voor het bewerken van de `worker.py` en `test_worker.py`.

### **Laag 1: De "No-Code" Strategie Bouwer**

* **Concept**: Het bouwen van een strategie door logische "LEGO-blokjes" op een visueel canvas met elkaar te verbinden.  
* **Interface**: Een drag-and-drop interface met een bibliotheek van door het platform aangeboden functies (Indicatoren, Vergelijkingen, Signaal Acties).  
* **Voorbeeld**: `[EMA(10)]` -> `[Kruist Boven]` -> `[EMA(50)]` -> `[Genereer Long Signaal]`.  
* **Testen**: Volledig geautomatiseerd via een scenario-bouwer ("Gegeven *dit* scenario, verwacht ik *deze* uitkomst").  
* **Doelgroep**: Quants zonder programmeerervaring; snelle prototyping van veelvoorkomende strategieën.

### **Laag 2: De "Low-Code" Scripting Helper**

* **Concept**: Een "Mad Libs" benadering waarbij de ontwikkelaar alleen de kernlogica invult in een gestructureerd script-venster, terwijl het platform de complexiteit van de S1mpleTrader-architectuur (DTO's, interfaces) volledig abstraheert.  
* **Interface**: Een formulier-achtige editor die de ontwikkelaar begeleidt. Indicatoren worden aangevraagd via een UI, en de kernlogica wordt geschreven in een klein Python-script dat gebruik maakt van simpele, door het platform aangeboden functies zoals `generate_signal()`.  
* **Testen**: Begeleid via een "Test Data Generator" UI en een "Assertie Helper" formulier.  
* **Doelgroep**: De gemiddelde quant die basis Python kent en zich puur wil focussen op de `if-then` logica van zijn strategie.

### **Laag 3: De "Pro-Code" Embedded IDE**

* **Concept**: Een volwaardige, in de browser geïntegreerde code-editor (zoals de Monaco Editor van VS Code) voor maximale vrijheid.  
* **Interface**: Een complete, in-browser IDE met syntax highlighting, IntelliSense voor S1mpleTrader-specifieke code, real-time linting, en de mogelijkheid om de `worker.py` en `test_worker.py` bestanden direct te bewerken.  
* **Testen**: Handmatig schrijven van `pytest` code in een apart tabblad van de editor.  
* **Doelgroep**: Ervaren ontwikkelaars of quants die zeer complexe, unieke strategieën willen bouwen die niet passen in de gestructureerde mallen van de hogere lagen.

---

## **F.4. Architectuur voor Plugin Internationalisatie (i18n)**

Om een uitwisselbaar ecosysteem te ondersteunen, moet de IDE de creatie van meertalige plugins faciliteren.

* **Structuur**: Elke plugin krijgt een eigen `locales/` map met `en.yaml`, `nl.yaml`, etc.  
* **Abstractie in de IDE**:  
  * De wizard voor het aanmaken van parameters (`schema.py`) en visualisaties (`context_schema.py`) zal geen code tonen, maar UI-formulieren.  
  * Voor elke parameter of visueel element (bv. een lijn in een grafiek) zal de UI, naast de technische configuratie, tekstvelden aanbieden voor "Display Label" en "Hulptekst".  
  * Op de achtergrond schrijft de `PluginEditorService` deze teksten niet hardcoded weg, maar genereert het de correcte `key-value` paren in de respectievelijke `locales/*.yaml` bestanden.  
* **Resultaat**: De quant vult simpele tekstvelden in, en het platform zorgt automatisch voor de volledige i18n-infrastructuur. Dit maakt het voor hem triviaal om zijn plugin meertalig te maken, wat essentieel is voor de bruikbaarheid binnen de bredere S1mpleTrader community.



---

# X_FRONTEND_INTEGRATION.md

# **X. Frontend Integratie: De UI als Intelligente IDE**

Versie: 2.1 (Details Hersteld)  
Status: Definitief  
Dit document beschrijft de volledige gebruikersworkflow en de frontend-architectuur die nodig is om de "supercharged" V2-ervaring te realiseren. Het vertaalt de architectonische blauwdruk naar een concreet, gebruikersgericht plan.

## **X.1. De Filosofie: De UI als IDE**

De kern van de V2-frontendstrategie is een paradigmaverschuiving: de web-UI is niet langer een simpele presentatielaag, maar de **primaire, geïntegreerde ontwikkelomgeving (IDE)** voor de kwantitatieve strateeg. Elke stap in de workflow, van het beheren van operaties tot het diepgaand analyseren van resultaten, vindt plaats binnen een naadloze, interactieve webapplicatie.

Dit maximaliseert de efficiëntie en verkort de **"Bouwen -> Meten -> Leren"**-cyclus van dagen of uren naar minuten.

## **X.2. De Werkruimtes: Een Context-Bewuste Workflow**

De hoofdnavigatie van de applicatie wordt gevormd door een reeks "werkruimtes". De workflow is hiërarchisch en context-bewust, beginnend bij de Operation.

| **OPERATION MANAGEMENT** | **STRATEGY BUILDER** | **BACKTESTING & ANALYSIS** | **LIVE MONITORING** | **PLUGIN DEVELOPMENT** |

## **X.3. De "Top-Down" Configuratie Flow**

De gebruiker wordt door een logische, gelaagde wizard geleid die frictie minimaliseert en contextuele hulp biedt op basis van de gemaakte keuzes.

### **Fase 1: Werkruimte "OPERATION MANAGEMENT" (Het Fundament)**

Dit is het onbetwiste startpunt voor elke activiteit. Een Operation definieert de "wereld" waarin strategieën opereren.

* **User Goal:** Het definiëren en beheren van de overkoepelende "draaiboeken" (operation.yaml) voor backtesting, paper trading en live trading.  
* **UI Componenten:**  
  1. **Operations Hub:** Een dashboard met een overzicht van alle geconfigureerde operaties (mijn_btc_operatie.yaml, live_eth_dca.yaml, etc.).  
  2. **Operation Creatie Wizard:** Een wizard die de gebruiker helpt een nieuw operation.yaml te configureren door hem door de velden te leiden.  
     * **Stap 1: Koppel Blueprints aan Werelden:** De gebruiker creëert strategy_links door een strategy_blueprint_id te selecteren uit de bibliotheek en deze te koppelen aan een execution_environment_id (die op hun beurt weer gedefinieerd zijn in environments.yaml).  
     * **Stap 2: Activeer Strategieën:** De gebruiker stelt per strategy_link in of deze is_active is.  
* **Vanuit dit dashboard** kan de gebruiker doorklikken om de strategieën binnen een operatie te beheren of een nieuwe strategie (strategy_blueprint.yaml) te creëren.

### **Fase 2: Werkruimte "STRATEGY BUILDER" (Context-Bewust Bouwen)**

Deze werkruimte wordt **altijd gestart vanuit de context van een specifieke Operation**. De wizard is nu "slim" en zich bewust van de grenzen en mogelijkheden die door de gekoppelde ExecutionEnvironments worden gedefinieerd.

* **User Goal:** Het intuïtief en foutloos samenstellen van een strategie-blueprint (strategy_blueprint.yaml) die gegarandeerd kan draaien binnen de geselecteerde "wereld".  
* **UI Componenten:**  
  1. **Data Selectie:** De wizard toont alleen de handelsparen en timeframes die beschikbaar zijn binnen de ExecutionEnvironment(s) van de actieve Operation.  
  2. **Visuele Workforce met Gefilterde Bibliotheek:** De gebruiker sleept plugins naar de workforce-secties (gegroepeerd per type: ContextWorkers, AnalysisWorkers, etc.). De plugin-bibliotheek is **dynamisch gefilterd**. Een plugin die rijke orderboek-data *vereist* (requires_context), wordt grijs weergegeven (uitgeschakeld) als de actieve Operation geen ExecutionEnvironment heeft die deze data levert. Een tooltip legt uit waarom.  
  3. **Configuratie Paneel:** Wanneer een plugin wordt geplaatst, verschijnt er een paneel met een **automatisch gegenereerd formulier** op basis van de schema.py van de plugin.  
  4. **Intelligent Timeframe Management:** Als een plugin een ander timeframe nodig heeft dan het execution_timeframe, detecteert de wizard dit en biedt de optie om de benodigde data vooraf te genereren (resamplen) of live te berekenen.  
* **Backend Interactie:** De UI haalt de gefilterde lijst plugins op via een PluginQueryService. Bij het opslaan stuurt de UI een JSON-representatie van de strategie naar een StrategyBlueprintEditorService, die het als een strategy_blueprint.yaml-bestand wegschrijft.

### **Fase 3: Werkruimte "BACKTESTING & ANALYSIS"**

* **User Goal:** Het rigoureus testen van strategieën en het diepgaand analyseren van de resultaten.  
* **UI Componenten:**  
  1. **Run Launcher:** Een sectie binnen de Operations Hub waar de gebruiker een Operation selecteert en een backtest, optimalisatie of varianten-test kan starten.  
  2. **Live Progress Dashboard:** Toont de live voortgang van een lopende Operation.  
  3. **Resultaten Hub:** Een centrale plek waar alle voltooide runs worden getoond, met doorklikmogelijkheden naar:  
     * **Optimization Results:** Een interactieve tabel om de beste parameter-sets te vinden.  
     * **Comparison Arena:** Een grafische vergelijking van strategie-varianten.  
     * **Trade Explorer:** De krachtigste analyse-tool. Hier kan de gebruiker door individuele trades klikken en op een grafiek precies zien wat de context was op het moment van de trade (actieve indicatoren, marktstructuur, etc.).  
* **Backend Interactie:** De UI roept de Operations-service, OptimizationService en VariantTestService aan.

### **Fase 4: Werkruimte "LIVE MONITORING"**

* **User Goal:** De prestaties van live-operaties continu monitoren.  
* **UI Componenten:**  
  * **Live Dashboard:** Een real-time dashboard (per Operation) dat de geaggregeerde PnL van de actieve StrategyLedgers toont, samen met open posities, orders, en een log-stream.  
  * Een prominente **"Noodstop"-knop** per strategy_link of voor de hele Operation, die een ShutdownRequested-event publiceert.  
* **Backend Interactie:** De UI leest de live-staat via API-endpoints die gekoppeld zijn aan de AggregatePortfolioUpdated- en LedgerStateChanged-events.

### **Fase 5: Werkruimte "PLUGIN DEVELOPMENT"**

* **User Goal:** Het snel en betrouwbaar ontwikkelen en testen van de herbruikbare "LEGO-stukjes" (plugins).  
* **UI Componenten:**  
  * **Plugin Registry Viewer:** Een overzichtstabel van alle ontdekte plugins.  
  * **Plugin Creator Wizard:** Een formulier om de boilerplate-code voor een nieuwe plugin te genereren.  
  * **Unit Test Runner:** Een UI-knop per plugin om de bijbehorende unit tests op de backend uit te voeren.  
* **Backend Interactie:** De UI communiceert met een PluginQueryService en een PluginEditorService.

## **X.4. Het Frontend-Backend Contract: BFF & TypeScript**

De naadloze ervaring wordt technisch mogelijk gemaakt door twee kernprincipes:

1. **Backend-for-Frontend (BFF):** De frontends/web/api/ is geen generieke API, maar een **backend die exclusief voor de frontends/web/ui/ werkt**. Hij levert data in exact het formaat dat de UI-componenten nodig hebben.  
2. **Contractuele Zekerheid met TypeScript:** We formaliseren het contract. Een tool in de ontwikkel-workflow leest de Pydantic-modellen en genereert automatisch corresponderende **TypeScript interfaces**. Een wijziging in de backend die niet in de frontend wordt doorgevoerd, leidt onmiddellijk tot een **compile-fout**, niet tot een onverwachte bug in productie.

Deze aanpak zorgt voor een robuust, ontkoppeld en tegelijkertijd perfect gesynchroniseerd ecosysteem.

---

