# A_Bijlage_Terminologie.md

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

---

## **Alfabetische Terminologie**

**AggregationStrategy** Een enum die bepaalt hoe een EventAdapter de resultaten van workers combineert. Opties: `COLLECT_ALL` (verzamel alle resultaten), `CHAIN_THROUGH` (output wordt input voor volgende), `NONE` (geen aggregatie).

**Atomic Writes (Journaling)** Een robuust state-saving mechanisme dat dataverlies bij een crash voorkomt door eerst naar een tijdelijk `.journal`-bestand te schrijven alvorens het originele state-bestand te overschrijven. Geïmplementeerd in de `IStatePersistor` en `IJournalPersistor` interfaces.

**Backend-for-Frontend (BFF)** Een gespecialiseerde API-laag in de architectuur die als enige doel heeft om data te leveren in het exacte formaat dat de Web UI nodig heeft, wat de frontend-code aanzienlijk versimpelt.

**BaseWorker** De absolute, abstracte basisklasse voor alle workers. Definieert alleen de `__init__`. Een ontwikkelaar erft hier nooit direct van, maar kiest altijd een van de twee ROL-definiërende kinderen: `StandardWorker` of `EventDrivenWorker`.

**BuildSpecs** Machine-instructies gegenereerd door ConfigTranslator uit configuratielagen. Bevat complete instructies voor runtime componenten inclusief workforce_spec, wiring_spec en environment_spec.

**Capability (Worker Capability)** Een extra vaardigheid die een worker kan bezitten, onafhankelijk van zijn ROL. Capabilities (zoals state, events, journaling) worden uitsluitend gedeclareerd in de `capabilities`-sectie van het `manifest.yaml`.

**ConfigTranslator** De centrale component die alle configuratielagen (PlatformConfig, OperationConfig, StrategyConfig) vertaalt naar machine-instructies (BuildSpecs).

**Configuratie-gedreven** Het kernprincipe dat het gedrag van de applicatie volledig wordt bestuurd door YAML-configuratiebestanden, niet door hardgecodeerde logica.

**Configuratie Lagen** Drie strikt gescheiden configuratieniveaus: PlatformConfig (globale instellingen), OperationConfig (werkruimte), StrategyConfig (gebruikersintentie).

**ContextWorker** De "Cartograaf". Een type plugin dat ruwe marktdata verrijkt met analytische context (bv. het berekenen van indicatoren). Produceert een verrijkte TradingContext.

**Contract-gedreven** Het kernprincipe dat alle data-uitwisseling en configuratie wordt gevalideerd door strikte schema's (Pydantic, TypeScript-interfaces).

**Causaal ID Framework** Het traceability systeem dat getypeerde, semantische IDs (`TradeID`, `OpportunityID`, `ThreatID`, `ScheduledID`) gebruikt om volledige causale reconstructie mogelijk te maken: "Waarom is deze trade geopend/gesloten?"

**Circuit Breaker** Een veiligheidsmechanisme, typisch binnen een ExecutionEnvironment, dat bij aanhoudende (netwerk)problemen de strategie in een veilige, passieve modus plaatst om verdere schade te voorkomen.

**Clock** De component binnen een ExecutionEnvironment die de "hartslag" (ticks) van het systeem genereert, ofwel gesimuleerd uit historische data (Backtest) of real-time (Live/Paper).

**connectors.yaml** Configuratiebestand dat de technische details (incl. secrets) voor verbindingen met externe, live partijen (bv. exchanges) definieert.

**DTO (Data Transfer Object)** Een Pydantic BaseModel (bv. Signal) dat dient als een strikt contract voor data die als payload op de EventBus wordt doorgegeven.

**data_sources.yaml** Configuratiebestand dat de catalogus van alle beschikbare lokale historische datasets (bv. Parquet-archieven) op schijf registreert.

**DispositionEnvelope** Een gestandaardiseerde 'envelope' die de intentie van een worker na uitvoering aangeeft. Bevat de disposition (CONTINUE, PUBLISH, STOP) en optioneel event_name en event_payload.

