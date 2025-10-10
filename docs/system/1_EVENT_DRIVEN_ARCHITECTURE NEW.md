# **S1mpleTrader V2 Architectuur: De Event-Gedreven Run Levenscyclus**

Versie: 3.3 (Gelaagd Portfolio Model \- Compleet)  
Status: Definitief

## **1\. Visie & Architectonische Principes**

### **1.1. Inleiding & Doel**

Dit document beschrijft de architectonische evolutie van S1mpleTrader V2 van een procedureel, hiërarchisch model naar een ontkoppeld, **event-gedreven model**. Dit ontwerp is de blauwdruk voor het beheren van de volledige levenscyclus van trading strategieën en operationele processen.

Het doel van deze architectuur is het verhogen van de robuustheid, schaalbaarheid en onderhoudbaarheid, met name in een complexe, multi-strategie, multi-asset en multi-exchange omgeving. De kern van dit ontwerp wordt gevormd door een centrale EventBus die als zenuwstelsel fungeert, waardoor componenten als gelijkwaardige, gespecialiseerde collega's met elkaar samenwerken via strikt gedefinieerde, contract-gedreven events.

### **1.2. Het Hybride Model: De Juiste Tool voor de Juiste Taak**

De architectuur hanteert een bewust **hybride model** om onnodige complexiteit te vermijden:

* **Event-Gedreven voor de Run Levenscyclus**: De dynamische, asynchrone en real-time flow van een actieve trading run (van marktdata naar beslissing naar executie) wordt volledig afgehandeld via de EventBus.  
* **Procedureel (Request-Response) voor Synchrone Taken**: Processen die van nature transactioneel en synchroon zijn, blijven procedureel. Dit geldt voor:  
  * **Configuratie & Validatie**: Het laden en valideren van YAML-bestanden gebeurt synchroon bij de start.  
  * **Gebruikersinteracties (UI)**: Een gebruiker die een strategie start via de UI, doet een directe API-call en verwacht een directe respons.  
  * **Interne Component Logica**: Complexe componenten zoals de StrategyEngine hebben intern een voorspelbare, procedurele logica.

## **2\. Component Categorieën: Een Strikte Scheiding van Verantwoordelijkheden**

Om de architecturale zuiverheid te bewaken, verdelen we de componenten in drie duidelijk gescheiden categorieën:

1. **Kernservices**: De fundamentele, langlevende componenten die het platform orkestreren en faciliteren.  
2. **De Analytische Pijplijn**: Een gespecialiseerde, stateless en procedurele flow voor het genereren van analytische handelsvoorstellen.  
3. **Operationele Agenten**: Stateful, portfolio-bewuste componenten die deterministische, op regels gebaseerde taken uitvoeren.

## **3\. Uitwerking van de Kerncomponenten**

### **3.1. Kernservices**

* **PortfolioSupervisor (De Operationeel Manager)**: Leest een portfolio.yaml en beheert de levenscyclus van de daarin gedefinieerde strategieën en ExecutionEnvironments. Fungeert als de hoogste risicomanager.  
* **RunOrchestrator (De Facilitator)**: Geïnstantieerd *per strategie*. Zet de benodigde specialisten op voor één run en publiceert de initiële RunStarted-event.  
* **ContextBootstrapper (De "Voorgloeier")**: Zorgt voor een complete, historisch correcte staat *voordat* de eerste live tick wordt verwerkt.  
* **ContextOrchestrator (De State Manager)**: Het **stateful hart** van een actieve run. Abonneert zich op MarketDataReceived en publiceert een verrijkte ContextReady.  
* **StrategyOperator (De Analytische Specialist)**: Abonneert zich op ContextReady, roept procedureel de StrategyEngine aan, en publiceert het resultaat als een StrategyProposalReady-event.  
* **ExecutionHandler (De Uitvoerder)**: Reageert op ExecutionApproved-events. Roept het StrategyLedger (in backtest) of de APIConnector (in live/paper) aan. Na de wijziging publiceert het een **LedgerStateChanged**\-event.  
* **AggregatePortfolioView (De Hoofd-Accountant)**: Luistert naar alle individuele **LedgerStateChanged**\-events van de actieve StrategyLedgers. Het aggregeert deze data om een overkoepelend beeld van de totale performance van het logische Portfolio te vormen en publiceert dit als een AggregatePortfolioUpdated-event.

### **3.2. De Analytische Pijplijn**

* **StrategyEngine (De Analist)**: Een **stateless** Backend-component die de **procedurele Fase 3-9 pijplijn** uitvoert. Zijn input is primair de marktdata; de LedgerState wordt enkel *read-only* gebruikt.

### **3.3. Operationele Agenten**

* **GridTraderAgent, DCAAgent, RebalancerAgent**: Stateful, portfolio-bewuste componenten die parallel aan de StrategyEngine opereren en reageren op events als ContextReady en LedgerStateChanged.

### **3.4. Loggers & Recorders**

* **AppLogger**: De standaard logger, geïnjecteerd in alle componenten.  
* **ContextRecorder**: Een losstaande "archivaris" die zich abonneert op ContextReady en StrategyProposalReady om data vast te leggen voor de "Trade Explorer" UI.  
* **ResultLogger**: Abonneert zich op RunFinished en BacktestCompleted om de finale resultaten op te slaan.

