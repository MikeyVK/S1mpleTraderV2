# 0_V2_ARCHITECTURE.md

# S1mpleTrader V2: Architectonische Blauwdruk
**Versie:** 2.0 · **Status:** Definitief

---

## Hoofdstuk 1: Visie & Kernprincipes

* **1.1. Visie**
  
  Het creëren van één uniforme, plugin-gedreven architectuur die de volledige levenscyclus van een handelsstrategie ondersteunt: van concept & ontwikkeling, via rigoureuze backtesting en optimalisatie, naar paper trading en uiteindelijk live executie.

* **1.2. Kernprincipes**

  * **Plugin First** Alle strategische en contextuele logica wordt ingekapseld in zelfstandige, ontdekbare en onafhankelijk testbare plugins. Dit is de doorontwikkeling van het Strategy Pattern uit V1: waar V1 een set uitwisselbare “specialisten” had, formaliseert V2 dit tot een gestandaardiseerd ecosysteem.

  * **Scheiding van Zorgen (Separation of Concerns)** Strikte scheiding tussen:
    - **Strategie-logica:** `StrategyEngine` (weet **hoe** de signaal-gedreven fasen (3-6) worden uitgevoerd).
    - **Executie-omgeving:** `ExecutionEnvironment` (weet **waar** het gebeurt — backtest, paper, live).
    - **Assemblage & Bouw:** Het `Assembly Team` (`PluginRegistry`, `WorkerBuilder`, `ContextBuilder`) weet hoe plugins worden beheerd en samengesteld.
    - **Portfolio:** `Portfolio` (weet alleen **wat** de financiële staat is en fungeert als “dom” grootboek).

  * **Configuratie-gedreven (Configuration-driven)** Samenstelling, gedrag en parametrisering van de actieve plugins worden volledig gedefinieerd in **mens-leesbare `YAML`-bestanden**. De code is de motor; **configuratie is de bestuurder**.

  * **Contract-gedreven (Contract-driven)** **Pydantic**-schema’s (en, voor de UI, **TypeScript**-interfaces) definiëren de contracten voor alle configuraties, **DTO**-input/output van plugins en data-uitwisseling tussen lagen. Dit borgt voorspelbaarheid, type-veiligheid en voorkomt runtime-fouten door ongeldige data.

---

## Hoofdstuk 2: Architectuur & Componenten

De architectuur is opgebouwd uit drie strikt gescheiden lagen (Frontend → Service → Backend) en wordt aangestuurd door gespecialiseerde entrypoints (`run_web.py`, `run_supervisor.py`, `run_backtest_cli.py`). Dit hoofdstuk beschrijft de verantwoordelijkheden van elke laag en de hoofdcomponenten zoals de `StrategyOperator`, `ExecutionEnvironment`, en het `Assembly Team`.

**→ Lees de volledige uitwerking in: `docs/system/2_ARCHITECTURE.md`**

---

## Hoofdstuk 3: De Anatomie van een Plugin

Een plugin is een zelfstandige package met eigen logica, contracten (**Pydantic**-modellen), manifest (`plugin_manifest.yaml`) en metadata. Elke plugin declareert zijn `type` (bv. `regime_context`, `signal_generator`, `execution_planner`, etc.), `dependencies`, en Pydantic-gevalideerde `params`.
 
**→ Lees de volledige uitwerking in: `docs/system/3_PLUGIN_ANATOMY.md`**

---

## Hoofdstuk 4: De Quant Workflow: Van Idee tot Inzicht

De kern van de strategie-executie is een systematische, **9-fasen trechter** die een idee valideert en omzet in een `TradeProposal`. Dit hoofdstuk beschrijft elke fase, van `Regime Context` tot de `Critical Event Detector`, en verduidelijkt de rollen van de `StrategyEngine` (de motor) en het `Assembly Team` (de bouwers).

**→ Lees de volledige uitwerking in: `docs/system/4_WORKFLOW_AND_ORCHESTRATOR.md`**

---

## Hoofdstuk 5: Frontend Integratie

De frontend in V2 is de primaire ontwikkelomgeving (IDE) voor de strateeg, ontworpen om de "Bouwen -> Meten -> Leren" cyclus te maximaliseren. Dit hoofdstuk beschrijft hoe de UI zichzelf dynamisch opbouwt op basis van ontdekte plugins en hun schema's. Het detailleert de verschillende "Werkruimtes", van de Strategy Builder tot de Trade Explorer, en legt uit hoe een strikt contract tussen de Pydantic-backend en de TypeScript-frontend zorgt voor een robuuste, naadloze gebruikerservaring.

**→ Lees de volledige uitwerking in: `docs/system/5_FRONTEND_INTEGRATION.md`**

---

## Hoofdstuk 6: Robuustheid & Operationele Betrouwbaarheid

Een live trading-systeem moet veerkrachtig zijn tegen crashes, corrupte data en netwerkproblemen. Dit hoofdstuk beschrijft de drie verdedigingslinies van de architectuur: atomische schrijfacties (journaling) om de integriteit van de staat te garanderen, protocollen voor netwerkveerkracht (heartbeat, reconnect, reconciliation) en een Supervisor-model voor automatische crash recovery.

**→ Lees de volledige uitwerking in: `docs/system/6_RESILIENCE_AND_OPERATIONS.md`**

