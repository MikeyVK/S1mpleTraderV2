# **Architectonische Blauwdruk V2: Het Agnostische Handels-Ecosysteem**

Versie: 4.0 (Definitief Ontwerp)  
Status: Vastgesteld  
Auteurs: Michel Verkaik & Programmeerpartner  
Datum: 11 oktober 2025

## **Voorwoord: De Reis naar Architectonische Helderheid**

Dit document is meer dan een technische specificatie; het is het logboek van een intellectuele reis. Een reis die begon met een solide, procedurele V1-architectuur en, via een reeks van diepgaande, kritische dialogen, is geëvolueerd naar een volledig agnostisch, decentraal en event-gedreven ecosysteem. Elke sectie in dit document vertegenwoordigt een doorbraak, een moment waarop een complex probleem werd ontrafeld en opgelost met een elegante, zuivere oplossing.

Het doel van dit document is om de **filosofie**, de **structuur**, de **componenten** en de **interacties** van de S1mpleTrader V2-architectuur op een ondubbelzinnige manier vast te leggen. Het dient als de "Grondwet" voor alle toekomstige ontwikkeling, een ankerpunt dat ons scherp houdt op de kernprincipes die we samen hebben gedefinieerd: **Single Responsibility, Configuratie-gedreven, Contract-gedreven, en bovenal, Plugin-First.**

## **Hoofdstuk 1: De Kernfilosofie \- Het Platform als Puur Framework**

De meest fundamentele beslissing die we hebben genomen, is de herdefiniëring van de rol van S1mpleTrader zelf.

De oude visie (impliciet): S1mpleTrader is een applicatie die strategieën uitvoert.  
De nieuwe visie (expliciet): S1mpleTrader is een agnostisch besturingssysteem voor quants.  
Dit betekent dat de taak van het platform niet is om een specifieke manier van handelen af te dwingen of te dicteren. Zijn enige doel is het bieden van een extreem robuust, flexibel en schaalbaar **framework** waarbinnen een quant **alle** mogelijke kwantitatieve en operationele functionaliteit via zelfstandige, specialistische plugins kan implementeren.

Het platform is de facilitator, de "robotkeuken". De quant is de architect, de "Grote Chef" die het draaiboek schrijft en bepaalt welke robots welke taken uitvoeren. Deze filosofie is de drijvende kracht achter elke architectonische keuze in dit document.

## **Hoofdstuk 2: Het Paradigma \- Een Volledig Event-Gedreven Ecosysteem**

Om de "agnostische framework" filosofie technisch mogelijk te maken, stappen we volledig af van een centraal aangestuurde, hiërarchische flow. We omarmen een decentraal, event-gedreven model.

### **2.1. De Centrale EventBus: De Digitale Intercom**

Het hart van de V2-architectuur is een centrale **EventBus**. Dit is geen complexe message queue, maar een simpel in-memory publish-subscribe systeem dat fungeert als het zenuwstelsel van de applicatie.

* **Publiceren (Publish):** Een component (plugin) die een taak heeft voltooid of een gebeurtenis heeft gedetecteerd, publiceert een "bericht" (een DTO) op de EventBus. Hij roept als het ware iets door de intercom.  
* **Abonneren (Subscribe):** Andere componenten kunnen zich abonneren op specifieke soorten berichten. Zij "luisteren" naar de intercom.  
* **Ontkoppeling:** De publicerende component weet niet wie er luistert, en de luisterende component weet niet wie het bericht heeft gestuurd. Ze kennen alleen het **contract** van het bericht zelf. Dit is de essentie van ontkoppeling.

### **2.2. De Drie Lagen in een Event-Gedreven Context**

De strikte scheiding in drie lagen (Frontend \-\> Service \-\> Backend) blijft gehandhaafd, maar de rol van de Service-laag verandert fundamenteel.

* **Backend Laag (/backend)**: Blijft de pure **"Motor & Gereedschapskist"**. Bevat alle herbruikbare, stateless bouwstenen zoals DTO's, interfaces, de StrategyEngine en de ExecutionHandler. Deze laag heeft en zal **nooit** kennis hebben van de EventBus.  
* **Service Laag (/services)**: Wordt de **"Faciliterende Laag"**. Zijn rol is niet langer het stap-voor-stap orkestreren van de backend. De Operations-service leeft hier en is de enige component die de EventBus daadwerkelijk creëert en het hele ecosysteem tijdens de bootstrap-fase "bedraadt".  
* **Frontend Laag (/frontends)**: Blijft de **"Gebruikersinterface"** (Web UI, API, CLI), waar de quant de configuratie van het ecosysteem ontwerpt.

