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