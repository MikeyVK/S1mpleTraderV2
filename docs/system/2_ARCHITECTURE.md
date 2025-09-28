# 2. Architectuur & Componenten

De applicatie is opgebouwd uit drie strikt gescheiden lagen die een **eenrichtingsverkeer** van afhankelijkheden afdwingen (`Frontend → Service → Backend`). Deze structuur ontkoppelt de lagen, maximaliseert de testbaarheid en garandeert de herbruikbaarheid van de `Backend`-laag als een onafhankelijke "engine".

---
## 2.1. De Gelaagde Architectuur

* **Frontend Laag (`/frontends`)**
    Verantwoordelijk voor alle gebruikersinteractie (CLI, Web API, Web UI). Vertaalt gebruikersinput naar aanroepen van de **Service**-laag en presenteert de resultaten.

* **Service Laag (`/services`)**
    Fungeert als de **lijm** en orkestreert Backend-componenten tot complete **business workflows**. Hier leven de `StrategyOperator`, `PortfolioSupervisor` en de **Analytische Services** (`OptimizationService`, `VariantTestService`).

* **Backend Laag (`/backend`)**
    De **engine** van de applicatie. Bevat de `AbstractPluginFactory specialisten`, het `Portfolio` en de `ExecutionEnvironments`. Deze laag is volledig onafhankelijk en ontworpen als een **library**.

* **ASCII-overzicht**
    ```
    +-------------------------------------------------------------+
    |  Frontend (CLI, Web API, Web UI)                            |
    +--------------------------+----------------------------------+
                               |
                               v
    +--------------------------+----------------------------------+
    |  Service (Orchestratie & Business Workflows)                |
    |  - PortfolioSupervisor, StrategyOperator,                   |
    |     OptimizationService, VariantTestService                 |
    +--------------------------+----------------------------------+
                               |
                               v
    +--------------------------+----------------------------------+
    |  Backend (Engine)                                           |
    |  - Portfolio, ExecutionEnvironments, Assembly Workers       |
    +-------------------------------------------------------------+
    ```
   
---

## 2.2. Visueel diagram (uitwerking)

+--------------------------------------------------------------------------------------------------+
|                                         FRONTEND LAAG                                            |
|                  (Web UI / CLI - De "Marketing & Communicatie" afdeling)                         |
└─────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                              │
           ┌──────────────────────────────────┴──────────────────────────────────┐
           │ Roept de juiste specialist aan voor de gevraagde dienst...          │
           v                                                                     v
+----------┴---------------------------------------------------------------------┴-----------------+
|                                          SERVICE LAAG                                            |
| (De "Gereedschapskist" met onafhankelijke specialisten, elk met een eigen taak)                  |
| ┌───────────────────────────────┐                                                                |
| │   Configuratie & Management   │                                                                |
| │      (De Archivarissen)       │                                                                |
| │-------------------------------|                                                                |
| │ - BlueprintQueryService       │                                                                |
| │ - BlueprintEditorService      │                                                                |
| │ - PluginEnrollmentService     │                                                                |
| └───────────────────────────────┘                                                                |
| ┌──────────────────────────┐      ┌───────────────────────────────┐                              |
| │   Analytische Services   │      │    WORKFLOW SERVICES          │                              |
| │     (De Onderzoekers)    │      │  (De Fabrieksmanagers)        │                              |
| │--------------------------│      │-------------------------------│                              |
| │ - OptimizationService    ├─────>│ - BacktestService             │                              |
| │ - VariantTestService     │      │ - TradingService (paper/live) │                              |
| └───────────┬──────────────┘      └────────────┬──────────────────┘                              |
|             │(roept herhaaldelijk aan)         │ 1. Ontvangt AppConfig                           |
|             │                                  │ 2. Bouwt de Environment                         |
|             └────────────────────────────────> │ 3. Instantieert                                 |
|                                                │    PortfolioSupervisor                          |
|                                                └────────────┬────────────┘                       |
|                                                             │                                    |
|                                                             v                                    |
|                           ┌─────────────────────────────────────────────────────────┐            |
|                           │                  OPERATIONELE SERVICES                  │            |
|                           │                      (De Operators)                     │            |
|                           │---------------------------------------------------------│            |
|                           │                PortfolioSupervisor                      │            |
|                           │        (De Ploegleider, stuurt de werkvloer aan)        │            |
|                           └─────────────────────────────┬───────────────────────────┘            |
|                                                         │ Managet een of meerdere...             |
|                                                         v                                        |
|                           ┌─────────────────────────────┴───────────────────────────┐            |
|                           │                   StrategyOperator(s)                   │            |
|                           │          (De Specialist, voert de 6 Fases uit)          │            |
|                           └─────────────────────────────────────────────────────────┘            |
+------------------------------------------------------------------------------------|-------------+
                                                                                     │
                  ┌───────────────────────────────────────────────────────────────────────────────┤
                  │ (De Operationele Services krijgen de Environment geïnjecteerd en gebruiken de │
                  │  Backend-componenten om hun taak uit te voeren)                               │
                  v                                                                               v
