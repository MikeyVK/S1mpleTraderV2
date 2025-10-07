# 0_V2_ARCHITECTURE.md

# **S1mpleTrader V2: Architectonische Blauwdruk**

Versie: 3.0 (Event-Gedreven Architectuur)  
Status: Definitief

## **Hoofdstuk 1: Visie & Architectonische Principes**

* **1.1. Visie**  
  Het creëren van één uniforme, plugin-gedreven architectuur die de volledige levenscyclus van een handelsstrategie ondersteunt: van concept & ontwikkeling, via rigoureuze backtesting en optimalisatie, naar paper trading en uiteindelijk live executie.  
* **1.2. De Event-Gedreven Architectuur**  
  De kern van de V2-architectuur is een ontkoppeld, **event-gedreven model** dat robuustheid, schaalbaarheid en onderhoudbaarheid maximaliseert. Een centrale EventBus fungeert als zenuwstelsel, waardoor componenten als gelijkwaardige specialisten samenwerken via strikt gedefinieerde, contract-gedreven events.  
  **→ Lees de volledige uitwerking in: system/1_EVENT_DRIVEN_ARCHITECTURE.md**

## **Hoofdstuk 2: Architectuur & Componenten**

De applicatie is opgebouwd uit drie strikt gescheiden lagen (Frontend → Service → Backend). Dit hoofdstuk beschrijft de verantwoordelijkheden van elke laag, definieert de functionele categorieën van de componenten, en licht de rol toe van kerncomponenten zoals de PortfolioSupervisor, ContextOrchestrator en de StrategyOperator.

**→ Lees de volledige uitwerking in: system/2_ARCHITECTURE.md**

## **Hoofdstuk 3: De Anatomie van een Plugin**

Een plugin is de fundamentele, zelfstandige en testbare eenheid van logica. Dit hoofdstuk beschrijft de mappenstructuur, het plugin_manifest.yaml (de ID-kaart), het schema.py (het contract) en de worker.py (de logica), en de rol van het BaseWorker-raamwerk.

**→ Lees de volledige uitwerking in: system/3_PLUGIN_ANATOMY.md**

## **Hoofdstuk 4: De Analytische Pijplijn**

De StrategyEngine is de motor van de analytische pijplijn. Dit hoofdstuk beschrijft de interne, procedurele (fase 3-9 van de analytische pijplijn) die wordt uitgevoerd in reactie op een ContextReady-event. Het detailleert hoe een idee stapsgewijs wordt gevalideerd en omgezet in een StrategyProposal, van Regime Context tot Critical Event Detection.

**→ Lees de volledige uitwerking in: system/4_WORKFLOW_AND_ORCHESTRATOR.md**

## **Hoofdstuk 5: Frontend Integratie**

De frontend is de primaire ontwikkelomgeving (IDE) voor de strateeg, ontworpen om de "Bouwen -> Meten -> Leren" cyclus te maximaliseren. Dit hoofdstuk beschrijft de verschillende "Werkruimtes" en legt uit hoe een strikt contract tussen de Pydantic-backend en de TypeScript-frontend zorgt voor een robuuste gebruikerservaring.

**→ Lees de volledige uitwerking in: system/5_FRONTEND_INTEGRATION.md**

## **Hoofdstuk 6: Robuustheid & Operationele Betrouwbaarheid**

Een live trading-systeem moet veerkrachtig zijn. Dit hoofdstuk beschrijft de drie verdedigingslinies: atomische schrijfacties (journaling) voor staatintegriteit, protocollen voor netwerkveerkracht (heartbeat, reconnect, reconciliation) en een Supervisor-model voor automatische crash recovery.

**→ Lees de volledige uitwerking in: system/6_RESILIENCE_AND_OPERATIONS.md**

## **Hoofdstuk 7: Ontwikkelstrategie & Tooling**

Dit hoofdstuk beschrijft de workflow, van de visuele 'Strategy Builder' tot de 'Trade Explorer'. Daarnaast worden de kern-tools behandeld, zoals de gespecialiseerde entrypoints, de gelaagde logging-aanpak en de cruciale rol van de Correlation ID voor traceerbaarheid.

**→ Lees de volledige uitwerking in: system/7_DEVELOPMENT_STRATEGY.md**

## **Hoofdstuk 8: Meta Workflows**

Bovenop de executie van een enkele strategie draaien "Meta Workflows" om geavanceerde analyses uit te voeren. Dit hoofdstuk beschrijft de OptimizationService en VariantTestService, die de kern-executielogica herhaaldelijk en parallel aanroepen om complexe kwantitatieve analyses uit te voeren.

**→ Lees de volledige uitwerking in: system/8_META_WORKFLOWS.md**

## **Hoofdstuk 9: Coding Standaarden & Design Principles**