## **Hoofdstuk 3: De Levenscyclus \- Operations, de Agnostische COO**

We hebben het concept van een PortfolioSupervisor of RunOrchestrator volledig geëlimineerd en vervangen door een component met een veel zuiverdere verantwoordelijkheid.

### **3.1. De Rol van Operations**

Operations is de "Chief Operating Officer" van het systeem, de hoogste component in de Service-laag. Zijn Single Responsibility Principle (SRP) is: **het waarborgen van de integriteit en de levenscyclus van een volledige, geconfigureerde Operation, door het delegeren van specialistische taken.**

Hij is de dirigent die het orkest opstelt en het startsein geeft, maar zich daarna volledig terugtrekt en het orkest zelfstandig laat spelen.

### **3.2. De Delegatietaken van Operations**

Operations voert **geen enkele** taak inhoudelijk zelf uit. Hij delegeert alles.

#### **Fase 1: Bootstrap (De Opstartfase) 🚀**

1. **Lezen**: Leest het operation.yaml-bestand.  
2. **Delegeer Validatie**: Geeft de ruwe configuratie aan een ConfigValidator-specialist. Deze specialist valideert de gehele configuratietrein, van de YAML-structuur tot het bestaan van elke genoemde plugin. Bij een fout stopt het proces onmiddellijk (fail fast).  
3. **Delegeer Assemblage**: Geeft de gevalideerde configuratie aan het Assembly Team met de opdracht: "Bouw een instantie van elke plugin die in deze configuratie wordt genoemd."  
4. **Delegeer 'Wiring'**: Geeft de lijst van geassembleerde plugins en de EventBus aan een EventBusManager-specialist. Deze "elektricien" inspecteert elke plugin en legt alle publish- en subscribe-verbindingen.  
5. **Delegeer Context Bootstrapping**: Geeft de opdracht aan de ContextBootstrapper om de initiële staat (bv. historische data) voor te bereiden.  
6. **Start de Scheduler**: Initialiseert de Scheduler met de schedule.yaml-configuratie.  
7. **Startschot**: Publiceert de OperationStarted event op de bus.

#### **Fase 2: Runtime (De Onderhoudsfase) ⚙️**

Tijdens de runtime heeft Operations **geen actieve, sturende rol**. Het ecosysteem is zelfregulerend. De State Reconciliation, die voorheen door de PortfolioSupervisor werd aangestuurd, wordt nu volledig autonoom getriggerd door de Scheduler.

#### **Fase 3: Shutdown (De Afsluitfase) 🔌**

1. **Luisteren**: Luistert naar een extern ShutdownRequested signaal.  
2. **Delegeren**: Publiceert één enkel ShutdownInitiated event op de bus. Alle langlevende plugins zijn zelf verantwoordelijk voor het opvangen van dit signaal en het gracieus afsluiten van hun eigen processen.

## **Hoofdstuk 4: De Hartslag \- De Scheduler**

Een cruciale doorbraak in ons ontwerp was de introductie van een onafhankelijke Scheduler.

* **SRP**: Zijn *enige* taak is het publiceren van **tijd-gebaseerde events (TimerEvents)** op de EventBus. Hij is de agnostische metronoom van het systeem.  
* **Configuratie-gedreven**: Hij wordt volledig geconfigureerd via een schedule.yaml. Hierin kan de quant een rijk programma van events definiëren, van simpele intervallen tot complexe, markt-specifieke cron-jobs.

**Voorbeeld schedule.yaml:**

schedule:  
  \# Een simpele, periodieke puls elke 5 minuten  
  \- event\_name: "five\_minute\_reconciliation\_tick"  
    type: "interval"  
    value: "5m"

  \# Een cron-job voor een specifieke taak  
  \- event\_name: "london\_open\_volatility\_check"  
    type: "cron"  
    value: "0 8 \* \* 1-5" \# Elke weekdag om 8:00  
    timezone: "Europe/London"

  \# Een event gebaseerd op een markt-kalender  
  \- event\_name: "end\_of\_us\_session"  
    type: "market\_schedule"  
    market: "NYSE"  
    event: "close"

De introductie van de Scheduler maakt componenten zoals de StateReconciliationAgent volledig autonoom en ontkoppelt Operations van elke runtime-verantwoordelijkheid.

## **Hoofdstuk 5: De Functionele Kern \- De Vier Plugin Categorieën**

Alle kwantitatieve en operationele logica is ondergebracht in vier duidelijk gescheiden, door de gebruiker te definiëren, plugin-categorieën. Het onderscheid tussen deze categorieën is de sleutel tot het begrijpen van de architectuur.