**environments.yaml** Configuratiebestand dat de "werelden" (ExecutionEnvironments) definieert en ze koppelt aan een connector_id of data_source_id.

**EventAdapter** Een generieke component die als "vertaler" fungeert tussen de EventBus en de (bus-agnostische) worker-componenten, geconfigureerd via wiring_specs uit BuildSpecs.

**Event Chain Validatie** Mechanisme dat automatisch valideert of alle event triggers een publisher hebben en vice versa. Voorkomt circular dependencies en waarschuwt voor "dode" events. Onderdeel van de Event Architecture.

**event_map.yaml** Configuratiebestand dat elke toegestane event-naam definieert en koppelt aan zijn verplichte DTO-contract.

**Event Topology** De term voor de volledige grafiek van event-producenten, -consumenten en hun onderlinge relaties. Kan automatisch worden gegenereerd (impliciete pijplijnen) of expliciet worden gedefinieerd (custom event chains).

**ExecutionEnvironment** De technische definitie van een "wereld" waarin een strategie kan draaien (Backtest, Paper, of Live). Verantwoordelijk voor het creëren van TradingContext.

**ExecutionWorker** De "Uitvoerder". Een type plugin dat luistert naar specifieke triggers om deterministische, op regels gebaseerde acties direct uit te voeren. Voert plannen uit en beheert actieve posities.

**Feedback Loop (Strategisch)** De door de gebruiker bestuurde "Bouwen -> Meten -> Leren" cyclus, gefaciliteerd door de Web UI.

**Feedback Loop (Technisch)** De real-time feedback binnen een run, waarbij de staat van de StrategyLedger de input kan zijn voor de volgende cyclus.

**Heartbeat** Een mechanisme in een live dataverbinding om de gezondheid van de connectie te monitoren door te controleren op periodieke signalen van de server.

**IDataPersistor** Protocol interface voor marktdata persistentie. Geoptimaliseerd voor grote volumes kolom-georiënteerde tijdreeksdata. Geïmplementeerd door ParquetPersistor.

**IEventHandler** Protocol interface voor event publicatie. Workers gebruiken deze abstractie in plaats van directe EventBus koppeling. Maakt workers testbaar en herbruikbaar.

**IJournalPersistor** Protocol interface voor strategy journal persistentie. Append-only, semi-gestructureerde historische logdata.

**Impliciete Pijplijnen** Event niveau waarbij het systeem automatisch de event chain genereert op basis van de workforce definitie. Voor 95% van standaard strategieën. Geen event management nodig voor de quant.

**IStatePersistor** Protocol interface voor plugin state persistentie. Kleine, transactionele, read-write data met atomische consistentie via journaling.

**ITradingContextProvider** Interface voor de service die DTO-gebaseerde 'point-in-time' context beheert en levert. Beheert toegang tot de tijdelijke TickCache.

**Manifest (plugin_manifest.yaml)** De "ID-kaart" van een plugin. Bevat alle metadata die het systeem nodig heeft. Dit is de Single Source of Truth voor de Capabilities van een worker, gedefinieerd in een centrale `capabilities`-sectie.

**Meta Workflows (Optimization, VariantTest)** Hoog-niveau operaties die de kern-executielogica herhaaldelijk en systematisch aanroepen voor complexe kwantitatieve analyses.

**OpportunityID** Getypeerde ID die de reden voor trade opening vastlegt. Gegenereerd door OpportunityWorker. Beantwoordt de vraag: "Waarom is deze trade geopend?"

**OpportunityWorker** De "Verkenner". Een type plugin dat de verrijkte context analyseert om handelskansen te detecteren. Herkent patronen en genereert "handelsideeën" zonder concrete plannen.

**ParallelRunService** Een herbruikbare backend-component die het efficiënt managen van een multiprocessing-pool voor parallelle backtests verzorgt, ter ondersteuning van Meta Workflows.

**PersistorFactory** De Assembly Team component die alle persistor-instanties creëert en beheert. De "hoofdaannemer" voor de Persistence Suite. Creëert IDataPersistor, IStatePersistor en IJournalPersistor implementaties.

