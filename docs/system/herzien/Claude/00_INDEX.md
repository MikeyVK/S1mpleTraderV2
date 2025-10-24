# S1mpleTrader V2 Architectuur - Index

**Versie:** 4.0  
**Status:** Definitief  
**Datum:** 2025-10-23

---

## Overzicht Herziene Documentatie

Deze documentatie beschrijft de **definitieve V4.0 architectuur** van S1mpleTrader, waarbij alle addenda volledig zijn geïntegreerd. De architectuur is gebaseerd op drie fundamentele paradigma's:

1. **Platgeslagen Event-Driven Netwerk** (geen Operators)
2. **Point-in-Time DTO-Gedreven Data** (geen enriched_df)
3. **BuildSpec-Gedreven Bootstrap** (ConfigTranslator)

---

## Hoofddocument

### [Voorwoord](Voorwoord.md)
- De Drie Fundamentele Paradigma's
- Architectuur Overzicht
- Kernprincipes
- Navigatie

---

## Afzonderlijke Hoofdstukken

### DEEL I: FUNDAMENTEN & COMMUNICATIE

#### [Hoofdstuk 1: Communicatie Architectuur](H1_Communicatie_Architectuur.md)
- Platgeslagen Event-Driven Netwerk
- EventAdapter als generieke uitvoerder
- EventWiringFactory als configurator
- Event Types (System vs Custom)
- Bootstrap Sequence

#### [Hoofdstuk 2: De Drie Configuratielagen & BuildSpecs](H2_Configuratielagen_BuildSpecs.md)
- Gelaagde configuratie (Platform, Operation, Strategy)
- ConfigTranslator & BuildSpecs
- OperationService als levenscyclus manager
- Validatie (Fail Fast)

#### [Hoofdstuk 3: Het Data Landschap (Point-in-Time)](H3_Data_Landschap_Point_in_Time.md)
- Minimale TradingContext
- ITradingContextProvider & Tick Cache
- Platform Providers (Toolbox)
- DispositionEnvelope voor flow control
- DTO Registry & Enrollment

### DEEL II: COMPONENTEN

#### [Hoofdstuk 4: Plugin Anatomie](H4_Plugin_Anatomie.md)
- Plugin mappenstructuur
- Manifest.yaml specificatie
- Worker.py implementatie (StandardWorker vs EventDrivenWorker)
- Schema.py parameter validatie
- DTO definitie & enrollment
- Testing requirements
- Complete voorbeelden

#### [Hoofdstuk 5: Worker Ecosysteem](H5_Worker_Ecosysteem.md)
- De 5 worker categorieën:
  - ContextWorker (7 sub-types)
  - OpportunityWorker (7 sub-types)
  - ThreatWorker (5 sub-types)
  - PlanningWorker (4 sub-types)
  - ExecutionWorker (4 sub-types)
- Input/output patronen per categorie
- Causale ID generatie
- Manifest templates
- Complete code voorbeelden

### DEEL III: ORKESTRATIE & WORKFLOW

#### [Hoofdstuk 6: Workflow Orkestratie](H6_Workflow_Orkestratie.md)
- Platgeslagen model (geen Operators)
- Complete tick lifecycle
- Flow patronen (sequentieel, parallel, event-driven)
- Strategy Builder UI wiring generatie
- Causale traceerbaarheid
- Feedback loops
- Voordelen vs Operator model

### DEEL IV: FRONTEND & GEBRUIKER

#### [Hoofdstuk 7: Frontend Integration](H7_Frontend_Integration.md)
- Strategy Builder UI (wiring generator)
- Plugin Library & Discovery
- Event Topology Viewer
- Trade Explorer (causale analyse)
- Live Monitoring Dashboard
- BFF API endpoints
- TypeScript interfaces

### DEEL V: OPERATIONS & DEVELOPMENT

#### [Hoofdstuk 8: Robuustheid & Operations](H8_Robuustheid_Operations.md)
- Persistence Suite (IDataPersistor, IStatePersistor, IJournalPersistor)
- Atomic writes & crash recovery
- Causaal Traceability Framework
- State reconciliation (live trading)
- Supervisor model
- Network resilience
- Health checks

#### [Hoofdstuk 9: Development Strategy](H9_Development_Strategy.md)
- Plugin development workflow
- Strategy development workflow
- Plugin IDE generator
- Testing strategie (Unit, Integration, E2E)
- Debugging tools
- Best practices DO's & DON'Ts

