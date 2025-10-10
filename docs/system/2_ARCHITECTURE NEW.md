# **2\. Architectuur & Componenten**

Versie: 4.3 (Gelaagd Portfolio Model \- Compleet)  
Status: Definitief

## **2.1. De Gelaagde Architectuur: Een Strikte Definitie**

De applicatie is opgebouwd uit drie strikt gescheiden lagen die een **eenrichtingsverkeer** van afhankelijkheden afdwingen (Frontend → Service → Backend). Deze scheiding is absoluut en dicteert waar elk component "leeft".

* **Backend Laag (/backend)**: De **"Motor & Gereedschapskist"**. Bevat alle herbruikbare, agnostische bouwstenen (klassen, DTO's, interfaces). Deze laag is volledig onafhankelijk, heeft geen kennis van business workflows, en weet niets van een EventBus. Het is een pure, importeerbare library.  
* **Service Laag (/services)**: De **"Orkestratielaag"**. Dit is de enige laag die de EventBus kent en beheert. Componenten hier orkestreren complete business workflows door de "gereedschappen" uit de Backend-laag aan te roepen in reactie op events.  
* **Frontend Laag (/frontends)**: De **"Gebruikersinterface"**. Verantwoordelijk voor alle gebruikersinteractie. Het communiceert uitsluitend met de Service-laag.

## **2.2. Het Gelaagde Configuratiemodel**

De kracht van S1mpleTrader V2 ligt in een gelaagd configuratiemodel dat een strikte scheiding aanbrengt tussen de *technische omgeving* en de *strategische logica*.

1. **environments.yaml (De Technische Basislaag)**: Dit bestand definieert de beschikbare **ExecutionEnvironments**. Een ExecutionEnvironment is een concrete "wereld" waarin een strategie kan draaien (bv. een live connector\_id of data\_archives voor een backtest).  
2. **portfolio.yaml (De Strategische Toplaag)**: Dit bestand definieert een logisch **Portfolio**. Het is de strategische container die overkoepelende risico-regels bevat en strategieën koppelt aan de ExecutionEnvironment waarin ze moeten draaien.  
3. **run\_blueprint.yaml (De Strategie Definitie)**: Dit bestand definieert de logica van één enkele, herbruikbare strategie.

## **2.3. Component Categorieën: Functionele Groepering**

Om de samenhang te verduidelijken, groeperen we componenten in functionele categorieën. Een terugkerend patroon is een Service-laag "Operator" die een corresponderende Backend-laag "Engine" of "Worker" aanstuurt.

1. **Kernservices (Service Laag)**: De fundamentele, langlevende componenten die het platform orkestreren.  
2. **De Context Pijplijn (Backend & Service Laag)**: De flow voor het stateful opbouwen van de marktcontext.  
3. **De Analytische Pijplijn (Backend & Service Laag)**: Een gespecialiseerde flow voor het genereren van analytische handelsvoorstellen.  
4. **Operationele Agenten (Service Laag)**: Componenten voor deterministische, portfolio-gestuurde taken.  
5. **De Executie Pijplijn (Backend & Service Laag)**: De flow voor het uitvoeren van goedgekeurde trades.  
6. **Bouwstenen (Backend Laag)**: De fundamentele, herbruikbare tools en definities.

## **2.4. Visueel Overzicht: Een Strikte Gelaagde Architectuur**

Dit diagram toont de correcte plaatsing en interactie van de componenten.

\+------------------------------------------------------------------------------------+  
|                                   FRONTEND LAAG                                    |  
\+------------------------------------------+-----------------------------------------+  
                                           | (API Calls naar Service Laag)  
                                           v  
\+====================================================================================+  
|                                     SERVICE LAAG                                   |  
|                          (Eigenaar van EventBus & Workflows)                       |  
|                                                                                    |  
|   \+-----------------------+      \+------------------+      \+-------------------+   |  
|   |  PortfolioSupervisor  |      |  ContextOrch.    |      |  Operationele     |   |  
|   | (leest portfolio.yaml)|      \+------------------+      |      Agenten      |   |  
|   \+-----------------------+                                \+-------------------+   |  
|           ^     |                      ^      |                  ^      |          |  
|           |     | \<Sub/Pub\>            |      | \<Sub/Pub\>        |      | \<Sub/Pub\>|  |  
|      \+----v-----v----------------------v------v------------------v------v--------+ |  
|      |                         DE CENTRALE EVENT BUS                            |   |  
|      \+-------------------^--------------------^--------------------------^-------+   |  
|                          | \<Sub/Pub\>          | \<Sub/Pub\>                |           |  
|                          |                    |                          |           |  
|   \+----------------------v--+      \+----------v-----------+      \+-------v--------+  |  
|   |    StrategyOperator   |      |   ExecutionHandler   |      | RunOrchestrator|  |  
|   \+-------------------------+      \+----------------------+      \+----------------+  |  
|                                                                                    |  
\\+====================================================================================+  
                                           | (gebruikt als library)  
                                           v  
\+------------------------------------------------------------------------------------+  
|                                     BACKEND LAAG                                   |  
|                  (De Gereedschapskist \- Kent de Service Laag NIET)                 |  
|                                                                                    |  
|  \- StrategyEngine (Klasse)    \- StrategyLedger (Klasse)   \- DTO's & Interfaces     |  
|  \- Assembly Team              \- ExecutionEnvironments     \- APIConnectors (Klasses)|  
|  \- (PluginRegistry, etc.)     \- (Backtest, Live, etc.)                             |  
|                                                                                    |  
\\+------------------------------------------------------------------------------------+

## **2.5. Componenten in Detail**

Deze sectie beschrijft de verantwoordelijkheden van elk kerncomponent, gegroepeerd per functionele categorie.

### **Kernservices (Service Laag)**

#### **PortfolioSupervisor (De Operationeel Manager)**

* **Verantwoordelijkheid:** Het actieve, centrale beheer van een logisch Portfolio. Dit is de "directiekamer". Het leest een portfolio.yaml ("Portfolio Blueprint") en is de eigenaar van de levenscyclus van de daarin gedefinieerde ExecutionEnvironments en strategieën. Het beheert de geaggregeerde PnL, past overkoepelende risico-regels toe en keurt StrategyProposalReady-events goed of af.  
* **Backend Gebruik:** Gebruikt een ExecutionEnvironmentFactory (onderdeel van het Assembly Team) om de benodigde ExecutionEnvironment-instanties te bouwen of te hergebruiken.

#### **RunOrchestrator (De Facilitator)**

* **Verantwoordelijkheid:** Een lichtgewicht component, geïnstantieerd *per strategie* door de PortfolioSupervisor. Zijn enige taak is het opzetten van de benodigde specialisten (zoals ContextOrchestrator, StrategyOperator) voor één run, het 'wiren' van de event-abonnementen, en het publiceren van de initiële RunStarted-event.

### **De Context Pijplijn**

#### **ContextBootstrapper (De "Voorgloeier") (Service Laag)**

* **Verantwoordelijkheid:** Zorgt ervoor dat de ContextOrchestrator een complete en historisch correcte staat heeft *voordat* de eerste live tick wordt verwerkt. Dit is cruciaal om te voorkomen dat beslissingen worden genomen op basis van onvolledige data.  
* **Backend Gebruik:** Gebruikt de relevante APIConnector (via de ExecutionEnvironment) om een bulk historische data op te halen.

#### **ContextOrchestrator (De State Manager) (Service Laag)**

* **Verantwoordelijkheid:** Het stateful hart van een actieve run. Beheert de "levende" TradingContext. Abonneert zich op MarketDataReceived en publiceert een verrijkte ContextReady voor elke tick.  
* **Backend Gebruik:** Gebruikt de ContextBuilder en het Assembly Team (met name de WorkerBuilder) om de Fase 1-2 ContextWorker\-plugins uit te voeren.

### **De Analytische Pijplijn**

#### **StrategyOperator (De Analytische Specialist) (Service Laag)**

* **Verantwoordelijkheid:** De brug tussen de context- en de analyse-fase. Het abonneert zich op ContextReady, roept procedureel de run()-methode van de StrategyEngine aan, en publiceert het resultaat als een StrategyProposalReady-event.  
* **Backend Gebruik:** Gebruikt een instantie van de StrategyEngine en roept diens run()-methode aan.

#### **StrategyEngine (De Analytische Motor) (Backend Laag)**

* **Verantwoordelijkheid:** De stateless, procedurele 9-fasen motor voor het genereren van analytische voorstellen. Het opereert op de TradingContext en produceert een EngineCycleResult, volledig agnostisch van de event-bus.

### **Operationele Agenten (Service Laag)**

#### **GridTraderAgent, RebalancerAgent, etc.**

* **Verantwoordelijkheid:** Het uitvoeren van deterministische, op regels gebaseerde, stateful taken die buiten de analytische pijplijn vallen (bv. grid trading, DCA, portfolio herbalancering). Ze worden beheerd door de PortfolioSupervisor.  
* **Backend Gebruik:** Lezen LedgerState DTO's om hun beslissingen te informeren.

### **De Executie Pijplijn**

#### **ExecutionHandler (De Uitvoerder) (Service Laag)**

* **Verantwoordelijkheid:** Luistert naar ExecutionApproved-events. Het is de brug naar de buitenwereld voor het uitvoeren van een trade.  
* **Backend Gebruik:** Roept de methodes aan op het StrategyLedger (in backtest) of de juiste APIConnector (in live/paper). **Cruciaal**: na een succesvolle executie publiceert de ExecutionHandler een LedgerStateChanged-event.

#### **ExecutionEnvironments & APIConnectors (Backend Laag)**

* **Verantwoordelijkheid:** ExecutionEnvironments zijn de dataleveranciers die MarketDataReceived-events produceren. APIConnectors zijn de "stekkers" die de specifieke logica bevatten om met een exchange te communiceren.

### **Bouwstenen (Backend Laag)**

#### **StrategyLedger (Het Grootboek)**

* **Verantwoordelijkheid:** Het "domme", agnostische grootboek voor **één specifieke strategie-run**. Het managet kapitaal (indien gesimuleerd), posities en openstaande orders voor die ene run. Het wordt gemuteerd door de ExecutionHandler en heeft zelf geen kennis van de EventBus.

#### **Assembly Team (PluginRegistry, WorkerBuilder, ContextBuilder, ConnectorFactory)**

* **Verantwoordelijkheid:** Het "technische projectbureau" dat op aanvraag van de Service-laag alle benodigde componenten ontdekt, valideert en bouwt (zowel plugins als connectoren).