## **4\. De Event Map: Contracten op de EventBus**

Dit is de definitieve lijst van events die de interactie tussen de componenten sturen.

| Event Naam | Payload (DTO Contract) | Publisher(s) | Subscriber(s) |
| :---- | :---- | :---- | :---- |
| **Run Lifecycle** |  |  |  |
| RunStarted | RunParameters | PortfolioSupervisor | ContextBootstrapper, ExecutionEnvironment |
| BootstrapComplete | BootstrapResult | ContextBootstrapper | ExecutionEnvironment |
| ShutdownRequested | ShutdownSignal | RiskMonitor, UI, RunOrchestrator | RunOrchestrator, PortfolioSupervisor |
| RunFinished | RunSummary | RunOrchestrator | ResultLogger, UI, DatabaseService |
| \--- | \--- | \--- | \--- |
| **Tick Lifecycle** |  |  |  |
| MarketDataReceived | MarketSnapshot | ExecutionEnvironment | ContextOrchestrator |
| ContextReady | TradingContext | ContextOrchestrator | StrategyOperator, Operationele Agenten, ContextRecorder, LiveDashboardUI |
| StrategyProposalReady | EngineCycleResult | StrategyOperator | PortfolioSupervisor, ContextRecorder |
| ExecutionApproved | List\[ExecutionDirective\] | PortfolioSupervisor, Operationele Agenten | ExecutionHandler, LiveDashboardUI |
| \--- | \--- | \--- | \--- |
| **Ledger & Portfolio Lifecycle** |  |  |  |
| **LedgerStateChanged** | **LedgerState** | ExecutionHandler | ContextOrchestrator, AggregatePortfolioView, Operationele Agenten, LiveDashboardUI |
| AggregatePortfolioUpdated | AggregateMetrics | AggregatePortfolioView | LiveDashboardUI, PortfolioSupervisor |
| \--- | \--- | \--- | \--- |
| **Backtest & Analysis** |  |  |  |
| BacktestCompleted | BacktestResult | RunOrchestrator | ResultPresenter (UI), DatabaseService, ResultLogger |

## **5\. De Levenscyclus in de Praktijk**

**A. Initialisatie (De "Bootstrap Fase")**

1. De PortfolioSupervisor valideert de portfolio.yaml, creëert de benodigde ExecutionEnvironments en RunOrchestrators, en publiceert RunStarted voor elke actieve strategie.  
2. De ContextBootstrapper reageert hierop, haalt bulk historische data op, "primed" de ContextOrchestrator, en publiceert BootstrapComplete.

**B. De Tick-Loop (De "Hartslag")**

3. De ExecutionEnvironment begint met het publiceren van MarketDataReceived-events.  
4. De ContextOrchestrator vangt elk event op, werkt zijn interne state bij, en publiceert een complete ContextReady.  
5. Zowel de StrategyOperator als eventuele Operationele Agenten reageren *parallel* op ContextReady.  
6. De StrategyOperator roept de StrategyEngine aan en publiceert (indien van toepassing) een StrategyProposalReady.  
7. De PortfolioSupervisor ontvangt dit voorstel, past zijn risicomanagement toe, en publiceert (indien goedgekeurd) ExecutionApproved.  
8. De ExecutionHandler voert de trade uit. De resulterende wijziging in het StrategyLedger leidt ertoe dat de ExecutionHandler een **LedgerStateChanged**\-event publiceert.  
9. De AggregatePortfolioView vangt LedgerStateChanged op en werkt de totale performance van het logische portfolio bij.

## **6\. Ontwerpoplossingen & Scenario Analyse**

### **6.1. Oplossingen voor Complexe Vraagstukken**

* **Multi-Strategie**: Beheerd door de PortfolioSupervisor die per strategie een run\_id toekent. Events worden via deze ID onderscheiden op de centrale EventBus.  
* **Multi-Exchange**: Geabstraheerd door een ExecutionEnvironmentFactory die de juiste APIConnector injecteert.  
* **Gelaagde Performance**: Opgelost door individuele StrategyLedger-objecten en een overkoepelende AggregatePortfolioView.

### **6.2. Scenario Analyse**

* **Grid Trader & DCA Strategie**: Worden geïmplementeerd als **Operationele Agenten**. Ze zijn stateful en reageren direct op ContextReady en LedgerStateChanged.  
* **Portfolio Rebalancer**: Wordt geïmplementeerd als een **Operationele Agent**. Het reageert op AggregatePortfolioUpdated.  
* **Analytische FVG Strategie**: Dit is de kerntaak van de **Analytische Pijplijn**. Een CrashDetector-plugin (Fase 9\) kan een analytisch CriticalEvent genereren, waarop een RiskMonitor (een aparte service) kan reageren.

## **7\. Integratie in de Documentatie**

Dit document (1\_EVENT\_DRIVEN\_ARCHITECTURE.md) is de primaire bron voor de run-levenscyclus architectuur. Andere documenten zullen worden bijgewerkt om naar dit document te verwijzen.