# S1mpleTrader V2: Architectuur Overzicht

**Versie:** 3.0
**Status:** Definitief
**Datum:** 2025-10-24

Dit document dient als de centrale gids voor S1mpleTrader V2, een configuratie-gedreven, event-driven trading platform gebouwd op strikte SOLID principes en dependency injection.

---

## **Inhoudsopgave**

1. [Visie & Filosofie](#visie--filosofie)
2. [Kernarchitectuur Principes](#kernarchitectuur-principes)
3. [Documentatie Structuur](#documentatie-structuur)
4. [Belangrijkste Componenten](#belangrijkste-componenten)
5. [Ontwikkelingsfilosofie](#ontwikkelingsfilosofie)

---

## **Visie & Filosofie**

S1mpleTrader is ontworpen als een **agnostisch besturingssysteem** voor kwantitatieve strategen. Het platform zelf dwingt geen specifieke manier van handelen af, maar biedt een extreem robuust, flexibel en schaalbaar **framework** waarin een quant alle mogelijke kwantitatieve en operationele functionaliteit kan implementeren via zelfstandige, specialistische plugins.

**Paradigma: "Configuratie is Koning"**

De architectuur benadrukt de configuratie-gedreven natuur van het systeem. Het 5-categorie worker ecosysteem wordt aangestuurd door data-gedreven operators die hun gedrag volledig ontlenen aan configuratie. De Persistence Suite garandeert atomische betrouwbaarheid, terwijl het Causale ID Framework volledige traceerbaarheid biedt van elke beslissing.

---

## **Kernarchitectuur Principes**

### **1. Plugin-First Filosofie**
- Alle businesslogica in herbruikbare, testbare plugins
- 5 worker categorieën: Context, Opportunity, Threat, Planning, Execution
- 27 sub-categorieën voor fijnmazige classificatie

### **2. Configuratie-Gedreven Design**
- YAML definieert gedrag, code is mechanica
- Drie configuratielagen: Platform, Operation, Strategy
- ConfigTranslator genereert runtime instructies (BuildSpecs)

### **3. Event-Driven Communicatie**
- Drie abstractieniveaus: Impliciet → Predefined → Custom
- Bus-agnostische workers via EventAdapter pattern
- Platgeslagen, expliciete worker-naar-worker wiring

### **4. Contract-Gedreven Development**
- Pydantic validatie voor alle data-uitwisseling
- Interface-based dependencies (geen concrete klassen)
- TypeScript interfaces voor frontend-backend contract

### **5. Dependency Injection**
- Constructor injection als standaard
- Factory pattern voor complexe objecten
- Testbaarheid via mock injection

### **6. Causale Traceability**
- Getypeerde IDs: OpportunityID, ThreatID, TradeID, ScheduledID
- Volledige "waarom"-analyse van elke beslissing
- StrategyJournal voor complete historie

---

## **Documentatie Structuur**

De documentatie is georganiseerd in een logische hiërarchie die overlap minimaliseert:

### **📋 01_Architecture_Overview.md** (Dit document)
Top-level overzicht van het complete systeem.

### **🔧 02_Core_Concepts/**
Kernbegrippen die de fundamenten vormen:

- **[01_Worker_Ecosystem.md](02_Core_Concepts/01_Worker_Ecosystem.md)** - 5-worker model + 27 sub-types
- **[02_Event_Architecture.md](02_Core_Concepts/02_Event_Architecture.md)** - 3-niveaus event system
- **[03_Configuration_Hierarchy.md](02_Core_Concepts/03_Configuration_Hierarchy.md)** - YAML structuur
- **[04_Traceability_Framework.md](02_Core_Concepts/04_Traceability_Framework.md)** - Causal ID systeem

### **🛠️ 03_Development/**
Plugin development en tooling:

- **[01_Plugin_Anatomy.md](03_Development/01_Plugin_Anatomy.md)** - Plugin structuur en manifest
- **[02_Development_Workflow.md](03_Development/02_Development_Workflow.md)** - Development process
- **[03_IDE_Features.md](03_Development/03_IDE_Features.md)** - UI/UX tooling

### **🏗️ 04_System_Architecture/**
Technische systeemarchitectuur:

- **[01_Component_Architecture.md](04_System_Architecture/01_Component_Architecture.md)** - Backend/frontend/services
- **[02_Data_Architecture.md](04_System_Architecture/02_Data_Architecture.md)** - DTOs, persistence, state
- **[03_Integration_Architecture.md](04_System_Architecture/03_Integration_Architecture.md)** - Event wiring, operators
- **[04_Security_Architecture.md](04_System_Architecture/04_Security_Architecture.md)** - Permissions, validation

### **⚙️ 05_Implementation/**
Implementatie details:

- **[01_Coding_Standards.md](05_Implementation/01_Coding_Standards.md)** - PEP8, patterns, DI
- **[02_Testing_Strategy.md](05_Implementation/02_Testing_Strategy.md)** - Unit, integration, E2E
- **[03_Deployment_Guide.md](05_Implementation/03_Deployment_Guide.md)** - Installation, configuratie

### **🚀 06_Advanced_Features/**
Geavanceerde functionaliteit:

- **[01_Meta_Workflows.md](06_Advanced_Features/01_Meta_Workflows.md)** - Optimization, variant testing
- **[02_Frontend_Integration.md](06_Advanced_Features/02_Frontend_Integration.md)** - UI/UX details
- **[03_Performance_Optimization.md](06_Advanced_Features/03_Performance_Optimization.md)** - Scaling, monitoring

### **📚 07_Appendices/**
Naslagwerken:

- **[01_Terminologie.md](07_Appendices/01_Terminologie.md)** - Complete begrippenlijst
- **[02_Openstaande_Vraagstukken.md](07_Appendices/02_Openstaande_Vraagstukken.md)** - Known unknowns
- **[03_Component_Index.md](07_Appendices/03_Component_Index.md)** - Componenten overzicht

---

## **Belangrijkste Componenten**

### **Backend Assembly Layer**
- **ContextBuilder** - Bootstrap orchestrator
- **OperatorFactory** - Creëert data-gedreven operators
- **WorkerBuilder** - Assembleert workforce met dependency injection
- **EventWiringFactory** - Creëert event adapters
- **PersistorFactory** - Beheert persistence suite

### **Backend Core Layer**
- **EventBus** - Centrale event distribution
- **Scheduler** - Tijd-gebaseerde event scheduling
- **StrategyLedger** - Operationele staat (snel)
- **StrategyJournal** - Causale historie (rijk)
- **BaseOperator** - Generieke, data-gedreven operator
- **BaseWorker** - Worker hiërarchie (Standard/EventDriven)

### **Persistence Suite**
- **IDataPersistor** - Marktdata (Parquet, grote volumes)
- **IStatePersistor** - Plugin state (JSON, atomic writes)
- **IJournalPersistor** - Strategy journal (JSON, append-only)

### **Services Layer**
- **OperationService** - Hoofdservice voor operation execution
- **SchedulerService** - Tijd-gebaseerde scheduling
- **Meta Workflows** - Optimization en variant testing services

---

## **Ontwikkelingsfilosofie**

### **"Bouwen → Meten → Leren" Cyclus**
De architectuur is ontworpen om deze cyclus te minimaliseren van uren naar minuten:

1. **Bouwen** - Visuele Strategy Builder met intelligente filtering
2. **Meten** - Real-time causale event stream + threat detection
3. **Leren** - Complete causale reconstructie + afgewezen kansen analyse

### **Progressive Complexity**
- **Beginners** - Impliciete event chains, standaard flows
- **Intermediate** - Predefined triggers, sub-categorie filtering
- **Experts** - Custom event chains, complete architectuur controle

### **Quality Gates**
- **100% Test Coverage** - TDD adagium strikt gevolgd
- **Contract Validatie** - Pydantic schemas voor alle configuratie
- **Event Chain Validatie** - Automatische integriteit checks
- **Dependency Injection** - Testbaarheid via constructor injection

---

## **Quick Start Guide**

### **Voor Strategie Ontwikkelaars**
1. **Start** - [02_Core_Concepts/01_Worker_Ecosystem.md](02_Core_Concepts/01_Worker_Ecosystem.md)
2. **Configureer** - [02_Core_Concepts/03_Configuration_Hierarchy.md](02_Core_Concepts/03_Configuration_Hierarchy.md)
3. **Develop** - [03_Development/01_Plugin_Anatomy.md](03_Development/01_Plugin_Anatomy.md)

### **Voor Plugin Ontwikkelaars**
1. **Leer** - [03_Development/01_Plugin_Anatomy.md](03_Development/01_Plugin_Anatomy.md)
2. **Bouw** - [03_Development/02_Development_Workflow.md](03_Development/02_Development_Workflow.md)
3. **Test** - [05_Implementation/02_Testing_Strategy.md](05_Implementation/02_Testing_Strategy.md)

### **Voor Architecten**
1. **Overzicht** - [04_System_Architecture/01_Component_Architecture.md](04_System_Architecture/01_Component_Architecture.md)
2. **Integratie** - [04_System_Architecture/03_Integration_Architecture.md](04_System_Architecture/03_Integration_Architecture.md)
3. **Standards** - [05_Implementation/01_Coding_Standards.md](05_Implementation/01_Coding_Standards.md)

---

## **Architectuur Highlights**

| Aspect | Implementatie |
|--------|---------------|
| **Worker Taxonomie** | 5 categorieën + 27 sub-types |
| **Event Architecture** | 3 abstractieniveaus (Impliciet → Predefined → Custom) |
| **Configuration** | 3 lagen (Platform → Operation → Strategy) |
| **Traceability** | 4 getypeerde IDs (Opportunity, Threat, Trade, Scheduled) |
| **Persistence** | 3 gespecialiseerde interfaces (Data, State, Journal) |
| **Testing** | 100% coverage requirement |
| **Dependency Injection** | Constructor injection + Factory pattern |
| **Frontend** | TypeScript + Pydantic contract |

---

## **Referenties**

Voor diepere uitwerkingen van specifieke concepten:

- **[Worker Ecosystem](02_Core_Concepts/01_Worker_Ecosystem.md)** - Complete 5-categorieën + 27 sub-types uitwerking
- **[Event Architecture](02_Core_Concepts/02_Event_Architecture.md)** - 3-niveaus event system details
- **[Configuration](02_Core_Concepts/03_Configuration_Hierarchy.md)** - YAML hiërarchie en ConfigTranslator
- **[Plugin Development](03_Development/01_Plugin_Anatomy.md)** - Plugin capabilities en event configuration
- **[System Architecture](04_System_Architecture/01_Component_Architecture.md)** - Complete component overzicht
- **[Coding Standards](05_Implementation/01_Coding_Standards.md)** - PEP8, patterns, dependency injection

---

**Einde Document**

*"Van rigide templates naar intelligente configuratie - waar strategieën tot leven komen door de kracht van declaratieve specificatie."*