---

## Hoofdstuk 7: Ontwikkelstrategie & Tooling

De ontwikkelstrategie van V2 is gebaseerd op een snelle, visuele 'Bouwen -> Meten -> Leren' cyclus, met de Web UI als de primaire ontwikkelomgeving (IDE). Dit hoofdstuk beschrijft de workflow, van de visuele 'Strategy Builder' tot de diepgaande 'Trade Explorer'. Daarnaast worden de kern-tools behandeld, zoals de gespecialiseerde entrypoints, de gelaagde logging-aanpak en de cruciale rol van de Correlation ID voor volledige traceerbaarheid van trades.

**→ Lees de volledige uitwerking in: `docs/system/7_DEVELOPMENT_STRATEGY.md`**

---

## Hoofdstuk 8: Meta Workflows

Bovenop de executie van een enkele strategie draaien "Meta Workflows" om geavanceerde analyses uit te voeren. Dit hoofdstuk beschrijft de `OptimizationService` en `VariantTestService`, die de kern-executielogica herhaaldelijk en parallel aanroepen om systematisch de beste parameters te vinden of om de robuustheid van strategie-varianten te testen. Dit maakt complexe kwantitatieve analyse een "eerste klas burger" binnen de architectuur.

**→ Lees de volledige uitwerking in: `docs/system/8_META_WORKFLOWS.md`**

---

## Hoofdstuk 9: Coding Standaarden

Een consistente en kwalitatieve codebase is essentieel. Dit hoofdstuk beschrijft de verplichte standaarden voor het S1mpleTrader V2 project, inclusief PEP 8, volledige type hinting en Google Style Docstrings. Het behandelt de kernprincipes van contract-gedreven ontwikkeling via Pydantic, de gelaagde logging-strategie met Correlation ID voor traceability, en de eis dat alle code vergezeld wordt van tests die via Continue Integratie worden gevalideerd.

**→ Lees de volledige uitwerking in: `docs/system/9_CODING_STANDAARDS.md`**

---

## Bijlages

* **`Bijlage A: Terminologie`**: Een uitgebreid naslagwerk met kernachtige beschrijvingen van alle belangrijke concepten, componenten en patronen binnen de S1mpleTrader V2-architectuur.
* **`Bijlage B: Openstaande Vraagstukken`**: Een overzicht van bekende "onbekenden" en complexe vraagstukken die tijdens de implementatie verder onderzocht moeten worden.

---

# 2_ARCHITECTURE.md

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

+---------------------------------------------------------------------------------------------------------+
|                                    GEBRUIKER (Via Web UI / API)                                         |
|    (Start runs, analyseert resultaten, beheert portfolio)                                               |
+-----------------------------------------------------+---------------------------------------------------+
                                                      |
           +------------------------------------------+------------------------------------------+
           |                                                                                     |
           v                                                                                     v
