# **X. Frontend Integratie: De UI als Intelligente IDE**

Versie: 2.1 (Details Hersteld)  
Status: Definitief  
Dit document beschrijft de volledige gebruikersworkflow en de frontend-architectuur die nodig is om de "supercharged" V2-ervaring te realiseren. Het vertaalt de architectonische blauwdruk naar een concreet, gebruikersgericht plan.

## **X.1. De Filosofie: De UI als IDE**

De kern van de V2-frontendstrategie is een paradigmaverschuiving: de web-UI is niet langer een simpele presentatielaag, maar de **primaire, geïntegreerde ontwikkelomgeving (IDE)** voor de kwantitatieve strateeg. Elke stap in de workflow, van het beheren van operaties tot het diepgaand analyseren van resultaten, vindt plaats binnen een naadloze, interactieve webapplicatie.

Dit maximaliseert de efficiëntie en verkort de **"Bouwen \-\> Meten \-\> Leren"**\-cyclus van dagen of uren naar minuten.

## **X.2. De Werkruimtes: Een Context-Bewuste Workflow**

De hoofdnavigatie van de applicatie wordt gevormd door een reeks "werkruimtes". De workflow is hiërarchisch en context-bewust, beginnend bij de Operation.

| **OPERATION MANAGEMENT** | **STRATEGY BUILDER** | **BACKTESTING & ANALYSIS** | **LIVE MONITORING** | **PLUGIN DEVELOPMENT** |

## **X.3. De "Top-Down" Configuratie Flow**

De gebruiker wordt door een logische, gelaagde wizard geleid die frictie minimaliseert en contextuele hulp biedt op basis van de gemaakte keuzes.

### **Fase 1: Werkruimte "OPERATION MANAGEMENT" (Het Fundament)**

Dit is het onbetwiste startpunt voor elke activiteit. Een Operation definieert de "wereld" waarin strategieën opereren.

* **User Goal:** Het definiëren en beheren van de overkoepelende "draaiboeken" (operation.yaml) voor backtesting, paper trading en live trading.  
* **UI Componenten:**  
  1. **Operations Hub:** Een dashboard met een overzicht van alle geconfigureerde operaties (mijn\_btc\_operatie.yaml, live\_eth\_dca.yaml, etc.).  
  2. **Operation Creatie Wizard:** Een wizard die de gebruiker helpt een nieuw operation.yaml te configureren door hem door de velden te leiden.  
     * **Stap 1: Koppel Blueprints aan Werelden:** De gebruiker creëert strategy\_links door een strategy\_blueprint\_id te selecteren uit de bibliotheek en deze te koppelen aan een execution\_environment\_id (die op hun beurt weer gedefinieerd zijn in environments.yaml).  
     * **Stap 2: Activeer Strategieën:** De gebruiker stelt per strategy\_link in of deze is\_active is.  
* **Vanuit dit dashboard** kan de gebruiker doorklikken om de strategieën binnen een operatie te beheren of een nieuwe strategie (strategy\_blueprint.yaml) te creëren.

### **Fase 2: Werkruimte "STRATEGY BUILDER" (Context-Bewust Bouwen)**

Deze werkruimte wordt **altijd gestart vanuit de context van een specifieke Operation**. De wizard is nu "slim" en zich bewust van de grenzen en mogelijkheden die door de gekoppelde ExecutionEnvironments worden gedefinieerd.

* **User Goal:** Het intuïtief en foutloos samenstellen van een strategie-blueprint (strategy\_blueprint.yaml) die gegarandeerd kan draaien binnen de geselecteerde "wereld".  
* **UI Componenten:**  
  1. **Data Selectie:** De wizard toont alleen de handelsparen en timeframes die beschikbaar zijn binnen de ExecutionEnvironment(s) van de actieve Operation.  
  2. **Visuele Workforce met Gefilterde Bibliotheek:** De gebruiker sleept plugins naar de workforce-secties (gegroepeerd per type: ContextWorkers, AnalysisWorkers, etc.). De plugin-bibliotheek is **dynamisch gefilterd**. Een plugin die rijke orderboek-data *vereist* (requires\_context), wordt grijs weergegeven (uitgeschakeld) als de actieve Operation geen ExecutionEnvironment heeft die deze data levert. Een tooltip legt uit waarom.  
  3. **Configuratie Paneel:** Wanneer een plugin wordt geplaatst, verschijnt er een paneel met een **automatisch gegenereerd formulier** op basis van de schema.py van de plugin.  
  4. **Intelligent Timeframe Management:** Als een plugin een ander timeframe nodig heeft dan het execution\_timeframe, detecteert de wizard dit en biedt de optie om de benodigde data vooraf te genereren (resamplen) of live te berekenen.  
* **Backend Interactie:** De UI haalt de gefilterde lijst plugins op via een PluginQueryService. Bij het opslaan stuurt de UI een JSON-representatie van de strategie naar een StrategyBlueprintEditorService, die het als een strategy\_blueprint.yaml-bestand wegschrijft.

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
  * Een prominente **"Noodstop"-knop** per strategy\_link of voor de hele Operation, die een ShutdownRequested-event publiceert.  
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