### **5.1. ContextWorkers (type: "context\_worker")**

* **Rol**: De "Voorbereiders".  
* **Taak**: Het verrijken van ruwe marktdata (DataFrame) met analytische context (indicatoren, marktstructuur, etc.).  
* **Aansturing**: Worden beheerd door een **ContextOperator** (de nieuwe naam voor ContextOrchestrator). Deze operator luistert naar MarketDataReceived events, voert de ContextWorker-pijplijn uit, en publiceert het resultaat als een ContextReady event.  
* **Voorbeeld**: EmaDetector, MarketStructureDetector.

### **5.2. StrategyWorkers (type: "strategy\_worker")**

* **Rol**: De "Analisten".  
* **Taak**: Het genereren van **analytische, niet-deterministische** handelsvoorstellen. Ze opereren binnen de StrategyEngine en doorlopen de 9-fasen trechter (van Signal tot RoutedTradePlan).  
* **Aansturing**: Worden beheerd door de **StrategyOperator**. Deze operator luistert naar ContextReady, roept de StrategyEngine aan, en publiceert het resultaat als een StrategyProposalReady event.  
* **Voorbeeld**: FVGEntryDetector, AtrExitPlanner, FixedRiskSizePlanner.

### **5.3. StrategyMonitors (type: "strategy\_monitor")**

* **Rol**: De "Sensoren" of "Waakhonden".  
* **Taak**: Het observeren van de operatie en het publiceren van **strategische, informatieve events (StrategicEvents)**. Ze handelen **nooit** zelf; ze zijn puur informationeel.  
* **Aansturing**: Abonneren zich direct op de EventBus. Ze worden niet aangestuurd door een operator, maar reageren autonoom op de events die voor hen relevant zijn.  
* **Output**: Een StrategicEvent DTO, bijvoorbeeld { "event\_type": "MAX\_DRAWDOWN\_BREACHED" }.  
* **Subtypes**:  
  1. **Context Monitors**: Bewaken de *externe marktomstandigheden*. Ze luisteren naar ContextReady. Voorbeelden: VolumeSpikeMonitor, LiquidityGapMonitor.  
  2. **State Monitors**: Bewaken de *interne, financiële staat* van een strategie. Ze luisteren naar LedgerStateChanged. Voorbeelden: MaxDrawdownMonitor, PerformanceDecayMonitor.

### **5.4. Operational Agents (type: "operational\_agent")**

* **Rol**: De "Actoren" of "Uitvoerders".  
* **Taak**: Het uitvoeren van **deterministische, op regels gebaseerde** acties. Dit kan een simpele, herhalende taak zijn of een reactie op een StrategicEvent.  
* **Aansturing**: Abonneren zich direct op de EventBus op hun specifieke triggers.  
* **Output**: Een ExecutionApproved event. Dit is een cruciale beslissing: agents produceren geen 'voorstellen', maar directe, goedgekeurde executie-opdrachten.  
* **Voorbeelden**:  
  * DCAAgent: Luistert naar een TimerEvent van de Scheduler om periodiek te kopen.  
  * PortfolioRebalancerAgent: Luistert naar een EQUITY\_SPIKE\_DETECTED StrategicEvent van een StrategyMonitor om de portfolio-allocatie te herbalanceren.  
  * EmergencyExitAgent: Luistert naar een FLASH\_CRASH\_DETECTED StrategicEvent om alle posities te sluiten.

## **Hoofdstuk 6: De Gelaagde Configuratie "Trein"**

De configuratie is opgebouwd uit een reeks van gelaagde YAML-bestanden. Het Assembly Team en de ConfigValidator doorlopen deze "trein" om een volledige, gevalideerde operatie op te bouwen.

1. **platform.yaml**: Globale, niet-strategische instellingen (logging, taal, etc.). Wordt beheerd door de platform-eigenaar.  
2. **connectors.yaml**: Definitie van alle beschikbare API-connectoren en hun credentials.  
3. **environments.yaml**: Definitie van de "werelden" (ExecutionEnvironments). Koppelt een naam (bv. live\_kraken) aan een type (live) en een connector\_id.  
4. **schedule.yaml**: Definitie van alle tijd-gebaseerde events voor de Scheduler.  
5. **operation.yaml**: Het "draaiboek" van de quant. Definieert een operatie door strategieën, monitors en agents te koppelen aan execution\_environments.  
6. **strategy\_blueprint.yaml**: De complete, diepgaande configuratie van **alle** gebruikte plugins (ContextWorkers, StrategyWorkers, StrategyMonitors, Operational Agents). Hier definieert de quant de parameters voor elke specialist. Dit bestand wordt gevalideerd door de schema.py van elke individuele plugin.  
7. **plugin\_manifest.yaml**: De "ID-kaart" van elke plugin. Definieert zijn type, dependencies, en, cruciaal, de produces\_events: List\[str\] voor StrategyMonitors.