+----------+----------------------------------+  +------------------------------------------------+------------+
|  OPERATIONELE HIËRARCHIE (SERVICE LAAG)     |  |          R&D / OFFLINE ANALYSE (META WORKFLOWS)             |
|  (Live / Paper Trading)                     |  |                                                             |
|                                             |  |  +---------------------------+                              |
|  +---------------------------------------+  |  |  |   OptimizationService /   |                              |
|  |       PortfolioSupervisor             |  |  |  |    VariantTestService     |                              |
|  |       (De "Fondsbeheerder")           |  |  |  +------------+--------------+                              |
|  +------------------+--------------------+  |  |               | (Analyseert configuratiepad)                |
|                     ^ (5. Events/Directives)|  |               |                                             |
|                     | (naar boven)          |  |  +------------+------------------------------------------+  |
|                     |                       |  |  | Scenario A (Micro/Meso)      |   | Scenario B (Macro) |  |
|  (6. Management Commando's)                 |  |  v                                  v                       |
|  (naar beneden)     v                       |  |  +-------------------------------+  +--------------------+  |
|  +------------------+--------------------+  |  |  | Simuleert 1x StrategyOperator |  | Simuleert 1x       |  |
|  |  StrategyOperator (Specialist) A      |  |  |  +-------------------------------+  | PortfolioSupervisor|  |
|  |  (Voorheen "WorkflowService")         |  |  |                                     +--------------------+  |
|  +---------------------------------------+  |  |                                                             |
|                                             |  +------------------------------------------------+------------+
|  +---------------------------------------+  |
|  |  StrategyOperator (Specialist) B      |  |                      Λ
|  |  (Draait parallel)                    |  |                      |
|  +---------------------------------------+  |                      | (Gebruikt dezelfde Backend componenten)
|                                             |                      |
+--------------------------------------------+----------------------+-------------------------------------+
                                             | (Roept Backend aan)
                                             v
+--------------------------------------------+-------------------------------------------------------------+
|                                        DE FUNDERING (BACKEND LAAG)                                       |
|                    (De herbruikbare, agnostische "Motor" & "Gereedschapskist")                           |
|                                                                                                          |
|  - StrategyEngine (De 9-fasen motor)            - AssemblyTeam (De bouwers: Registry, Builder)           |
|  - ExecutionEnvironments (Backtest/Live/Paper)  - Portfolio (De "domme" boekhouder)                      |
|  - Alle DTO's, Interfaces & Utilities           - DirectiveFlattener (De vertaler)                       |
|                                                                                                          |
+----------------------------------------------------------------------------------------------------------+


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
* **Verantwoordelijkheid:** Definieert de "wereld" (Backtest, Paper, Live) waarin de strategie opereert. Het ontkoppelt de strategie-logica volledig van de data- en executiebronnen.
* **Componenten:**
  * **`DataSource`**: Levert marktdata (uit een CSV-bestand of een live WebSocket).
  * **`Clock`**: Genereert de "hartslag" van het systeem.
  * **`ExecutionHandler`**: Voert `Trade` DTO's uit.

#### **2.4.5. Het Portfolio (Het Grootboek)**
* **Laag:** Backend (`backend/core/portfolio.py`)
* **Verantwoordelijkheid:** Het "domme" grootboek. Managet kapitaal, posities en openstaande orders. Het is volledig agnostisch over de omgeving en wordt geïnitialiseerd met simpele waarden, niet met een config-object.
* **Proces:**
    * Houdt de cash-balans en de totale waarde van het portfolio bij.
    * Registreert openstaande orders en actieve posities per `correlation_id`.
* **Output:** Een continu bijgewerkte equity curve en een lijst van `ClosedTrade` DTO's.

#### **2.4.6. Assembly Team (`PluginRegistry`, `WorkerBuilder`, `ContextBuilder`)**
* **Laag:** Backend
* **Verantwoordelijkheid:** Het "technische projectbureau". Bestaat uit specialisten die plugins ontdekken, valideren, bouwen en de context-pijplijn (Fase 1 & 2) uitvoeren.

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
    * ***V2 voorbeeld:*** Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe `exit_planner`-plugin; de `StrategyEngine` hoeft hiervoor niet aangepast te worden.

* **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.
    * ***V2 voorbeeld:*** De `BacktestService` (Service-laag) hangt af van de `BaseEnvironment`-interface, niet van de specifieke `BacktestEnvironment`. Hierdoor zijn de services volledig herbruikbaar in elke context.

### **Kernpatronen**
* **Factory Pattern:** Het `Assembly Team` (met `WorkerBuilder`) centraliseert het ontdekken, valideren en creëren van alle plugins.
* **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.
* **DTO’s (Data Transfer Objects):** Pydantic-modellen (`Signal`, `TradePlan`, `ClosedTrade`) zorgen voor een voorspelbare en type-veilige dataflow tussen alle componenten.

---

# 3_PLUGIN_ANATOMY.md

# 3. De Anatomie van een V2 Plugin

Dit document beschrijft de gedetailleerde structuur en de technische keuzes achter de plugins in de S1mpleTrader V2 architectuur. Plugins zijn de specialistische, onafhankelijke en testbare bouwstenen van elke strategie.

---
## 3.1. Fundamentele Mappenstructuur

Elke plugin is een opzichzelfstaande Python package. Deze structuur garandeert dat logica, contracten en metadata altijd bij elkaar blijven, wat essentieel is voor het "Plugin First" principe.

Een typische plugin heeft de volgende structuur:

plugins/[plugin_naam]/
├── plugin_manifest.yaml  # De ID-kaart (wie ben ik?)
├── worker.py             # De Logica (wat doe ik?)
├── schema.py             # Het Contract (wat heb ik nodig?)
└── state.json            # (Optioneel) Het Geheugen (wat was mijn vorige staat?)


* `plugin_manifest.yaml`: De "ID-kaart" van de plugin. Dit bestand maakt de plugin vindbaar en begrijpelijk voor de `AbstractPluginFactory`.
* `worker.py`: Bevat de Python-klasse met de daadwerkelijke businesslogica van de plugin.
* `schema.py`: Bevat het Pydantic-model dat de structuur en validatieregels voor de configuratieparameters van de plugin definieert.
* `state.json`: Dit bestand is **optioneel** en wordt alleen gebruikt door 'stateful' plugins (zoals een Grid Trading manager die zijn openstaande orders moet onthouden). De `StrategyOrchestrator` is verantwoordelijk voor het aanroepen van `load_state()` en `save_state()` op de worker, maar de worker zelf beheert de inhoud van dit bestand.

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
## 3.3. Het Manifest: De Zelfbeschrijvende ID-kaart

Het `plugin_manifest.yaml` is de kern van het "plugin discovery" mechanisme. Het stelt de `AbstractPluginFactory` in staat om een plugin volledig te begrijpen, te valideren en correct te categoriseren **zonder de Python-code te hoeven inspecteren**.

Dit manifest is een contract dat de volgende cruciale informatie vastlegt:

* **`name`**: De unieke, machine-leesbare naam van de plugin (bv. `market_structure_detector`).
* **`version`**: Semantische versie (bv. "1.0.1") om dependency management mogelijk te maken.
* **`type`**: De belangrijkste categorie-aanduiding. Dit veld bepaalt in welke van de workflow-fasen van de `StrategyOrchestrator` de plugin thuishoort. Mogelijke waarden zijn:
    * `regime_context`
    * `structural_context`
    * `signal_generator`
    * `signal_refiner`
    * `execution_planner`
    * `exit_planner`
    * `size_planner`
    * `portfolio_overlay`
* **`entry_class`**: De exacte naam van de hoofdklasse in het `worker.py` bestand (bv. `MarketStructureDetector`).
* **`schema_path`**: Het pad naar het Python-bestand dat het Pydantic-schema bevat (meestal `schema.py`).
* **`params_class`**: De exacte naam van de Pydantic-klasse in het `schema.py` bestand (bv. `MarketStructureParams`).
* **`stateful`**: Een boolean (`true` / `false`) die aangeeft of de plugin een `state.json`-bestand gebruikt.
* **`dependencies`**: Een lijst van datavelden die de plugin verwacht als input. Voor een `ContextWorker` is dit een lijst van kolomnamen (bv. `['high', 'low', 'close']`) die aanwezig moeten zijn in de DataFrame. De `AbstractPluginFactory` valideert hierop voordat de plugin wordt uitgevoerd.

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

# 4. De Quant Workflow & Orkestratie

Dit document beschrijft de volledige "data-assemblagelijn" van de S1mpleTrader V2 architectuur. De kern is een gelaagde workflow die een handelsidee systematisch transformeert, valideert en omzet in een uitvoerbaar handelsplan.

---
## 4.1. De Workflow Trechter: Een Praktijkvoorbeeld

       ┌───────────────────────────────────────────┐
       │        RUWE DATAFRAME (OHLCV)             │
       └────────────────────┬──────────────────────┘
                            │
                            v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 1: REGIME CONTEXT (De "Weerman")                            │
│ Plugin: regime_context                                           │
│ Taak:   Voegt macro-context toe (bv. regime='trending').         │
└────────────────────┬─────────────────────────────────────────────┘
│
v
┌───────────────────────────────────────────┐
│   VERRIJKTE DATAFRAME (enriched_df)       │
└────────────────────┬──────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 2: STRUCTURELE CONTEXT (De "Cartograaf")                    │
│ Plugin: structural_context                                       │
│ Taak:   Voegt micro-context toe (bv. is_mss, support_level).     │
└────────────────────┬─────────────────────────────────────────────┘
│
v
┌───────────────────────────────────────────┐
│   FINALE ENRICHED DATAFRAME               │
└────────────────────┬──────────────────────┘
│ (Start StrategyEngine Loop)
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 3: SIGNAAL GENERATIE (De "Verkenner")                       │
│ Plugin: signal_generator                                         │
│ Taak:   Detecteert een specifieke, actiegerichte gebeurtenis.    │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: Signal
│ -------------------------------
│ { correlation_id, timestamp, asset,
│   direction, signal_type }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 4: SIGNAAL VERFIJNING (De "Kwaliteitscontroleur")           │
│ Plugin: signal_refiner                                           │
│ Taak:   Keurt Signal goed of af op basis van secundaire criteria.│
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
│ Taak:   Bepaalt de precieze entry-prijs.                         │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: EntrySignal
│ -------------------------------
│ { correlation_id (gepromoot),
│   signal: Signal (genest),
│   + entry_price }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 6: EXIT PLANNING (De "Strateeg")                            │
│ Plugin: exit_planner                                             │
│ Taak:   Berekent de initiële stop-loss en take-profit.           │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: RiskDefinedSignal
│ -------------------------------
│ { correlation_id (gepromoot),
│   entry_signal: EntrySignal (genest),
│   + sl_price, tp_price }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 7: SIZE PLANNING (De "Logistiek Manager")                   │
│ Plugin: size_planner                                             │
│ Taak:   Berekent de definitieve positiegrootte.                  │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: TradePlan
│ -------------------------------
│ { correlation_id (gepromoot),
│   risk_defined_signal: RiskDefinedSignal (genest),
│   + position_value_quote, position_size_asset }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 8: ORDER ROUTING (De "Verkeersleider")                      │
│ Plugin: order_router                                             │
│ Taak:   Vertaalt het plan naar technische executie-instructies.  │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: RoutedTradePlan
│ -------------------------------
│ { correlation_id (gepromoot),
│   trade_plan: TradePlan (genest),
│   + order_type, time_in_force, ... }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 9: CRITICAL EVENT DETECTION (De "Waakhond")                 │
│ Plugin: critical_event_detector                                  │
│ Taak:   Detecteert systeem-brede risico's (bv. max drawdown).    │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: CriticalEvent
│ -------------------------------
│ { correlation_id, event_type, timestamp }
│
v
┌───────────────────────────────────────────┐
│        FINAAL TRADEPROPOSAL DTO           │
│ { routed_trade_plan?, critical_event? }   │
└────────────────────┬──────────────────────┘
│
v
[ Naar de Workflow Service & ExecutionHandler ]

Elk handelsidee wordt systematisch gevalideerd door een vaste, logische trechter. We volgen een concreet voorbeeld: een **"Market Structure Shift + FVG Entry"** strategie.

#### **Fase 1: Regime Context (De "Weerman")**
* **Doel:** Wat is de algemene "weersverwachting" van de markt? Deze fase classificeert de marktomstandigheid zonder data weg te gooien.
* **Input:** De ruwe `DataFrame` met OHLCV-data.
* **Proces (voorbeeld):** Een `ADXContext`-plugin (`type: regime_context`) berekent de ADX-indicator en voegt een nieuwe kolom `regime` toe. Deze kolom krijgt de waarde 'trending' als `ADX > 25` en 'ranging' als `ADX < 25`.
* **Output:** Een verrijkte `DataFrame`. Er wordt geen data verwijderd; er wordt alleen een contextuele "tag" toegevoegd aan elke rij.

#### **Fase 2: Structurele Context (De "Cartograaf")**
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?
* **Input:** De verrijkte `DataFrame` uit Fase 1.
* **Proces (voorbeeld):** Een `MarketStructureDetector`-plugin (`type: structural_context`) analyseert de prijs en voegt twee nieuwe kolommen toe: `trend_direction` (met waarden als `bullish` of `bearish`) en `is_mss` (een `True`/`False` vlag op de candle waar een Market Structure Shift plaatsvindt).
* **Output:** De finale `enriched_df`. We hebben nu "slimme" data met meerdere lagen context, klaar voor de `StrategyEngine`.

#### **Fase 3: Signaal Generatie (De "Verkenner")**
* **Doel:** Waar is de precieze, actiegerichte trigger? We zoeken naar een Fair Value Gap (FVG) ná een Market Structure Shift.
* **Input:** De `enriched_df` (via het `TradingContext` object).
* **Proces (voorbeeld):** Een `FVGEntryDetector`-plugin (`type: signal_generator`) scant de data. Wanneer het een rij tegenkomt waar `is_mss` `True` is, begint het te zoeken naar een FVG. Als het er een vindt, genereert het een signaal.
* **Output:** Een **`Signal` DTO**. Dit object krijgt een unieke `correlation_id` (UUID) en bevat de essentie: `{asset: 'BTC/EUR', timestamp: '...', direction: 'long', signal_type: 'fvg_entry'}`.

#### **Fase 4: Signaal Verfijning (De "Kwaliteitscontroleur")**
* **Doel:** Is er bevestiging voor het signaal? We willen volume zien bij de FVG-entry.
* **Input:** Het `Signal` DTO en het `TradingContext`.
* **Proces (voorbeeld):** Een `VolumeSpikeRefiner`-plugin (`type: signal_refiner`) controleert het volume op de timestamp van het `Signal`. Als het volume te laag is, wordt het signaal afgekeurd.
* **Output:** Het **gevalideerde `Signal` DTO** of `None`. De `correlation_id` blijft behouden.

#### **Fase 5: Entry Planning (De "Timing Expert")**
* **Doel:** Wat is de precieze entry-prijs voor ons goedgekeurde signaal?
* **Input:** Het gevalideerde `Signal` DTO.
* **Proces (voorbeeld):** Een `LimitEntryPlanner`-plugin (`type: entry_planner`) bepaalt dat de entry een limietorder moet zijn op de 50% retracement van de FVG.
* **Output:** Een **`EntrySignal` DTO**. Dit DTO *nest* het originele `Signal` en verrijkt het met `{ entry_price: 34500.50 }`. De `correlation_id` wordt gepromoot naar het top-level voor gemakkelijke toegang.

#### **Fase 6: Exit Planning (De "Strateeg")**
* **Doel:** Wat is het initiële plan voor risico- en winstmanagement?
* **Input:** Het `EntrySignal` DTO.
* **Proces (voorbeeld):** Een `LiquidityTargetExit`-plugin (`type: exit_planner`) plaatst de stop-loss onder de laatste swing low en de take-profit op de volgende major liquidity high.
* **Output:** Een **`RiskDefinedSignal` DTO**. Nest het `EntrySignal` en voegt `{ sl_price: 34200.0, tp_price: 35100.0 }` toe.

#### **Fase 7: Size Planning (De "Logistiek Manager")**
* **Doel:** Wat is de definitieve positiegrootte, gegeven ons risicoplan en kapitaal?
* **Input:** Het `RiskDefinedSignal` DTO en het `Portfolio` (via `TradingContext`).
* **Proces (voorbeeld):** Een `FixedRiskSizer`-plugin (`type: size_planner`) berekent de positiegrootte zodat het risico (`entry_price - sl_price`) exact 1% van de totale equity van het portfolio is.
* **Output:** Een **`TradePlan` DTO**. Dit DTO nest het `RiskDefinedSignal` en bevat de finale, berekende `{ position_value_quote: 1000.0, position_size_asset: 0.0289 }`. Dit is het complete *strategische* plan.

#### **Fase 8: Order Routing (De "Verkeersleider")**
* **Doel:** Hoe moet dit strategische plan *technisch* worden uitgevoerd?
* **Input:** Het `TradePlan` DTO.
* **Proces (voorbeeld):** Een `DefaultRouter`-plugin (`type: order_router`) vertaalt het plan naar concrete order-instructies.
* **Output:** Een **`RoutedTradePlan` DTO**. Dit nest het `TradePlan` en voegt de *tactische* executie-instructies toe, zoals `{ order_type: 'limit', time_in_force: 'GTC' }`. Dit is de definitieve opdracht voor de `ExecutionHandler`.

#### **Fase 9: Critical Event Detection (De "Waakhond")**
* **Doel:** Zijn er systeem-brede risico's die onmiddellijke actie vereisen, los van nieuwe trades?
* **Input:** De volledige `TradingContext` en de lijst van `RoutedTradePlan`'s.
* **Proces (voorbeeld):** Een `MaxDrawdownDetector`-plugin (`type: critical_event_detector`) controleert de equity curve van het `Portfolio`. Als de drawdown een drempel overschrijdt, genereert het een event.
* **Output:** Een **`CriticalEvent` DTO** (bv. `{ event_type: 'MAX_DRAWDOWN_BREACHED' }`) of `None`.

**Finale Output: Het `TradeProposal` DTO**
De `StrategyEngine` verpakt de outputs van Fase 8 en 9 in één enkel `TradeProposal`-object. Dit object wordt teruggestuurd naar de `Workflow Service`, die het interpreteert en de juiste acties onderneemt (bv. de `RoutedTradePlan` naar de `ExecutionHandler` sturen of de run stoppen bij een `CriticalEvent`).

---
## 4.2. Rolverdeling: De Manager en de Motor

### **De Workflow Service (bv. `BacktestService`) (De Manager)**
Een service zoals de `BacktestService` is de **"manager"** van een enkele run. Hij is de eigenaar van de setup-logica en bereidt de fabriek voor.

* **Plek:** `Service`-laag.
* **Verantwoordelijkheid:** Het end-to-end voorbereiden en starten van een strategie-executie.

#### **Procesflow van de Service:**
1.  **Initialisatie:** Ontvangt de `AppConfig` van de frontend of CLI.
2.  **Bouwfase:** Instantieert alle benodigde, langlevende backend-componenten:
    * De `ExecutionEnvironment` (bv. `BacktestEnvironment`).
    * Het `Portfolio` (geïnitialiseerd met simpele waarden, niet de config).
    * Het `Assembly Team` (`PluginRegistry`, `WorkerBuilder`, `ContextBuilder`).
3.  **Assemblage:** Gebruikt het `Assembly Team` om de `StrategyEngine` te bouwen, en injecteert een "toolbox" met alle benodigde, geïnstantieerde plugin-workers.
4.  **Context Preparatie (Fase 1 & 2):** Roept de `ContextBuilder` aan om de `enriched_df` te genereren.
5.  **Startschot:** Creëert het finale `TradingContext` DTO (met de `enriched_df`, `Portfolio`, etc.) en roept de `run()`-methode van de `StrategyEngine` aan, waarmee de controle wordt overgedragen.

### **De `StrategyEngine` (De Motor)**
De `StrategyEngine` is de **"motor"** van de executie-loop (Fase 3-9). Hij weet niets van de setup, maar is een expert in het efficiënt doorlopen van de signaal-pijplijn.

* **Plek:** `Backend`-laag.
* **Verantwoordelijkheid:** Het uitvoeren van de event-loop, gestuurd door de `Clock`, en het doorlopen van de DTO-trechter van `Signal` tot `TradeProposal`.
* **Procesflow van de Engine:**
    1.  **Start:** De `run()`-methode wordt aangeroepen door de `Service`.
    2.  **Event Loop:** Voor elke `tick` van de `Clock`:
        * Vraagt alle `signal_generator` plugins om een lijst van `Signal` DTO's.
        * Voor elk `Signal`, leidt het door de volledige trechter (Fase 4-8), waarbij elke stap de DTO verder nest en verrijkt via de `BaseWorker`-automatisering.
        * Roept de `critical_event_detector` plugins aan (Fase 9).
        * `yield` elk `TradeProposal` terug naar de `Service`.

### **Het `Assembly Team` (De Technische Projectmanager)**
Het `Assembly Team` (`PluginRegistry`, `WorkerBuilder`, `ContextBuilder`) is het **"technische projectbureau"**. Het weet niets over de fasen, maar is expert in het beheren en bouwen van plugins.

* **Plek:** `Backend`-laag.
* **Verantwoordelijkheid:** Het ontdekken, bouwen en technisch orkestreren van de context-pijplijn.
* **Taken in Detail:**
    * **Plugin Discovery:** Scant de `plugins/`-map en bouwt het `PluginRegistry`.
    * **Worker Constructie:** Bouwt op aanvraag van de `Workflow Service` alle benodigde, gevalideerde plugin-instanties.
    * **Orkestratie van Context:** Voert de `context_pipeline` (Fase 1 & 2) uit.

---
## 4.3. De Feedback Loops: Technisch vs. Strategisch

De architectuur faciliteert twee cruciale cycli:

1.  **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** **een run**. De staat van het `Portfolio` (het "domme" grootboek) wordt via het `TradingContext` object gebruikt als input voor plugins in latere fasen (bv. de `SizePlanner` in Fase 7).
2.  **De Strategische "Supercharged" Ontwikkelcyclus (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** **de runs**, volgens het **"Bouwen -> Meten -> Leren"** principe. Je analyseert de resultaten van een backtest in de Web UI (**Meten**), ontdekt een zwakte (**Leren**), past de `YAML`-configuratie aan in de Strategy Builder (**Bouwen**) en start direct een nieuwe run.

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
    * **Visuele Pijplijn:** Een grafische weergave van de 6-fasen trechter. Elke fase is een "slot" waar een of meerdere plugins in gesleept kunnen worden.
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
* **Backend Interactie:** De UI roept de `StrategyOrchestrator`, `OptimizationService` en `VariantTestService` aan. De resultaten worden opgehaald via de `VisualizationService`, die kant-en-klare "visualisatie-pakketten" (JSON-data voor grafieken en tabellen) levert.

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

    3.  **`StrategyOrchestrator` (met Circuit Breaker):**
        * **Principe:** Als de `LiveDataSource` na een configureerbaar aantal pogingen geen verbinding kan herstellen, moet het systeem in een veilige modus gaan om verdere schade te voorkomen.
        * **Proces:** De `DataSource` stuurt een `CONNECTION_LOST`-event naar de `Orchestrator`. De `Orchestrator` activeert dan de **Circuit Breaker**:
            * Het stopt onmiddellijk met het verwerken van nieuwe signalen.
            * Het stuurt een kritieke alert (via e-mail, Telegram, etc.) naar de gebruiker.
            * Het kan (optioneel) proberen alle open posities te sluiten als laatste redmiddel.

---
## 6.3. Applicatie Crash Recovery (Supervisor Model)

* **Probleem:** Het hoofdproces van de `StrategyOrchestrator` kan crashen door een onverwachte bug in een plugin of een geheugenprobleem.
* **Architectonische Oplossing:** We scheiden het *starten* van de applicatie van de *applicatie zelf* door middel van een **Supervisor (Watchdog)**-proces, aangestuurd door `run_supervisor.py`.

* **Gedetailleerde Workflow:**
    1.  **Entrypoint `run_supervisor.py`:** Dit is het enige script dat je handmatig start in een live-omgeving.
    2.  **Supervisor Proces:** Dit script start een extreem lichtgewicht en robuust "supervisor"-proces. Zijn enige taak is het spawnen van een *kind-proces* voor de daadwerkelijke `StrategyOrchestrator` en het monitoren van dit kind-proces.
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
    3.  De gebruiker sleept plugins naar de "slots" in een visuele weergave van de 6-fasen trechter.
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
* **Integratietests:** Testen de samenwerking tussen de `StrategyOrchestrator` en de `Assembly`-componenten.
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

De `StrategyOrchestrator` is de motor die in staat is om **één enkele** strategie-configuratie uit te voeren. Meta Workflows zijn services in de `Service`-laag die deze motor herhaaldelijk en systematisch aanroepen om complexe, kwantitatieve vragen te beantwoorden.

Ze fungeren als "onderzoekleiders" die de `StrategyOrchestrator` als een werknemer behandelen, en leunen zwaar op de `ParallelRunService` om duizenden backtests efficiënt en parallel uit te voeren. Waar optimalisatie in V1 een ad-hoc script was, wordt het in V2 een **"eerste klas burger"** van de architectuur.

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
    * Elke worker ontvangt één configuratie, start een `StrategyOrchestrator` en voert een volledige backtest uit.

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

# 9_CODING_STANDAARDS.md

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
    * **Principe:** Alle user-facing strings (labels in de UI, rapportages, log-berichten voor de gebruiker) moeten via een internationalisatie-laag lopen, niet hardcoded in de code staan.
    * **Implementatie:** Een centrale `Translator`-klasse laadt `YAML`-bestanden uit de `/locales` map. Code gebruikt vertaalsleutels (bv. `log.backtest.complete`).
    * **Interactie met Logger:** De `Translator` wordt één keer geïnitialiseerd en geïnjecteerd in de `LogFormatter`. De formatter is de enige component binnen het logsysteem die sleutels vertaalt naar leesbare berichten. Componenten die direct output genereren (zoals `Presenters`) krijgen de `Translator` ook apart geïnjecteerd.

* **Configuratie Formaat:** `YAML` is de standaard voor alle door mensen geschreven configuratie. `JSON` wordt gebruikt voor machine-naar-machine data-uitwisseling.


---

# A_BIJLAGE_TEMINOLOGIE.md

# Bijlage A: Terminologie

Dit document dient als een uitgebreid naslagwerk voor alle kerntbegrippen, componenten en patronen binnen de S1mpleTrader V2-architectuur.

**6-Fasen Trechter:** De fundamentele, sequentiële workflow die elk handelsidee valideert (`Regime` -> `Context` -> `Signaal` -> `Verfijning` -> `Constructie` -> `Overlay`).
**Assembly Team:** De conceptuele naam voor de verzameling backend-componenten (`PluginRegistry`, `WorkerBuilder`, `ContextPipelineRunner`) die samen de technische orkestratie van plugins verzorgen.
**Atomic Writes (Journaling):** Het robuuste state-saving mechanisme dat dataverlies bij een crash voorkomt door eerst naar een tijdelijk `.journal`-bestand te schrijven.
**Backend-for-Frontend (BFF):** Een gespecialiseerde API-laag die data levert in het exacte formaat dat de Web UI nodig heeft, wat de frontend-code versimpelt.
**Blueprint (`run_blueprint.yaml`):** Een door de gebruiker gedefinieerd `YAML`-bestand dat een complete strategie-configuratie beschrijft, inclusief alle geselecteerde plugins en hun parameters.
**Circuit Breaker:** Een veiligheidsmechanisme in de `LiveEnvironment` dat, bij aanhoudende netwerkproblemen, de strategie in een veilige modus plaatst.
**Clock:** De component binnen een `ExecutionEnvironment` die de "hartslag" van het systeem genereert, ofwel gesimuleerd (voor backtests) of real-time.
**Configuratie-gedreven:** Het kernprincipe dat het gedrag van de applicatie wordt bestuurd door `YAML`-configuratiebestanden, niet door hardgecodeerde logica.
**Contract-gedreven:** Het kernprincipe dat alle data-uitwisseling wordt gevalideerd door strikte schema's (Pydantic voor de backend, TypeScript voor de frontend).
**Context Pipeline:** De door de `ContextPipelineRunner` beheerde executie van `ContextWorker`-plugins (Fase 1 & 2), die de ruwe marktdata verrijkt tot een `enriched_df`.
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
**Meta Workflows:** Hoog-niveau services (`OptimizationService`, `VariantTestService`) die de `StrategyOrchestrator` herhaaldelijk aanroepen voor complexe analyses.
**OptimizationService:** De service die een grote parameterruimte systematisch doorzoekt door duizenden backtests parallel uit te voeren.
**ParallelRunService:** Een herbruikbare backend-component die het efficiënt managen van een `multiprocessing`-pool voor parallelle backtests verzorgt.
**Plugin:** De fundamentele, zelfstandige en testbare eenheid van logica in het systeem, bestaande uit een `manifest`, `worker` en `schema`.
**PluginRegistry:** De specialistische klasse binnen het `Assembly Team` die verantwoordelijk is voor het scannen van de `plugins/`-map en het valideren van alle manifesten.
**Portfolio:** De backend-component die fungeert als het "domme grootboek" en de financiële staat van het systeem (kapitaal, posities, orders) bijhoudt.
**Pydantic:** De Python-bibliotheek die wordt gebruikt voor datavalidatie en het definiëren van de data-contracten via `BaseModel`-klassen.
**Schema (`schema.py`):** Het bestand binnen een plugin dat het Pydantic-model bevat dat de configuratieparameters van die specifieke plugin definieert en valideert.
**State Reconciliation:** Het cruciale proces na een netwerk-reconnect waarbij de interne `Portfolio`-staat wordt gesynchroniseerd met de 'single source of truth': de exchange.
**Strategy Builder:** De "werkruimte" in de Web UI waar een gebruiker visueel een strategie kan samenstellen door plugins te selecteren en te configureren.
**StrategyOrchestrator:** De "regisseur" in de Service-laag. Deze component is verantwoordelijk voor het uitvoeren van de 6-fasen trechter voor één enkele strategie-configuratie.
**StrategyWorker:** Een type plugin dat wordt gebruikt in de besluitvormingsfases (3-6) van de trechter en die opereert op DTO's in plaats van de `DataFrame`.
**Supervisor Model:** Het crash-recovery mechanisme voor live trading, waarbij een lichtgewicht "watchdog"-proces de `StrategyOrchestrator` monitort en herstart.
**Trade Explorer:** De "werkruimte" in de Web UI die een diepgaande visuele analyse van de trades en de context van een enkele backtest-run mogelijk maakt.
**TypeScript:** De programmeertaal die voor de frontend wordt gebruikt om een type-veilig contract met de Pydantic-backend te garanderen via automatisch gegenereerde interfaces.
**VariantTestService:** De service die een klein, gedefinieerd aantal strategie-varianten "head-to-head" met elkaar vergelijkt onder identieke marktomstandigheden.
**Worker (`worker.py`):** Het bestand binnen een plugin dat de Python-klasse met de daadwerkelijke businesslogica bevat.
**WorkerBuilder:** De specialistische klasse binnen het `Assembly Team` die op aanvraag een geïnstantieerd en gevalideerd `worker`-object bouwt.

---

# B_BIJLAGE_OPENSTAANDE_VRAAGSTUKKEN.md

Bijlage B: Openstaande Vraagstukken & Onderzoekspunten
Dit document bevat een lijst van bekende "onbekenden" en complexe vraagstukken die tijdens de detailimplementatie van de V2-architectuur verder onderzocht en opgelost moeten worden. Ze worden hier vastgelegd om te verzekeren dat ze niet vergeten worden.

B.1. State Management voor Stateful Plugins

Vraagstuk: Hoe persisteren, beheren en herstellen we de staat van stateful plugins (bv. een Grid Trading-strategie die zijn openstaande grid-levels moet onthouden) op een robuuste manier, met name na een applicatiecrash?

Zie ook: docs/system/6_RESILIENCE_AND_OPERATIONS.md

B.2. Data Synchronisatie in Live Omgevingen

Vraagstuk: Hoe gaat de LiveEnvironment om met asynchrone prijs-ticks die voor verschillende assets op verschillende momenten binnenkomen? Moet de orkestratie tick-gedreven zijn (complexer, maar nauwkeuriger) of bar-gedreven (eenvoudiger, maar met mogelijke vertraging)?

B.3. Performance en Geheugengebruik

Vraagstuk: Wat is de meest efficiënte strategie voor het beheren van geheugen bij grootschalige Multi-Time-Frame (MTF) analyses, met name wanneer dit over meerdere assets parallel gebeurt? Hoe voorkomen we onnodige duplicatie van data in het geheugen?

B.4. Debugging en Traceability

Vraagstuk: Welke tools of modi moeten we ontwikkelen om het debuggen van complexe, parallelle runs te faciliteren? Hoe kan een ontwikkelaar eenvoudig de volledige levenscyclus van één specifieke trade volgen (traceability) door alle lagen en plugins heen?

Zie ook: Het concept van een Correlation ID in docs/development/KanBan/product_backlog.csv.

---

