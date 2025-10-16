# **Overdrachtsdocument: Verfijningen en Afwijkingen op de S1mpleTrader V2 Architectuur**

Versie: 2.1 (Evolutie van de Blauwdruk)  
Status: Definitief

## **1\. Voorwoord: Van Pijplijn naar Ecosysteem**

Dit document legt de fundamentele verfijningen vast die zijn voortgekomen uit een diepgaande analyse van de oorspronkelijke S1mpleTrader V2 architectuurblauwdruk. De oorspronkelijke documenten blijven de basis, maar de hier beschreven wijzigingen vertegenwoordigen een significante evolutie in het denken, gericht op het maximaliseren van de Single Responsibility Principle (SRP), modulariteit en de intuïtiviteit voor de eindgebruiker (de quant).

De kern van de evolutie is de transitie van een relatief lineaire, door analyse gedreven **pijplijn** naar een dynamisch, data-gedreven **ecosysteem van samenwerkende, specialistische agenten**.

## **2\. Kernafwijking \#1: De Evolutie van 4 naar 5 Worker Categorieën**

De meest fundamentele wijziging is de herstructurering van de worker-categorieën.

### **Afwijking van 2\_ARCHITECTURE v2.md en enums.py:**

Het oorspronkelijke model van vier workers (Context, Analysis, Monitor, Execution) is geëvolueerd naar een meer granulair en logisch model van vijf workers. De rollen van AnalysisWorker en MonitorWorker zijn herzien en de nieuwe PlanningWorker is geïntroduceerd.

### **De Nieuwe Worker Categorieën en Hun Strikte SRP:**

1. **ContextWorker \- "De Cartograaf"**:  
   * **Rol (ongewijzigd):** Het in kaart brengen en verrijken van de markt met objectieve context. De basis van alle intelligentie.  
2. **OpportunityWorker \- "De Verkenner" (Voorheen AnalysisWorker)**:  
   * **Nieuwe, Strikte Rol:** De *enige* taak is het **herkennen van handelskansen**. Dit omvat technische patronen, fundamentele events, sentiment, etc. Deze worker beantwoordt de vraag: "Is hier een kans?".  
   * **Output:** Een OpportunitySignal DTO.  
3. **ThreatWorker \- "De Waakhond" (Voorheen MonitorWorker)**:  
   * **Nieuwe, Strikte Rol:** De *enige* taak is het **detecteren van risico's en bedreigingen**. Dit omvat portfolio-, markt-, en systeemrisico's. Deze worker beantwoordt de vraag: "Is hier een gevaar?".  
   * **Output:** Een ThreatDetected DTO.  
4. **PlanningWorker \- "De Strateeg" (Nieuw)**:  
   * **Nieuwe Categorie:** Deze worker overbrugt de kloof tussen kans en actie. Zijn *enige* taak is het **transformeren van een abstracte OpportunitySignal naar een concreet, volledig uitgewerkt TradePlan DTO**.  
   * **Rationale:** Dit haalt alle management- en planningslogica (entry, exit, size, routing) uit de oude AnalysisWorker, wat leidt tot een veel zuiverdere scheiding.  
5. **ExecutionWorker \- "De Uitvoerder"**:  
   * **Rol (verduidelijkt):** De *enige* taak is het **initiëren, uitvoeren en actief beheren** van trades en operationele taken op basis van een TradePlan en actieve Threats.

## **3\. Kernafwijking \#2: Deconstructie van de Analytische Pijplijn**

De lineaire 9-fasen pijplijn is vervangen door een flexibeler, parallel en data-gedreven model.

### **Afwijking van 5\_DE\_ANALYTISCHE\_PIJPLIJN.md:**

De lineaire pijplijn die beschreven staat, is verouderd. De fasen zijn herverdeeld over de nieuwe Worker-categorieën, wat leidt tot een logischere en krachtigere dataflow.

### **De Nieuwe Dataflow:**

           \+--------------------+  
           | ExecutionEnv       |  
           | (Bron van data &   |  
           | strategy\_link\_id)  |  
           \+----------+---------+  
                      |  
                      v (Initieel, "ruw" TradingContext)  
           \+----------+---------+  
           | ContextOperator    |  
           | (Verrijkt Context) |  
           \+----------+---------+  
                      |  
                      v (Volledig, "rijk" ContextReady event)  
           \+----------+-----------+-------------------+  
           |                      |                   |  
           v                      v                   v  
