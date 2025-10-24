# 06_Frontend_Integration.md

# **S1mpleTrader: Frontend Integratie: De UI als Intelligente IDE**

Dit document beschrijft de volledige gebruikersworkflow en de frontend-architectuur die nodig is om de optimale gebruikerservaring te realiseren, gebaseerd op het platgeslagen, configuratie-gedreven model.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [De Filosofie: De UI als IDE](#de-filosofie-de-ui-als-ide)
3. [De Werkruimtes: Een Context-Bewuste Workflow](#de-werkruimtes-een-context-bewuste-workflow)
4. [De Top-Down Configuratie Flow](#de-top-down-configuratie-flow)
5. [Het Frontend-Backend Contract: BFF & TypeScript](#het-frontend-backend-contract-bff--typescript)
6. [Platgeslagen Workflow Visualisatie](#platgeslagen-workflow-visualisatie)
7. [Architectuur Features](#architectuur-features)

---

## **Executive Summary**

Dit document beschrijft de frontendstrategie, die de web-UI transformeert van een simpele presentatielaag naar de **primaire, geïntegreerde ontwikkelomgeving (IDE)** voor de kwantitatieve strateeg. De architectuur is ontworpen om de fundamentele architectuur volledig te ondersteunen, waardoor de "Bouwen → Meten → Leren"-cyclus wordt versneld van uren naar minuten.

### **Kernkenmerken**

**1. Context-Bewuste Werkruimtes**
- De UI is georganiseerd in context-bewuste werkruimtes (`Operation Management`, `Strategy Builder`, `Backtesting & Analysis`, etc.) die de gebruiker door een logische, hiërarchische workflow leiden.

**2. Visuele Workforce Builder**
- Een visuele editor voor het samenstellen van strategieën, gebaseerd op de 5 worker-categorieën en 27 sub-categorieën, die de complexiteit van de onderliggende YAML-configuratie verbergt.

**3. Manifest-Gedreven UI**
- De UI wordt dynamisch gegenereerd op basis van de `manifest.yaml` en `schema.py` van de plugins. Componenten zoals de `Plugin Library` en `Configuratie Panelen` passen zich aan de metadata van de plugins aan.

**4. Platgeslagen Workflow Visualisatie**
- De `Strategy Builder` genereert complete `strategy_wiring_map` voor directe worker-bedrading
- Event chain visualisatie toont de flow tussen workers
- Real-time validatie van event integriteit

**5. Causale Traceability Visualisatie**
- De `Trade Explorer` en `StrategyJournal Viewer` bieden diepgaande analysemogelijkheden door het visualiseren van de causale keten (`OpportunityID` → `TradeID` → `ThreatID`), waardoor de "waarom"-vraag achter elke trade beantwoord kan worden.

### **Design Principes**

✅ **UI als IDE** - De webapplicatie is de primaire omgeving voor strategie-ontwikkeling en -analyse.
✅ **Configuratie-gedreven** - De UI is een visuele schil over de onderliggende YAML-configuratie.
✅ **"Fail Fast" in de UI** - De UI voorkomt ongeldige configuraties door alleen compatibele en beschikbare opties te tonen.
✅ **Contractuele Zekerheid** - Een strikt contract tussen frontend en backend, afgedwongen door TypeScript-interfaces die automatisch worden gegenereerd uit Pydantic-modellen.

---

## **De Filosofie: De UI als IDE**

De kern van de frontendstrategie is een paradigmaverschuiving: de web-UI is niet langer een simpele presentatielaag, maar de **primaire, geïntegreerde ontwikkelomgeving (IDE)** voor de kwantitatieve strateeg. Elke stap in de workflow, van het beheren van operaties tot het diepgaand analyseren van resultaten, vindt plaats binnen een naadloze, interactieve webapplicatie.

**Architectuur Ondersteuning:**
- Volledige ondersteuning voor 5 worker categorieën
- 27 sub-categorieën voor fijnmazige classificatie
- Event configuratie wizard (3 niveaus: Implicit/Predefined/Custom)
- Worker gedrag configuratie UI
- Causaal traceability framework visualisatie

Dit maximaliseert de efficiëntie en verkort de **"Bouwen → Meten → Leren"**-cyclus van dagen of uren naar minuten.

---

## **De Werkruimtes: Een Context-Bewuste Workflow**

De hoofdnavigatie van de applicatie wordt gevormd door een reeks "werkruimtes". De workflow is hiërarchisch en context-bewust, beginnend bij de Operation.

| **OPERATION MANAGEMENT** | **STRATEGY BUILDER** | **BACKTESTING & ANALYSIS** | **LIVE MONITORING** | **PLUGIN DEVELOPMENT** |

### **Werkruimte Updates**

**STRATEGY BUILDER** (Grootste update):
- **5 Worker Categorieën** gevisualiseerd (Context, Opportunity, Threat, Planning, Execution)
- **Plugin Bibliotheek** gefilterd op **27 sub-categorieën**:
  - ContextType (7): regime_classification, structural_analysis, indicator_calculation, etc.
  - OpportunityType (7): technical_pattern, momentum_signal, mean_reversion, etc.
  - ThreatType (5): portfolio_risk, market_risk, system_health, etc.
  - PlanningPhase (4): entry_planning, exit_planning, size_planning, order_routing
  - ExecutionType (4): trade_initiation, position_management, risk_safety, operational
- **Event Configuratie Wizard** (3 niveaus)
- **Worker Orkestratie Visualisatie** (NIEUW)

**BACKTESTING & ANALYSIS**:
- **Causale ID Filtering** (OpportunityID, ThreatID, TradeID)
- **StrategyJournal Viewer** (inclusief afgewezen kansen)
- **Causale Reconstructie Tool**
- **Event Chain Visualisatie**

**LIVE MONITORING**:
- **Ledger vs Journal** onderscheid
- **Real-time Causal Event Stream**
- **Threat Detection Alerts** met ThreatID linking

---

## **De Top-Down Configuratie Flow**

De gebruiker wordt door een logische, gelaagde wizard geleid die frictie minimaliseert en contextuele hulp biedt op basis van de gemaakte keuzes.

### **Fase 1: Werkruimte "OPERATION MANAGEMENT" (Het Fundament)**

Dit is het onbetwiste startpunt voor elke activiteit. Een Operation definieert de "wereld" waarin strategieën opereren.

* **User Goal:** Het definiëren en beheren van de overkoepelende "draaiboeken" ([`operation.yaml`](config/operation.yaml)) voor backtesting, paper trading en live trading.
* **UI Componenten:**
  1. **Operations Hub:** Een dashboard met een overzicht van alle geconfigureerde operaties (mijn_btc_operatie.yaml, live_eth_dca.yaml, etc.).
  2. **Operation Creatie Wizard:** Een wizard die de gebruiker helpt een nieuw operation.yaml te configureren door hem door de velden te leiden.
     * **Stap 1: Koppel Blueprints aan Werelden:** De gebruiker creëert strategy_links door een strategy_blueprint_id te selecteren uit de bibliotheek en deze te koppelen aan een execution_environment_id (die op hun beurt weer gedefinieerd zijn in [`environments.yaml`](config/environments.yaml)).
     * **Stap 2: Activeer Strategieën:** De gebruiker stelt per strategy_link in of deze is_active is.
* **Vanuit dit dashboard** kan de gebruiker doorklikken om de strategieën binnen een operatie te beheren of een nieuwe strategie ([`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml)) te creëren.

---

### **Fase 2: Werkruimte "STRATEGY BUILDER" (Context-Bewust Bouwen)**

Deze werkruimte wordt **altijd gestart vanuit de context van een specifieke Operation**. De wizard is nu "slim" en zich bewust van de grenzen en mogelijkheden die door de gekoppelde ExecutionEnvironments worden gedefinieerd.

* **User Goal:** Het intuïtief en foutloos samenstellen van een strategie-blueprint ([`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml)) die gegarandeerd kan draaien binnen de geselecteerde "wereld".

#### **Data Selectie**

De wizard toont alleen de handelsparen en timeframes die beschikbaar zijn binnen de ExecutionEnvironment(s) van de actieve Operation.

#### **Visuele Workforce Builder**

**5-Categorieën Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  WORKFORCE CONFIGURATION                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. CONTEXT WORKERS - "De Cartograaf"               │   │
│  │  Verrijkt marktdata met objectieve context          │   │
│  │                                                       │   │
│  │  [+] Add ContextWorker                              │   │
│  │      Filter by:  [All ▼] [regime_classification]    │   │
│  │                           [structural_analysis]      │   │
│  │                           [indicator_calculation]    │   │
│  │                           ... 7 sub-types total      │   │
│  │                                                       │   │
│  │  📦 EMA Detector (indicator_calculation)            │   │
│  │  📦 Market Structure Detector (structural_analysis) │   │
│  │  📦 ADX Regime Classifier (regime_classification)   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. OPPORTUNITY WORKERS - "De Verkenner"             │   │
│  │  Herkent handelskansen op basis van patronen        │   │
│  │                                                       │   │
│  │  [+] Add OpportunityWorker                          │   │
│  │      Filter by:  [All ▼] [technical_pattern]        │   │
│  │                           [momentum_signal]          │   │
│  │                           [mean_reversion]           │   │
│  │                           ... 7 sub-types total      │   │
│  │                                                       │   │
│  │  📦 FVG Detector (technical_pattern)                │   │
│  │      ⚙️ OpportunityID: auto-generated              │   │
│  │  📦 Liquidity Sweep Detector (momentum_signal)      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. THREAT WORKERS - "De Waakhond"                   │   │
│  │  Detecteert risico's en bedreigingen (parallel)     │   │
│  │                                                       │   │
│  │  [+] Add ThreatWorker                               │   │
│  │      Filter by:  [All ▼] [portfolio_risk]           │   │
│  │                           [market_risk]              │   │
│  │                           [system_health]            │   │
│  │                           ... 5 sub-types total      │   │
│  │                                                       │   │
│  │  📦 Max Drawdown Monitor (portfolio_risk)           │   │
│  │      ⚙️ ThreatID: auto-generated                   │   │
│  │      🎯 Trigger: on_ledger_update                   │   │
│  │  📦 News Event Monitor (market_risk)                │   │
│  │      🎯 Trigger: on_context_ready                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4. PLANNING WORKERS - "De Strateeg"                 │   │
│  │  Transformeert kansen naar uitvoerbare plannen       │   │
│  │                                                       │   │
│  │  Gestructureerd in 4 fasen:                         │   │
│  │                                                       │   │
│  │  📋 Entry Planning                                  │   │
│  │     📦 Limit Entry at FVG                           │   │
│  │                                                       │   │
│  │  📋 Exit Planning                                   │   │
│  │     📦 Liquidity Target Exit                        │   │
│  │     📦 ATR-based Stops                              │   │
│  │                                                       │   │
│  │  📋 Size Planning                                   │   │
│  │     📦 Fixed Risk Sizer (1% risk)                   │   │
│  │                                                       │   │
│  │  📋 Order Routing                                   │   │
│  │     📦 Limit Order Router                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  5. EXECUTION WORKERS - "De Uitvoerder"             │   │
│  │  Voert uit en beheert actieve posities              │   │
│  │                                                       │   │
│  │  Gestructureerd in 4 sub-categorieën:               │   │
│  │                                                       │   │
│  │  🎬 Trade Initiation                                │   │
│  │     📦 Default Plan Executor                        │   │
│  │                                                       │   │
│  │  📊 Position Management                             │   │
│  │     📦 Partial Profit Taker                         │   │
│  │     📦 Trailing Stop Manager                        │   │
│  │                                                       │   │
│  │  🛡️ Risk & Safety                                   │   │
│  │     📦 Emergency Exit on News                       │   │
│  │                                                       │   │
│  │  ⚙️ Operational                                     │   │
│  │     (geen workers in deze strategie)                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### **Plugin Bibliotheek - Dynamische Filtering op Multiple Dimensies**

```typescript
interface PluginFilter {
  workerType?: WorkerType;           // Context, Opportunity, Threat, Planning, Execution
  subType?: SubType;                 // 27 sub-categorieën
  capabilities?: string[];           // "state", "events", "journaling"
  requiresContext?: string[];        // Rijke data vereisten
  executionEnv?: string;             // Compatibel met huidige environment
}

interface PluginCard {
  name: string;
  displayName: string;
  type: WorkerType;
  subtype: SubType;
  description: string;
  capabilities: string[];           // ["state", "events"]
  dependencies: {
    requires: string[];             // DataFrame columns
    requiresContext: string[];      // Rijke data
  };
  isCompatible: boolean;            // Voor huidige environment
  disabledReason?: string;          // Waarom niet beschikbaar
}
```

**UI Visualisatie:**
```
┌─────────────────────────────────────────────────────────────┐
│  PLUGIN LIBRARY                                              │
├─────────────────────────────────────────────────────────────┤
│  Filters:                                                    │
│  Worker Type:  [OpportunityWorker ▼]                        │
│  Sub-Type:     [technical_pattern ▼]                        │
│  Capabilities: [☐ state] [☐ events] [☐ journaling]         │
│  Environment:  [live_kraken_main ▼]                         │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│                                                              │
│  📦 FVG Detector                      ⭐⭐⭐⭐⭐ (12 reviews)  │
│  Type: OpportunityWorker → technical_pattern               │
│  Detecteert Fair Value Gaps na structurele breaks          │
│                                                              │
│  ✅ Compatible | 🏷️ No special capabilities               │
│  📊 Requires: close, high, low                             │
│  [Add to Workforce]  [Preview Config]  [View Docs]         │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│                                                              │
│  📦 Adaptive DCA Planner              ⭐⭐⭐⭐⭐ (15 reviews) │
│  Type: PlanningWorker → entry_planning                     │
│  Event-driven DCA planner met risk assessment              │
│                                                              │
│  ✅ Compatible | 🏷️ Capabilities: [state], [events]      │
│  [Add to Workforce]  [Configure]  [View Docs]             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### **Worker Orkestratie Visualisatie**

**Doel:** Visuele editor voor worker-bedrading die quants in staat stelt flow te configureren zonder YAML te bewerken.

**UI Componenten:**

```
┌─────────────────────────────────────────────────────────────┐
│  WORKER ORKESTRATIE                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ContextWorker Flow                               │    │
│  │  Manages: ContextWorker plugins                   │    │
│  │                                                      │    │
│  │  Flow Strategy:                                  │    │
│  │  ● SEQUENTIAL  ○ PARALLEL                       │    │
│  │                                                      │    │
│  │  📊 Data Flow Preview:                           │    │
│  │  ┌──────────────────────────────────────────┐      │    │
│  │  │  Worker 1 → Worker 2 → Worker 3 → Output │      │    │
│  │  │  (Sequential chaining)                    │      │    │
│  │  └──────────────────────────────────────────┘      │    │
│  │                                                      │    │
│  │  ℹ️ Rationale: Context workers moeten sequentieel │    │
│  │     draaien omdat latere workers afhankelijk zijn  │    │
│  │     van de output van eerdere workers.             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  OpportunityWorker Flow                           │    │
│  │  Manages: OpportunityWorker plugins               │    │
│  │                                                      │    │
│  │  Flow Strategy:                                  │    │
│  │  ○ SEQUENTIAL  ● PARALLEL                       │    │
│  │                                                      │    │
│  │  📊 Data Flow Preview:                           │    │
│  │  ┌──────────────────────────────────────────┐      │    │
│  │  │    ┌─ Worker 1 ─┐                        │      │    │
│  │  │    ├─ Worker 2 ─┤→ [Signal 1, Signal 2] │      │    │
│  │  │    └─ Worker 3 ─┘                        │      │    │
│  │  │  (Parallel collection)                   │      │    │
│  │  └──────────────────────────────────────────┘      │    │
│  │                                                      │    │
│  │  ℹ️ Rationale: Opportunity detection is onafhanke-│    │
│  │     lijk - verschillende detectoren kunnen tegelijk│    │
│  │     verschillende patronen herkennen.               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  [... ThreatWorker, PlanningWorker, ExecutionWorker]        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  💾 Save Configuration                              │    │
│  │  ○ Global (base_wiring.yaml)                       │    │
│  │  ● Strategy Override (strategy_blueprint.yaml)     │    │
│  │                                                      │    │
│  │  [Cancel]  [Validate]  [Save & Apply]              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**TypeScript Interface:**

```typescript
// Frontend: Worker flow configuration
interface WorkerFlowConfig {
  workerType: WorkerType;
  flowStrategy: FlowStrategy;
  rationale?: string;
}

enum FlowStrategy {
  SEQUENTIAL = "SEQUENTIAL",
  PARALLEL = "PARALLEL"
}

// Preview component
function DataFlowPreview({ config }: { config: WorkerFlowConfig }) {
  if (config.flowStrategy === FlowStrategy.SEQUENTIAL) {
    return <SequentialChainDiagram />;
  } else if (config.flowStrategy === FlowStrategy.PARALLEL) {
    return <ParallelCollectionDiagram />;
  }
}
```

#### **Event & Capability Configuratie**

De event-configuratie is onlosmakelijk verbonden met de events-capability in het manifest.yaml. De UI toont de configuratie-opties binnen de context van de worker die de events-capability heeft aangevraagd.

**Voorbeeld: Event-Driven Worker Configuratie**
```
┌─────────────────────────────────────────────────────────────┐
│  WORKER CONFIGURATION: Adaptive DCA Planner                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🏷️ Type: PlanningWorker → entry_planning                 │
│  📦 ROL: EventDrivenWorker                                  │
│                                                              │
│  ✅ Capabilities (van manifest.yaml):                        │
│     - state                                                  │
│     - events                                                 │
│                                                              │
│  ⚙️ Parameters (van schema.py):                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  base_amount:    [1000  ] EUR                       │    │
│  │  min_amount:     [500   ] EUR                       │    │
│  │  max_amount:     [2000  ] EUR                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  📡 Event Capability Configuratie (van manifest.yaml):       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Publishes:                                         │    │
│  │  - Event: [dca_plan_ready ▼]                      │    │
│  │    Payload: [TradePlan ▼]                           │    │
│  │  [+ Add Publication]                                │    │
│  │                                                      │    │
│  │  Wirings (Luistert naar):                           │    │
│  │  - Event: [dca_opportunity_scored ▼]              │    │
│  │    Invokes: [on_opportunity_scored ▼] (methode)     │    │
│  │                                                      │    │
│  │  - Event: [dca_risk_assessed ▼]                   │    │
│  │    Invokes: [on_risk_assessed ▼] (methode)          │    │
│  │  [+ Add Wiring]                                     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  🆔 Causale IDs:                                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Receives: OpportunityID (from scorer)             │    │
│  │            ThreatID (from assessor)                 │    │
│  │  Generates: TradeID (new trade plan)                │    │
│  │  Links: OpportunityID → TradeID (causaal)          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  [Cancel]  [Save]  [Visualize Event Flow]                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

* **Backend Interactie:** De UI haalt de gefilterde lijst plugins op via een `PluginQueryService`. Bij het opslaan stuurt de UI een JSON-representatie van de strategie naar een `StrategyBlueprintEditorService`, die het als een [`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml)-bestand wegschrijft.

---

### **Fase 3: Werkruimte "BACKTESTING & ANALYSIS"**

* **User Goal:** Het rigoureus testen van strategieën en het diepgaand analyseren van de resultaten met volledige causale traceability.

#### **UI Componenten**

1. **Run Launcher:** Een sectie binnen de Operations Hub waar de gebruiker een Operation selecteert en een backtest, optimalisatie of varianten-test kan starten.

2. **Live Progress Dashboard:** Toont de live voortgang van een lopende Operation.

3. **Resultaten Hub:** Een centrale plek waar alle voltooide runs worden getoond, met doorklikmogelijkheden naar:

   **a) Optimization Results:** Een interactieve tabel om de beste parameter-sets te vinden.

   **b) Comparison Arena:** Een grafische vergelijking van strategie-varianten.

   **c) Trade Explorer (Enhanced):** De krachtigste analyse-tool met causale traceability.

#### **Trade Explorer (Causale Features)**

**Causale ID Filtering:**

```
┌─────────────────────────────────────────────────────────────┐
│  TRADE EXPLORER                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Filters:                                                    │
│  Date Range:      [2024-01-01] to [2024-12-31]             │
│  Trade Outcome:   [All ▼] [Profitable] [Loss] [BE]         │
│                                                              │
│  🆔 Causale Filtering (NIEUW):                              │
│  OpportunityID:   [abc-123-...    ] [🔍 Search]            │
│  ThreatID:        [def-456-...    ] [🔍 Search]            │
│  TradeID:         [ghi-789-...    ] [🔍 Search]            │
│                                                              │
│  ────────────────────────────────────────────────────────   │
│                                                              │
│  📊 Trade #1: Profitable (+2.3%)                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  🆔 TradeID: ghi-789-abc                           │    │
│  │  📈 Opened: 2024-06-15 10:30:00                   │    │
│  │  📉 Closed: 2024-06-15 14:20:00                   │    │
│  │                                                      │    │
│  │  🔗 Causale Keten:                                 │    │
│  │  ┌──────────────────────────────────────────┐      │    │
│  │  │  Opened because:                          │      │    │
│  │  │  💡 OpportunityID: abc-123-xyz            │      │    │
│  │  │     → FVG detected after BOS             │      │    │
│  │  │     → Score: 85/100                       │      │    │
│  │  │                                            │      │    │
│  │  │  Closed because:                          │      │    │
│  │  │  🎯 Target reached (+2.3%)                │      │    │
│  │  │  ⚠️ No threats detected                   │      │    │
│  │  └──────────────────────────────────────────┘      │    │
│  │                                                      │    │
│  │  [View Context] [View Journal] [Reconstruct]       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  📊 Trade #2: Loss (-1.0%)                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  🆔 TradeID: jkl-012-def                           │    │
│  │  📈 Opened: 2024-06-16 09:15:00                   │    │
│  │  📉 Closed: 2024-06-16 09:45:00 (Early Exit!)     │    │
│  │                                                      │    │
│  │  🔗 Causale Keten:                                 │    │
│  │  ┌──────────────────────────────────────────┐      │    │
│  │  │  Opened because:                          │      │    │
│  │  │  💡 OpportunityID: def-456-uvw            │      │    │
│  │  │     → Liquidity sweep detected            │      │    │
│  │  │     → Score: 75/100                       │      │    │
│  │  │                                            │      │    │
│  │  │  Closed because:                          │      │    │
│  │  │  ⚠️ ThreatID: mno-789-pqr                │      │    │
│  │  │     → HIGH_VOLATILITY_DETECTED            │      │    │
│  │  │     → Emergency exit triggered            │      │    │
│  │  └──────────────────────────────────────────┘      │    │
│  │                                                      │    │
│  │  [View Context] [View Journal] [Reconstruct]       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**StrategyJournal Viewer:**

```
┌─────────────────────────────────────────────────────────────┐
│  STRATEGY JOURNAL                                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Show: [☑ Opportunities] [☑ Threats] [☑ Trades]            │
│        [☑ Accepted] [☑ Rejected]                            │
│                                                              │
│  ────────────────────────────────────────────────────────   │
│                                                              │
│  2024-06-15 10:30:00 | OPPORTUNITY_DETECTED                 │
│  💡 OpportunityID: abc-123-xyz                              │
│  Type: fvg_entry                                            │
│  Signal: FVG detected after BOS at 50,125                   │
│  Score: 85/100                                              │
│  Context: Bullish HTF bias, London session                  │
│                                                              │
│  2024-06-15 10:30:05 | OPPORTUNITY_ACCEPTED ✅              │
│  💡 OpportunityID: abc-123-xyz → 🆔 TradeID: ghi-789-abc   │
│  Decision: No active threats, proceed with entry            │
│                                                              │
│  ────────────────────────────────────────────────────────   │
│                                                              │
│  2024-06-15 11:45:00 | OPPORTUNITY_DETECTED                 │
│  💡 OpportunityID: stu-901-wxy                              │
│  Type: breakout_signal                                      │
│  Signal: Break of structure at 50,500                       │
│  Score: 70/100                                              │
│                                                              │
│  2024-06-15 11:45:02 | OPPORTUNITY_REJECTED ❌              │
│  💡 OpportunityID: stu-901-wxy                              │
│  ⚠️ ThreatID: vwx-234-yz                                   │
│  Reason: MAX_DRAWDOWN_THRESHOLD (current: 8.5%, max: 10%)  │
│  Decision: Skip trade, risk too high                        │
│                                                              │
│  ────────────────────────────────────────────────────────   │
│                                                              │
│  [Export CSV] [Export JSON] [Filter by OpportunityID]      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Causale Reconstructie Tool:**

```
┌─────────────────────────────────────────────────────────────┐
│  CAUSALE RECONSTRUCTIE: Trade #1                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Complete Event Chain                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │  10:29:55  MarketDataReceived                       │    │
│  │     ↓                                                │    │
│  │  10:30:00  ContextEnriched                          │    │
│  │     ├─→ EMA 20/50 crossed                           │    │
│  │     ├─→ Market structure: BOS detected              │    │
│  │     └─→ Session: London killzone                    │    │
│  │     ↓                                                │    │
│  │  10:30:00  OpportunityDetected                      │    │
│  │     💡 OpportunityID: abc-123-xyz                   │    │
│  │     Signal: FVG detected after BOS                  │    │
│  │     Worker: fvg_detector                            │    │
│  │     Score: 85/100                                   │    │
│  │     ↓                                                │    │
│  │  10:30:02  ThreatCheck                              │    │
│  │     ✅ No active threats                            │    │
│  │     Portfolio drawdown: 2.3% (max: 10%)            │    │
│  │     Volatility percentile: 45 (max: 95)            │    │
│  │     ↓                                                │    │
│  │  10:30:05  PlanReady                                │    │
│  │     🆔 TradeID: ghi-789-abc                         │    │
│  │     Entry: 50,125 (limit order)                     │    │
│  │     Stop: 50,050 (liquidity zone)                   │    │
│  │     Target: 50,250 (opposite liquidity)             │    │
│  │     Size: 0.1 BTC (1% risk)                         │    │
│  │     ↓                                                │    │
│  │  10:30:10  TradeExecuted                            │    │
│  │     Entry filled at 50,125                          │    │
│  │     ↓                                                │    │
│  │  14:20:00  TradeExited                              │    │
│  │     Exit reason: Target reached                     │    │
│  │     Exit price: 50,275 (+2.3%)                      │    │
│  │                                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  📈 Context Snapshot at Trade Time:                         │
│  [View Chart] [View Indicators] [View Orderbook]           │
│                                                              │
│  [Export Timeline] [Compare with Similar Trades]           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**TypeScript Interfaces:**

```typescript
// Causale trade analysis DTOs
interface TradeAnalysis {
  tradeId: string;
  opportunityId: string;      // ✨ Waarom geopend
  threatId?: string;          // ✨ Waarom gesloten (als threat)
  openedAt: Date;
  closedAt: Date;
  outcome: "profit" | "loss" | "breakeven";
  pnl: number;
  causaleChain: CausaleEvent[];
}

interface CausaleEvent {
  timestamp: Date;
  eventType: "OPPORTUNITY_DETECTED" | "OPPORTUNITY_ACCEPTED" | "OPPORTUNITY_REJECTED" 
           | "THREAT_DETECTED" | "TRADE_OPENED" | "TRADE_CLOSED";
  opportunityId?: string;
  threatId?: string;
  tradeId?: string;
  details: Record<string, any>;
  reason?: string;             // Voor rejections/closures
}

interface StrategyJournalEntry {
  timestamp: Date;
  eventType: string;
  opportunityId?: string;
  threatId?: string;
  tradeId?: string;
  signalType?: string;
  details: Record<string, any>;
  decision?: "accepted" | "rejected";
  rejectionReason?: string;
}
```

* **Backend Interactie:** De UI roept de Operations-service, OptimizationService en VariantTestService aan. Nieuwe services: `CausaleAnalysisService`, `JournalQueryService`.

---

### **Fase 4: Werkruimte "LIVE MONITORING"**

* **User Goal:** De prestaties van live-operaties continu monitoren met onderscheid tussen operationele staat en analytische geschiedenis.

#### **UI Componenten**

**Live Dashboard:**

```
┌─────────────────────────────────────────────────────────────┐
│  LIVE OPERATION: ICT_SMC_Strategy                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 StrategyLedger (Operationele Staat)                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Capital:           €10,000                         │    │
│  │  Realized PnL:      +€523.45 (+5.23%)              │    │
│  │  Unrealized PnL:    -€12.30 (-0.12%)               │    │
│  │                                                      │    │
│  │  Open Positions: 1                                  │    │
│  │  • BTC/EUR: 0.05 @ 50,125 (2h ago)                │    │
│  │    Current: 50,100 (-0.05%)                         │    │
│  │                                                      │    │
│  │  Recently Closed: 3                                 │    │
│  │  • Trade #12: +2.3% (4h ago)                       │    │
│  │  • Trade #13: +1.8% (6h ago)                       │    │
│  │  • Trade #14: -1.0% (8h ago, threat exit)          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  📜 StrategyJournal (Analytische Historie)                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Total Opportunities Detected: 47                   │    │
│  │  • Accepted: 15 (31.9%)                            │    │
│  │  • Rejected: 32 (68.1%)                            │    │
│  │                                                      │    │
│  │  Rejection Reasons:                                 │    │
│  │  • MAX_DRAWDOWN_THRESHOLD: 18 (56.3%)             │    │
│  │  • HIGH_VOLATILITY: 9 (28.1%)                      │    │
│  │  • NEWS_EVENT: 5 (15.6%)                           │    │
│  │                                                      │    │
│  │  [View Full Journal] [Export Analysis]             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ⚠️ Active Threats (Real-time)                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  🟡 Portfolio Drawdown: 6.2% (Threshold: 10%)      │    │
│  │     🆔 ThreatID: xyz-123-abc                       │    │
│  │     Severity: MEDIUM                                │    │
│  │     Action: Monitoring                              │    │
│  │                                                      │    │
│  │  🟢 Market Volatility: Normal (Percentile: 45)     │    │
│  │  🟢 Connection: Stable (Latency: 23ms)             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  📡 Real-time Causal Event Stream                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  14:25:32  ContextEnriched                          │    │
│  │  14:25:33  OpportunityDetected                      │    │
│  │            💡 OpportunityID: new-789-xyz            │    │
│  │            Type: fvg_entry, Score: 72/100           │    │
│  │  14:25:34  ThreatCheck                              │    │
│  │            ⚠️ ThreatID: thr-456-def                │    │
│  │            Type: PORTFOLIO_RISK (6.2% drawdown)     │    │
│  │  14:25:35  OpportunityRejected                      │    │
│  │            Reason: Risk threshold too close         │    │
│  │            💡 OpportunityID: new-789-xyz REJECTED   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  🚨 EMERGENCY CONTROLS                                      │
│  [⏸️ Pause Strategy] [🛑 Close All Positions] [⚙️ Settings]│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**TypeScript Interfaces:**

```typescript
// Live monitoring DTOs
interface LiveStrategyState {
  ledger: StrategyLedgerSnapshot;
  journal: StrategyJournalSummary;
  activeThreats: ActiveThreat[];
  realtimeEventStream: CausaleEvent[];
}

interface StrategyLedgerSnapshot {
  capital: number;
  realizedPnl: number;
  unrealizedPnl: number;
  openPositions: Position[];
  recentlyClosed: Position[];  // Last 10 for context
}

interface StrategyJournalSummary {
  totalOpportunities: number;
  accepted: number;
  rejected: number;
  rejectionReasons: Record<string, number>;
}

interface ActiveThreat {
  threatId: string;
  threatType: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  details: Record<string, any>;
  timestamp: Date;
  action: "monitoring" | "throttling" | "emergency_exit";
}
```

* Een prominente **"Noodstop"-knop** per strategy_link of voor de hele Operation, die een `ShutdownRequested`-event publiceert.
* **Backend Interactie:** De UI leest de live-staat via API-endpoints die gekoppeld zijn aan de `AggregatePortfolioUpdated`- en `LedgerStateChanged`-events. Nieuw: `JournalStreamService` voor real-time journal updates.

---

### **Fase 5: Werkruimte "PLUGIN DEVELOPMENT"**

* **User Goal:** Het snel en betrouwbaar ontwikkelen en testen van de herbruikbare "LEGO-stukjes" (plugins).
* **UI Componenten:**
  * **Plugin Registry Viewer:** Een overzichtstabel van alle ontdekte plugins met sub-categorie filtering.
  * **Plugin Creator Wizard:** Een formulier om de boilerplate-code voor een nieuwe plugin te genereren, inclusief keuze voor capabilities (stateful/event-aware/journaling).
  * **Unit Test Runner:** Een UI-knop per plugin om de bijbehorende unit tests op de backend uit te voeren.
  * **Capability Selector:** Visuele wizard voor het kiezen van plugin capabilities (BaseWorker, BaseStatefulWorker, BaseEventAwareWorker, BaseJournalingWorker).
* **Backend Interactie:** De UI communiceert met een `PluginQueryService` en een `PluginEditorService`.

---

## **Het Frontend-Backend Contract: BFF & TypeScript**

De naadloze ervaring wordt technisch mogelijk gemaakt door twee kernprincipes:

1. **Backend-for-Frontend (BFF):** De [`frontends/web/api/`](frontends/web/api/) is geen generieke API, maar een **backend die exclusief voor de [`frontends/web/ui/`](frontends/web/ui/) werkt**. Hij levert data in exact het formaat dat de UI-componenten nodig hebben.

2. **Contractuele Zekerheid met TypeScript:** We formaliseren het contract. Een tool in de ontwikkel-workflow leest de Pydantic-modellen en genereert automatisch corresponderende **TypeScript interfaces**. Een wijziging in de backend die niet in de frontend wordt doorgevoerd, leidt onmiddellijk tot een **compile-fout**, niet tot een onverwachte bug in productie.

### **DTO Interfaces**

**DTOs voor causale traceability:**

```typescript
// backend/dtos/pipeline/opportunity_signal.ts (gegenereerd uit Pydantic)
interface OpportunitySignal {
  opportunityId: string;          // ✨ Causale ID
  timestamp: Date;
  asset: string;
  direction: "long" | "short";
  signalType: string;
  metadata: Record<string, any>;
  score?: number;                 // ✨ Opportunity score
}

// backend/dtos/execution/threat_signal.ts
interface ThreatSignal {
  threatId: string;               // ✨ Causale ID
  threatType: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  timestamp: Date;
  details: Record<string, any>;
  affectedStrategy?: string;
}

// backend/dtos/pipeline/trade_plan.ts
interface TradePlan {
  tradeId: string;                // ✨ Trade tracking ID
  opportunityId: string;          // ✨ Causale link naar opportunity
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
  size: number;
  direction: "long" | "short";
  metadata: Record<string, any>;
}

// backend/dtos/execution/routed_trade_plan.ts
interface RoutedTradePlan extends TradePlan {
  routingStrategy: string;
  orderType: "MARKET" | "LIMIT" | "STOP";
  executionTactics?: ExecutionTactics;
}
```

**Event Configuration DTOs:**

```typescript
// backend/core/event_config.ts
interface PluginEventConfig {
  triggers?: string[];            // Events this plugin listens to
  publishes?: PublishedEvent[];   // Events this plugin emits
  requiresAll?: boolean;          // Wait for all triggers?
}

interface PublishedEvent {
  eventName: string;
  payloadType: string;
  description?: string;
}

// backend/core/worker_flow_config.ts
interface WorkerFlowConfig {
  workerType: WorkerType;
  flowStrategy: FlowStrategy;
  rationale?: string;
}
```

### **BFF API Endpoints**

**Endpoints voor causale analyse:**

```typescript
// GET /api/analysis/causal-chain/:tradeId
// Returns complete causal event chain for a trade
interface CausalChainResponse {
  tradeId: string;
  opportunityId: string;
  threatId?: string;
  events: CausaleEvent[];
  contextSnapshots: ContextSnapshot[];
}

// GET /api/journal/:strategyId
// Returns StrategyJournal entries with filtering
interface JournalQueryParams {
  startDate?: Date;
  endDate?: Date;
  eventTypes?: string[];
  opportunityIds?: string[];
  threatIds?: string[];
  includeRejected?: boolean;
}

// GET /api/plugins/registry
// Returns plugin library with sub-category filtering
interface PluginRegistryResponse {
  plugins: PluginCard[];
  subCategories: {
    contextTypes: string[];
    opportunityTypes: string[];
    threatTypes: string[];
    planningPhases: string[];
    executionTypes: string[];
  };
}

// POST /api/workers/configure-flow
// Save worker flow configuration (global or per-strategy)
interface WorkerFlowConfigRequest {
  scope: "global" | "strategy";
  strategyId?: string;
  workers: WorkerFlowConfig[];
}
```

Deze aanpak zorgt voor een robuust, ontkoppeld en tegelijkertijd perfect gesynchroniseerd ecosysteem.

---

## **Platgeslagen Workflow Visualisatie**

### **Strategy Builder met Worker Orkestratie**

**Features:**
- Visuele representatie van worker flow strategies
- Drag-and-drop worker arrangement
- Real-time flow preview
- Event chain validation

**UI Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  STRATEGY BUILDER                                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ Worker Flow Configuration ──────────────────────────┐  │
│  │                                                     │  │
│  │ Context Phase:                                      │  │
│  │ ├─ Flow: SEQUENTIAL                                │  │
│  │ ├─ Workers: ema_detector, market_structure         │  │
│  │ └─ Preview: Worker 1 → Worker 2 → Output           │  │
│  │                                                     │  │
│  │ Opportunity Phase:                                  │  │
│  │ ├─ Flow: PARALLEL                                  │  │
│  │ ├─ Workers: fvg_detector, breakout_scanner         │  │
│  │ └─ Preview: [Worker 1 + Worker 2] → Signals        │  │
│  │                                                     │  │
│  │ Threat Phase:                                       │  │
│  │ ├─ Flow: PARALLEL                                  │  │
│  │ ├─ Workers: max_drawdown_monitor                   │  │
│  │ └─ Preview: Threats → Risk Assessment              │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
│  [Edit Configuration] [Validate] [Save & Run]              │
└─────────────────────────────────────────────────────────────┘
```

### **Event Chain Visualisatie**

**Features:**
- Real-time event flow preview
- Circular dependency detection
- Dead-end event warnings
- Payload type consistency checks

**UI Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  EVENT CHAIN VISUALISATIE                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Your strategy's event flow:                                 │
│                                                              │
│  TRIGGERS (incoming):                                        │
│  ┌────────────────────────────────────────────────┐          │
│  │  on_schedule:weekly_dca                          │          │
│  │  Source: Scheduler (schedule.yaml)              │          │
│  │  Frequency: Every Monday 10:00                  │          │
│  └────────────────────────────────────────────────┘          │
│           │                                                    │
│           ▼                                                    │
│  ┌────────────────────────────────────────────────┐          │
│  │  adaptive_dca_planner.process()                 │ ◀─ YOU   │
│  └────────────────────────────────────────────────┘          │
│           │                                                    │
│           ▼                                                    │
│  PUBLISHES (outgoing):                                       │
│  ┌────────────────────────────────────────────────┐          │
│  │  dca_opportunity_scored (Signal)                │          │
│  │  Subscribers: [2 found ✓]                      │          │
│  │  ├─ dca_risk_assessor                           │          │
│  │  └─ strategy_logger                             │          │
│  └────────────────────────────────────────────────┘          │
│                                                              │
│  Validation Results:                                         │
│  ✓ All triggers have publishers                             │
│  ✓ All published events have subscribers                    │
│  ✓ No circular dependencies detected                        │
│  ✓ Payload DTO types are consistent                         │
│                                                              │
│  [← Back] [Save Configuration]                               │
└─────────────────────────────────────────────────────────────┘
```

---

## **Architectuur Features: Samenvatting**

### **UI Componenten**

**Strategy Builder:**
- ✨ **5-Worker Categorieën Layout** met visuele scheiding
- ✨ **27 Sub-Categorie Filters** in plugin bibliotheek
- ✨ **Worker Flow Configuration** met data flow preview
- ✨ **Capability Indicators** op plugin cards
- ✨ **Causale ID Information** in configuratie panels

**Backtesting & Analysis:**
- ✨ **Causale ID Filtering** (OpportunityID, ThreatID, TradeID)
- ✨ **StrategyJournal Viewer** met rejected opportunities
- ✨ **Causale Reconstructie Tool** (complete event chain)
- ✨ **Event Chain Visualizer** (grafische weergave)

**Live Monitoring:**
- ✨ **Ledger vs Journal** gescheiden displays
- ✨ **Real-time Causal Event Stream** viewer
- ✨ **Threat Detection Alerts** met ThreatID linking
- ✨ **Rejection Reasons Dashboard** (waarom werden kansen afgewezen)

### **TypeScript Type Safety**

**Het systeem biedt volledige type safety voor:**
- ✅ Alle 5 worker categorieën + 27 sub-types
- ✅ Event configuration (triggers, publishes, requiresAll)
- ✅ Worker flow configuration (flow strategies)
- ✅ Causale IDs (OpportunityID, ThreatID, TradeID, ScheduledID)
- ✅ Plugin capabilities (Stateful, EventAware, Journaling)
- ✅ StrategyJournal entries met causale links

### **User Experience Improvements**

**Voor de Beginner:**
- Impliciete event chains (geen configuratie nodig)
- Duidelijke worker categorieën met beschrijvende namen
- Gefilterde plugin bibliotheek (alleen compatibele plugins)
- Automatische causale ID generatie

**Voor de Intermediate:**
- Predefined triggers (eenvoudige event configuratie)
- Sub-categorie filtering voor betere plugin discovery
- Worker flow configuratie UI met rationale
- Trade Explorer met causale filtering

**Voor de Expert:**
- Custom event chains met visuele editor
- Event chain validation en preview
- Complete causale reconstructie tools
- Worker flow override per strategy

---

## **Implementatie Prioriteiten**

### **Phase 1: Core Support (Must Have)**

1. ✅ **5 Worker Categorieën** in Workforce Builder
2. ✅ **27 Sub-Categorie Filtering** in Plugin Library
3. ✅ **Capability Indicators** op plugin cards
4. ✅ **Basic Causale ID Display** in Trade Explorer

**Tijdsinschatting:** 4 weken

### **Phase 2: Worker Flow Configuration (Important)**

1. ✅ **Worker Flow Configuration UI**
2. ✅ **Data Flow Preview** componenten
3. ✅ **Strategy Override** support

**Tijdsinschatting:** 3 weken

### **Phase 3: Advanced Causale Features (Nice to Have)**

1. ✅ **StrategyJournal Viewer** met rejected opportunities
2. ✅ **Causale Reconstructie Tool**
3. ✅ **Real-time Event Stream**
4. ✅ **Threat Detection Dashboard**

**Tijdsinschatting:** 3 weken

**Totaal:** ~10 weken (2.5 maanden) voor volledige UI support

---

## **Gerelateerde Documenten**

Voor diepere uitwerkingen van specifieke concepten:

- **Architectuur:** [`2_Architectuur_Componenten.md`](2_Architectuur_Componenten.md) - V3 Core architectuur
- **Worker Taxonomie:** [`WORKER_TAXONOMIE_V3.md`](../development/251014%20Bijwerken%20documentatie/WORKER_TAXONOMIE_V3.md) - Volledige 5-categorieën + 27 sub-types uitwerking
- **Configuratie:** [`3_Configuratie_Trein.md`](3_Configuratie_Trein.md) - YAML configuratie inclusief worker flow
- **Plugin Anatomie:** [`4_Plugin_Anatomie.md`](4_Plugin_Anatomie.md) - Plugin capabilities en event configuration
- **Workflow:** [`5_Workflow_Orkestratie.md`](5_Workflow_Orkestratie.md) - Event workflows en causale IDs

---

## **Conclusie**

De frontend integratie transformeert de UI van een simpele presentatielaag naar een volledig geïntegreerde IDE voor kwantitatieve strategen. De 6 paradigma-shifts worden allemaal ondersteund met intuïtieve, krachtige UI componenten die de complexiteit verbergen voor beginners maar de volledige kracht beschikbaar maken voor experts.

**Kernvoordelen:**
- ✅ **Intuïtiever:** 5 duidelijke worker categorieën + 27 herkenbare sub-types
- ✅ **Krachtiger:** Volledige causale traceability ("waarom werd deze trade geopend/gesloten?")
- ✅ **Flexibeler:** Worker flow configuratie (van simpel naar expert)
- ✅ **Transparanter:** Ledger/Journal scheiding + rejected opportunities logging
- ✅ **Configureerbaar:** Worker flow aanpasbaar zonder code wijzigingen

**De "Bouwen → Meten → Leren" cyclus is nu sneller dan ooit:**
- **Bouwen:** Visuele workforce builder met intelligente filtering (minuten)
- **Meten:** Real-time causale event stream + threat detection (seconden)
- **Leren:** Complete causale reconstructie + afgewezen kansen analyse (minuten)

---

**Einde Frontend Integratie Document**