#### [Hoofdstuk 10: Meta Workflows](H10_Meta_Workflows.md)
- OptimizationService (parameter sweeps)
- VariantTestService (A/B testing)
- WalkForwardService (temporal validation)
- ParallelRunService (parallel execution)
- Impact op architectuur
- BuildSpecs usage in meta workflows

### DEEL VI: STANDAARDEN & BIJLAGEN

#### [Hoofdstuk 11: Coding Standards](H11_Coding_Standards.md)
- Code kwaliteit (PEP 8)
- Contract-gedreven development
- Dependency injection
- DTO best practices
- Point-in-Time principe
- Testing standards
- Internationalisatie
- SOLID principles
- Quick reference checklists

#### [Bijlage A: Terminologie](Bijlage_A_Terminologie.md)
- Alfabetische terminologie lijst
- Deprecated terms (V3.0 → V4.0)
- Afkortingen

---

## Belangrijkste Wijzigingen vs V3.0

### Vervallen Concepten ❌

- BaseOperator klasse
- operators.yaml configuratie
- Operator-gedreven orkestratie
- enriched_df in TradingContext
- Impliciete data doorgifte

### Nieuwe Concepten ✨

- EventAdapter per component
- BuildSpecs & ConfigTranslator
- ITradingContextProvider
- Tick Cache (DTO-only)
- DispositionEnvelope
- UI-gegenereerde strategy_wiring_map
- DTO Registry
- Point-in-Time garantie

### Behouden Concepten ✅

- 5 Worker categorieën
- 27 Sub-types
- Causaal ID Framework
- Persistence Suite interfaces
- Plugin-First filosofie
- SOLID principes

---

## Leesaanbevelingen

### Voor Nieuwe Developers

1. Start met **Voorwoord** (paradigma's begrijpen)
2. Lees **H2: Configuratielagen** (hoe configuratie werkt)
3. Lees **H3: Data Landschap** (hoe data flow werkt)
4. Lees **H4: Plugin Anatomie** (hoe een plugin bouwen)
5. Lees **H5: Worker Ecosysteem** (welk worker type kiezen)

### Voor Architects

1. Lees **H1: Communicatie** (EventAdapter model)
2. Lees **H6: Workflow** (platgeslagen orkestratie)
3. Lees **H2: Configuratielagen** (BuildSpecs filosofie)
4. Lees **Bijlage A** (terminologie)

### Voor Migratie van V3.0

1. Lees **Bijlage A** (deprecated terms)
2. Lees **Voorwoord** (paradigma shifts)
3. Lees **Bijlage B: Migratie Gids** (komt binnenkort)

---

## Quick Reference

### Kerncomponenten

| Component | Locatie | Type |
|-----------|---------|------|
| ConfigTranslator | `backend/config/translator.py` | Backend |
| EventAdapter | `backend/assembly/event_adapter.py` | Backend |
| EventWiringFactory | `backend/assembly/event_wiring_factory.py` | Backend |
| TickCacheManager | `backend/core/tick_cache_manager.py` | Backend |
| ITradingContextProvider | `backend/core/interfaces/context_provider.py` | Interface |
| OperationService | `services/operation_service.py` | Service |

### Configuratie Bestanden

| Bestand | Laag | Doel |
|---------|------|------|
| platform.yaml | 1 | Globale instellingen |
| operation.yaml | 2 | Werkruimte definitie |
| connectors.yaml | 2 | Exchange verbindingen |
| schedule.yaml | 2 | Tijd-triggers |
| platform_wiring_map.yaml | 2 | Singleton bedrading |
| strategy_blueprint.yaml | 3 | Workforce definitie |
| strategy_wiring_map.yaml | 3 | Worker bedrading (UI) |

### Key Interfaces

- `ITradingContextProvider` - Tick Cache toegang
- `IOhlcvProvider` - Historische data
- `IStateProvider` - Worker state
- `IJournalWriter` - Logging
- `ILedgerProvider` - Financiële staat
- `IExecutionProvider` - Trade execution

---

## Contact & Vragen

Voor vragen over de architectuur of suggesties voor verbeteringen, zie de documentatie in de originele `docs/system/` directory of raadpleeg het development team.

---

**Laatst bijgewerkt:** 2025-10-23  
**Volgende review:** Bij architectuur wijzigingen