\+----------+---------+ \+----------+---------+ \+----------+---------+  
| OpportunityOperator| | ThreatOperator     | | (Andere Listeners) |  
| (Vindt Kansen)     | | (Vindt Bedreigingen)| |                    |  
\+----------+---------+ \+----------+---------+ \+----------+---------+  
           |                      |  
           v (OpportunitySignal)  | (ThreatDetected)  
\+----------+---------+            |  
| PlanningOperator   |            |  
| (Maakt een Plan)   |            |  
\+----------+---------+            |  
           |                      |  
           v (TradePlan)          |  
\+----------+----------------------+---------+  
| ExecutionOperator                        |  
| (Weegt Plan vs. Bedreiging en Voert Uit) |  
\+------------------------------------------+

## **4\. Kernafwijking \#3: Uniforme Abstractie van de Service & Persistence Laag**

We hebben de implementatie van de Operators en de Persistence-laag geüniformeerd en geabstraheerd om het DRY-principe en SRP maximaal te respecteren.

### **A. De Data-Gedreven Operator (BaseOperator)**

* **Afwijking:** Het concept van vijf aparte, hard-gecodeerde Operator-klassen is vervangen door één enkele, generieke BaseOperator-klasse.  
* **Nieuwe Realiteit:** Het gedrag van elke operator-instantie (SEQUENTIAL, PARALLEL, etc.) wordt nu volledig gedicteerd door een nieuw centraal configuratiebestand, operators.yaml, en gevalideerd door een OperatorConfig-schema. De OperatorFactory leest deze configuratie en bouwt de operators dynamisch op.

### **B. De Persistence Suite (PersistorFactory)**

* **Afwijking:** De ad-hoc en inconsistente manier van state- en journal-afhandeling is vervangen door een formele, uniforme Persistence Suite.  
* **Nieuwe Realiteit:** Een PersistorFactory creëert en beheert drie gespecialiseerde persistors, elk achter een duidelijke interface:  
  1. IDataPersistor: Voor historische marktdata (gebruikt ParquetPersistor).  
  2. IStatePersistor: Voor de read-write state van workers (gebruikt een generieke JsonPersistor).  
  3. IJournalPersistor: Voor het append-only StrategyJournal (gebruikt dezelfde generieke JsonPersistor).

## **5\. Kernafwijking \#4: Verfijning van de Plugin-Anatomie & Traceability**

### **A. De Drie-eenheid van BaseWorker-Capaciteiten**

* **Afwijking:** De afhandeling van state, events en journaling is volledig geüniformeerd. De onnodige JournalAdapter en StrategyJournal-service zijn verwijderd.  
* **Nieuwe Realiteit:** Een plugin kan erven van drie onafhankelijke basisklassen die elk een specifieke capaciteit bieden via **Dependency Injection**, wat de plugin 100% agnostisch houdt:  
  1. **BaseStatefulWorker**: Krijgt een IStatePersistor geïnjecteerd voor synchrone state-afhandeling.  
  2. **BaseEventAwareWorker**: Wordt bediend door een PluginEventAdapter voor asynchrone event-communicatie.  
  3. **BaseJournalingWorker**: Krijgt een IJournalPersistor geïnjecteerd voor het direct en ontkoppeld loggen naar het journaal.

### **B. De StrategyJournal en Causale Traceability**

* **Afwijking:** Het concept van een simpele CorrelationID is geëvolueerd naar een rijk Traceability Framework. De StrategyLedger is gezuiverd van historische data.  
* **Nieuwe Realiteit:**  
  1. **StrategyLedger (Staat):** Bevat *alleen* de actuele, operationele staat van trades. Het is snel en gefocust.  
  2. **StrategyJournal (Geschiedenis):** Een aparte, append-only log die het *volledige verhaal* vastlegt, inclusief **afgewezen kansen**. Dit wordt de primaire bron voor de TradeExplorer UI en diepgaande performance-analyse.  
  3. **Causale ID's:** We introduceren getypeerde ID's (TradeID, OpportunityID, ThreatID, ScheduledID) die in het StrategyJournal worden vastgelegd om de **causaliteit** (de "waarom") achter elke actie te kunnen traceren en analyseren.