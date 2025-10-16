# **S1mpleTrader V2.1: Finale Architectonische Verfijningen**

**Versie:** 2.1

**Status:** Definitief

## **1\. Introductie**

Dit document dient als het finale addendum op de S1mpleTrader V2.0 architectuurdocumentatie. Het legt de laatste, cruciale ontwerpbeslissingen vast die voort zijn gekomen uit diepgaande analyses van de oorspronkelijke blauwdruk. Deze verfijningen leiden tot een architectuur die conceptueel zuiverder, robuuster en krachtiger is.

De belangrijkste wijzigingen zijn:

1. De evolutie naar een **5-categorie worker ecosysteem**.  
2. De introductie van een geavanceerd **Traceability Framework**.  
3. De formele scheiding tussen de **StrategyLedger** en het **StrategyJournal**.

## **2\. Kernafwijking \#1: Het 5-Categorie Worker Ecosysteem**

De oorspronkelijke 4 workers (Context, Analysis, Monitor, Execution) zijn geherstructureerd naar 5, meer gespecialiseerde categorieën die de workflow van een quant intuïtiever weerspiegelen.

* **1\. ContextWorker ("De Cartograaf"):** Rol ongewijzigd. Verrijkt ruwe data tot een bruikbare "kaart".  
* **2\. OpportunityWorker ("De Verkenner"):** Een specialisatie van de voormalige AnalysisWorker. Zijn **enige taak** is het detecteren van *kansen* (technisch, fundamenteel, event-gedreven, etc.).  
* **3\. ThreatWorker ("De Waakhond"):** Een specialisatie van de voormalige MonitorWorker. Zijn **enige taak** is het detecteren van *bedreigingen* (portfolio-, markt-, of systeemrisico's).  
* **4\. PlanningWorker ("De Strateeg"):** Een **nieuwe, cruciale categorie**. Zijn enige taak is het omzetten van een OpportunitySignal in een concreet, uitvoerbaar TradePlan (entry, exit, size, routing).  
* **5\. ExecutionWorker ("De Uitvoerder"):** Rol ongewijzigd, maar nu zuiverder. Voert plannen uit en beheert actieve posities en operationele taken.

De OpportunityWorker en ThreatWorker draaien parallel na de Context-fase, waardoor de Planning- en Execution-fases kunnen reageren op een volledige, 360-graden analyse van de situatie.

## **3\. Kernafwijking \#2: Het Traceability Framework**

Om de "race condities" en complexe interacties in een parallel systeem analyseerbaar te maken, wordt de simpele CorrelationID vervangen door een rijk, causaal framework.

* **TradeID (Het Ankerpunt):** Een unieke ID die wordt gegenereerd bij het initiëren van een trade. Dit is de primaire sleutel die de volledige levenscyclus van een trade identificeert.  
* **Causal IDs (De "Waarom"-ID's):** Deze ID's worden opgeslagen in relatie tot een TradeID in het StrategyJournal en leggen de *reden* voor een actie vast.  
  * **OpportunityID:** Gegenereerd door een OpportunityWorker. Vertegenwoordigt de **reden voor het openen** van een trade.  
  * **ThreatID:** Gegenereerd door een ThreatWorker. Vertegenwoordigt de **reden voor een ingreep** (bv. het sluiten van een trade).  
  * **ScheduledID:** Gegenereerd door de Scheduler. Vertegenwoordigt een **tijd-gedreven reden** voor een actie (bv. DCA, rebalancing).

Dit framework maakt het mogelijk om in de analyse de exacte causale keten van elke trade te reconstrueren ("geopend vanwege kans X, gesloten vanwege bedreiging Y").

## **4\. Kernafwijking \#3: Scheiding van StrategyLedger en StrategyJournal**

Om de SRP te maximaliseren en de performance te optimaliseren, worden de operationele staat en de analytische geschiedenis strikt gescheiden.

* **StrategyLedger (Het "Domme" Grootboek):**  
  * **Verantwoordelijkheid:** Het bijhouden van de **actuele, operationele, veranderlijke staat** van open en gesloten trades.  
  * **Inhoud:** Bevat alleen de strikt noodzakelijke data voor de uitvoering (posities, PnL, actieve stop-loss, etc.). Het bevat **geen** causale ID's. Het is gebouwd voor snelheid.  
* **StrategyJournal (De "Intelligente" Notulist):**  
  * **Verantwoordelijkheid:** Het fungeren als een **onveranderlijk, chronologisch en causaal logboek** van *alle* gebeurtenissen en beslissingen binnen een strategie.  
  * **Inhoud:** Logt niet alleen de trades, maar ook de gedetecteerde kansen, de actieve bedreigingen, en de redenen waarom kansen werden **afgewezen**. Dit is de primaire databron voor de Trade Explorer UI en diepgaande performance-analyse.