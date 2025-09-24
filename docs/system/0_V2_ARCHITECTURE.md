# S1mpleTrader V2: Architectonische Blauwdruk

## Hoofdstuk 1: Visie & Kernprincipes

* **1.1. Visie:** Het creëren van één uniforme, plugin-gedreven architectuur die de volledige levenscyclus van een strategie ondersteunt: van ontwikkeling en backtesting tot paper trading en live executie.

* **1.2. Kernprincipes:**
    * **Plugin First:** Alle strategische en contextuele logica wordt ingekapseld in zelfstandige, ontdekbare plugins.
    * **Scheiding van Zorgen:** Strikte scheiding tussen strategie-logica (`StrategyOrchestrator`), de executie-omgeving (`ExecutionEnvironment`), en het beheer van de staat (`Portfolio`).
    * **Configuratie-gedreven:** De samenstelling en het gedrag van de `Orchestrator` en plugins wordt volledig gedefinieerd in `YAML`-bestanden.
    * **Contract-gedreven:** Pydantic-schema's en TypeScript-interfaces definiëren de "contracten" voor alle configuraties, data-uitwisseling en de input/output van plugins.

## Hoofdstuk 2: De Gelaagde Architectuur (Overzicht)

De applicatie is opgebouwd uit drie strikt gescheiden lagen die een **eenrichtingsverkeer** van afhankelijkheden afdwingen (`Frontend -> Service -> Backend`). Deze structuur ontkoppelt de lagen en garandeert de herbruikbaarheid van de `Backend`.

* **2.1. Hoofdcomponenten & Lagen:**
    * **Frontend Laag (`/frontends`):** Verantwoordelijk voor alle gebruikersinteractie (CLI, Web API). Deze laag vertaalt gebruikersinput naar aanroepen van de `Service` laag en presenteert de resultaten. [cite_start]Het volgt een Model-View-Presenter (MVP) patroon, waarbij de `_app.py` de `Controller` is, de `Service` het `Model`, en de `Presenter` de `View` die de output formatteert[cite: 1155].
    * [cite_start]**Service Laag (`/services`):** Fungeert als de "lijm" en orkestreert de `Backend` componenten om complete business workflows uit te voeren[cite: 1154]. Dit is de laag waar de `StrategyOrchestrator` en de `Meta-Wrappers` (`OptimizationWrapper`, `VariantTestWrapper`) leven. [cite_start]Services worden geïnitialiseerd en doorgegeven via Dependency Injection[cite: 1185].
    * **Backend Laag (`/backend`):** De motor van de applicatie. Het bevat de `AbstractPluginFactory`, de `Portfolio`, en de `ExecutionEnvironments`. [cite_start]Deze laag is volledig onafhankelijk en ontworpen als een library[cite: 1155, 1184]. [cite_start]Het hanteert het Strategy Pattern, waarbij componenten uitwisselbare "strategieën" zijn die via configuratie worden gekozen[cite: 1184].

* **2.2. Visueel Diagram:**


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
      │                          │                        │
      └─> (roept vele malen aan) │                        │
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
                                 │ (Wordt gevoed door)
                                 ▼
      ┌────────────────────[ AbstractPluginFactory ]────────────────────┐
      │   (Ontdekt, valideert, bouwt en orkestreert alle plugins)       │
      └──────────────────────────┬──────────────────────────────────────┘
                                 │
                                 │ (Maakt gebruik van)
                                 ▼
      ┌────────────────────[ Plugins (*_worker.py) ]────────────────────┐
      │      (Gecategoriseerd op `type` in hun `plugin_manifest.yaml`)  │
      └─────────────────────────────────────────────────────────────────┘


## Hoofdstuk 3: De Anatomie van een Plugin

* **3.1. Basisstructuur:** Een plugin is een zelfstandige package die zijn eigen logica, contracten en metadata bevat.
* **3.2. Gedetailleerde Uwerking:** Voor een diepgaande analyse van de bestandsstructuur, de `YAML` vs. `JSON` afweging, en de aanpak voor stateful plugins, zie het subdocument:
    * **-> `docs/system/3_PLUGIN_ANATOMY.md`**

## Hoofdstuk 4: De Workflow & Orkestratie

