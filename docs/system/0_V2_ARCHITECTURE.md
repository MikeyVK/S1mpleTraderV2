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

* **3.1. Basisstructuur** Een plugin is een zelfstandige package met eigen logica, contracten (**Pydantic**-modellen), manifest (`plugin_manifest.yaml`) en metadata. Elke plugin declareert zijn `type` (bv. `regime_context`, `signal_generator`, `execution_planner`, etc.), `dependencies`, en Pydantic-gevalideerde `params`.

* **3.2. Gedetailleerde uitwerking** Voor bestandsstructuur, **YAML vs. JSON**-beleid en aanpak voor **stateful** plugins:  
  **→ `docs/system/3_PLUGIN_ANATOMY.md`**

---

## Hoofdstuk 4: De Quant Workflow: Van Idee tot Inzicht

De kern van de strategie-executie is een systematische, multi-fase trechter die een idee valideert en omzet in een concrete trade. Dit hoofdstuk beschrijft elke fase, van Regime Context tot de Portfolio Overlay, en verduidelijkt de rollen van de `StrategyEngine` (de motor) en het `Assembly Team` (de technische projectmanager).

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