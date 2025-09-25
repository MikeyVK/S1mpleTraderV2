# 2. Architectuur & Componenten

De applicatie is opgebouwd uit drie strikt gescheiden lagen die een **eenrichtingsverkeer** van afhankelijkheden afdwingen (`Frontend → Service → Backend`). Deze structuur ontkoppelt de lagen, maximaliseert de testbaarheid en garandeert de herbruikbaarheid van de `Backend`-laag als een onafhankelijke "engine".

---
## 2.1. De Gelaagde Architectuur

* **Frontend Laag (`/frontends`)**
    Verantwoordelijk voor alle gebruikersinteractie (CLI, Web API, Web UI). Vertaalt gebruikersinput naar aanroepen van de **Service**-laag en presenteert de resultaten.

* **Service Laag (`/services`)**
    Fungeert als de **lijm** en orkestreert Backend-componenten tot complete **business workflows**. Hier leven de `StrategyOrchestrator` en de **Meta-Wrappers** (`OptimizationService`, `VariantTestService`).

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
    |  - StrategyOrchestrator, OptimizationService, VariantTest   |
    +--------------------------+----------------------------------+
                               |
                               v
    +--------------------------+----------------------------------+
    |  Backend (Engine)                                          |
    |  - Portfolio, ExecutionEnvironments, AbstractPluginFactory  |
    +-------------------------------------------------------------+
    ```
   
---

## 2.2. Visueel diagram (uitwerking)

  ```
            [ Gebruiker start via CLI met `mode:` ]
                             │
                             ▼
        ┌───────────────────────────────────────────┐
        │          APPLICATIE ENTRYPOINT            │
        └────────────────────┬──────────────────────┘
                             │
    ┌────────────────────────┴────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
  [ Meta-Wrapper ]     [ StrategyOrchestrator ]     [ StrategyOrchestrator ]
  ├── Optimization         (Draait de 6 Fases)      (Draait de 6 Fases)
  └── VariantTest                │                        │
     │                           │                        │
     └─> (roept vele malen aan)  │                        │
                                 ▼                        ▼
  ┌────────────────────[ ExecutionEnvironment ]───────────────────────────────┐
  │       (Bepaalt WAAR data vandaan komt en WAAR orders heengaan)            │
  ├──────────────────────────┬───────────────────────┬────────────────────────┤
  │ BacktestEnvironment      │ PaperTradeEnvironment │ LiveEnvironment        │
  ├──────────────────────────┼───────────────────────┼────────────────────────┤
  │ DataSource: CSV          │ DataSource: WebSocket │ DataSource: WebSocket  │
  │ Clock:      Simulated    │ Clock:      Real-time │ Clock:      Real-time  │
  │ ExecHandler: Simulator   │ ExecHandler: Simulator│ ExecHandler: API-Calls │
  └──────────────────────────┴───────────────────────┴────────────────────────┘
  │
  │ (Beheert de staat van)
  ▼
  ┌────────────────────[ Portfolio ]────────────────────────────────────┐
  │ (Centraal Grootboek: Kapitaal, Posities per strategie, Open Orders) │
  └──────────────────────────┬──────────────────────────────────────────┘
  │
  │ (Wordt gevoed door en bevraagd door overlays)
  ▼
  ┌────────────────────[ AbstractPluginFactory ]────────────────────┐
  │  Team van specialisten: `PluginRegistry`, `WorkerBuilder`,      │
  │  `ContextPipelineRunner`                                        │
  │  (Ontdekt, valideert, bouwt en orkestreert alle plugins)        │
  └──────────────────────────┬──────────────────────────────────────┘
                             │
                             │ (Maakt gebruik van)
                             ▼
  ┌────────────────────[ Plugins (*_worker.py) ]────────────────────┐
  │   (gecategoriseerd op `type` in `plugin_manifest.yaml`)          │
  └─────────────────────────────────────────────────────────────────┘
  ```

## 2.3. Gespecialiseerde Entrypoints

De V2-architectuur stapt af van één generieke `main.py` en introduceert doelgerichte starters in de project root:

* **`run_web.py`**: Start de Web UI en de bijbehorende API. Dit is de primaire interface voor strategie-ontwikkeling, analyse en monitoring.
* **`run_supervisor.py`**: Start de live trading-omgeving op een robuuste, minimalistische manier (de "aan"-knop).
* **`run_backtest_cli.py`**: Dient als "headless" entrypoint voor geautomatiseerde taken zoals regressietesten en CI/CD-workflows.

---
## 2.4. Componenten in Detail

Hieronder volgt een gedetailleerde beschrijving van elk hoofdcomponent.

#### **2.4.1. Meta-Wrappers**
* **Laag:** Service (bv. `services/optimization_service.py`)
* **Verantwoordelijkheid:** Beheert complexe workflows die de `StrategyOrchestrator` herhaaldelijk aanroepen.
* **Voorbeelden en Proces:**
    * De **`OptimizationService`** genereert een grote set van configuratie-varianten en gebruikt een `ParallelRunService` om voor elke variant een backtest te draaien.
    * De **`VariantTestService`** voert een kleine, gedefinieerde set van varianten parallel uit om de prestaties onder identieke omstandigheden direct te vergelijken.
* **Output:** Een verzameling van `BacktestResult` objecten, klaar voor analyse en presentatie.

#### **2.4.2. StrategyOrchestrator**
* **Laag:** Service
* **Verantwoordelijkheid:** De "regisseur". Voert de volledige 6-fasen trechter uit voor **één enkele** strategie-configuratie binnen één specifieke omgeving. Het component is agnostisch over de omgeving; het weet niet of het een backtest, paper of live trade is.
* **Input:** Een `AppConfig` object en een geïnitialiseerd `ExecutionEnvironment` object.

#### **2.4.3. ExecutionEnvironment**
* **Laag:** Backend
* **Verantwoordelijkheid:** Definieert de "wereld" (Backtest, Paper, Live) waarin de strategie opereert. Het ontkoppelt de strategie-logica volledig van de data- en executiebronnen.
* **Componenten:**
    * **`DataSource`**: Levert marktdata (uit een CSV-bestand of een live WebSocket).
    * **`Clock`**: Genereert de "hartslag" van het systeem (simuleert tijd in een backtest, volgt de echte tijd live).
    * **`ExecutionHandler`**: Voert `Trade` DTO's uit (simuleert fills in het `Portfolio` of stuurt echte orders naar een exchange API).

#### **2.4.4. Portfolio**
* **Laag:** Backend (`backend/core/portfolio.py`)
* **Verantwoordelijkheid:** Het "domme" grootboek. Managet kapitaal, posities en openstaande orders.
* **Proces:**
    * Houdt de cash-balans en de totale waarde van het portfolio bij.
    * Registreert openstaande orders en actieve posities per `strategy_id`.
* **Output:** Een continu bijgewerkte equity curve en een lijst van `ClosedTrade` DTO's.

#### **2.4.5. Assembly Team (`AbstractPluginFactory`)**
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
    * ***V2 voorbeeld:*** Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe `trade_constructor`-plugin; de `StrategyOrchestrator` hoeft hiervoor niet aangepast te worden.

* **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.
    * ***V2 voorbeeld:*** De `StrategyOrchestrator` hangt af van de `BaseEnvironment`-interface, niet van de specifieke `BacktestEnvironment`. Hierdoor is de orchestrator volledig herbruikbaar in elke context.

### **Kernpatronen**
* **Factory Pattern:** De `AbstractPluginFactory` centraliseert het ontdekken, valideren en creëren van alle plugins op basis van hun `plugin_manifest.yaml`.
* **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.
* **DTO’s (Data Transfer Objects):** Pydantic-modellen (`Signal`, `Trade`, `ClosedTrade`) zorgen voor een voorspelbare en type-veilige dataflow tussen alle componenten.