**Platform (Het "Quant Operating System")** De fundamentele visie van S1mpleTrader als een agnostisch besturingssysteem dat een flexibel framework biedt voor plugins.

**platform.yaml** Configuratiebestand met globale, niet-strategische platforminstellingen.

**PlanningWorker** De "Strateeg". Een type plugin dat handelskansen transformeert naar concrete, uitvoerbare plannen. Bepaalt entry, exit, size en routing.

**Plugin** De fundamentele, zelfstandige en testbare eenheid van businesslogica in het systeem, behorend tot een van de vijf Worker-categorieën.

**Plugin-First** De filosofie dat alle businesslogica wordt geïmplementeerd in de vorm van onafhankelijke, herbruikbare en testbare plugins.

**Point-in-Time Principe** Alle data-uitwisseling is gebaseerd op de informatie die relevant is voor één specifiek moment (tick). Workers opereren op basis van de staat nu, niet op basis van een groeiende historische dataset.

**Predefined Triggers** Event niveau met voorgedefinieerde trigger namen voor common use cases: `on_context_ready`, `on_signal_generated`, `on_ledger_update`, `on_position_opened`, `on_position_closed`, `on_schedule`.

**ROL (Worker Rol)** De fundamentele, architecturale rol van een worker, die bepaalt hoe de worker wordt aangeroepen. Een ontwikkelaar kiest de ROL door te erven van `StandardWorker` (voor de georkestreerde pijplijn) of `EventDrivenWorker` (voor autonome, event-based acties).

**RoutedTradePlan** DTO voor een volledig uitgewerkt trade plan. Output van PlanningWorker, bevat entry, exit, size en routing details. Klaar voor executie door ExecutionWorker.

**schedule.yaml** Configuratiebestand dat de Scheduler configureert om op gezette tijden (interval of cron) specifieke, tijd-gebaseerde events te publiceren.

**ScheduledID** Getypeerde ID voor tijd-gedreven acties. Gegenereerd door de Scheduler. Beantwoordt de vraag: "Waarom is deze actie nu uitgevoerd?"

**Schema (schema.py)** Het bestand binnen een plugin dat het Pydantic-model bevat dat de configuratieparameters van die specifieke plugin definieert en valideert.

**StandardWorker** Een abstracte basisklasse die de ROL definieert van een worker die deelneemt aan de georkestreerde pijplijn. Dwingt de implementatie van een `process`-methode af.

**State Reconciliation** Het "pull"-proces voor live-omgevingen waarbij de interne StrategyLedger-staat periodiek wordt gevalideerd en gecorrigeerd tegen de "enige bron van waarheid": de exchange.

**Strategy Builder** De specifieke "werkruimte" in de Web UI waar een gebruiker visueel een strategy_blueprint.yaml kan samenstellen.

**strategy_blueprint.yaml** De gedetailleerde "receptenkaart". Beschrijft de volledige configuratie van plugins (workforce) en parameters voor één strategie.

**StrategyJournal** Het append-only, historische logbestand dat de volledige causale geschiedenis van een strategie-run vastlegt. Bevat opportunity detections, rejected opportunities (met ThreatID), trade executions en alle causale links.

**StrategyLedger** Het "domme grootboek". Een backend-component dat de financiële staat (kapitaal, posities, PnL) bijhoudt voor één enkele, geïsoleerde strategie-run. Alleen operationele state, geen historie.

**Supervisor Model** Het crash-recovery mechanisme voor live trading, waarbij een extern "watchdog"-proces de hoofdapplicatie monitort en indien nodig herstart.

**ThreatID** Getypeerde ID die de reden voor ingreep vastlegt. Gegenereerd door ThreatWorker. Beantwoordt de vraag: "Waarom is deze trade gesloten/aangepast?"

**ThreatWorker** De "Waakhond". Een type plugin dat de staat van de operatie observeert en informatieve, strategische events publiceert, maar nooit zelf handelt. Detecteert risico's en bedreigingen.

