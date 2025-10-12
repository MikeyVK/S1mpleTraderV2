# **1\. S1mpleTrader V2: De Communicatie Architectuur**

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

De EventAdapter is een generieke, herbruikbare "vertaler" wiens enige taak het is om een brug te slaan tussen de EventBus en een pure business-component (Operator). Zijn gedrag wordt niet in code, maar in configuratie gedefinieerd via de wiring\_map.yaml.

**Voorbeeld van een wiring\_map.yaml-regel:**

\# wiring\_map.yaml  
\- adapter\_id: "AnalysisPipelineAdapter"  
  listens\_to: "ContextReady"  
  invokes:  
    component: "AnalysisOperator"  
    method: "run\_pipeline"  
  publishes\_result\_as: "StrategyProposalReady"

Deze regel instrueert het systeem om:

1\. Een EventAdapter te creëren.  

2\. Deze adapter te laten luisteren naar het ContextReady\\-event.  

3\. Wanneer dat event binnenkomt, de run\\\_pipeline()\\-methode van de AnalysisOperator aan te roepen met de event-payload.  

4\. Als de methode een resultaat teruggeeft, dit resultaat te publiceren op de bus onder de naam StrategyProposalReady.

### **1.2.2. De Rol van de EventWiringFactory**

Tijdens het opstarten van de applicatie leest de EventWiringFactory de volledige wiring\_map.yaml. Voor elke regel in de map creëert en configureert het een EventAdapter-instantie en abonneert deze op de EventBus.

## **1.3. De Levenscyclus in de Praktijk**

### **1.3.1. De Bootstrap Fase (Het "Bedraden" van het Systeem)**

1. De gebruiker start een Operation via een entrypoint.  
2. De applicatie laadt de volledige "Configuratie Trein".  
3. De **ComponentBuilder** (onderdeel van het Assembly Team) instantieert alle benodigde, pure business-componenten (Operators en Workers).  
4. De **ContextBootstrapper** zorgt voor het vullen van de initiële, rijke context *voordat* de Operation live gaat.  
5. De **EventWiringFactory** leest de wiring\_map.yaml en creëert de EventAdapters, die zich abonneren op de EventBus.  
6. Het OperationStarted-event wordt gepubliceerd. Het systeem is nu "live".

### **1.3.2. Een Runtime Voorbeeld (De Tick-Loop)**

1. Een ExecutionEnvironment publiceert een MarketDataReceived-event.  
2. De **EventAdapter** voor de ContextOperator wordt geactiveerd.  
3. De adapter roept de run\_pipeline()-methode van de ContextOperator aan.  
4. De ContextOperator retourneert een TradingContext DTO.  
5. De adapter publiceert dit resultaat als een ContextReady-event.  
6. **Parallel** worden nu alle adapters wakker die luisteren naar ContextReady (voor de AnalysisOperator, MonitorWorker, etc.), en de cyclus herhaalt zich.

## **1.4. De Event Map: De Grondwet van de Communicatie**

De event\_map.yaml definieert alle toegestane events en hun contracten.

| Event Naam | Payload (DTO Contract) | Mogelijke Publisher(s) | Mogelijke Subscriber(s) |
| :---- | :---- | :---- | :---- |
| **Operation Lifecycle** |  |  |  |
| OperationStarted | OperationParameters | Operations | EventAdapter (voor ContextOperator), ContextBootstrapper |
| BootstrapComplete | BootstrapResult | ContextBootstrapper | ExecutionEnvironment |
| ShutdownRequested | ShutdownSignal | UI, EventAdapter (van MonitorWorker) | Operations |
| OperationFinished | OperationSummary | Operations | ResultLogger, UI |
| \--- | \--- | \--- | \--- |
| **Tick Lifecycle** |  |  |  |
| MarketDataReceived | MarketSnapshot | ExecutionEnvironment | EventAdapter (voor ContextOperator) |
| ContextReady | TradingContext | EventAdapter (van ContextOperator) | EventAdapter (voor AnalysisOperator, MonitorWorker, ExecutionWorker) |
| StrategyProposalReady | EngineCycleResult | EventAdapter (van AnalysisOperator) | EventAdapter (voor ExecutionOperator) |
| ExecutionApproved | List\[ExecutionDirective\] | EventAdapter (van ExecutionOperator) | ExecutionEnvironment |
| \--- | \--- | \--- | \--- |
| **State & Monitoring Lifecycle** |  |  |  |
| LedgerStateChanged | LedgerState | ExecutionEnvironment | EventAdapter (voor MonitorWorker) |
| AggregatePortfolioUpdated | AggregateMetrics | EventAdapter (van MonitorWorker) | EventAdapter (voor ExecutionWorker), UI |
| \--- | \--- | \--- | \--- |
| **Analyse Lifecycle** |  |  |  |
| BacktestCompleted | BacktestResult | Operations | ResultLogger, UI |