+-----------------┴------------------------------------------[ BACKEND LAAG (DE "ENGINE") ]-------┴-------------+
|                                                                                                               |
|   ┌──────────────────────┐   wordt gebruikt door   ┌──────────────────────┐                                   |
|   │     Assembly Team    │<────────────────────────┤   StrategyOperator   │                                   |
|   │ (Plugin Specialisten)│                         └──────────────────────┘                                   |
|   └──────────┬───────────┘                                                                                    |
|              │ Gebruikt                                                                                       |
|              v                                                                                                |
|   ┌──────────┴──────────┐                                                                                     |
|   │       Plugins       │                                                                                     |
|   └─────────────────────┘                                                                                     |
|                                                                                                               |
|   ┌──────────────────────┐   wordt gelezen door   ┌──────────────────────┐                                    |
|   │      Portfolio       │<───────────────────────┤  PortfolioSupervisor │                                    |
|   │   (Het Grootboek)    │                        └──────────────────────┘                                    |
|   └──────────▲───────────┘                                                                                    |
|              │ Werkt bij                                                                                      |
|   ┌──────────┴───────────┐                                                                                    |
|   │ ExecutionEnvironment │ (Bevat de ExecutionHandler die het Portfolio bijwerkt)                             |
|   │    (Het Chassis)     │                                                                                    |
|   └──────────────────────┘                                                                                    |
|                                                                                                               |
+---------------------------------------------------------------------------------------------------------------+
---
## 2.3. Gespecialiseerde Entrypoints

De V2-architectuur stapt af van één generieke `main.py` en introduceert doelgerichte starters in de project root:

* **`run_web.py`**: Start de Web UI en de bijbehorende API. Dit is de primaire interface voor strategie-ontwikkeling, analyse en monitoring.
* **`run_supervisor.py`**: Start de live trading-omgeving op een robuuste, minimalistische manier (de "aan"-knop). Deze entrypoint is ontworpen om de `PortfolioSupervisor` te starten voor het managen van een live portfolio.
* **`run_backtest_cli.py`**: Dient als "headless" entrypoint voor geautomatiseerde taken. Deze kan elke service aanroepen, van een simpele `StrategyOperator` tot een complexe `OptimizationService` voor CI/CD-workflows.

---
## 2.4. Componenten in Detail: De Service Laag Hiërarchie

De Service-laag is geen verzameling losse componenten, maar een gestructureerde hiërarchie van "Operators" en "Services" met duidelijk afgebakende verantwoordelijkheden. De `ExecutionEnvironment` fungeert hierbij als de cruciale schakelaar die bepaalt of een operator in een Backtest-, Paper- of Live-modus draait.

#### **2.4.1. Niveau 1: De StrategyOperator (De Specialist)**
* **Laag:** Service
* **Verantwoordelijkheid:** Het uitvoeren van één enkele strategie (de 6-fasen trechter) voor één instrument. Dit is wat voorheen de `StrategyOrchestrator` werd genoemd; de nieuwe naam benadrukt zijn actieve, operationele rol.
* **Proces:** De `StrategyOperator` is de "regisseur" van de 6-fasen trechter. Hij is volledig agnostisch over de omgeving; hij ontvangt een geïnitialiseerde `ExecutionEnvironment` en weet niet of hij een backtest of een live trade uitvoert.

