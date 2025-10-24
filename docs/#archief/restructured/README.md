# S1mpleTrader V2 Documentatie - Gereorganiseerde Versie

Deze map bevat de gereorganiseerde documentatie van S1mpleTrader V2, ontworpen om overlap te minimaliseren en informatie logisch te groeperen.

## Nieuwe Structuur

### 📋 01_Architecture_Overview.md
Top-level overzicht van het complete systeem.

### 🔧 02_Core_Concepts/
Kernbegrippen die de fundamenten van het systeem vormen:

- **01_Worker_Ecosystem.md** - 5-worker model + 27 sub-types
- **02_Event_Architecture.md** - 3-niveaus event system (Impliciet → Predefined → Custom)
- **03_Configuration_Hierarchy.md** - YAML configuratie structuur
- **04_Traceability_Framework.md** - Causal ID systeem (OpportunityID, ThreatID, TradeID, ScheduledID)

### 🛠️ 03_Development/
Plugin development en tooling:

- **01_Plugin_Anatomy.md** - Plugin structuur, manifest, capabilities
- **02_Development_Workflow.md** - Development process en best practices
- **03_IDE_Features.md** - UI/UX tooling voor development

### 🏗️ 04_System_Architecture/
Technische systeemarchitectuur:

- **01_Component_Architecture.md** - Backend, frontend, services lagen
- **02_Data_Architecture.md** - DTOs, persistence suite, state management
- **03_Integration_Architecture.md** - Event wiring, operators, dependency injection
- **04_Security_Architecture.md** - Permissions, validation, security

### ⚙️ 05_Implementation/
Implementatie details en standaarden:

- **01_Coding_Standards.md** - PEP8, patterns, dependency injection
- **02_Testing_Strategy.md** - Unit, integration, E2E testing
- **03_Deployment_Guide.md** - Installation en configuratie

### 🚀 06_Advanced_Features/
Geavanceerde functionaliteit:

- **01_Meta_Workflows.md** - Optimization en variant testing services
- **02_Frontend_Integration.md** - UI/UX implementatie details
- **03_Performance_Optimization.md** - Scaling en monitoring

### 📚 07_Appendices/
Naslagwerken en aanvullende informatie:

- **01_Terminologie.md** - Complete begrippenlijst
- **02_Openstaande_Vraagstukken.md** - Known unknowns en onderzoekspunten
- **03_Component_Index.md** - Overzicht van alle componenten

## Voordelen van deze Structuur

✅ **Minimale Overlap** - Elk concept heeft één primaire locatie
✅ **Logische Groepering** - Gerelateerde concepten bij elkaar
✅ **Progressieve Diepgang** - Van overzicht naar implementatie details
✅ **Cross-References** - Documenten verwijzen naar elkaar
✅ **Behoud van Informatie** - Alle originele content is behouden

## Migratie van Originele Documentatie

| Origineel Document | Nieuwe Locatie | Status |
|-------------------|----------------|---------|
| 00_Architecture_Overview.md | 01_Architecture_Overview.md | 🔄 |
| 01_Bus_communicatie_structuur.md | 02_Core_Concepts/02_Event_Architecture.md | 🔄 |
| 02_Architectuur_Componenten.md | 02_Core_Concepts/01_Worker_Ecosystem.md | 🔄 |
| 03_Configuratie_Trein.md | 02_Core_Concepts/03_Configuration_Hierarchy.md | 🔄 |
| 04_Plugin_Anatomie.md | 03_Development/01_Plugin_Anatomy.md | 🔄 |
| 05_Workflow_Orkestratie.md | 02_Core_Concepts/01_Worker_Ecosystem.md | 🔄 |
| 06_Frontend_Integration.md | 06_Advanced_Features/02_Frontend_Integration.md | 🔄 |
| 08_Development_Strategy.md | 03_Development/02_Development_Workflow.md | 🔄 |
| 09_META_WORKFLOWS.md | 06_Advanced_Features/01_Meta_Workflows.md | 🔄 |
| 10_CODING_STANDARDS_DESIGN_PRINCIPLES.md | 05_Implementation/01_Coding_Standards.md | 🔄 |
| 11_COMPLETE_SYSTEM_DESIGN.md | 04_System_Architecture/ | 🔄 |
| A_Bijlage_Terminologie.md | 07_Appendices/01_Terminologie.md | 🔄 |
| B_BIJLAGE_OPENSTAANDE_VRAAGSTUKKEN.md | 07_Appendices/02_Openstaande_Vraagstukken.md | 🔄 |
| D_BIJLAGE_PLUGIN_IDE.md | 03_Development/03_IDE_Features.md | 🔄 |

## Navigatie Tips

- **Begin bij 01_Architecture_Overview.md** voor het grote plaatje
- **Duik in 02_Core_Concepts/** voor de fundamenten
- **Ga naar 03_Development/** voor plugin development
- **Bekijk 04_System_Architecture/** voor technische details
- **Controleer 07_Appendices/** voor naslaginformatie

Elk document bevat cross-references naar gerelateerde documenten om de navigatie te vergemakkelijken.