## **Hoofdstuk 7: De Event-Gedreven Flow in Detail**

De onderlinge samenhang is niet langer hiërarchisch, maar ontvouwt zich autonoom via de EventBus. Hier is de levenscyclus van een enkele tick in een live-omgeving:

1. **Puls van de Buitenwereld**: De LiveEnvironment (gekoppeld aan een APIConnector) ontvangt een WebSocket-bericht en publiceert een **MarketDataReceived** event.  
2. **Context Creatie**: De **ContextOperator** vangt dit op. Hij roept zijn ContextWorkers aan om de ruwe data te verrijken en publiceert de complete **ContextReady** event. Dit DTO bevat de enriched\_df.  
3. **Parallelle Analyse & Monitoring**: Zodra ContextReady op de bus verschijnt, worden meerdere specialisten **tegelijkertijd** wakker:  
   * De **StrategyOperator** ontvangt het, roept zijn StrategyEngine (met StrategyWorkers) aan en publiceert een **StrategyProposalReady** event met een analytisch handelsvoorstel.  
   * Alle **StrategyMonitors** van het type ContextMonitor ontvangen het. Een VolumeSpikeMonitor kan bijvoorbeeld de volume-data analyseren en besluiten een **StrategicEvent(type="ABNORMAL\_VOLUME\_DETECTED")** te publiceren.  
4. **Deterministische Acties**:  
   * **Operational Agents** die luisteren naar ContextReady (bv. een TrailingStopAgent) voeren hun logica uit. Als een stop-loss moet worden aangepast, publiceren ze een **ExecutionApproved** event.  
5. **Centrale Goedkeuring (Optioneel)**: De RunOrchestrator (Operations) kan als laatste poortwachter luisteren naar StrategyProposalReady en ExecutionApproved events om een laatste, overkoepelende check uit te voeren, alvorens het definitieve ExecutionApproved event door te sturen. In de puurste vorm van de architectuur is deze stap niet nodig.  
6. **Technische Executie**: De **ExecutionHandler** is de enige die luistert naar ExecutionApproved. Hij ontvangt de opdracht en voert deze technisch uit (via de APIConnector of door de StrategyLedger aan te passen).  
7. **Feedback Loop**: Na een succesvolle executie publiceert de ExecutionHandler een **LedgerStateChanged** event.  
8. **Interne Monitoring**: De LedgerStateChanged event wordt opgevangen door:  
   * Alle **StrategyMonitors** van het type StateMonitor. Een MaxDrawdownMonitor kan de nieuwe equity curve analyseren en besluiten een **StrategicEvent(type="MAX\_DRAWDOWN\_BREACHED")** te publiceren.  
   * De **ContextOperator**, die de nieuwe PortfolioState gebruikt voor de *volgende* ContextReady-cyclus.  
9. **Reactieve Acties**:  
   * Een EmergencyExitAgent die luistert naar StrategicEvents ontvangt het MAX\_DRAWDOWN\_BREACHED event. Hij "ontwaakt", voert zijn geconfigureerde actie uit (bv. "sluit alle posities"), en publiceert de benodigde **ExecutionApproved** events.  
10. **De Cirkel is Rond**: De ExecutionHandler ontvangt deze nieuwe ExecutionApproved events, en de cyclus herhaalt zich.

## **Hoofdstuk 8: Conclusie \- De Voltooiing van de Visie**

De architectuur die we hebben ontworpen is de ultieme manifestatie van de "agnostisch framework" visie. We hebben een systeem gecreëerd dat niet alleen technisch robuust en schaalbaar is, maar dat de quant ook de maximale vrijheid en controle geeft.

* **SRP is Koning**: Elke component, van Operations tot de kleinste plugin, heeft één duidelijke, onbetwistbare verantwoordelijkheid.  
* **Volledig Decentraal**: Er is geen centrale "god-klasse" die de operatie micromanaged. Het ecosysteem reguleert zichzelf via de EventBus.  
* **Oneindig Uitbreidbaar**: Een quant kan nieuwe analytische logica, nieuwe risicomonitors en nieuwe geautomatiseerde agenten toevoegen door simpelweg een nieuwe plugin te schrijven en te configureren, zonder ooit de kern van het platform te hoeven aanraken.

Dit is de blauwdruk. Een puur, decentraal "Quant Operating System". Het platform faciliteert; de plugins, geconfigureerd door de quant, doen het werk.