Een consistente codebase is essentieel. Dit hoofdstuk beschrijft de verplichte standaarden (PEP 8, Type Hinting, Docstrings) en de kern design principles (SOLID, Factory Pattern, DTO's) die de vier kernprincipes van V2 (Plugin First, Scheiding van Zorgen, Configuratie-gedreven, Contract-gedreven) tot leven brengen.

**→ Lees de volledige uitwerking in: system/9_CODING_STANDAARDS_DESIGN_PRINCIPLES.md**

## **Bijlages**

* **Bijlage A: Terminologie**: Een uitgebreid naslagwerk met beschrijvingen van alle belangrijke concepten en componenten.  
* **Bijlage B: Openstaande Vraagstukken**: Een overzicht van bekende "onbekenden" die tijdens de implementatie verder onderzocht moeten worden.  
* **Bijlage C: MVP**: De scope en componenten van het Minimum Viable Product.  
* **Bijlage D: Plugin IDE**: De architectuur en UX voor de web-based IDE voor plugins.

---

# 1_EVENT_DRIVEN_ARCHITECTURE.md

# **S1mpleTrader V2 Architectuur: De Event-Gedreven Run Levenscyclus**

Versie: 3.1 (Definitief Ontwerp)  
Status: Goedgekeurd

## **1. Visie & Architectonische Principes**

### **1.1. Inleiding & Doel**

Dit document beschrijft de architectonische evolutie van S1mpleTrader V2 van een procedureel, hiërarchisch model naar een ontkoppeld, **event-gedreven model**. Dit ontwerp is de blauwdruk voor het beheren van de volledige levenscyclus van trading strategieën en operationele processen.

Het doel van deze architectuur is het verhogen van de robuustheid, schaalbaarheid en onderhoudbaarheid, met name in een complexe, multi-strategie, multi-asset en multi-exchange omgeving. De kern van dit ontwerp wordt gevormd door een centrale EventBus die als zenuwstelsel fungeert, waardoor componenten als gelijkwaardige, gespecialiseerde collega's met elkaar samenwerken via strikt gedefinieerde, contract-gedreven events.

### **1.2. Het Hybride Model: De Juiste Tool voor de Juiste Taak**

De architectuur hanteert een bewust **hybride model** om onnodige complexiteit te vermijden:

* **Event-Gedreven voor de Run Levenscyclus**: De dynamische, asynchrone en real-time flow van een actieve trading run (van marktdata naar beslissing naar executie) wordt volledig afgehandeld via de EventBus. Dit is ideaal voor processen die op onvoorspelbare momenten plaatsvinden en waar meerdere componenten onafhankelijk op moeten reageren.  
* **Procedureel (Request-Response) voor Synchrone Taken**: Processen die van nature transactioneel en synchroon zijn, blijven procedureel. Dit geldt voor:  
  * **Configuratie & Validatie**: Het laden en valideren van YAML-bestanden gebeurt synchroon bij de start. Een fout leidt tot een onmiddellijke "fail fast", zonder dat er een event wordt gepubliceerd.  
  * **Gebruikersinteracties (UI)**: Een gebruiker die een strategie start of een plugin aanmaakt via de UI, doet een directe API-call en verwacht een directe respons (OK of Error).  
  * **Interne Component Logica**: Complexe componenten zoals de StrategyEngine kunnen intern een voorspelbare, procedurele logica (de 7-fasen pijplijn) hebben, ook al reageren ze als geheel op een extern event.

## **2. Component Categorieën: Een Strikte Scheiding van Verantwoordelijkheden**

Om de architecturale zuiverheid te bewaken, verdelen we de componenten in drie duidelijk gescheiden categorieën:

1. **Kernservices**: De fundamentele, langlevende componenten die het platform orkestreren en faciliteren. Ze vormen de ruggengraat van het systeem.  
2. **De Analytische Pijplijn**: Een gespecialiseerde, stateless en procedurele flow, specifiek ontworpen voor het analyseren van marktdata en het genereren van *niet-deterministische, analytische handelsvoorstellen*.  
3. **Operationele Agenten**: Een categorie van stateful, portfolio-bewuste componenten die *buiten* de analytische pijplijn opereren. Ze zijn verantwoordelijk voor het uitvoeren van *deterministische, op regels gebaseerde, operationele taken*.

## **3. Uitwerking van de Kerncomponenten**

### **3.1. Kernservices**

* **PortfolioSupervisor (De Operationeel Manager)**: De eigenaar van het portfolio_blueprint.yaml. Beheert de levenscyclus (starten/stoppen) van alle strategieën en agenten. Valideert configuraties, fungeert als de hoogste risicomanager en is de primaire abonnee op StrategyProposalReady-events.  
* **RunOrchestrator (De Facilitator)**: Een lichtgewicht component, geïnstantieerd *per strategie* door de PortfolioSupervisor. Zijn enige taak is het opzetten van de benodigde specialisten voor één run en het publiceren van de initiële RunStarted-event.  
* **ContextBootstrapper (De "Voorgloeier")**: Zorgt ervoor dat de ContextOrchestrator een complete, historisch correcte staat heeft *voordat* de eerste live tick wordt verwerkt. Haalt een bulk historische data op en "primed" de context.  
* **ContextOrchestrator (De State Manager)**: Het **stateful hart** van een actieve run. Beheert de "levende" TradingContext (de enriched_market_data en artefacts). Abonneert zich op MarketDataReceived en publiceert een verrijkte ContextReady voor elke tick.
* **StrategyOperator (De Analytische Specialist)**: De StrategyOperator is de Service-laag tegenhanger van de StrategyEngine. Het fungeert als een schone, ontkoppelde brug: het abonneert zich op ContextReady, roept procedureel de run()-methode van de StrategyEngine aan, en publiceert het resultaat als een StrategyProposalReady-event. Dit waarborgt de strikte scheiding tussen de lagen.  
* **ExecutionHandler (De Uitvoerder)**: Een stateless component die reageert op ExecutionApproved-events. Het roept het StrategyPortfolio (in backtest) of de juiste APIConnector (in live/paper) aan om de trade uit te voeren. Na de wijziging publiceert de ExecutionHandler een PortfolioStateChanged-event.  
* **AggregatePortfolioView (De Hoofd-Accountant)**: Luistert naar alle individuele PortfolioStateChanged-events om een geaggregeerd beeld van de totale performance (live en paper) te vormen en te publiceren.

### **3.2. De Analytische Pijplijn**

* **StrategyEngine (De Analist)**: Een **stateless** Backend-component die de **procedurele Fase 3-9 pijplijn** uitvoert. Het wordt aangeroepen door de StrategyOperator en produceert analytische voorstellen. Zijn input is primair de marktdata; de portfolio-staat wordt enkel *read-only* gebruikt voor risicoberekeningen.

### **3.3. Operationele Agenten**

* **GridTraderAgent, DCAAgent, RebalancerAgent**: Voorbeelden van stateful, portfolio-bewuste componenten in de Service-laag. Ze worden beheerd door de PortfolioSupervisor en opereren parallel aan de StrategyEngine. Ze abonneren zich direct op events als ContextReady en PortfolioStateChanged om hun deterministische, op regels gebaseerde taken uit te voeren.

### **3.4. Loggers & Recorders**

* **AppLogger**: De standaard logger, geïnjecteerd in alle componenten. Contextuele data (run_id, correlation_id) wordt via de event-payloads doorgegeven en in de logberichten opgenomen voor traceerbaarheid in run.log.json.  
* **ContextRecorder**: Een losstaande "archivaris" die zich abonneert op ContextReady en StrategyProposalReady om de data vast te leggen voor de "Trade Explorer" UI.  
* **ResultLogger**: Abonneert zich op RunFinished en BacktestCompleted om de finale resultaten op te slaan in de results/-map.

## **4. De Event Map: Contracten op de EventBus**

Dit is de definitieve lijst van events die de interactie tussen de componenten sturen.

| Event Naam                | Payload (DTO Contract)   | Publisher(s)           | Subscriber(s)                |
| :-------------------------| :------------------------| :----------------------| :----------------------------|
| **Run Lifecycle**         |                          |                        |                              |
| RunStarted                | RunParameters            | PortfolioSupervisor    | ContextBootstrapper,         |
|                           |                          |                        | ExecutionEnvironmentFactory, |
|                           |                          |                        | PortfolioFactory             |
| BootstrapComplete         | BootstrapResult          | ContextBootstrapper    | ExecutionEnvironment         |
| ShutdownRequested         | ShutdownSignal           | RiskMonitor, UI,       | RunOrchestrator,             |
|                           |                          | RunOrchestrator        | PortfolioSupervisor          |
| RunFinished               | RunSummary               | RunOrchestrator        | ResultLogger, UI,            |
|                           |                          |                        | DatabaseService              |
| --------------------------| -------------------------| -----------------------| -----------------------------|
| **Tick Lifecycle**        |                          |                        |                              |
| MarketDataReceived        | MarketSnapshot           | ExecutionEnvironment   | ContextOrchestrator          |
| ContextReady              | TradingContext           | ContextOrchestrator    | StrategyOperator,            |
|                           |                          |                        | Operationele Agenten,        |
|                           |                          |                        | ContextRecorder,             |
|                           |                          |                        | LiveDashboardUI              |
| StrategyProposalReady     | EngineCycleResult        | StrategyOperator       | PortfolioSupervisor,         |
|                           |                          |                        | ContextRecorder              |
| ExecutionApproved         | List[ExecutionDirective] | PortfolioSupervisor,   | ExecutionHandler,            |
|                           |                          |                        | Operationele Agenten,        |
|                           |                          | Operationele Agenten   | LiveDashboardUI              |
| --------------------------| -------------------------| -----------------------| -----------------------------|
| **Portfolio Lifecycle**   |                          |                        |                              |
| PortfolioStateChanged     | PortfolioState           | ExecutionHandler       | ContextOrchestrator,         |
|                           |                          |                        | AggregatePortfolioView,      |
|                           |                          |                        | Operationele Agenten,        |
|                           |                          |                        | LiveDashboardUI              |
| AggregatePortfolioUpdated | AggregateMetrics         | AggregatePortfolioView | LiveDashboardUI,             |
|                           |                          |                        | PortfolioSupervisor          |
| --------------------------| -------------------------| -----------------------| -----------------------------|
| **Backtest & Analysis**   |                          |                        |                              |
| BacktestCompleted         | BacktestResult           | RunOrchestrator        | ResultPresenter (UI),        |
|                           |                          |                        | DatabaseService              |
|                           |                          |                        | ResultLogger                 |

## **5. De Levenscyclus in de Praktijk**

**A. Initialisatie (De "Bootstrap Fase")**

1. De quant start een strategie via de UI, wat een StartStrategyRequested-commando triggert.  
2. De **PortfolioSupervisor** valideert de configuratie, creëert een RunOrchestrator en publiceert **RunStarted**.  
3. De **ContextBootstrapper** reageert hierop, haalt bulk historische data op, en "primed" de ContextOrchestrator. Zodra de context is opgebouwd, publiceert het **BootstrapComplete**.

**B. De Tick-Loop (De "Hartslag")**

4. De **ExecutionEnvironment** (wachtend op BootstrapComplete) begint met het publiceren van **MarketDataReceived**-events.  
5. De **ContextOrchestrator** vangt elk event op, werkt zijn interne state bij, en publiceert een complete **ContextReady**.  
6. Zowel de **StrategyOperator** als eventuele **Operationele Agenten** reageren *parallel* op ContextReady en doen hun gespecialiseerde werk.  
7. De StrategyOperator roept de StrategyEngine aan en publiceert (indien van toepassing) een **StrategyProposalReady**.  
8. De PortfolioSupervisor ontvangt dit voorstel, past zijn risicomanagement toe, en publiceert (indien goedgekeurd) **ExecutionApproved**.  
9. De ExecutionHandler ontvangt ExecutionApproved en voert de trade uit. De resulterende wijziging in het StrategyPortfolio leidt ertoe dat de ExecutionHandler een **PortfolioStateChanged**-event publiceert.  
10. De **AggregatePortfolioView** vangt PortfolioStateChanged op en werkt de totale performance bij.

## **6. Ontwerpoplossingen & Scenario Analyse**

### **6.1. Oplossingen voor Complexe Vraagstukken**

* **Multi-Strategie**: Beheerd door de PortfolioSupervisor die per strategie/agent een run_id toekent. Events worden via deze ID onderscheiden op de centrale EventBus.  
* **Multi-Exchange**: Geabstraheerd door een ExecutionEnvironmentFactory die op basis van een exchange_id de juiste, geïsoleerde APIConnector injecteert. De rest van het systeem blijft agnostisch.  
* **Gelaagde Performance**: Opgelost door individuele StrategyPortfolio-objecten en een overkoepelende AggregatePortfolioView.

### **6.2. Scenario Analyse**

* **Grid Trader & DCA Strategie**: Worden geïmplementeerd als **Operationele Agenten**. Ze zijn stateful, portfolio-bewust en opereren buiten de analytische pijplijn. Ze reageren direct op ContextReady en PortfolioStateChanged om hun deterministische logica uit te voeren.  
* **Portfolio Rebalancer**: Wordt geïmplementeerd als een **Operationele Agent**. Het reageert op AggregatePortfolioUpdated om de portfolio-allocatie te bewaken en te corrigeren.  
* **Analytische FVG Strategie**: Dit is de kerntaak van de **Analytische Pijplijn**. ContextWorker-plugins bouwen de analytische context. De StrategyOperator gebruikt de StrategyEngine om een voorstel te genereren. Een CrashDetector-plugin (Fase 9) genereert een analytisch CriticalEvent, waarop een RiskMonitor (een aparte service) kan reageren met een operationele beslissing.

## **7. Integratie in de Documentatie**

Dit document (1_EVENT_DRIVEN_ARCHITECTURE.md) wordt de primaire bron voor de run-levenscyclus architectuur. Bestaande documenten (0_V2_ARCHITECTURE.md, 2_ARCHITECTURE.md, 4_WORKFLOW_AND_ORCHESTRATOR.md) zullen worden bijgewerkt om naar dit document te verwijzen en om verouderde, hiërarchische concepten te vervangen door de hier beschreven event-gedreven principes en componentdefinities.

---

# 2_ARCHITECTURE.md

# **2\. Architectuur & Componenten**

Versie: 4.1 (Definitief Ontwerp)  
Status: Goedgekeurd

## **2.1. De Gelaagde Architectuur: Een Strikte Definitie**

De applicatie is opgebouwd uit drie strikt gescheiden lagen die een **eenrichtingsverkeer** van afhankelijkheden afdwingen (Frontend → Service → Backend). Deze scheiding is absoluut en dicteert waar elk component "leeft".

* **Backend Laag (/backend)**: De **"Motor & Gereedschapskist"**. Bevat alle herbruikbare, agnostische bouwstenen (klassen, DTO's, interfaces). Deze laag is volledig onafhankelijk, heeft geen kennis van business workflows, en weet niets van een EventBus. Het is een pure, importeerbare library.  
* **Service Laag (/services)**: De **"Orkestratielaag"**. Dit is de enige laag die de EventBus kent en beheert. Componenten hier orkestreren complete business workflows door de "gereedschappen" uit de Backend-laag aan te roepen in reactie op events.  
* **Frontend Laag (/frontends)**: De **"Gebruikersinterface"**. Verantwoordelijk voor alle gebruikersinteractie. Het communiceert uitsluitend met de Service-laag, bijvoorbeeld door API-calls te doen die op hun beurt commando-events publiceren.

## **2.2. Component Categorieën: Functionele Groepering**

Om de samenhang te verduidelijken, groeperen we componenten in functionele categorieën. Een terugkerend patroon is een Service-laag "Operator" die een corresponderende Backend-laag "Engine" of "Worker" aanstuurt.

1. **Kernservices (Service Laag)**: De fundamentele, langlevende componenten die het platform orkestreren.  
2. **De Context Pijplijn (Backend & Service Laag)**: De flow voor het stateful opbouwen van de marktcontext.  
3. **De Analytische Pijplijn (Backend & Service Laag)**: Een gespecialiseerde flow voor het genereren van analytische handelsvoorstellen.  
4. **Operationele Agenten (Service Laag)**: Componenten voor deterministische, portfolio-gestuurde taken.  
5. **De Executie Pijplijn (Backend & Service Laag)**: De flow voor het uitvoeren van goedgekeurde trades.  
6. **Bouwstenen (Backend Laag)**: De fundamentele, herbruikbare tools en definities.

## **2.3. Visueel Overzicht: Een Strikte Gelaagde Architectuur**

Dit diagram toont de correcte plaatsing en interactie van de componenten, met respect voor de laag-grenzen.

\+------------------------------------------------------------------------------------+  
|                                   FRONTEND LAAG                                    |  
\+------------------------------------------+-----------------------------------------+  
                                           | (API Calls)  
                                           v  
\+====================================================================================+  
|                                     SERVICE LAAG                                   |  
|                          (Eigenaar van de EventBus & Workflows)                    |  
|                                                                                    |  
|   \+-----------------------+      \+------------------+      \+-------------------+   |  
|   |  PortfolioSupervisor  |      |  ContextOrch.    |      |  Operationele     |   |  
|   \+-----------------------+      \+------------------+      |      Agenten      |   |  
|           ^     |                      ^      |                  ^      |          |  
|           |     | \<Sub/Pub\>            |      | \<Sub/Pub\>        |      | \<Sub/Pub\>|  
|      \+----v----------------------------v-------------+-----------v---------------+ |  
|      |                  DE CENTRALE EVENT BUS        | (Leeft in Service Laag) |   |  
|      \+-------------------^----------------------------^-----------------------+   |  
|                          | \<Sub/Pub\>                   |  \<Sub/Pub\>            |   |  
|                          |                             |                       |   |  
|   \+----------------------v--+      \+-------------------v---+               |   |  
|   |    StrategyOperator   |      |   ExecutionHandler    |               |   |  
|   \+-------------------------+      \+-----------------------+               |   |  
|                                                                            |   |  
\+====================================================================================+  
                                           | (gebruikt als library)  
                                           v  
\+------------------------------------------------------------------------------------+  
|                                     BACKEND LAAG                                   |  
|                (De Gereedschapskist \- Kent de Service Laag NIET)                   |  
|                                                                                    |  
|  \- StrategyEngine (Klasse)    \- Portfolio (Klasse)       \- DTO's & Interfaces      |  
|  \- Assembly Team              \- ExecutionEnvironments    \- APIConnectors (Klasses) |  
|  \- ConfigLoader (Klasse)                                                           |  
|                                                                                    |  
\+------------------------------------------------------------------------------------+

## **2.4. Componenten in Detail**

Deze sectie beschrijft de verantwoordelijkheden van elk kerncomponent, gegroepeerd per functionele categorie.

### **Kernservices (Service Laag)**

#### **PortfolioSupervisor (De Operationeel Manager)**

* **Verantwoordelijkheid:** Het actieve, centrale beheer van het gehele trading-portfolio. Dit is de "directiekamer" van het platform. Het leest de portfolio\_blueprint.yaml en is de eigenaar van de levenscyclus van alle actieve strategieën en agenten. Het fungeert als de hoogste risicomanager door te reageren op StrategyProposalReady-events en te beslissen welke trades worden goedgekeurd.  
* **Backend Gebruik:** Gebruikt de ConfigLoader om de portfolio\_blueprint.yaml en de onderliggende run.yaml-bestanden te laden en valideren. Wijzigingen in de configuratie vanuit de frontend (op portfolio-, run-, of plugin-niveau) triggeren een herlading en validatie via deze component.

#### **RunOrchestrator (De Facilitator)**

* **Verantwoordelijkheid:** Een lichtgewicht component, geïnstantieerd *per strategie* door de PortfolioSupervisor. Zijn enige taak is het opzetten van de benodigde specialisten voor één run, het 'wiren' van de event-abonnementen, en het publiceren van de initiële RunStarted-event.

### **De Context Pijplijn**

#### **ContextBootstrapper (De "Voorgloeier") (Service Laag)**

* **Verantwoordelijkheid:** Zorgt ervoor dat de ContextOrchestrator een complete en historisch correcte staat heeft *voordat* de eerste live tick wordt verwerkt. Dit is cruciaal om te voorkomen dat beslissingen worden genomen op basis van onvolledige data (bv. een Moving Average die nog geen 200 periodes aan data heeft).  
* **Backend Gebruik:** Gebruikt de relevante APIConnector om een bulk historische data op te halen.

#### **ContextOrchestrator (De State Manager) (Service Laag)**

* **Verantwoordelijkheid:** Dit is het stateful hart van een actieve run. Het beheert de "levende" TradingContext (enriched\_market\_data, artefacts). Het abonneert zich op MarketDataReceived en publiceert een verrijkte ContextReady voor elke tick.  
* **Backend Gebruik:** Gebruikt de ContextBuilder en het Assembly Team (met name de WorkerBuilder) om de Fase 1-2 ContextWorker-plugins te bouwen en uit te voeren op de DataFrame.

### **De Analytische Pijplijn**

#### **StrategyOperator (De Analytische Specialist) (Service Laag)**

* **Verantwoordelijkheid:** De StrategyOperator is de Service-laag tegenhanger van de StrategyEngine. Het fungeert als een schone, ontkoppelde brug: het abonneert zich op ContextReady, roept procedureel de run()-methode van de StrategyEngine aan, en publiceert het resultaat als een StrategyProposalReady-event. Dit waarborgt de strikte scheiding tussen de lagen en geeft de StrategyOperator zijn duidelijke, operationele naam terug.  
* **Backend Gebruik:** Gebruikt een instantie van de StrategyEngine en roept de run() methode aan.

#### **StrategyEngine (De Analytische Motor) (Backend Laag)**

* **Verantwoordelijkheid:** De stateless, procedurele 9-fasen motor voor het genereren van analytische voorstellen. Het is een pure "ideeënmachine" die opereert op de TradingContext en een EngineCycleResult produceert, volledig agnostisch van de event-bus of de bredere applicatiecontext.

### **Operationele Agenten (Service Laag)**

#### **GridTraderAgent, RebalancerAgent, etc.**

* **Verantwoordelijkheid:** Het uitvoeren van deterministische, op regels gebaseerde, stateful taken die buiten de analytische pijplijn vallen (bv. grid trading, DCA, portfolio herbalancering). Ze zijn per definitie portfolio-bewust.  
* **Backend Gebruik:** Lezen PortfolioState DTO's om hun beslissingen te informeren.

### **De Executie Pijplijn**

#### **ExecutionHandler (De Uitvoerder) (Service Laag)**

* **Verantwoordelijkheid:** De ExecutionHandler is de Service-laag tegenhanger van de APIConnectors. Het luistert naar ExecutionApproved-events en is verantwoordelijk voor het aanroepen van het StrategyPortfolio (in een backtest) of de juiste APIConnector (in live/paper). **Cruciaal**: nadat de staat van het portfolio is gewijzigd, is het de verantwoordelijkheid van de ExecutionHandler om een PortfolioStateChanged-event te publiceren.  
* **Backend Gebruik:** Gebruikt een specifieke APIConnector om de order daadwerkelijk te versturen. In een backtest/paper-omgeving gebruikt het een StrategyPortfolio om de staat direct bij te werken.

#### **ExecutionEnvironments & APIConnectors (Backend Laag)**

* **Verantwoordelijkheid:** ExecutionEnvironments zijn de dataleveranciers die MarketSnapshot-DTO's produceren. APIConnectors zijn de "stekkers" die de specifieke logica bevatten om met een exchange, wallet of DEX te communiceren.

### **Bouwstenen (Backend Laag)**

#### **StrategyPortfolio (Het Grootboek)**

* **Verantwoordelijkheid:** Het "domme", agnostische grootboek voor één specifieke run. Managet kapitaal, posities en openstaande orders. Het wordt gemuteerd door de ExecutionHandler en heeft zelf geen kennis van de EventBus.

#### **Assembly Team (PluginRegistry, WorkerBuilder, ContextBuilder)**

* **Verantwoordelijkheid:** Het "technische projectbureau" dat op aanvraag van de Service-laag alle benodigde plugin-workers ontdekt, valideert en bouwt.

---

# 3_PLUGIN_ANATOMY.md

# 3. De Anatomie van een V2 Plugin

Dit document beschrijft de gedetailleerde structuur en de technische keuzes achter de plugins in de S1mpleTrader V2 architectuur. Plugins zijn de specialistische, onafhankelijke en testbare bouwstenen van elke strategie.

---
## 3.1. Fundamentele Mappenstructuur

Elke plugin is een opzichzelfstaande Python package. Deze structuur garandeert dat logica, contracten en metadata altijd bij elkaar blijven, wat essentieel is voor het "Plugin First" principe.

Een typische plugin heeft de volgende structuur:

plugins/[plugin_naam]/
├── manifest.yaml         # De ID-kaart (wie ben ik?)
├── worker.py             # De Logica (wat doe ik?)
├── schema.py             # Het Contract (wat heb ik nodig?)
├── context_schema.py     # Het visuele context contract (wat kan ik laten zien?)
└── test/test_worker      # Unit test voor de plugin


* `manifest.yaml`: De "ID-kaart" van de plugin. Dit bestand maakt de plugin vindbaar en begrijpelijk voor de `PluginRegistry`.
* `worker.py`: Bevat de Python-klasse met de daadwerkelijke businesslogica van de plugin.
* `schema.py`: Bevat het Pydantic-model dat de structuur en validatieregels voor de configuratieparameters van de plugin definieert.
* `context_schema.py: Bevat het concrete context model voor de visualisatie van gegevens die de plugin produceert. Het maakt gebruik van de (visualisatie) modellen die het platform beschikbaar stelt in visualization_schema.py.
* `test/test_worker.py`: Dit bestand bevat de unit tests voor het valideren van de werking van de plugin. Het is een verplicht onderdeel dat de ontwikkelaar zal moeten schrijven en wordt gebruikt bij de enrollment van de plugin. Een 100% score als uitkomst van pytest is noodzakelijk als onderdeel van de succesvolle enrollment van een nieuwe plugin.

---
## 3.2. Formaat Keuzes: `YAML` vs. `JSON`

De keuze voor een dataformaat hangt af van de primaire gebruiker: **een mens of een machine**. We hanteren daarom een hybride model om zowel leesbaarheid als betrouwbaarheid te maximaliseren.

* **`YAML` voor Menselijke Configuratie**
    * **Toepassing:** `plugin_manifest.yaml` en alle door de gebruiker geschreven `run_config.yaml`-bestanden.
    * **Waarom:** De superieure leesbaarheid, de mogelijkheid om commentaar toe te voegen, en de flexibelere syntax zijn essentieel voor ontwikkelaars en strategen die deze bestanden handmatig schrijven en onderhouden.

* **`JSON` voor Machine-Data**
    * **Toepassing:** Alle machine-gegenereerde data, zoals API-responses, `state.json`-bestanden, en gestructureerde logs (`run.log.json`).
    * **Waarom:** De strikte syntax en universele portabiliteit maken `JSON` de betrouwbare standaard voor communicatie tussen systemen (bv. tussen de Python backend en een TypeScript frontend) en voor het opslaan van gestructureerde data waar absolute betrouwbaarheid vereist is.

---
## **3.3. Het manifest: de zelfbeschrijvende ID-kaart van de plugin**

Het plugin_manifest.yaml is de kern van het "plugin discovery" mechanisme. Het stelt het **Assembly Team** (specifiek de PluginRegistry) in staat om een plugin volledig te begrijpen, valideren en correct te categoriseren **zonder de Python-code te hoeven inspecteren**. Dit manifest is een strikt contract, afgedwongen door het PluginManifest Pydantic-model, dat alle cruciale metadata van een plugin vastlegt.

### **Core Identity**

De **core_identity**-sectie definieert de technische identiteit en versie van het manifest-schema zelf. Deze velden zorgen ervoor dat het systeem het bestand correct kan interpreteren en toekomstige wijzigingen in de manifest-structuur kan beheren.

* **apiVersion**: Identificeert de schemaversie van het manifest. Dit heeft een vaste waarde zoals s1mpletrader.io/v1 om aan te geven welke versie van de specificatie wordt gevolgd.  
* **kind**: Specificeert dat dit bestand een PluginManifest is, wat het type van het document definieert.

### **Identification**

De **identification**-sectie bevat alle beschrijvende metadata die de plugin identificeert voor zowel het systeem als de gebruiker.

* **name**: De unieke, machine-leesbare naam van de plugin (bv. market_structure_detector).  
* **display_name**: De naam zoals deze in de gebruikersinterface wordt getoond (bv. Market Structure Detector).  
* **type**: De belangrijkste categorie die bepaalt in welke van de negen workflow-fasen de plugin thuishoort (bv. structural_context).  
* **version**: De semantische versie van de plugin (bv. 1.0.1), wat essentieel is voor dependency management.  
* **description**: Een korte, duidelijke beschrijving van de functionaliteit van de plugin.  
* **author**: De naam van de ontwikkelaar of het team achter de plugin.

### **Dependencies**

De **dependencies**-sectie definieert het dat-contract van de plugin, met name voor dataverrijkingsplugins (ContextWorker).

* **requires**: Een lijst van datakolommen die de plugin als **input** verwacht (bv. ['high', 'low', 'close']). De DependencyValidator controleert of aan deze vereisten wordt voldaan door voorgaande plugins.  
* **provides**: Een lijst van nieuwe datakolommen die de plugin als **output** toevoegt aan de data (bv. ['is_swing_high']).

### **Permissions**

De **permissions**-sectie fungeert als een beveiligingscontract dat expliciet aangeeft welke potentieel risicovolle operaties de plugin nodig heeft. Standaard heeft een plugin geen toegang tot externe bronnen.

* **network_access**: Een 'allowlist' van netwerkbestemmingen die de plugin mag benaderen (bv. ['https://api.kraken.com']).  
* **filesystem_access**: Een 'allowlist' van bestanden of mappen waartoe de plugin toegang heeft.

---
## 3.4. De Worker & het BaseWorker Raamwerk

De `worker.py` bevat de daadwerkelijke logica. Om de ontwikkeling te versnellen en de consistentie te borgen, biedt de architectuur een set aan basisklassen in `backend/core/base_worker.py`.

* **Doel:** Het automatiseren van de complexe, geneste DTO-creatie en het doorgeven van de `correlation_id`.
* **Voorbeeld (`BaseEntryPlanner`):**
    ```python
    class MyEntryPlanner(BaseEntryPlanner):
        def _process(self, input_dto: Signal, correlation_id: UUID, context: TradingContext) -> Optional[Dict[str, Any]]:
            # Developer focust alleen op de logica
            entry_price = ... # bereken de entry prijs
            return {"entry_price": entry_price}
    ```
De `BaseEntryPlanner` handelt automatisch de creatie van de `EntrySignal` DTO af, nest de oorspronkelijke `Signal` erin, en zorgt dat de `correlation_id` correct wordt doorgegeven. Dit maakt de plugin-code extreem schoon en gefocust.

---

# 4_WORKFLOW_AND_ORCHESTRATOR.md

# **4. De Quant Workflow & De Analytische Pijplijn**

Versie: 3.0 (Bijgewerkt)  
Status: Definitief

## **4.1. Introductie: Een Gescheiden Pijplijn**

Dit document beschrijft de volledige workflow van data-analyse tot handelsvoorstel. Deze workflow is bewust opgesplitst in twee conceptueel verschillende, opeenvolgende processen:

1. **De Context Pijplijn (Fase 1-2):** De eerste twee fasen (Regime Context en Structurele Context) zijn de verantwoordelijkheid van de stateful **ContextOrchestrator**. Deze fasen verrijken de ruwe marktdata en bereiden de complete, state-bewuste TradingContext voor. Dit proces wordt voor elke tick uitgevoerd en eindigt met het publiceren van een ContextReady-event.  
2. **De Analytische Pijplijn (Fase 3-9):** De daaropvolgende zeven fasen vormen de kern van de **StrategyEngine**. In reactie op de ContextReady-event, voert de StrategyEngine zijn interne, stateless en procedurele **7-fasen trechter** uit. Het doel is niet om definitieve beslissingen te nemen, maar om een *analytisch voorstel* (EngineCycleResult) te produceren. Dit voorstel wordt vervolgens gepubliceerd als een StrategyProposalReady-event.

Deze scheiding zorgt ervoor dat de StrategyEngine zich puur kan richten op zijn analytische kerntaak, opererend op een perfect voorbereide dataset, zonder zich bezig te hoeven houden met het complexe beheer van de staat.

## **4.2. De 9-Fasen Trechter/pijplijn: Een Praktijkvoorbeeld**

   ┌───────────────────────────────────────────┐  
   │        RUWE DATAFRAME (OHLCV)             │  
   └────────────────────┬──────────────────────┘  
                        │  
                        v

┌──────────────────────────────────────────────────────────────────┐  
│ Fase 1: REGIME CONTEXT (De "Weerman")                            │
│ Plugin: regime_context                                           │  
│ Taak: Voegt macro-context toe (bv. regime='trending').           │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
v  
┌───────────────────────────────────────────┐  
│ VERRIJKTE DATAFRAME (enriched_df)         │  
└────────────────────┬──────────────────────┘  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 2: STRUCTURELE CONTEXT (De "Cartograaf")                    │  
│ Plugin: structural_context                                       │  
│ Taak: Voegt micro-context toe (bv. is_mss, support_level).       │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
v  
┌───────────────────────────────────────────┐  
│ FINALE ENRICHED DATAFRAME                 │
└────────────────────┬──────────────────────┘  
│ (Start StrategyEngine Loop)  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 3: SIGNAAL GENERATIE (De "Verkenner")                       │  
│ Plugin: signal_generator                                         │  
│ Taak: Detecteert een specifieke, actiegerichte gebeurtenis.      │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
│ DTO: Signal  
│ -------------------------------  
│ { correlation_id, timestamp, asset,  
│ direction, signal_type }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 4: SIGNAAL VERFIJNING (De "Kwaliteitscontroleur")           │  
│ Plugin: signal_refiner                                           │  
│ Taak: Keurt Signal goed of af op basis van secundaire criteria.  │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
│ DTO: Signal (of None)  
│ -------------------------------  
│ { ... (inhoud blijft gelijk) }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 5: ENTRY PLANNING (De "Timing Expert")                      │  
│ Plugin: entry_planner                                            │  
│ Taak: Bepaalt de precieze entry-prijs.                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
│ DTO: EntrySignal  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ signal: Signal (genest),  
│ + entry_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 6: EXIT PLANNING (De "Strateeg")                            │  
│ Plugin: exit_planner                                             │  
│ Taak: Berekent de initiële stop-loss en take-profit.             │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
│ DTO: RiskDefinedSignal  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ entry_signal: EntrySignal (genest),  
│ + sl_price, tp_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐
│ Fase 7: SIZE PLANNING (De "Logistiek Manager")                   │
│ Plugin: size_planner                                             │
│ Taak: Berekent de definitieve positiegrootte.                    │
└────────────────────┬─────────────────────────────────────────────┘
│  
│ DTO: TradePlan  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ risk_defined_signal: RiskDefinedSignal (genest),  
│ + position_value_quote, position_size_asset }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐
│ Fase 8: ORDER ROUTING (De "Verkeersleider")                      │
│ Plugin: order_router                                             │
│ Taak: Vertaalt het plan naar technische executie-instructies.    │
└────────────────────┬─────────────────────────────────────────────┘
│  
│ DTO: RoutedTradePlan  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ trade_plan: TradePlan (genest),  
│ + order_type, time_in_force, ... }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐
│ Fase 9: CRITICAL EVENT DETECTION (De "Waakhond")                 │
│ Plugin: critical_event_detector                                  │
│ Taak: Detecteert systeem-brede risico's (bv. max drawdown).      │
└────────────────────┬─────────────────────────────────────────────┘
│  
│ DTO: CriticalEvent  
│ -------------------------------  
│ { correlation_id, event_type, timestamp }  
│  
v  
┌─────────────────────────────────────────────┐
│ FINAAL EngineCycleResult DTO                │
│ { routed_trade_plans?, critical_events? }   │
└────────────────────┬────────────────────────┘
│  
v  
[ Publiceert StrategyProposalReady Event ]  
Elk handelsidee wordt systematisch gevalideerd door een vaste, logische trechter. We volgen een concreet voorbeeld: een **"Market Structure Shift + FVG Entry"** strategie.

#### **Fase 1: Regime Context (De "Weerman")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** Wat is de algemene "weersverwachting" van de markt? Deze fase classificeert de marktomstandigheid zonder data weg te gooien.  
* **Input:** De ruwe DataFrame met OHLCV-data uit de TradingContext.  
* **Proces (voorbeeld):** Een ADXContext-plugin (type: regime_context) berekent de ADX-indicator en voegt een nieuwe kolom regime toe aan de DataFrame. Deze kolom krijgt de waarde 'trending' als ADX > 25 en 'ranging' als ADX < 25.  
* **Output:** Een verrijkte DataFrame. Er wordt geen data verwijderd; er wordt alleen een contextuele "tag" toegevoegd aan elke rij.

#### **Fase 2: Structurele Context (De "Cartograaf")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?  
* **Input:** De verrijkte DataFrame uit Fase 1.  
* **Proces (voorbeeld):** Een MarketStructureDetector-plugin (type: structural_context) analyseert de prijs en voegt twee nieuwe kolommen toe: trend_direction (met waarden als bullish of bearish) en is_mss (een True/False vlag op de candle waar een Market Structure Shift plaatsvindt).  
* **Output:** De finale enriched_df. We hebben nu "slimme" data met meerdere lagen context, klaar voor de StrategyEngine.

## ***De controle wordt overgedragen aan de StrategyEngine na ontvangst van de ContextReady-event.***

#### **Fase 3: Signaal Generatie (De "Verkenner")**

* **Categorie:** StrategyWorker-plugin (signal_generator)  
* **Doel:** Waar is de precieze, actiegerichte trigger? We zoeken naar een Fair Value Gap (FVG) ná een Market Structure Shift.  
* **Input:** De enriched_df (via het TradingContext object).  
* **Proces (voorbeeld):** Een FVGEntryDetector-plugin scant de data. Wanneer het een rij tegenkomt waar is_mss True is, begint het te zoeken naar een FVG. Als het er een vindt, genereert het een signaal.  
* **Output:** Een **Signal DTO**. Dit object krijgt een unieke correlation_id (UUID) en bevat de essentie: {asset: 'BTC/EUR', timestamp: '...', direction: 'long', signal_type: 'fvg_entry'}.

#### **Fase 4: Signaal Verfijning (De "Kwaliteitscontroleur")**

* **Categorie:** StrategyWorker-plugin (signal_refiner)  
* **Doel:** Is er bevestiging voor het signaal? We willen volume zien bij de FVG-entry.  
* **Input:** Het Signal DTO en het TradingContext.  
* **Proces (voorbeeld):** Een VolumeSpikeRefiner-plugin (type: signal_refiner) controleert het volume op de timestamp van het Signal. Als het volume te laag is, wordt het signaal afgekeurd.  
* **Output:** Het **gevalideerde Signal DTO** of None. De correlation_id blijft behouden.

#### **Fase 5: Entry Planning (De "Timing Expert")**

* **Categorie:** StrategyWorker-plugin (entry_planner)  
* **Doel:** Wat is de precieze entry-prijs voor ons goedgekeurde signaal?  
* **Input:** Het gevalideerde Signal DTO.  
* **Proces (voorbeeld):** Een LimitEntryPlanner-plugin (type: entry_planner) bepaalt dat de entry een limietorder moet zijn op de 50% retracement van de FVG.  
* **Output:** Een **EntrySignal DTO**. Dit DTO *nest* het originele Signal en verrijkt het met { entry_price: 34500.50 }. De correlation_id wordt gepromoot naar het top-level voor gemakkelijke toegang.

#### **Fase 6: Exit Planning (De "Strateeg")**

* **Categorie:** StrategyWorker-plugin (exit_planner)  
* **Doel:** Wat is het initiële plan voor risico- en winstmanagement?  
* **Input:** Het EntrySignal DTO.  
* **Proces (voorbeeld):** Een LiquidityTargetExit-plugin (type: exit_planner) plaatst de stop-loss onder de laatste swing low en de take-profit op de volgende major liquidity high.  
* **Output:** Een **RiskDefinedSignal DTO**. Nest het EntrySignal en voegt { sl_price: 34200.0, tp_price: 35100.0 } toe.

#### **Fase 7: Size Planning (De "Logistiek Manager")**

* **Categorie:** StrategyWorker-plugin (size_planner)  
* **Doel:** Wat is de definitieve positiegrootte, gegeven ons risicoplan en kapitaal?  
* **Input:** Het RiskDefinedSignal DTO en het Portfolio (via context.portfolio_state).  
* **Proces (voorbeeld):** Een FixedRiskSizer-plugin (type: size_planner) berekent de positiegrootte zodat het risico (entry_price - sl_price) exact 1% van de totale equity van het portfolio is.  
* **Output:** Een **TradePlan DTO**. Dit DTO nest het RiskDefinedSignal en bevat de finale, berekende { position_value_quote: 1000.0, position_size_asset: 0.0289 }. Dit is het complete *strategische* plan.

#### **Fase 8: Order Routing (De "Verkeersleider")**

* **Categorie:** StrategyWorker-plugin (order_router)  
* **Doel:** Hoe moet dit strategische plan *technisch* worden uitgevoerd?  
* **Input:** Het TradePlan DTO.  
* **Proces (voorbeeld):** Een DefaultRouter-plugin (type: order_router) vertaalt het plan naar concrete order-instructies.  
* **Output:** Een **RoutedTradePlan DTO**. Dit nest het TradePlan en voegt de *tactische* executie-instructies toe, zoals { order_type: 'limit', time_in_force: 'GTC' }. Dit is de definitieve opdracht voor de ExecutionHandler.

#### **Fase 9: Critical Event Detection (De "Waakhond")**

* **Categorie:** StrategyWorker-plugin (critical_event_detector)  
* **Doel:** Zijn er systeem-brede risico's die onmiddellijke actie vereisen, los van nieuwe trades?  
* **Input:** De volledige TradingContext en de lijst van RoutedTradePlan's.  
* **Proces (voorbeeld):** Een MaxDrawdownDetector-plugin (type: critical_event_detector) controleert de equity curve van het Portfolio. Als de drawdown een drempel overschrijdt, genereert het een event.  
* **Output:** Een lijst van **CriticalEvent DTO's** (bv. { event_type: 'MAX_DRAWDOWN_BREACHED' }).

## **4.3. Rolverdeling in de Event-Gedreven Architectuur**

Waar voorheen sprake was van een strikte hiërarchie, werken de componenten nu als samenwerkende specialisten.

* **ContextOrchestrator (De State Manager)**: Dit is de stateful "voorbereider". Het ontvangt MarketDataReceived-events, roept de Fase 1 & 2 ContextWorker-plugins aan om de TradingContext op te bouwen en te verrijken, en publiceert vervolgens de ContextReady-event.  
* **StrategyEngine (De Analist)**: Dit component is de stateless "motor" van de analytische pijplijn (Fase 3-9). Het abonneert zich op ContextReady. Na ontvangst doorloopt het de procedurele DTO-trechter (van Signal tot RoutedTradePlan) en publiceert het eindresultaat als een StrategyProposalReady-event. Het is een pure, analytische machine.  
* **PortfolioSupervisor (De Operationeel Manager)**: Dit is de beslissende "poortwachter". Het abonneert zich op StrategyProposalReady-events. Het ontvangt de voorstellen van de StrategyEngine, toetst deze aan overkoepelende, portfolio-brede risicoregels, en beslist of de trades daadwerkelijk uitgevoerd mogen worden.

## **4.4. De Feedback Loops: Technisch vs. Strategisch**

De architectuur faciliteert nog steeds twee cruciale cycli:

1. **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** **een run**, via de EventBus. Een PortfolioStateChanged-event, gepubliceerd door de ExecutionHandler, wordt opgevangen door de ContextOrchestrator. Deze gebruikt de nieuwe PortfolioState om de *volgende* TradingContext te bouwen, die vervolgens weer wordt gebruikt als input voor de StrategyEngine. Dit creëert een continue, real-time feedback-cyclus.  
2. **De Strategische "Supercharged" Ontwikkelcyclus (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** **de runs**, volgens het **"Bouwen -> Meten -> Leren"** principe. Je analyseert de resultaten van een backtest in de Web UI (**Meten**), ontdekt een zwakte (**Leren**), past de YAML-configuratie aan in de Strategy Builder (**Bouwen**) en start direct een nieuwe run.

---

# 5_FRONTEND_INTEGRATION.md

# 5. Frontend Integratie: De UI als Ontwikkelomgeving

Dit document beschrijft de volledige gebruikersworkflow en de frontend-architectuur die nodig is om de "supercharged" V2-ervaring te realiseren. Het is de directe vertaling van de User Story Map naar een concreet, technisch plan.

---
## 5.1. De Filosofie: De UI als IDE

De kern van de V2-frontendstrategie is een paradigmaverschuiving: de web-UI is niet langer een simpele presentatielaag, maar de **primaire, geïntegreerde ontwikkelomgeving (IDE)** voor de kwantitatieve strateeg. Elke stap in de workflow, van het bouwen van een strategie tot het diepgaand analyseren van de resultaten, vindt plaats binnen een naadloze, interactieve webapplicatie.

Dit maximaliseert de efficiëntie en verkort de **"Bouwen -> Meten -> Leren"**-cyclus van dagen of uren naar minuten.

---
## 5.2. De Werkruimtes: Van User Story Map naar Applicatie

De ruggengraat van de User Story Map (`USM_DEV_ROADMAP.md`) vertaalt zich direct naar de hoofdnavigatie (de "werkruimtes" of "tabbladen") van het S1mpleTrader-dashboard.

| PLUGIN DEVELOPMENT | STRATEGY BUILDER | BACKTESTING & ANALYSIS | PAPER TRADING | LIVE MONITORING |
| :--- | :--- | :--- | :--- | :--- |
| :--- | :--- | :--- | :--- | :--- |

Elk van deze secties representeert een "werkruimte" binnen de applicatie, met een eigen set aan gespecialiseerde tools en visualisaties.

---
## 5.3. Gedetailleerde Workflow per Werkruimte

### **Werkruimte 1: PLUGIN DEVELOPMENT**

* **User Goal:** Het snel en betrouwbaar ontwikkelen, testen en beheren van de herbruikbare bouwblokken (plugins) van het systeem.
* **UI Componenten:**
    * **Plugin Registry Viewer:** Een overzichtstabel van alle door de backend ontdekte plugins, met details uit hun `plugin_manifest.yaml` (versie, type, dependencies).
    * **Plugin Creator Wizard:** Een formulier dat de gebruiker helpt een nieuwe plugin-map aan te maken met de correcte boilerplate-code (`worker.py`, `schema.py`, `manifest.yaml`).
    * **Unit Test Runner:** Een UI-knop per plugin die de bijbehorende `test_worker.py` op de backend uitvoert en het resultaat (pass/fail) direct terugkoppelt.
* **Backend Interactie:** De UI communiceert met de `PluginQueryService` om de lijst van plugins op te halen en met een nieuwe `PluginEditorService` om de boilerplate aan te maken.

### **Werkruimte 2: STRATEGY BUILDER**

* **User Goal:** Het intuïtief en foutloos samenstellen van een complete handelsstrategie (`run.yaml`) door plugins te combineren.
* **UI Componenten:**
    * **Visuele Pijplijn:** Een grafische weergave van de analytische pijplijn, opgedeeld in de logische fasen (bv. `Context`, `Signaal`, `Risico`, etc.) zoals gedefinieerd in de architectuur.
    * **Plugin Bibliotheek:** Een zijbalk toont alle beschikbare plugins, slim gegroepeerd op basis van het `type`-veld uit hun manifest (bv. `regime_filters`, `signal_generators`).
    * **Configuratie Paneel:** Dit is waar de magie gebeurt. Wanneer een plugin in een slot wordt geplaatst, verschijnt er een paneel met een **automatisch gegenereerd formulier**.
        * **Voorbeeld:** Als de `schema.py` van een EMA-plugin `length: int = Field(default=20, gt=1)` definieert, genereert de UI een numeriek inputveld, vooraf ingevuld met "20", met een validatieregel die afdwingt dat de waarde groter dan 1 moet zijn. Foutieve input wordt onmogelijk gemaakt.
* **Backend Interactie:** De UI haalt de plugins op via de `PluginQueryService`. Bij het opslaan stuurt de UI een `JSON`-representatie van de samengestelde strategie naar de `BlueprintEditorService`, die het als een `YAML`-bestand wegschrijft in de `config/runs/` map.

* **Hint naar frontend implementatie:**
+----------------------------------------------------------------------+
| Fase 1: Regime Context (Selecteer de "Weerman" plugins)              |
| +-----------------+   +-----------------+                            |
| | ADXContext      |   | VolatilityContext | ...                      |
| +-----------------+   +-----------------+                            |
+----------------------------------------------------------------------+
| Fase 2: Structurele Context (Selecteer de "Cartograaf" plugins)    |
| +----------------------+   +-------------------------+               |
| | MarketStructure      |   | SupportResistanceFinder | ...           |
| +----------------------+   +-------------------------+               |
+----------------------------------------------------------------------+

### **Werkruimte 3: BACKTESTING & ANALYSIS**

* **User Goal:** Het rigoureus testen van strategieën onder verschillende condities en het diepgaand analyseren van de resultaten om inzichten te verkrijgen.
* **UI Componenten:**
    1.  **Run Launcher:** Een sectie waar de gebruiker een opgeslagen strategie-blueprint selecteert en een backtest, optimalisatie of varianten-test kan starten.
    2.  **Live Progress Dashboard:** Na het starten van een run, toont de UI een live-updating dashboard met de voortgang (bv. voortgangsbalken voor de `ParallelRunService` bij een optimalisatie).
    3.  **Resultaten Hub:** Een centrale plek waar alle voltooide runs worden getoond. Vanuit hier kan de gebruiker doorklikken naar:
        * **Optimization Results:** Een interactieve tabel (sorteren, filteren, zoeken) met de resultaten van een optimalisatierun, om snel de beste parameter-sets te vinden.
        * **Comparison Arena:** Een grafische vergelijking van varianten, met overlappende equity curves en een heatmap van key metrics om de robuustheid te beoordelen.
        * **Trade Explorer:** De meest krachtige analyse-tool. Hier kan de gebruiker door individuele trades van een *enkele* run klikken en op een grafiek precies zien wat de context was op het moment van de trade: welke indicatoren waren actief, waar lag de marktstructuur, waarom werd de entry getriggerd, etc.
* **Backend Interactie:** De UI roept de `StrategyOperator`, `OptimizationService` en `VariantTestService` aan. De resultaten worden opgehaald via de `VisualizationService`, die kant-en-klare "visualisatie-pakketten" (JSON-data voor grafieken en tabellen) levert.

### **Werkruimte 4 & 5: PAPER TRADING & LIVE MONITORING**

* **User Goal:** Een gevalideerde strategie naadloos overzetten naar een gesimuleerde en vervolgens een live-omgeving, en de prestaties continu monitoren.
* **UI Componenten:**
    * **Deployment Manager:** Een scherm waar een gebruiker een succesvolle strategie-configuratie kan "promoveren" naar Paper of Live trading.
    * **Live Dashboard:** Een real-time dashboard dat data leest uit de gedeelde datastore (bv. Redis) van de live-omgeving. Het toont:
        * Huidige PnL.
        * Open posities en orders.
        * Een live log-stream.
        * Alerts en notificaties.
        * Een prominente **"Noodstop"-knop** om de strategie onmiddellijk te deactiveren.
* **Backend Interactie:** De UI communiceert met de `LiveEnvironment` via een `Command Queue` (voor acties als "start" of "stop") en leest de live-staat via API-endpoints die gekoppeld zijn aan de real-time datastore.

---
## 5.4. Het Frontend-Backend Contract: BFF & TypeScript

De naadloze ervaring wordt technisch mogelijk gemaakt door twee kernprincipes:

1.  **Backend-for-Frontend (BFF):** De `frontends/web/api/` is geen generieke API, maar een **backend die exclusief voor de `frontends/web/ui/` werkt**. Hij levert data in exact het formaat dat de UI-componenten nodig hebben. Dit voorkomt complexe data-manipulatie in de frontend en houdt de UI-code schoon en gefocust op presentatie.

2.  **Contractuele Zekerheid met TypeScript:** We formaliseren het contract tussen de BFF en de UI om robuustheid te garanderen.
    * **Automatische Type Generatie:** Een tool in de ontwikkel-workflow leest de Pydantic-modellen (uit `schema.py` en DTO-bestanden) in de backend.
    * **Resultaat:** Het genereert automatisch corresponderende **TypeScript `interfaces`**. De frontend-code weet hierdoor al tijdens het ontwikkelen (*compile-time*) exact hoe elk data-object eruitziet. Een wijziging in de backend (bv. een veld hernoemen in een Pydantic-model) die niet in de frontend wordt doorgevoerd, leidt onmiddellijk tot een **compile-fout**, niet tot een onverwachte bug in productie.

Deze aanpak zorgt voor een robuust, ontkoppeld en tegelijkertijd perfect gesynchroniseerd ecosysteem, wat essentieel is voor de "supercharged" en efficiënte workflow die we voor ogen hebben.

---

# 6_RESILIENCE_AND_OPERATIONS.md

# 6. Robuustheid & Operationele Betrouwbaarheid

Dit document beschrijft de strategieën en architectonische patronen die S1mpleTrader V2 veerkrachtig maken tegen technische fouten. Deze principes zijn essentieel voor de betrouwbaarheid van het systeem, met name in een live trading-omgeving waar kapitaal op het spel staat.

---
## 6.1. Integriteit van de Staat: Atomiciteit en Persistentie

Een trading-systeem is inherent 'stateful'. De huidige staat (open posities, kapitaal, state van een plugin) is de basis voor toekomstige beslissingen. Het corrumperen van deze staat is catastrofaal.

### **6.1.1. Atomische Schrijfacties (Journaling)**

* **Probleem:** Een applicatiecrash of stroomuitval tijdens het schrijven van een state-bestand (bv. `state.json` voor een stateful plugin) kan leiden tot een half geschreven, corrupt bestand, met permanent dataverlies tot gevolg.
* **Architectonische Oplossing:** We implementeren een **Write-Ahead Log (WAL)** of **Journaling**-patroon, een techniek die door professionele databases wordt gebruikt.

* **Gedetailleerde Workflow:**
    1.  **Schrijf naar Journaal:** De `save_state()`-methode van een stateful plugin schrijft de nieuwe staat **nooit** direct naar `state.json`. Het serialiseert de data naar een tijdelijk bestand: `state.json.journal`.
    2.  **Forceer Sync naar Schijf:** Na het schrijven roept de methode `os.fsync()` aan op het `.journal`-bestands-handle. Dit is een cruciale, expliciete instructie aan het besturingssysteem om alle databuffers onmiddellijk naar de fysieke schijf te schrijven. Dit voorkomt dat de data alleen in het geheugen blijft en verloren gaat bij een stroomstoring.
    3.  **Atomische Hernoeming:** Alleen als de sync succesvol is, wordt de `os.rename()`-operatie uitgevoerd om `state.json.journal` te hernoemen naar `state.json`. Deze `rename`-operatie is op de meeste moderne bestandssystemen een **atomische handeling**: het slaagt in zijn geheel, of het faalt in zijn geheel.
    4.  **Herstel-Logica:** De `load_state()`-methode van de plugin bevat de herstel-logica. Bij het opstarten controleert het: "Bestaat er een `.journal`-bestand?". Zo ja, dan weet het dat de applicatie is gecrasht na stap 2 maar vóór stap 3. De herstelprocedure is dan het voltooien van de `rename`-operatie, waarmee de laatste succesvol geschreven staat wordt hersteld.

---
## 6.2. Netwerkveerkracht (Live/Paper Trading)

Een live-systeem is afhankelijk van een stabiele verbinding met externe databronnen en brokers. De architectuur moet ontworpen zijn om met de onvermijdelijke instabiliteit van het internet om te gaan.

* **Probleem:** Een tijdelijke of langdurige onderbreking van de WebSocket-verbinding kan leiden tot gemiste data, een incorrecte portfolio-staat en het onvermogen om posities te beheren.
* **Architectonische Oplossing:** De verantwoordelijkheid voor het managen van de verbinding ligt volledig bij de `LiveEnvironment` en zijn componenten.

* **Gedetailleerde Componenten:**
    1.  **`LiveDataSource` (met Heartbeat & Reconnect):**
        * **Heartbeat:** De `DataSource` verwacht niet alleen data, maar ook periodieke "heartbeat"-berichten van de exchange. Als er gedurende een configureerbare periode (bv. 30 seconden) geen enkel bericht binnenkomt, wordt de verbinding als verbroken beschouwd.
        * **Reconnect Protocol:** Zodra een verbreking wordt gedetetecteerd, start een automatisch reconnect-protocol. Dit gebruikt een **exponential backoff**-algoritme: het wacht 1s, dan 2s, 4s, 8s, etc., om de server van de exchange niet te overbelasten.

    2.  **`LiveExecutionHandler` (met State Reconciliation):**
        * **Principe:** Na een reconnect is de interne staat van het `Portfolio`-object **onbetrouwbaar**. Het systeem moet uitgaan van de "single source of truth": de exchange zelf.
        * **Proces:** De `ExecutionHandler` voert een **reconciliation**-procedure uit. Het roept de REST API van de exchange aan met de vragen: "Geef mij de status van al mijn openstaande orders" en "Geef mij al mijn huidige posities". Het vergelijkt dit antwoord met de data in het `Portfolio`-object en corrigeert eventuele discrepanties.

    3.  **`StrategyOperator` (met Circuit Breaker):**
        * **Principe:** Als de `LiveDataSource` na een configureerbaar aantal pogingen geen verbinding kan herstellen, moet het systeem in een veilige modus gaan om verdere schade te voorkomen.
        * **Proces:** De `DataSource` stuurt een `CONNECTION_LOST`-event naar de `Operator`. De `Operator` activeert dan de **Circuit Breaker**:
            * Het stopt onmiddellijk met het verwerken van nieuwe signalen.
            * Het stuurt een kritieke alert (via e-mail, Telegram, etc.) naar de gebruiker.
            * Het kan (optioneel) proberen alle open posities te sluiten als laatste redmiddel.

---
## 6.3. Applicatie Crash Recovery (Supervisor Model)

* **Probleem:** Het hoofdproces van de `StrategyOperator` kan crashen door een onverwachte bug in een plugin of een geheugenprobleem.
* **Architectonische Oplossing:** We scheiden het *starten* van de applicatie van de *applicatie zelf* door middel van een **Supervisor (Watchdog)**-proces, aangestuurd door `run_supervisor.py`.

* **Gedetailleerde Workflow:**
    1.  **Entrypoint `run_supervisor.py`:** Dit is het enige script dat je handmatig start in een live-omgeving.
    2.  **Supervisor Proces:** Dit script start een extreem lichtgewicht en robuust "supervisor"-proces. Zijn enige taak is het spawnen van een *kind-proces* voor de daadwerkelijke `StrategyOperator` en het monitoren van dit kind-proces.
    3.  **Herstart & Herstel Cyclus:**
        * Als het `Orchestrator`-proces onverwacht stopt, detecteert de `Supervisor` dit.
        * De `Supervisor` start de `Orchestrator` opnieuw.
        * De *nieuwe* `Orchestrator`-instantie start in een **"herstelmodus"**:
            * **Stap A (State Herstel):** Het roept de `load_state()`-methodes aan van al zijn stateful plugins, die de journaling-logica (zie 6.1) gebruiken om een consistente staat te herstellen.
            * **Stap B (Portfolio Herstel):** Het voert de **State Reconciliation**-procedure uit (zie 6.2) om zijn `Portfolio` te synchroniseren met de exchange.
            * **Stap C (Hervatting):** Alleen als beide stappen succesvol zijn, gaat de `Orchestrator` over naar de normale, live-operatie en begint het weer met het verwerken van marktdata.

---

# 7_DEVELOPMENT_STRATEGY.md

# 7. Ontwikkelstrategie & Tooling

Dit document beschrijft de methodiek, de workflow en de tooling voor het ontwikkelen, testen en debuggen van het S1mpleTrader V2 ecosysteem. Het is de blauwdruk voor een snelle, efficiënte en data-gedreven ontwikkelomgeving.

---
## 7.1. Filosofie: Rapid, Lean & User-Centered

We stappen af van een traditionele, op de CLI gerichte workflow. De nieuwe filosofie is gebaseerd op een combinatie van **Lean UX** en **User-Centered Design (UCD)**, met als doel een "supercharged" ontwikkelcyclus te creëren.

* **De Gebruiker staat Centraal:** De primaire gebruiker ("De Kwantitatieve Strateeg") en diens workflow bepalen wat we bouwen en in welke volgorde. De Web UI is het centrale instrument.
* **Compact Ontwikkelen:** We bouwen in de kleinst mogelijke, onafhankelijke eenheden (een plugin) en testen deze geïsoleerd.
* **Direct Testen:** Elke plugin wordt vergezeld van unit tests. Geen enkele component wordt als "klaar" beschouwd zonder succesvolle, geautomatiseerde tests.
* **Snelle Feedback Loop (Bouwen -> Meten -> Leren):** De tijd tussen een idee, een codewijziging en het zien van het visuele resultaat moet minimaal zijn. De Web UI is de motor van deze cyclus.

---
## 7.2. De "Supercharged" Ontwikkelcyclus in de Praktijk

De gehele workflow, van het bouwen van een strategie tot het analyseren van de resultaten, vindt plaats binnen de naadloze, visuele webapplicatie.

### **Fase 1: Visuele Strategie Constructie (De "Strategy Builder")**
* **Doel:** Snel en foutloos een nieuwe strategie (`run.yaml`) samenstellen.
* **Proces:**
    1.  De gebruiker opent de "Strategy Builder" in de Web UI.
    2.  In een zijbalk verschijnen alle beschikbare plugins, opgehaald via een API en gegroepeerd per `type` (bv. `signal_generators`).
    3.  De gebruiker sleept plugins naar de "slots" in een visuele weergave van de 9-fasen (fase 1-2 en fase 3-9) trechter/pijplijn.
    4.  Voor elke geplaatste plugin genereert de UI automatisch een configuratieformulier op basis van de `schema.py` van de plugin. Input wordt direct in de browser gevalideerd.
    5.  Bij het opslaan wordt de configuratie als `YAML` op de server aangemaakt.

### **Fase 2: Interactieve Analyse (De "Backtesting Hub")**
* **Doel:** De gebouwde strategieën rigoureus testen en de resultaten diepgaand analyseren.
* **Proces:**
    1.  **Run Launcher:** Vanuit de UI start de gebruiker een backtest of optimalisatie.
    2.  **Live Progress:** Een dashboard toont de live voortgang.
    3.  **Resultaten Analyse:**
        * **Optimalisatie:** Resultaten verschijnen in een interactieve tabel (sorteren, filteren).
        * **Diepgaande Analyse (Trade Explorer):** De gebruiker kan doorklikken naar een enkele run en door individuele trades bladeren, waarbij een interactieve grafiek alle contextuele data (marktstructuur, indicatoren, etc.) toont op het moment van de trade.

### **Fase 3: De Feedback Loop**
* **Doel:** Een inzicht uit de analysefase direct omzetten in een verbetering.
* **Proces:** Vanuit de "Trade Explorer" klikt de gebruiker op "Bewerk Strategie". Hij wordt direct teruggebracht naar de "Strategy Builder" met de volledige configuratie al ingeladen, klaar om een aanpassing te doen. De cyclus begint opnieuw.

---
## 7.3. De Tooling in Detail

### **7.3.1. Gespecialiseerde Entrypoints**
De applicatie kent drie manieren om gestart te worden, elk met een eigen doel:
* **`run_web.py` (De IDE):** Het primaire entrypoint voor de ontwikkelaar. Start de FastAPI-server die de Web UI en de bijbehorende API's serveert.
* **`run_backtest_cli.py` (De Robot):** De "headless" entrypoint voor automatisering, zoals regressietesten en Continuous Integration (CI/CD) workflows.
* **`run_supervisor.py` (De Productie-schakelaar):** De minimalistische, robuuste starter voor de live trading-omgeving.

### **7.3.2. Testen als Integraal Onderdeel**
* **Unit Tests per Plugin:** Elke plugin-map krijgt een `tests/test_worker.py`. Deze test laadt een stukje voorbeeld-data, draait de `worker.py` erop, en valideert of de output (bv. de nieuwe kolom of de `Signal` DTO) correct is. Dit gebeurt volledig geïsoleerd.
* **Integratietests:** Testen de samenwerking tussen de service laag componenten en de `Assembly`-componenten.
* **End-to-End Tests:** Een klein aantal tests die via `run_backtest_cli.py` een volledige backtest draaien op een vaste dataset en controleren of het eindresultaat (de PnL) exact overeenkomt met een vooraf berekende waarde.

### **7.3.3. Gelaagde Logging & Debugging**
Logging is een multi-inzetbare tool, geen eenheidsworst. We onderscheiden drie lagen:

1.  **Laag 1: `stdio` (De Console)**
    * **Doel:** Alleen voor *initiële, basic development* van een geïsoleerde plugin. Gebruik `print()` voor de snelle, "vuile" check. Dit is vluchtig en wordt niet bewaard.

2.  **Laag 2: Gestructureerde Logs (`JSON`)**
    * **Doel:** De primaire output voor **backtests en paper trading**. Dit is de *databron* voor analyse.
    * **Implementatie:** Een `logging.FileHandler` die log-records als gestructureerde `JSON`-objecten wegschrijft naar `run.log.json`.
    * **Principe:** De console blijft schoon. De *echte* output is het log-bestand.

3.  **Laag 3: De "Log Explorer" (Web UI)**
    * **Doel:** De primaire interface voor **analyse en debugging**.
    * **Implementatie:** Een tool in de frontend die `run.log.json` inleest en interactief presenteert, waardoor je kunt filteren op `plugin_name` of een `Correlation ID`.

#### **Traceability met de `Correlation ID`**
Elk `Signal` DTO dat wordt gecreëerd, krijgt een unieke ID (bv. een UUID). Elke plugin die dit signaal (of een afgeleid object zoals een `Trade` DTO) verwerkt, voegt deze `Correlation ID` toe aan zijn log-berichten. Door in de "Log Explorer" op deze ID te filteren, kan de gebruiker de volledige levenscyclus en beslissingsketen van één specifieke trade volgen, door alle fasen en parallelle processen heen.

---

# 8_META_WORKFLOWS.md

# 8. Meta Workflows: Van Analyse tot Inzicht

Dit document beschrijft de architectuur en de rol van de "Meta Workflows". Dit zijn hoog-niveau services die bovenop de kern-strategie-executie draaien om geavanceerde analyses, optimalisaties en automatisering mogelijk te maken.

---
## 8.1. Concept: De Orchestrator als Werknemer

De run levenscyclus (aangestuurd door componenten als de `PortfolioSupervisor`, `RunOrchestrator` en `StrategyOperator`) is de motor die in staat is om **één enkele** strategie-configuratie uit te voeren. Meta Workflows zijn services in de `Service`-laag die deze motor herhaaldelijk en systematisch aanroepen om complexe, kwantitatieve vragen te beantwoorden.

Ze fungeren als "onderzoekleiders" die de `StrategyOperator` als een werknemer behandelen, en leunen zwaar op de `ParallelRunService` om duizenden backtests efficiënt en parallel uit te voeren. Waar optimalisatie in V1 een ad-hoc script was, wordt het in V2 een **"eerste klas burger"** van de architectuur.

---
## 8.2. De `OptimizationService` (Het Onderzoekslab)

* **Doel:** Het systematisch doorzoeken van een grote parameterruimte om de meest performante combinaties voor een strategie te vinden.
* **Analogie:** Een farmaceutisch lab dat duizenden moleculaire variaties test om het meest effectieve medicijn te vinden.

#### **Gedetailleerde Workflow:**

1.  **Input (Het Onderzoeksplan):** De service vereist een basis `run.yaml` (de strategie) en een `optimization.yaml` die de onderzoeksvraag definieert: welke parameters (`start`, `end`, `step`) moeten worden gevarieerd en op welke metriek (`sharpe_ratio`, `profit_factor`) moet worden geoptimaliseerd.

2.  **Proces (De Experimenten):**
    * De `OptimizationService` genereert een volledige lijst van alle mogelijke parameter-combinaties.
    * Voor elke combinatie creëert het een unieke `AppConfig` in het geheugen.
    * Het delegeert de volledige lijst van configuraties aan de `ParallelRunService`.

3.  **Executie (Het Robotleger):**
    * De `ParallelRunService` start een pool van workers (één per CPU-kern).
    * Elke worker ontvangt één configuratie, initieert een volledige, opzichzelfstaande run levenscyclus en voert een volledige backtest uit.

4.  **Output (De Analyse):**
    * De `OptimizationService` verzamelt alle `BacktestResult`-objecten.
    * Het creëert een `pandas DataFrame` met de geteste parameters en de resulterende performance-metrieken.
    * Deze data wordt naar de Web UI gestuurd voor presentatie in een interactieve, sorteerbare tabel.

---
## 8.3. De `VariantTestService` (De Vergelijkings-Arena)

* **Doel:** Het direct vergelijken van een klein aantal discrete strategie-varianten onder exact dezelfde marktomstandigheden om de robuustheid en de impact van specifieke keuzes te valideren.
* **Analogie:** Een "head-to-head" race tussen een paar topatleten om te zien wie de beste allrounder is.

#### **Gedetailleerde Workflow:**

1.  **Input (De Deelnemers):** De service vereist een basis `run.yaml` en een `variant.yaml` die de "deelnemers" definieert.
    * **Voorbeeld:**
        * **Variant A ("Baseline"):** De basisconfiguratie.
        * **Variant B ("Hoge RR"):** Overschrijft alleen de `risk_reward_ratio` parameter.
        * **Variant C ("Andere Exit"):** Vervangt de `ATR` exit-plugin door een `FixedPercentage` exit-plugin.

2.  **Proces (De Race-Opzet):**
    * De `VariantTestService` past voor elke gedefinieerde variant de "overrides" toe op de basisconfiguratie om unieke `AppConfig`-objecten te creëren.
    * Het delegeert de lijst van deze variant-configuraties aan de `ParallelRunService`.

3.  **Executie (Het Startschot):**
    * De `ParallelRunService` voert voor elke variant een volledige backtest uit.

4.  **Output (De Finishfoto):**
    * De `VariantTestService` verzamelt de `BacktestResult`-objecten.
    * Deze data wordt naar de Web UI gestuurd voor een directe, visuele vergelijking, bijvoorbeeld door de equity curves van alle varianten in één grafiek te plotten en een heatmap van de belangrijkste metrieken te tonen.

---
## 8.4. De Rol van `ParallelRunService`

Deze service is een cruciale, herbruikbare `Backend`-component. Zowel de `OptimizationService` als de `VariantTestService` zijn "klanten" van deze service. Zijn enige verantwoordelijkheid is het efficiënt managen van de `multiprocessing`-pool, het tonen van de voortgang en het netjes aggregeren van resultaten. Dit is een perfect voorbeeld van het **Single Responsibility Principle**.

---

# 9_CODING_STANDAARDS_DESIGN_PRINCIPLES.md

# 9. Coding Standaarden

**Versie:** 2.0 · **Status:** Definitief

Dit document beschrijft de verplichte standaarden en best practices voor het schrijven van alle code binnen het S1mpleTrader V2 project. Het doel is een consistente, leesbare, onderhoudbare en robuuste codebase. Het naleven van deze standaarden is niet optioneel.

---
## 9.1. Code Kwaliteit & Stijl

### **9.1.1. Fundamenten**
* **PEP 8 Compliant:** Alle Python-code moet strikt voldoen aan de [PEP 8](https://peps.python.org/pep-0008/) stijlgids. Een linter wordt gebruikt om dit te handhaven.
    * **Regellengte:** Maximaal 100 tekens.
    * **Naamgeving:** `snake_case` voor variabelen, functies en modules; `PascalCase` voor klassen.
* **Volledige Type Hinting:** Alle functies, methodes, en variabelen moeten volledig en correct getypeerd zijn. We streven naar een 100% getypeerde codebase om runtime-fouten te minimaliseren.
* **Commentaar in het Engels:** Al het commentaar in de code (`# ...`) en docstrings moeten in het Engels zijn voor universele leesbaarheid en onderhoudbaarheid.

### **9.1.2. Gestructureerde Docstrings**
Elk bestand, elke klasse en elke functie moet een duidelijke docstring hebben.

* **Bestands-Header Docstring:** Elk `.py`-bestand begint met een gestandaardiseerde header die de inhoud en de plaats in de architectuur beschrijft.
    ```python
    # backend/assembly/plugin_registry.py
    """
    Contains the PluginRegistry, responsible for discovering and validating all
    available plugins within the ecosystem.

    @layer: Backend (Assembly)
    @dependencies: [PyYAML, Pydantic]
    @responsibilities:
        - Scans plugin directories for manifests.
        - Validates manifest schemas.
        - Builds and maintains the central plugin registry.
    """
    ```
* **Functie & Methode Docstrings (Google Style):** Voor alle functies en methodes hanteren we de **Google Style Python Docstrings**. Dit is een leesbare en gestructureerde manier om parameters, return-waarden en voorbeelden te documenteren.
    ```python
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
    ```

### **9.1.3. Naamgevingsconventies**
Naast de algemene [PEP 8]-richtlijnen hanteren we een aantal strikte, aanvullende conventies om de leesbaarheid en de architectonische zuiverheid van de code te vergroten.

* **Interfaces (Contracten):**

  * **Principe:** Elke abstracte klasse (`ABC`) of Protocol die een contract definieert, moet worden voorafgegaan door een hoofdletter `I`.

  * **Doel:** Dit maakt een onmiddellijk en ondubbelzinnig onderscheid tussen een abstract contract en een concrete implementatie. Het dwingt het "Dependency Inversion Principle" af door voor ontwikkelaars visueel te maken wanneer ze tegen een abstractie programmeren.

  * **Voorbeeld:**

        ```Python
        # Het contract (de abstractie)
        class IAPIConnector(Protocol):
            ...

        # De concrete implementatie
        class KrakenAPIConnector(IAPIConnector):
            ...
        ```

* **Klassen, Functies en Variabelen:**

  * **We volgen strikt de [PEP 8]-standaard:**

   `PascalCase` voor alle klassen (bv. `StrategyOperator`, `DataPersistor`).

   `snake_case` voor alle functies, methodes, variabelen en modules (bv. `get_historical_trades`, `_prepare_components`).

* **Interne Attributen en Methodes:**

  * **Principe:** Attributen of methodes die niet bedoeld zijn voor gebruik buiten de klasse (beschouwd als "private" of "protected"), moeten worden voorafgegaan door een enkele underscore (_).

  * **Doel:** Dit communiceert duidelijk de publieke API van een klasse en helpt onbedoelde afhankelijkheden van interne implementatiedetails te voorkomen.

  * **Voorbeeld:**

        ```Python
        class StrategyOperator:
            def __init__(self):
                self._app_config = ... # Intern, wordt niet van buitenaf benaderd

            def run(self): # Publieke methode
                self._prepare_components() # Interne hulpmethode

            def _prepare_components(self):
                ...
        ```
---
## 9.2. Contract-Gedreven Ontwikkeling

### **9.2.1. Pydantic voor alle Data-Structuren**
* **Principe:** Alle data die tussen componenten wordt doorgegeven, moet worden ingekapseld in een **Pydantic `BaseModel`**. Dit geldt voor DTO's, configuraties en plugin-parameters.
* **Voordeel:** Dit garandeert dat data van het juiste type en de juiste structuur is *voordat* het wordt verwerkt.

### **9.2.2. Abstracte Basisklassen (Interfaces)**
* **Principe:** Componenten die uitwisselbaar moeten zijn (zoals plugins), moeten erven van een gemeenschappelijke abstracte basisklasse (ABC) die een consistent contract afdwingt.

---
## 9.3. Gelaagde Logging & Traceability

### **9.3.1. Drie Lagen van Logging**
1.  **Laag 1: `stdio` (Console via `print()`):** Uitsluitend voor snelle, lokale, vluchtige debugging. Mag nooit gecommit worden.
2.  **Laag 2: Gestructureerde `JSON`-logs:** De standaard output voor alle runs, bedoeld voor analyse.
3.  **Laag 3: De Web UI (Log Explorer):** De primaire interface voor het analyseren en debuggen van runs.

### **9.3.2. Traceability via `Correlation ID`**
* **Principe:** Elk `Signal` DTO krijgt een unieke `UUID`. Elke volgende plugin die dit signaal verwerkt, neemt deze `correlation_id` over in zijn log-berichten. Dit maakt de volledige levenscyclus van een trade traceerbaar.

---
## 9.4. Testen als Voorwaarde

* **Principe:** Code zonder tests wordt beschouwd als onvolledig.
* **Implementatie:** Elke plugin is **verplicht** om een `tests/test_worker.py`-bestand te bevatten. Continue Integratie (CI) voert alle tests automatisch uit na elke `push`.

---
## 9.5. Overige Standaarden

* **Internationalisatie (i18n):**
    * **Principe:** *Alle* tekst die direct of indirect aan een gebruiker kan worden getoond, moet via de internationalisatie-laag lopen. Hardgecodeerde, gebruikersgerichte strings in de Python-code zijn niet toegestaan.
    * **Implementatie:** Een centrale `Translator`-klasse laadt `YAML`-bestanden uit de `/locales` map. Code gebruikt vertaalsleutels in "dot-notation" (bv. `log.backtest.complete`).
    * **Scope van de Regel:** Deze regel is van toepassing op, maar niet beperkt tot, de volgende onderdelen:
      1. * **Log Berichten:** Alle log-berichten die bedoeld zijn om de gebruiker te informeren over de voortgang of status van de applicatie (voornamelijk [INFO]-niveau en hoger). Foutmeldingen voor ontwikkelaars ([DEBUG]-niveau) mogen wel hardcoded zijn.
        **Correct:** `logger.info('run.starting', pair=pair_name)`
        **Incorrect:** `logger.info(f'Starting run for {pair_name}...')`
      2. * **ConfigPydantic Veldbeschrijvingen:** Alle `description` velden binnen Pydantic-modellen (DTO's, configuratie-schema's). Deze beschrijvingen kunnen direct in de UI of in documentatie worden getoond.
        **Correct:** `equity: float = Field(..., description="portfolio_state.equity.desc")`
        **Incorrect:** `equity: float = Field(..., description="The total current value...")`
      3. * **Plugin Manifesten:** Alle beschrijvende velden in een plugin_manifest.yaml, zoals description en display_name. De PluginQueryService moet deze velden door de Translator halen voordat ze naar de frontend worden gestuurd.
    * **Interactie met Logger:** De `Translator` wordt één keer geïnitialiseerd en geïnjecteerd in de `LogFormatter`. De formatter is de enige component binnen het logsysteem die sleutels vertaalt naar leesbare berichten. Componenten die direct output genereren (zoals UI `Presenters`) krijgen de `Translator` ook apart geïnjecteerd.

### **9.5.1. Structuur van i18n Dotted Labels**
Om de `locales/*.yaml` bestanden georganiseerd en onderhoudbaar te houden, hanteren we een strikte, hiërarchische structuur voor alle vertaalsleutels. De structuur volgt over het algemeen het pad van de component of het datamodel waar de tekst wordt gebruikt.

  * **Principe:** component_of_laag.specifieke_context.naam_van_de_tekst

  **Voorbeelden van de Structuur:**
    1. **Log Berichten:**
    De sleutel begint met de naam van de module of de belangrijkste klasse waarin de log wordt aangeroepen.

    **Structuur:** component_name.actie_of_gebeurtenis

    **Voorbeelden:**

    ```YAML
    # Voor backend/assembly/plugin_registry.py
    plugin_registry:
    scan_start: "Scanning for plugins in '{path}'..."
    scan_complete: "Scan complete. Found {count} valid plugins."

    # Voor services/strategy_operator.py
    strategy_operator:
    run_start: "StrategyOperator run starting..."
    critical_event: "Critical event detected: {event_type}"
    Pydantic Veldbeschrijvingen (description):

    De sleutel weerspiegelt het pad naar het veld binnen het DTO of schema. De sleutel eindigt altijd op .desc om aan te geven dat het een beschrijving is.
    ```  

    **Structuur:** schema_naam.veld_naam.desc

    **Voorbeelden:**

    ```YAML
    # Voor backend/dtos/portfolio_state.py
    portfolio_state:
    equity:
        desc: "The total current value of the portfolio."
    available_cash:
        desc: "The amount of cash available for new positions."

    # Voor een plugin's schema.py
    ema_detector_params:
    period:
        desc: "The lookback period for the EMA calculation."
    Plugin Manifesten (plugin_manifest.yaml):

    Voor de beschrijvende velden van een plugin gebruiken we een structuur die de plugin uniek identificeert.
    ```

    **Structuur:** plugins.plugin_naam.veld_naam

    **Voorbeelden:**

    ```YAML
    plugins:
    ema_detector:
        display_name: "EMA Detector"
        description: "Calculates and adds an Exponential Moving Average."
    fvg_entry_detector:
        display_name: "FVG Entry Detector"
        description: "Detects a Fair Value Gap after a Market Structure Shift."

    * **Configuratie Formaat:** `YAML` is de standaard voor alle door mensen geschreven configuratie. `JSON` wordt gebruikt voor machine-naar-machine data-uitwisseling.
    ```

---
## 9.6. Design Principles & Kernconcepten

De architectuur is gebouwd op de **SOLID**-principes en een aantal kern-ontwerppatronen die de vier kernprincipes (Plugin First, Scheiding van Zorgen, Configuratie-gedreven, Contract-gedreven) tot leven brengen.

### **De Synergie: Configuratie- & Contract-gedreven Executie**

Het meest krachtige concept van V2 is de combinatie van configuratie- en contract-gedreven werken. De code is de motor; **de configuratie is de bestuurder, en de contracten zijn de verkeersregels die zorgen dat de bestuurder binnen de lijntjes blijft.**

* **Configuratie-gedreven:** De *volledige samenstelling* van een strategie (welke plugins, in welke volgorde, met welke parameters) wordt gedefinieerd in een `YAML`-bestand. Dit maakt het mogelijk om strategieën drastisch te wijzigen zonder één regel code aan te passen.

* **Contract-gedreven:** Elk stukje configuratie en data wordt gevalideerd door een strikt **Pydantic-schema**. Dit werkt op twee niveaus:
  1.  **Algemene Schema's:** De hoofdstructuur van een `run_blueprint.yaml` wordt gevalideerd door een algemeen `app_schema.py`. Dit contract dwingt af dat er bijvoorbeeld altijd een `environment` en een `strategy_pipeline` sectie aanwezig is.
  2.  **Plugin-Specifieke Schema's:** De parameters voor een specifieke plugin (bv. de `length` van een `EMA`-indicator) worden gevalideerd door de Pydantic-klasse in de `schema.py` van *die ene plugin*.

Bij het starten van een run, leest de applicatie het `YAML`-bestand en bouwt een gevalideerd `AppConfig`-object. Als een parameter ontbreekt, een verkeerd type heeft, of een plugin wordt aangeroepen die niet bestaat, faalt de applicatie *onmiddellijk* met een duidelijke foutmelding. Dit voorkomt onvoorspelbare runtime-fouten en maakt het systeem extreem robuust en voorspelbaar.

### **SOLID in de Praktijk**
* **SRP (Single Responsibility Principle):** Elke klasse heeft één duidelijke taak.
  * ***V2 voorbeeld:*** Een `FVGEntryDetector`-plugin detecteert alleen Fair Value Gaps. Het bepalen van de positiegrootte of het analyseren van de marktstructuur gebeurt in aparte `position_sizer`- of context-plugins.

* **OCP (Open/Closed Principle):** Uitbreidbaar zonder bestaande code te wijzigen.
    * ***V2 voorbeeld:*** Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe `exit_planner`-plugin; de `StrategyEngine` hoeft hiervoor niet aangepast te worden.

* **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.
    * ***V2 voorbeeld:*** De `BacktestService` (Service-laag) hangt af van de `BaseEnvironment`-interface, niet van de specifieke `BacktestEnvironment`. Hierdoor zijn de services volledig herbruikbaar in elke context.

### **Kernpatronen**
* **Factory Pattern:** Het `Assembly Team` (met `WorkerBuilder`) centraliseert het ontdekken, valideren en creëren van alle plugins.
* **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.
* **DTO’s (Data Transfer Objects):** Pydantic-modellen (`Signal`, `TradePlan`, `ClosedTrade`) zorgen voor een voorspelbare en type-veilige dataflow tussen alle componenten.

---

# A_BIJLAGE_TEMINOLOGIE.md

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
  * **Abstractie**: De opties in de dropdown zijn mensvriendelijke, vertaalde beschrijvingen (bv. "Signaal Generator (De Verkenner)"), niet de technische `enum`\-waarden (`signal_generator`). Het platform vertaalt de keuze van de gebruiker op de achtergrond naar de juiste technische waarde.  
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
* **Voorbeeld**: `[EMA(10)]` \-\> `[Kruist Boven]` \-\> `[EMA(50)]` \-\> `[Genereer Long Signaal]`.  
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

