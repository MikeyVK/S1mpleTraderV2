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