#### **2.4.2. Niveau 2: De PortfolioSupervisor (De Ploegleider)**
* **Laag:** Service
* **Verantwoordelijkheid:** Het managen van de levenscyclus en het risico van een portfolio van meerdere, gelijktijdig actieve `StrategyOperator`-instanties.
* **Proces:**
  * Leest een `portfolio_blueprint.yaml` die definieert welke strategieën (en dus `StrategyOperators`) actief zijn.
  * Ontvangt "trade-voorstellen" van de individuele `StrategyOperators`.
  * Past overkoepelend, portfolio-breed risicomanagement toe (bv. "maximale totale exposure").
  * Alleen goedgekeurde trade-voorstellen worden doorgestuurd naar de `ExecutionHandler` van de gedeelde `ExecutionEnvironment`.
* **Belang:** Deze component kan, net als elke andere operator, worden uitgevoerd in een `BacktestEnvironment` om een volledige, complexe portfolio-strategie tegen historische data te testen.

#### **2.4.3. Niveau 3: Analytische Services (De Onderzoekers)**
* **Laag:** Service (bv. `services/optimization_service.py`)
* **Verantwoordelijkheid:** Het uitvoeren van grootschalige, analytische experimenten om kwantitatieve vragen te beantwoorden.
* **Voorbeelden en Proces:**
  * De **`OptimizationService`** genereert een grote set van configuratie-varianten. Via een volledig gekwalificeerd pad (bv. `"workforce.structural_context.my_plugin.params.length"`) weet het precies welke parameter het moet aanpassen, of dit nu een diepe plugin-parameter is of een hoog-niveau risico-parameter in de `PortfolioSupervisor`.
  * De **`VariantTestService`** voert een kleine, gedefinieerde set van varianten uit om de prestaties direct te vergelijken.
* **Executie:** Deze services zijn de enige componenten die de `ParallelRunService` aanroepen om hun experimenten (die een `StrategyOperator` of zelfs een hele `PortfolioSupervisor` kunnen aanroepen) efficiënt en parallel uit te voeren.

#### **2.4.4. De ExecutionEnvironment (Het Chassis / De Wereld)**
* **Laag:** Backend
* **Verantwoordelijkheid:** Definieert de "wereld" (Backtest, Paper, Live) waarin een Operator of Supervisor opereert. Dit is de cruciale abstractielaag die de strategie-logica volledig ontkoppelt van de data- en executiebronnen.
* **Componenten:**
  * **`DataSource`**: Levert marktdata (uit een CSV-bestand of een live WebSocket).
  * **`Clock`**: Genereert de "hartslag" van het systeem.
  * **`ExecutionHandler`**: Voert `Trade` DTO's uit.

#### **2.4.5. Het Portfolio (Het Grootboek)**
* **Laag:** Backend (`backend/core/portfolio.py`)
* **Verantwoordelijkheid:** Het "domme" grootboek. Managet kapitaal, posities en openstaande orders. Het wordt gedeeld en bijgewerkt door de `ExecutionHandler`, en gelezen door de `PortfolioSupervisor` voor risicobeslissingen.* **Proces:**
    * Houdt de cash-balans en de totale waarde van het portfolio bij.
    * Registreert openstaande orders en actieve posities per `strategy_id`.
* **Output:** Een continu bijgewerkte equity curve en een lijst van `ClosedTrade` DTO's.

#### **2.4.6. Assembly Team (`AbstractPluginFactory`)**
* **Laag:** Backend/Assembly
* **Verantwoordelijkheid:** Het "technische projectbureau". Bestaat uit de `PluginRegistry`, `WorkerBuilder`, en `ContextPipelineRunner`. Ontdekt, valideert, bouwt en orkestreert de technische executie van plugins.

---
## 2.5. Design Principles & Kernconcepten

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
  * ***V2 voorbeeld:*** Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe `trade_constructor`-plugin; de `StrategyOperator` (de regisseur van de pipeline) hoeft hiervoor niet aangepast te worden.

* **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.
  * ***V2 voorbeeld:*** De `StrategyOperator` en `PortfolioSupervisor` hangen af van de `BaseEnvironment`-interface, niet van de specifieke `BacktestEnvironment`. Hierdoor zijn de Service-laag componenten volledig herbruikbaar in elke context.

### **Kernpatronen**
* **Factory Pattern:** De `AbstractPluginFactory` centraliseert het ontdekken, valideren en creëren van alle plugins op basis van hun `plugin_manifest.yaml`.
* **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.
* **DTO’s (Data Transfer Objects):** Pydantic-modellen (`Signal`, `Trade`, `ClosedTrade`) zorgen voor een voorspelbare en type-veil