* **4.1. De 6-Fasen Trechter:** De `StrategyOrchestrator` voert een vaste, logische trechter uit om van marktanalyse tot een goedgekeurde trade te komen. Elke fase fungeert als een filter; een "nee" in een vroege fase stopt het proces. De fasen zijn: 
    1.  **Regime Analyse:** Bepaalt het overkoepelende marktkarakter (trending, ranging, etc.).
    2.  **Structurele Context:** Identificeert belangrijke niveaus zoals support/resistance en marktstructuur (HH/LL).
    3.  **Signaal Generatie:** Zoekt naar precieze, actiegerichte triggers binnen de vastgestelde context.
    4.  **Signaal Verfijning:** Zoekt naar confluentie door het signaal te valideren met onafhankelijke factoren (bv. volume, hogere timeframes).
    5.  **Trade Constructie:** Vertaalt het bevestigde signaal naar een concreet handelsplan (entry, exit, positiegrootte).
    6.  **Portfolio Overlay:** Voert een finale risicocheck uit op portfolio-niveau (bv. maximale drawdown, sectorconcentratie).

* **4.2. De Rol van de `StrategyOrchestrator`:** De `Orchestrator` is de "regisseur". Het is zijn verantwoordelijkheid om de `AbstractPluginFactory` aan te sturen om de 6 fasen in de correcte, vaste volgorde uit te voeren. Hij beheert de 'state' van de backtest (de huidige tijdstap) en zorgt ervoor dat de juiste data naar de juiste plugins gaat.

* **4.3. De Rol van de `AbstractPluginFactory`:** De `Factory` is de "technische projectmanager". Zijn taken zijn:
    * [cite_start]**Plugin Discovery:** Het scannen van `plugin`-mappen en het bouwen van een register van alle beschikbare workers op basis van hun `plugin_manifest.yaml`[cite: 1791].
    * **Orkestratie van Context:** Het uitvoeren van de `context_pipeline` (Fase 1 & 2), waarbij het de seriële groepen en parallelle workers beheert.
    * **Dataflow Management:** Het doorgeven van de `DataFrame` (de "snijplank") van de ene contextgroep naar de volgende en het valideren dat de door plugins vereiste data (`dependencies`) aanwezig is.
    * **Worker Constructie:** Het op aanvraag bouwen van `StrategyWorker`-instanties voor de latere fasen.

## Hoofdstuk 5: Frontend Integratie

* **5.1. Visie:** De architectuur is ontworpen om een rijke, dynamische frontend (web-based UI) te ondersteunen, waarbij de UI zichzelf opbouwt op basis van de ontdekte plugins.
* **5.2. Gedetailleerde Uwerking:** Voor de rol van TypeScript en de communicatie tussen de Pydantic-backend en een frontend, zie het subdocument:
    * **-> `docs/system/5_FRONTEND_INTEGRATION.md`**

## Hoofdstuk 6: Robuustheid & Operationele Betrouwbaarheid

* **6.1. Principe:** Het systeem moet veerkrachtig zijn tegen crashes en netwerkproblemen, met name in een live trading-omgeving.
* **6.2. Gedetailleerde Uwerking:** Voor de strategieën rondom atomische schrijfacties, state management, en het omgaan met connectiviteitsverlies, zie het subdocument:
    * **-> `docs/system/6_RESILIENCE_AND_OPERATIONS.md`**

## Hoofdstuk 7: Kritische Vraagstukken & Openstaande Beslissingen

Dit hoofdstuk documenteert de "bekende onbekenden" die in de detail-uitwerking moeten worden opgelost:
* **7.1. State Management:** Hoe wordt de staat van stateful plugins (zoals Grid-strategieën) exact gepersisteerd en hersteld?
* **7.2. Data Synchronisatie:** Hoe gaat de `LiveEnvironment` om met asynchrone data-ticks voor verschillende assets (tick-driven vs. bar-driven)?
* **7.3. Performance:** Hoe optimaliseren we geheugengebruik bij grootschalige Multi-Time Frame analyses op meerdere assets?
* **7.4. Debugging & Traceability:** Welke tools en modi worden ontwikkeld om het debuggen van een complexe, parallelle run te faciliteren?