**TickCache** Tijdelijke dataopslag die alleen DTO-instanties bevat die intermediaire resultaten binnen die ene tick vertegenwoordigen. Leeft extreem kort en wordt weggegooid na elke tick.

**Trade Explorer** De specifieke "werkruimte" in de Web UI die een diepgaande visuele analyse van de trades en de context van een voltooide run mogelijk maakt. Verrijkt met causale reconstructie via het Causaal ID Framework.

**TradeID** Getypeerde ID als ankerpunt voor trade lifecycle. Gegenereerd door PlanningWorker of ExecutionWorker. Primaire sleutel in StrategyJournal.

**TradingContext** DTO dat de volledige trading context bevat. Het wordt direct gecreëerd door de ExecutionEnvironment. Bevat OHLCV data, verrijkte context en metadata.

**TypeScript** De programmeertaal die voor de frontend wordt gebruikt om een type-veilig contract met de Pydantic-backend te garanderen via automatisch gegenereerde interfaces.

**UI-Gedreven Flow Configuratie** Het proces waarbij gebruikers via de Strategy Builder UI visueel de worker flow configureren, resulterend in een strategy_wiring_map.yaml.

**Worker (worker.py)** Het bestand binnen een plugin dat de Python-klasse met de daadwerkelijke businesslogica bevat.

**WorkerBuilder** De specialistische klasse binnen het Assembly Team die de volledige workforce assembleert, classificeert, valideert en dependencies injecteert op basis van manifest capabilities.

**wiring_map.yaml** De "bouwtekening" van de dataflow. Beschrijft expliciet welke methode op welk component wordt aangeroepen als reactie op een specifiek event.

---

## **Architectuur: Kernconcepten**

### **Worker Taxonomie (5 Categorieën)**
De fundamentele organisatie van businesslogica:
1. **ContextWorker** - "De Cartograaf" (verrijkt data)
2. **OpportunityWorker** - "De Verkenner" (detecteert kansen)
3. **ThreatWorker** - "De Waakhond" (detecteert risico's)
4. **PlanningWorker** - "De Strateeg" (maakt plannen)
5. **ExecutionWorker** - "De Uitvoerder" (voert uit & beheert)

### **Platgeslagen Orkestratie**
Geen Operator-laag meer; directe worker-naar-worker communicatie via expliciete wiring_specs gegenereerd door UI.

### **Configuratie Lagen**
Drie gescheiden configuratieniveaus:
- **PlatformConfig** - Globale, statische platform instellingen
- **OperationConfig** - Specifieke werkruimte met strategieën en omgevingen
- **StrategyConfig** - Gebruikersintentie voor één strategie

### **Point-in-Time Data Model**
DTO-centric data-uitwisseling met TickCache voor synchrone doorgifte en ITradingContextProvider voor data toegang.

### **Manifest-Gedreven Capability Model**
De architectuur scheidt de ROL van een worker van zijn CAPABILITIES:
- **ROL (via Klasse):** De ontwikkelaar kiest een basisklasse die de rol definieert.
  - `StandardWorker`: Voor de georkestreerde pijplijn (`process()`-methode).
  - `EventDrivenWorker`: Voor autonome, event-gedreven logica.
- **CAPABILITIES (via Manifest):** Extra vaardigheden worden aangevraagd in `manifest.yaml`.
  - `capabilities.state: { enabled: true }`
  - `capabilities.events: { enabled: true }`
  - `capabilities.journaling: { enabled: true }`
De WorkerBuilder leest dit contract en injecteert de benodigde dependencies.

### **Causale Traceability**
Het Causaal ID Framework gebruikt getypeerde IDs:
- **TradeID** - Ankerpunt van trade
- **OpportunityID** - Waarom geopend?
- **ThreatID** - Waarom gesloten/aangepast?
- **ScheduledID** - Waarom nu?

### **Event Architectuur (3 Niveaus)**
1. **Impliciete Pijplijnen** - Automatisch gegenereerd (95% gebruik)
2. **Predefined Triggers** - Voorgedefinieerde trigger namen
3. **Custom Event Chains** - Volledige controle voor experts

---

**Einde Document**