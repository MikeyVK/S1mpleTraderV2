# **S1mpleTrader V2: Architectonische Blauwdruk**

Versie: 3.0 (Event-Gedreven Architectuur)  
Status: Definitief

## **Hoofdstuk 1: Visie & Architectonische Principes**

* **1.1. Visie**  
  Het creëren van één uniforme, plugin-gedreven architectuur die de volledige levenscyclus van een handelsstrategie ondersteunt: van concept & ontwikkeling, via rigoureuze backtesting en optimalisatie, naar paper trading en uiteindelijk live executie.  
* **1.2. De Event-Gedreven Architectuur**  
  De kern van de V2-architectuur is een ontkoppeld, **event-gedreven model** dat robuustheid, schaalbaarheid en onderhoudbaarheid maximaliseert. Een centrale EventBus fungeert als zenuwstelsel, waardoor componenten als gelijkwaardige specialisten samenwerken via strikt gedefinieerde, contract-gedreven events.  
  **→ Lees de volledige uitwerking in: system/1_EVENT_DRIVEN_ARCHITECTURE.md**

## **Hoofdstuk 2: Architectuur & Componenten**

De applicatie is opgebouwd uit drie strikt gescheiden lagen (Frontend → Service → Backend). Dit hoofdstuk beschrijft de verantwoordelijkheden van elke laag, definieert de functionele categorieën van de componenten, en licht de rol toe van kerncomponenten zoals de PortfolioSupervisor, ContextOrchestrator en de StrategyOperator.

**→ Lees de volledige uitwerking in: system/2_ARCHITECTURE.md**

## **Hoofdstuk 3: De Anatomie van een Plugin**

Een plugin is de fundamentele, zelfstandige en testbare eenheid van logica. Dit hoofdstuk beschrijft de mappenstructuur, het plugin_manifest.yaml (de ID-kaart), het schema.py (het contract) en de worker.py (de logica), en de rol van het BaseWorker-raamwerk.

**→ Lees de volledige uitwerking in: system/3_PLUGIN_ANATOMY.md**

## **Hoofdstuk 4: De Analytische Pijplijn**

De StrategyEngine is de motor van de analytische pijplijn. Dit hoofdstuk beschrijft de interne, procedurele (fase 3-9 van de analytische pijplijn) die wordt uitgevoerd in reactie op een ContextReady-event. Het detailleert hoe een idee stapsgewijs wordt gevalideerd en omgezet in een StrategyProposal, van Regime Context tot Critical Event Detection.

**→ Lees de volledige uitwerking in: system/4_WORKFLOW_AND_ORCHESTRATOR.md**

## **Hoofdstuk 5: Frontend Integratie**

De frontend is de primaire ontwikkelomgeving (IDE) voor de strateeg, ontworpen om de "Bouwen -> Meten -> Leren" cyclus te maximaliseren. Dit hoofdstuk beschrijft de verschillende "Werkruimtes" en legt uit hoe een strikt contract tussen de Pydantic-backend en de TypeScript-frontend zorgt voor een robuuste gebruikerservaring.

**→ Lees de volledige uitwerking in: system/5_FRONTEND_INTEGRATION.md**

## **Hoofdstuk 6: Robuustheid & Operationele Betrouwbaarheid**

Een live trading-systeem moet veerkrachtig zijn. Dit hoofdstuk beschrijft de drie verdedigingslinies: atomische schrijfacties (journaling) voor staatintegriteit, protocollen voor netwerkveerkracht (heartbeat, reconnect, reconciliation) en een Supervisor-model voor automatische crash recovery.

**→ Lees de volledige uitwerking in: system/6_RESILIENCE_AND_OPERATIONS.md**

## **Hoofdstuk 7: Ontwikkelstrategie & Tooling**

Dit hoofdstuk beschrijft de workflow, van de visuele 'Strategy Builder' tot de 'Trade Explorer'. Daarnaast worden de kern-tools behandeld, zoals de gespecialiseerde entrypoints, de gelaagde logging-aanpak en de cruciale rol van de Correlation ID voor traceerbaarheid.

**→ Lees de volledige uitwerking in: system/7_DEVELOPMENT_STRATEGY.md**

## **Hoofdstuk 8: Meta Workflows**

Bovenop de executie van een enkele strategie draaien "Meta Workflows" om geavanceerde analyses uit te voeren. Dit hoofdstuk beschrijft de OptimizationService en VariantTestService, die de kern-executielogica herhaaldelijk en parallel aanroepen om complexe kwantitatieve analyses uit te voeren.

**→ Lees de volledige uitwerking in: system/8_META_WORKFLOWS.md**

## **Hoofdstuk 9: Coding Standaarden & Design Principles**

Een consistente codebase is essentieel. Dit hoofdstuk beschrijft de verplichte standaarden (PEP 8, Type Hinting, Docstrings) en de kern design principles (SOLID, Factory Pattern, DTO's) die de vier kernprincipes van V2 (Plugin First, Scheiding van Zorgen, Configuratie-gedreven, Contract-gedreven) tot leven brengen.

**→ Lees de volledige uitwerking in: system/9_CODING_STANDAARDS_DESIGN_PRINCIPLES.md**

## **Bijlages**

* **Bijlage A: Terminologie**: Een uitgebreid naslagwerk met beschrijvingen van alle belangrijke concepten en componenten.  
* **Bijlage B: Openstaande Vraagstukken**: Een overzicht van bekende "onbekenden" die tijdens de implementatie verder onderzocht moeten worden.  
* **Bijlage C: MVP**: De scope en componenten van het Minimum Viable Product.  
* **Bijlage D: Plugin IDE**: De architectuur en UX voor de web-based IDE voor plugins.