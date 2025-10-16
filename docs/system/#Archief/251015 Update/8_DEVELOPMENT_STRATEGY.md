# **8. Ontwikkelstrategie & Tooling**

**Versie:** 3.0 (V3 Architectuur - Event-Driven & Opt-in Complexiteit)  
**Status:** Definitief  
**Laatst Bijgewerkt:** 2025-10-14

Dit document beschrijft de methodiek, de workflow en de tooling voor het ontwikkelen, testen en debuggen van het S1mpleTrader V3 ecosysteem. Het is de blauwdruk voor een snelle, efficiënte en data-gedreven ontwikkelomgeving met volledige event-driven capabilities.

---

## **Inhoudsopgave**

1. [Filosofie: Rapid, Lean & Progressive Complexity](#81-filosofie-rapid-lean--progressive-complexity)
2. [De "Supercharged" Ontwikkelcyclus](#82-de-supercharged-ontwikkelcyclus)
3. [Plugin Development Workflow (V3)](#83-plugin-development-workflow-v3)
4. [Event Debugging Tools](#84-event-debugging-tools-nieuw)
5. [De Tooling in Detail](#85-de-tooling-in-detail)
6. [Development Workflow per Worker Type](#86-development-workflow-per-worker-type)
7. [Testing Strategieën](#87-testing-strategieën)
8. [Logging & Traceability](#88-logging--traceability)

---

## **8.1. Filosofie: Rapid, Lean & Progressive Complexity**

### **8.1.1. Kernprincipes**

We stappen af van een traditionele, op de CLI gerichte workflow. De nieuwe filosofie is gebaseerd op een combinatie van **Lean UX**, **User-Centered Design (UCD)** en **Progressive Complexity**, met als doel een "supercharged" ontwikkelcyclus te creëren.

* **De Gebruiker staat Centraal:** De primaire gebruiker ("De Kwantitatieve Strateeg") en diens workflow bepalen wat we bouwen en in welke volgorde. De Web UI is het centrale instrument.
* **Compact Ontwikkelen:** We bouwen in de kleinst mogelijke, onafhankelijke eenheden (een plugin) en testen deze geïsoleerd.
* **Opt-in Complexiteit:** Start simpel (90% blijft [`BaseWorker`](../../backend/core/base_worker.py)), voeg alleen capabilities toe wanneer echt nodig.
* **Direct Testen:** Elke plugin wordt vergezeld van unit tests. Geen enkele component wordt als "klaar" beschouwd zonder succesvolle, geautomatiseerde tests.
* **Snelle Feedback Loop (Bouwen → Meten → Leren):** De tijd tussen een idee, een codewijziging en het zien van het visuele resultaat moet minimaal zijn. De Web UI is de motor van deze cyclus.
* **Event-Driven is Optioneel:** Gebruik events alleen wanneer nodig - 95% van plugins gebruikt de impliciete pijplijn.

### **8.1. Filosofie: Rapid, Lean & De Scheiding van ROL en CAPABILITIES**

De ontwikkelstrategie van V3 is gebouwd op een fundamenteel principe: de strikte scheiding tussen de **ROL** van een worker (zijn architecturale doel) en zijn **CAPABILITIES** (zijn extra vaardigheden). Dit vervangt de oude "complexiteitsniveaus".

**Pijler 1: De ROL Bepaalt de Workflow (Code)**

De ontwikkelaar maakt een expliciete, architecturale keuze door een van de twee basisklassen te kiezen. Dit bepaalt hoe de worker wordt aangestuurd.

-   **`StandardWorker` (90% van de gevallen)**
    -   **ROL**: Een deelnemer in een voorspelbare, door een operator georkestreerde pijplijn (sequentieel of parallel).
    -   **Gebruik**: Voor alle lineaire data-transformaties. "Het werkt gewoon."

-   **`EventDrivenWorker` (10% van de gevallen)**
    -   **ROL**: Een autonome agent die reageert op events en onafhankelijk van een operator-pijplijn functioneert.
    -   **Gebruik**: Voor complexe, asynchrone workflows, monitoring, of wanneer een worker op meerdere triggers moet reageren.

**Pijler 2: CAPABILITIES Bepalen de Vaardigheden (Configuratie)**

Alle extra vaardigheden worden aangevraagd in de `capabilities`-sectie van het `manifest.yaml`. De `WorkerBuilder` leest dit manifest en injecteert de benodigde functionaliteit dynamisch in de worker-instantie.

```yaml
# manifest.yaml
capabilities:
  # Vraagt state-persistence aan.
  # De WorkerBuilder injecteert 'self.state' en 'self.commit_state()'.
  state:
    enabled: true
    state_dto: "dtos.state_dto.MyWorkerState"

  # Vraagt event-communicatie aan.
  # De WorkerBuilder injecteert 'self.emit()' en koppelt de wirings.
  events:
    enabled: true
    publishes:
      - as_event: "MyCustomEvent"
        payload_dto: "MyCustomDTO"
    wirings:
      - listens_to: "SomeTrigger"
        invokes:
          method: "on_some_trigger"
```

Deze "opt-in" benadering houdt de basis-worker extreem simpel en veilig, en de complexiteit wordt alleen toegevoegd waar het expliciet nodig is.

---

## **8.2. De "Supercharged" Ontwikkelcyclus**

De gehele workflow, van het bouwen van een strategie tot het analyseren van de resultaten, vindt plaats binnen de naadloze, visuele webapplicatie.

### **8.2.1. Fase 1: Visuele Strategie Constructie (De "Strategy Builder")**

**Doel:** Snel en foutloos een nieuwe strategie ([`strategy_blueprint.yaml`](../../config/runs/strategy_blueprint.yaml)) samenstellen.

**V3 Updates:**
- Worker type selector met 5 hoofdcategorieën
- Sub-categorie filter met 27 opties
- Capability badges (State, Events, Journaling)
- Event topology preview
- Operator configuratie visualisatie

**Proces:**
1. De gebruiker opent de "Strategy Builder" in de Web UI.
2. In een zijbalk verschijnen alle beschikbare plugins, opgehaald via een API en gegroepeerd per type en sub-type:
   ```
   ├─ ContextWorker (12)
   │  ├─ Regime Classification (3)
   │  ├─ Structural Analysis (4)
   │  └─ Indicator Calculation (5)
   ├─ OpportunityWorker (23)
   │  ├─ Technical Pattern (8) ⭐⭐⭐⭐⭐
   │  ├─ Momentum Signal (5) ⭐⭐⭐⭐
   │  └─ Mean Reversion (3) ⭐⭐⭐
   ├─ ThreatWorker (8)
   │  ├─ Portfolio Risk (3)
   │  └─ Market Risk (2)
   ├─ PlanningWorker (15)
   │  ├─ Entry Planning (4)
   │  ├─ Exit Planning (5)
   │  ├─ Size Planning (3)
   │  └─ Order Routing (3)
   └─ ExecutionWorker (6)
      ├─ Trade Initiation (2)
      ├─ Position Management (2)
      └─ Operational (2)
   ```
3. De gebruiker sleept plugins naar de "slots" in een visuele weergave van de workforce.
4. Voor elke geplaatste plugin genereert de UI automatisch een configuratieformulier op basis van de [`schema.py`](../../plugins/) van de plugin. Input wordt direct in de browser gevalideerd.
5. **NIEUW:** Event-aware plugins tonen een "⚡ Configure Events" knop voor event setup.
6. **NIEUW:** Real-time event chain validatie tijdens het bouwen.
7. Bij het opslaan wordt de configuratie als YAML op de server aangemaakt.

**Operator Configuratie Visualisatie:**

```yaml
# Automatisch gegenereerd op basis van operators.yaml
Operators:
  Context    → SEQUENTIAL  → CHAIN_THROUGH
  Opportunity → PARALLEL   → COLLECT_ALL
  Threat     → PARALLEL   → COLLECT_ALL
  Planning   → SEQUENTIAL  → CHAIN_THROUGH
  Execution  → EVENT_DRIVEN → NONE
```

### **8.2.2. Fase 2: Interactieve Analyse (De "Backtesting Hub")**

**Doel:** De gebouwde strategieën rigoureus testen en de resultaten diepgaand analyseren.

**V3 Updates:**
- Causale ID filtering (opportunity_id, threat_id, trade_id)
- Event flow timeline visualizer
- Rejection reason analysis
- Event chain performance metrics

**Proces:**
1. **Run Launcher:** Vanuit de UI start de gebruiker een backtest of optimalisatie voor een specifieke Operation.
2. **Live Progress:** Een dashboard toont de live voortgang met event counts.
3. **Resultaten Analyse:**
   * **Optimalisatie:** Resultaten verschijnen in een interactieve tabel (sorteren, filteren).
   * **Diepgaande Analyse (Trade Explorer):** De gebruiker kan doorklikken naar een enkele run en door individuele trades bladeren, waarbij een interactieve grafiek alle contextuele data (marktstructuur, indicatoren, etc.) toont op het moment van de trade.
   * **NIEUW - Causale Reconstructie:** Voor elke trade:
     - Klik op trade → Toont opportunity_id → Navigeer naar origineel signaal
     - Bekijk waarom trade werd geopend (opportunity details)
     - Bekijk waarom trade werd gesloten (threat_id indien van toepassing)
     - Visualiseer volledige beslissingsketen

**Trade Explorer - Causale View:**

```
Trade #42 (BTC/EUR)
├─ Opened: 2025-10-14 10:05:00
│  └─ Opportunity ID: uuid-456 ← Klikbaar
│     ├─ Type: fvg_entry (Technical Pattern)
│     ├─ Detector: fvg_detector
│     ├─ Context: Market structure break detected
│     └─ Metadata: {gap_size: 8.5, volume_percentile: 85}
│
├─ Modified: 2025-10-14 11:30:00
│  └─ Threat ID: uuid-789 ← Klikbaar
│     ├─ Type: MAX_DRAWDOWN_BREACHED
│     ├─ Detector: max_drawdown_monitor
│     └─ Action: Stop moved to breakeven
│
└─ Closed: 2025-10-14 14:00:00
   └─ Reason: Take profit hit
   └─ P&L: +€125.00
```

### **8.2.3. Fase 3: De Feedback Loop**

**Doel:** Een inzicht uit de analysefase direct omzetten in een verbetering.

**V3 Updates:**
- Event chain aanpassing direct vanuit Trade Explorer
- Plugin capability upgrade suggesties
- A/B testing voor event-driven vs. impliciete workflows

**Proces:** Vanuit de "Trade Explorer" klikt de gebruiker op "Bewerk Strategie". Hij wordt direct teruggebracht naar de "Strategy Builder" met de volledige [`strategy_blueprint.yaml`](../../config/runs/strategy_blueprint.yaml) al ingeladen, klaar om een aanpassing te doen. De cyclus begint opnieuw.

---

## **8.3. Plugin Development Workflow (V3)**

### **8.3.1. De Nieuwe Plugin Wizard - Intelligente Begeleiding**

De Plugin IDE leidt de ontwikkelaar door een gestructureerd proces.

**Stap 1: ROL Selectie**

De wizard stelt de fundamentele vraag:

> "Is deze worker onderdeel van een voorspelbare, stapsgewijze pijplijn, of moet hij autonoom reageren op onvoorspelbare events?"

-   **Pijplijn → `StandardWorker`**: De wizard genereert een `worker.py` met een `process()`-methode.
-   **Autonoom → `EventDrivenWorker`**: De wizard genereert een lege `worker.py` (zonder `process()`-methode) en adviseert om de `events`-capability in het manifest te configureren.

**Stap 2: Capability Selectie (via Manifest)**

In plaats van een "beslisboom" voor basisklassen, presenteert de wizard nu een "capability matrix" die direct het `manifest.yaml`-bestand aanpast.

```
┌──────────────────────────────────────────────────┐
│ 🔧 CAPABILITIES (manifest.yaml)                  │
│                                                   │
│ [ ] State Persistence (state)                    ℹ️  │
│     Voegt 'self.state' en 'self.commit_state()' toe │
│                                                   │
│ [ ] Event Communication (events)                 ℹ️  │
│     Voegt 'self.emit()' toe en configureert      │
│     'publishes' en 'wirings'.                    │
│                                                   │
│ [ ] Historical Journaling (journaling)           ℹ️  │
│     Voegt 'self.log_entries()' toe.              │
└──────────────────────────────────────────────────┘
```

Wanneer een checkbox wordt aangevinkt, wordt de corresponderende sectie automatisch aan het `manifest.yaml` toegevoegd, klaar om geconfigureerd te worden.

**Stap 3: Code Generatie**

De wizard genereert code die past bij de gekozen ROL, en voegt commentaar toe dat verwijst naar de aangevraagde capabilities.

**Voorbeeld: `StandardWorker` met `state` capability**

```python
# Auto-generated by S1mpleTrader Plugin IDE v3.1
# ROL: StandardWorker
# Capabilities: [state]

from backend.core.base_worker import StandardWorker
from backend.dtos.state.trading_context import TradingContext

class MyStatefulWorker(StandardWorker):
    """
    Deze worker heeft de 'state' capability aangevraagd in zijn manifest.
    'self.state' en 'self.commit_state()' zullen dynamisch
    worden geïnjecteerd door de WorkerBuilder.
    """
    def process(self, context: TradingContext) -> None:
        # Voorbeeld van state-gebruik
        counter = self.state.get('counter', 0)
        self.state['counter'] = counter + 1
        self.commit_state() # Slaat de state atomisch op
```

---

## **8.4. Event Debugging Tools** ✨ **NIEUW**

### **8.4.1. Event Chain Validator Output**

**Toegang:** Tools → Event Chain Validator

**Doel:** Valideer event integriteit tijdens ontwikkeling en startup.

**Output Format:**

```
┌──────────────────────────────────────────────────────┐
│ Event Chain Validation Results                       │
│ Strategy: mss_fvg_strategy                           │
│ Timestamp: 2025-10-14 10:00:00                       │
├──────────────────────────────────────────────────────┤
│                                                       │
│ ✓ Check 1: Publisher/Subscriber Consistency          │
│   All 12 events have valid publishers                │
│                                                       │
│ ✓ Check 2: Circular Dependencies                     │
│   No circular event chains detected                  │
│                                                       │
│ ⚠️ Check 3: Dead-End Events                          │
│   Warning: 'debug_signal_logged' has no subscribers │
│   Published by: fvg_detector                         │
│   Recommendation: Remove or add subscriber           │
│                                                       │
│ ✓ Check 4: Payload DTO Type Consistency              │
│   All event payloads match expected types            │
│                                                       │
├──────────────────────────────────────────────────────┤
│ Summary: 3/4 passed, 1 warning                       │
│                                                       │
│ [View Details] [Export Report] [Fix Warnings]        │
└──────────────────────────────────────────────────────┘
```

**Detailed Validation Report:**

```yaml
validation_report:
  timestamp: "2025-10-14T10:00:00Z"
  strategy: "mss_fvg_strategy"
  
  checks:
    - name: "Publisher/Subscriber Consistency"
      status: "PASS"
      events_checked: 12
      
    - name: "Circular Dependencies"
      status: "PASS"
      
    - name: "Dead-End Events"
      status: "WARNING"
      warnings:
        - event: "debug_signal_logged"
          publisher: "fvg_detector"
          subscribers: []
          recommendation: "Add subscriber or remove event"
          
    - name: "DTO Type Consistency"
      status: "PASS"
      
  event_graph:
    nodes: 15
    edges: 22
    longest_chain: 5
```

### **8.4.2. Event Topology Viewer**

**Toegang:** Tools → Event Topology Viewer

**Doel:** Visueel begrip van event chains en dependencies.

**Visual Representation:**

```
┌────────────────────────────────────────────────────────┐
│ Event Topology: mss_fvg_strategy                       │
│                                                         │
│ Filters: [Worker Type ▼] [Event Name: ___________]    │
│ Layout:  [Hierarchical ▼] [Export PNG]                │
├────────────────────────────────────────────────────────┤
│                                                         │
│              ┌───────────────┐                         │
│              │ Environment   │                         │
│              └───────┬───────┘                         │
│                      │ ContextReady                    │
│                      ▼                                  │
│       ┌──────────────────────────┐                     │
│       │ ContextOperator          │                     │
│       │ • ema_detector           │                     │
│       │ • market_structure       │                     │
│       └──────────┬───────────────┘                     │
│                  │ ContextEnriched                     │
│           ┌──────┴──────┬──────────────┐              │
│           ▼             ▼              ▼               │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│    │Opportun- │  │ Threat   │  │Scheduler │          │
│    │ity Op    │  │ Op       │  │          │          │
│    │fvg_det   │  │max_dd    │  │weekly_dca│          │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│         │             │             │                  │
│         │SignalsGen   │ThreatsDetect│WEEKLY_DCA       │
│         └──────┬──────┴──────┬──────┘                 │
│                ▼             ▼                         │
│        ┌───────────────────────────┐                  │
│        │ PlanningOperator           │                  │
│        │ • entry: limit_planner    │                  │
│        │ • exit: liquidity_target  │                  │
│        │ • size: fixed_risk        │                  │
│        │ • route: default_router   │                  │
│        └─────────┬─────────────────┘                  │
│                  │ PlansReady                         │
│                  ▼                                     │
│        ┌─────────────────────┐                        │
│        │ ExecutionOperator    │                        │
│        │ default_executor     │                        │
│        └──────────────────────┘                        │
│                                                         │
│ Click node for details | Click edge for payload schema│
└────────────────────────────────────────────────────────┘
```

**Node Detail Panel:**

```
┌────────────────────────────────────────┐
│ Plugin: fvg_detector                   │
│ Type: OpportunityWorker                │
│ Sub-type: Technical Pattern            │
├────────────────────────────────────────┤
│ Triggers:                              │
│ └─ ContextEnriched (implicit)          │
│                                         │
│ Publishes:                             │
│ └─ SignalsGenerated (via operator)     │
│                                         │
│ Dependencies:                          │
│ Requires: high, low, close             │
│ Provides: Signal DTOs                  │
│                                         │
│ Base Class: BaseWorker                 │
│ Complexity: 0 ⭐ (Simple)               │
│                                         │
│ [View Source] [Edit] [Clone]           │
└────────────────────────────────────────┘
```

### **8.4.3. Causale ID Tracer**

**Toegang:** Trade Explorer → Select Trade → [Trace Causality]

**Doel:** Reconstructeer volledige beslissingsketen voor één trade.

**Trace Output:**

```
┌────────────────────────────────────────────────────────┐
│ Causale Reconstructie: Trade #42                       │
│ Asset: BTC/EUR | Entry: €50,100 | Exit: €50,225       │
│ P&L: +€125.00 | Duration: 3h 55m                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│ 🔍 OPPORTUNITY DETECTION                                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                         │
│ Timestamp: 2025-10-14 10:00:00                         │
│ Opportunity ID: uuid-abc-123 ← ROOT CAUSE              │
│                                                         │
│ Plugin: fvg_detector (OpportunityWorker)               │
│ Type: Technical Pattern / FVG Entry                    │
│                                                         │
│ Context at Detection:                                  │
│ • Market Structure: Bullish Break of Structure         │
│ • EMA Alignment: 20 > 50 > 200 (trending up)          │
│ • Volume: 85th percentile spike                        │
│ • Gap Size: 8.5 pips                                   │
│                                                         │
│ Signal Metadata:                                       │
│ {                                                      │
│   "gap_size": 8.5,                                    │
│   "volume_percentile": 85,                            │
│   "bos_confirmed": true,                              │
│   "fvg_midpoint": 50050.00                            │
│ }                                                      │
│                                                         │
│ [View Raw Signal DTO] [Replay Context]                │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ 🎯 PLANNING PHASE                                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                         │
│ Timestamp: 2025-10-14 10:00:05                         │
│ Trade ID: uuid-def-456                                 │
│ Linked to: Opportunity uuid-abc-123 ← CAUSALE LINK     │
│                                                         │
│ Entry Planning:                                        │
│ • Plugin: limit_entry_at_fvg                          │
│ • Entry Price: €50,100 (FVG midpoint)                 │
│ • Order Type: Limit                                    │
│                                                         │
│ Exit Planning:                                         │
│ • Plugin: liquidity_target_exit                       │
│ • Stop Loss: €49,500 (below order block)             │
│ • Take Profit: €51,000 (opposite liquidity)          │
│ • Risk:Reward: 1:1.5                                  │
│                                                         │
│ Size Planning:                                         │
│ • Plugin: fixed_risk_sizer                            │
│ • Risk per Trade: 1.0% of capital                     │
│ • Position Size: 0.02 BTC                             │
│                                                         │
│ [View Full Trade Plan] [Compare With Similar]         │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ 🛡️ THREAT MONITORING (During Trade)                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                         │
│ Timestamp: 2025-10-14 11:30:00                         │
│ Threat ID: uuid-ghi-789                                │
│                                                         │
│ Plugin: max_drawdown_monitor (ThreatWorker)           │
│ Type: Portfolio Risk / Max Drawdown                    │
│ Severity: MEDIUM                                       │
│                                                         │
│ Details:                                               │
│ • Current Drawdown: 1.8%                              │
│ • Max Allowed: 2.0%                                   │
│ • Action Taken: Stop moved to breakeven               │
│ • Reason: "Approaching max drawdown threshold"        │
│                                                         │
│ Impact on Trade #42:                                   │
│ Stop Loss: €49,500 → €50,100 (breakeven)             │
│ Result: Protected profit when price dipped            │
│                                                         │
│ [View Full Threat Event] [See Other Affected Trades]  │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ ⚡ EXECUTION EVENTS                                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                         │
│ 10:05:00 - Trade Opened                                │
│ │ Entry: €50,100                                       │
│ │ Size: 0.02 BTC                                       │
│ │                                                       │
│ 11:30:00 - Stop Modified (Threat Response)             │
│ │ New Stop: €50,100 (breakeven)                        │
│ │ Threat ID: uuid-ghi-789                              │
│ │                                                       │
│ 14:00:00 - Trade Closed                                │
│ │ Exit: €50,225                                        │
│ │ Reason: Take profit hit                              │
│ │ P&L: +€125.00                                        │
│                                                         │
└────────────────────────────────────────────────────────┘

[Export Trace] [Compare With Similar Trades] [Replay]
```

### **8.4.4. Event Flow Timeline Visualizer**

**Toegang:** Tools → Event Timeline

**Doel:** Chronologische visualisatie van alle events tijdens een run.

**Timeline View:**

```
┌────────────────────────────────────────────────────────┐
│ Event Flow Timeline                                     │
│ Run: mss_fvg_backtest_20251014                         │
│ Duration: 24h | Events: 1,247 | Trades: 23             │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Filter: [Event Type ▼] [Worker ▼] [Search: _______]   │
│ Zoom:   [1h] [4h] [1d] [All]                           │
│                                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                         │
│ 00:00 ├─────────────────────────────────────────────┤ │
│       │                                              │ │
│ 02:00 │  ●  ContextReady                            │ │
│       │   └─> SignalsGenerated (2 signals)          │ │
│       │       └─> PlansReady (2 plans)              │ │
│       │           └─> Trade Opened #1               │ │
│       │                                              │ │
│ 04:00 │  ●  ContextReady                            │ │
│       │   └─> SignalsGenerated (1 signal)           │ │
│       │       ⚠️  ThreatsDetected (Volatility Spike)│ │
│       │       └─> PlansReady (rejected due to risk) │ │
│       │                                              │ │
│ 06:00 │  ●  Trade Closed #1 (+€85)                  │ │
│       │                                              │ │
│ 08:00 │  ●  ContextReady                            │ │
│       │   └─> SignalsGenerated (3 signals)          │ │
│       │       └─> PlansReady (3 plans)              │ │
│       │           ├─> Trade Opened #2               │ │
│       │           ├─> Trade Opened #3               │ │
│       │           └─> Trade Opened #4               │ │
│       │                                              │ │
│ 10:00 │  ⏰ WEEKLY_DCA_TICK (Scheduled)             │ │
│       │   ├─> dca_opportunity_scored                │ │
│       │   └─> dca_risk_assessed                     │ │
│       │       └─> dca_plan_ready                    │ │
│       │           └─> DCA Purchase Executed         │ │
│       │                                              │ │
│ 12:00 │  ⚠️  MAX_DRAWDOWN_BREACHED                  │ │
│       │   └─> Emergency: All stops → breakeven     │ │
│       │                                              │ │
│ ...   │                                              │ │
│       │                                              │ │
│ 24:00 ├─────────────────────────────────────────────┤ │
│                                                         │
│ Click any event for details                            │
│ Click trade marker to jump to Trade Explorer           │
│                                                         │
└────────────────────────────────────────────────────────┘

Legend:
● Normal event    ⚠️ Threat event    ⏰ Scheduled    💰 Trade
```

**Event Detail Popup:**

```
┌─────────────────────────────────────────┐
│ Event: SignalsGenerated                 │
│ Time: 2025-10-14 02:00:00               │
├─────────────────────────────────────────┤
│ Operator: OpportunityOperator           │
│ Workers Executed: 3 (parallel)          │
│                                          │
│ Results:                                 │
│ • fvg_detector: 1 signal                │
│   └─ opportunity_id: uuid-abc-123       │
│ • breakout_scanner: 1 signal            │
│   └─ opportunity_id: uuid-def-456       │
│ • divergence_finder: 0 signals          │
│                                          │
│ Total Signals: 2                        │
│ Execution Time: 42ms                    │
│                                          │
│ [View Full Context] [Replay]            │
└─────────────────────────────────────────┘
```

---

## **8.5. De Tooling in Detail**

### **8.5.1. Gespecialiseerde Entrypoints**

De applicatie kent drie manieren om gestart te worden, elk met een eigen doel:

* **[`run_web.py`](../../run_web.py) (De IDE):** Het primaire entrypoint voor de ontwikkelaar. Start de FastAPI-server die de Web UI en de bijbehorende API's serveert.
* **[`run_backtest_cli.py`](../../run_backtest_cli.py) (De Robot):** De "headless" entrypoint voor het uitvoeren van een Operation, ideaal voor automatisering, zoals regressietesten en Continuous Integration (CI/CD) workflows.
* **[`run_supervisor.py`](../../run_supervisor.py) (De Productie-schakelaar):** De minimalistische, robuuste starter voor de live trading-omgeving, die het Operations-proces monitort.

### **8.5.2. Strategy Builder met Operator Configuratie**

**V3 Enhancement:** Visuele representatie van operator gedrag.

```
┌────────────────────────────────────────────────────────┐
│ Strategy Builder                                        │
│                                                         │
│ ┌─ Operator Configuration Preview ──────────────────┐  │
│ │                                                    │  │
│ │ Context Phase:                                     │  │
│ │ ├─ Execution: SEQUENTIAL                          │  │
│ │ ├─ Aggregation: CHAIN_THROUGH                     │  │
│ │ └─ Workers (2):                                    │  │
│ │    ├─ ema_detector                                │  │
│ │    └─ market_structure_detector                   │  │
│ │                                                    │  │
│ │ Opportunity Detection:                             │  │
│ │ ├─ Execution: PARALLEL ⚡                         │  │
│ │ ├─ Aggregation: COLLECT_ALL                       │  │
│ │ └─ Workers (2):                                    │  │
│ │    ├─ fvg_detector                                │  │
│ │    └─ volume_spike_refiner                        │  │
│ │                                                    │  │
│ │ Threat Monitoring:                                 │  │
│ │ ├─ Execution: PARALLEL ⚡                         │  │
│ │ ├─ Aggregation: COLLECT_ALL                       │  │
│ │ └─ Workers (1):                                    │  │
│ │    └─ max_drawdown_monitor                        │  │
│ │                                                    │  │
│ │ Planning Phase:                                    │  │
│ │ ├─ Execution: SEQUENTIAL                          │  │
│ │ ├─ Aggregation: CHAIN_THROUGH                     │  │
│ │ └─ Sub-phases:                                     │  │
│ │    ├─ Entry: limit_entry_planner                  │  │
│ │    ├─ Exit: liquidity_target_exit                 │  │
│ │    ├─ Size: fixed_risk_sizer                      │  │
│ │    └─ Route: default_router                       │  │
│ │                                                    │  │
│ │ Execution Phase:                                   │  │
│ │ ├─ Execution: EVENT_DRIVEN 📡                     │  │
│ │ ├─ Aggregation: NONE                              │  │
│ │ └─ Workers (1):                                    │  │
│ │    └─ default_plan_executor                       │  │
│ │                                                    │  │
│ └────────────────────────────────────────────────────┘  │
│                                                         │
│ [Edit Configuration] [Validate] [Save & Run]           │
└────────────────────────────────────────────────────────┘
```

### **8.5.3. Trade Explorer met Causale Reconstructie**

**V3 Enhancement:** Volledige causale chain visualisatie per trade.

**Features:**
- Click op trade → Toon opportunity_id → Navigeer naar origineel signaal
- Bekijk alle threats die deze trade beïnvloedden
- Visualiseer volledige beslissingsketen
- Export causale graph als diagram
- Compare met similar trades (zelfde opportunity type)

**Causale Graph View:**

```
Trade #42 Beslissingsketen:

2025-10-14 10:00:00
    ├─ [CONTEXT] Market Structure Break Detected
    │  Plugin: market_structure_detector
    │  Output: is_bos=true, trend_direction='bullish'
    │
    └─> [OPPORTUNITY] FVG Entry Signal
        Opportunity ID: uuid-abc-123
        Plugin: fvg_detector
        Metadata: gap_size=8.5, volume_percentile=85
        │
        └─> [PLANNING] Entry/Exit/Size Planning
            Trade ID: uuid-def-456
            Entry: €50,100 | Stop: €49,500 | Target: €51,000
            Size: 0.02 BTC (1% risk)
            │
            └─> [EXECUTION] Trade Opened
                10:05:00 - Position opened
                │
                ├─> [THREAT] Max Drawdown Warning
                │   11:30:00 - Threat ID: uuid-ghi-789
                │   Plugin: max_drawdown_monitor
                │   Action: Stop moved to breakeven
                │
                └─> [EXECUTION] Trade Closed
                    14:00:00 - Take profit hit
                    Exit: €50,225 | P&L: +€125.00
```

### **8.5.4. Plugin IDE met Capability Selectors**

**V3 Enhancement:** Visuele capability matrix en real-time complexity feedback.

**Features:**
- Interactive beslisboom voor base class selectie
- Live preview van gegenereerde code
- Event configuration wizard (3 niveaus)
- Automatic manifest.yaml generation
- Test template generation met fixtures
- Real-time event chain validatie

---

## **8.6. Development Workflow per Worker Type**

### **8.6.1. ContextWorker Development**

**Karakteristieken:**
- Altijd [`BaseWorker`](../../backend/core/base_worker.py) (geen state/events nodig)
- Input: [`TradingContext`](../../backend/dtos/state/trading_context.py) met base DataFrame
- Output: Verrijkte `TradingContext` met extra kolommen
- Sequential execution in operator

**Workflow:**

```python
# 1. Definieer requirements in manifest.yaml
identification:
  type: "context_worker"
  subtype: "indicator_calculation"

dependencies:
  requires: ['close']  # Input kolommen
  provides: ['ema_20', 'ema_50']  # Output kolommen

# 2. Implementeer pure logica in worker.py
class EMADetector(BaseWorker):
    def process(self, context: TradingContext) -> TradingContext:
        # Pure calculation - geen state, geen events
        context.enriched_df['ema_20'] = \
            context.enriched_df['close'].ewm(span=20).mean()
        context.enriched_df['ema_50'] = \
            context.enriched_df['close'].ewm(span=50).mean()
        
        return context

# 3. Test met fixtures
def test_ema_detector():
    context = create_test_context(prices=[100, 102, 101, 103])
    detector = EMADetector(params)
    
    result = detector.process(context)
    
    assert 'ema_20' in result.enriched_df.columns
    assert result.enriched_df['ema_20'].iloc[-1] > 100
```

### **8.6.2. OpportunityWorker Development**

**Karakteristieken:**
- Meestal [`BaseWorker`](../../backend/core/base_worker.py) (95%)
- Soms [`BaseEventAwareWorker`](../../backend/core/base_worker.py) voor scheduled/complex flows
- Input: Verrijkte [`TradingContext`](../../backend/dtos/state/trading_context.py)
- Output: List van [`Signal`](../../backend/dtos/pipeline/signal.py) DTOs met `opportunity_id`
- Parallel execution in operator

**Workflow (Simpel):**

```python
# manifest.yaml
identification:
  type: "opportunity_worker"
  subtype: "technical_pattern"

dependencies:
  requires: ['high', 'low', 'close', 'is_bos']

# worker.py
class FVGDetector(BaseWorker):
    def process(self, context: TradingContext) -> List[Signal]:
        signals = []
        
        for i in range(len(context.enriched_df) - 3):
            if self._is_fvg(context.enriched_df, i):
                signals.append(Signal(
                    opportunity_id=uuid4(),  # ← Causale ID
                    timestamp=context.enriched_df.index[i],
                    asset=context.asset_pair,
                    direction='long',
                    signal_type='fvg_entry',
                    metadata={'gap_size': self._calc_gap_size(i)}
                ))
        
        return signals
```

**Workflow (Event-Aware):**

```python
# manifest.yaml
identification:
  type: "opportunity_worker"
  subtype: "technical_pattern"

event_config:
  triggers:
    - "on_schedule:weekly_dca"
  publishes:
    - event_name: "dca_opportunity_scored"
      payload_type: "Signal"

# worker.py
class DcaOpportunityScorer(BaseEventAwareWorker):
    def process(self, context: TradingContext) -> List[Signal]:
        score = self._calculate_score(context)
        
        if score > self.params.threshold:
            signal = Signal(
                opportunity_id=uuid4(),
                metadata={'opportunity_score': score}
            )
            
            # Publish voor downstream workers
            self.emit("dca_opportunity_scored", signal)
            
            return [signal]
        
        return []
```

### **8.6.3. ThreatWorker Development**

**Karakteristieken:**
- Meestal [`BaseWorker`](../../backend/core/base_worker.py)
- Vaak gebruikt met predefined triggers (`on_ledger_update`)
- Input: [`TradingContext`](../../backend/dtos/state/trading_context.py) en/of [`StrategyLedger`](../../backend/core/strategy_ledger.py)
- Output: Optional [`CriticalEvent`](../../backend/dtos/execution/critical_event.py) DTO met `threat_id`
- Parallel execution in operator

**Workflow:**

```python
# manifest.yaml
identification:
  type: "threat_worker"
  subtype: "portfolio_risk"

event_config:
  triggers:
    - "on_ledger_update"  # Predefined trigger

# worker.py
class MaxDrawdownMonitor(BaseWorker):
    def process(self, 
                ledger: StrategyLedger,
                context: TradingContext) -> Optional[CriticalEvent]:
        
        current_dd = ledger.calculate_drawdown()
        
        if current_dd > self.params.max_drawdown_percent:
            return CriticalEvent(
                threat_id=uuid4(),  # ← Causale ID
                timestamp=context.current_timestamp,
                threat_type='MAX_DRAWDOWN_BREACHED',
                severity='HIGH',
                metadata={
                    'current_drawdown': current_dd,
                    'max_allowed': self.params.max_drawdown_percent
                }
            )
        
        return None
```

### **8.6.4. PlanningWorker Development**

**Karakteristieken:**
- Altijd [`BaseWorker`](../../backend/core/base_worker.py) voor standard planning
- [`BaseEventAwareWorker`](../../backend/core/base_worker.py) voor complex coordination
- Input: Depends on sub-phase (Signal → EntrySignal → RiskDefinedSignal → TradePlan)
- Output: Next DTO in chain
- Sequential execution (chain through)

**Workflow (Entry Planning):**

```python
# manifest.yaml
identification:
  type: "planning_worker"
  subtype: "entry_planning"

# worker.py
class LimitEntryPlanner(BaseWorker):
    def process(self, signal: Signal) -> EntrySignal:
        # Bepaal entry prijs op basis van signal metadata
        entry_price = self._calculate_entry_price(signal)
        
        return EntrySignal(
            **signal.dict(),  # Inherit all signal fields
            entry_price=entry_price,
            entry_type='LIMIT'
        )
```

**Workflow (Event Coordination):**

```python
# manifest.yaml
identification:
  type: "planning_worker"
  subtype: "entry_planning"

event_config:
  triggers:
    - "dca_opportunity_scored"
    - "dca_risk_assessed"
  requires_all: true  # Wait for BOTH!
  publishes:
    - event_name: "dca_plan_ready"
      payload_type: "TradePlan"

# worker.py
class AdaptiveDCAPlanner(BaseEventAwareWorker):
    def __init__(self, params):
        super().__init__(params)
        self._opportunity_score = None
        self._risk_level = None
    
    def on_event(self, event_name: str, payload: Any):
        if event_name == "dca_opportunity_scored":
            self._opportunity_score = payload.metadata['score']
        elif event_name == "dca_risk_assessed":
            self._risk_level = payload.metadata['risk_level']
    
    def process(self, context: TradingContext) -> Optional[TradePlan]:
        # Only execute when both events received
        if self._opportunity_score is None or self._risk_level is None:
            return None
        
        # Calculate adaptive amount
        amount = self._decide_amount(
            self._opportunity_score,
            self._risk_level
        )
        
        if amount > 0:
            plan = TradePlan(
                trade_id=uuid4(),
                amount=amount,
                # ... rest of plan
            )
            
            self.emit("dca_plan_ready", plan)
            return plan
        
        return None
```

### **8.6.5. ExecutionWorker Development**

**Karakteristieken:**
- [`BaseWorker`](../../backend/core/base_worker.py) voor simple execution
- [`BaseStatefulWorker`](../../backend/core/base_worker.py) voor position management (state nodig)
- [`BaseEventAwareWorker`](../../backend/core/base_worker.py) voor scheduled/emergency actions
- Event-driven execution in operator
- Side effects (market orders, position modifications)

**Workflow (Stateful Position Management):**

```python
# manifest.yaml
identification:
  type: "execution_worker"
  subtype: "position_management"

# worker.py
class TrailingStopManager(BaseStatefulWorker):
    def process(self, 
                context: TradingContext,
                ledger: StrategyLedger) -> None:
        
        for position in ledger.open_positions:
            current_price = context.current_price
            
            # Lees state
            hwm_key = f"hwm_{position.trade_id}"
            hwm = self.state.get(hwm_key, position.entry_price)
            
            # Update high water mark
            if current_price > hwm:
                self.state[hwm_key] = current_price
                self.commit_state()  # ← Atomic write
                
                # Calculate new stop
                new_stop = hwm * (1 - self.params.trail_percent)
                
                # Execute stop modification
                self.execution_env.modify_stop(
                    position.trade_id,
                    new_stop
                )
```

---

## **8.7. Testing Strategieën**

### **8.7.1. Unit Tests per Plugin**

Elke plugin-map krijgt een [`tests/test_worker.py`](../../plugins/). Deze test laadt een stukje voorbeeld-data, draait de [`worker.py`](../../plugins/) erop, en valideert of de output correct is. Dit gebeurt volledig geïsoleerd.

**Test Structure:**

```python
# tests/test_worker.py
import pytest
from backend.dtos.state.trading_context import TradingContext
from plugins.opportunity_workers.fvg_detector.worker import FVGDetector

@pytest.fixture
def test_context():
    """Create minimal test context with FVG pattern."""
    return TradingContext(
        timestamp=...,
        enriched_df=pd.DataFrame({
            'high': [100, 105, 110, 108, 115],
            'low': [98, 103, 109, 107, 113],
            'close': [99, 104, 109, 108, 114]
        }),
        asset_pair='BTC/EUR'
    )

def test_fvg_detector_finds_gap(test_context):
    """Test that FVG detector finds valid gap."""
    detector = FVGDetector(params={'min_gap_size': 5})
    
    signals = detector.process(test_context)
    
    assert len(signals) == 1
    assert signals[0].signal_type == 'fvg_entry'
    assert signals[0].opportunity_id is not None

def test_fvg_detector_no_gap_small_threshold():
    """Test that small gaps are ignored."""
    context = create_context_without_gap()
    detector = FVGDetector(params={'min_gap_size': 10})
    
    signals = detector.process(context)
    
    assert len(signals) == 0
```

**Test Coverage Requirements:**
- ✓ Happy path (normale werking)
- ✓ Edge cases (lege data, edge values)
- ✓ Parameter validation
- ✓ DTO structure validation
- ✓ Voor event-aware: event emission tests

### **8.7.2. Testen van Workers met Capabilities**

Omdat `capabilities` dynamisch worden geïnjecteerd, blijven de workers zelf eenvoudig te testen. We hoeven alleen de geïnjecteerde methodes te mocken.

**Testen van een `state`-capability worker:**

```python
# tests/test_stateful_worker.py
from unittest.mock import MagicMock

def test_my_stateful_worker_updates_state():
    # 1. Maak een instantie van de worker
    worker = MyStatefulWorker(params={})
    
    # 2. Mock de geïnjecteerde attributen
    worker.state = {} # Start met een lege state dictionary
    worker.commit_state = MagicMock() # Mock de commit-methode
    
    # 3. Voer de businesslogica uit
    context = create_test_context()
    worker.process(context)
    
    # 4. Valideer de assertions
    assert worker.state['counter'] == 1
    worker.commit_state.assert_called_once()
```

**Testen van een `events`-capability worker:**

```python
# tests/test_event_worker.py
from unittest.mock import MagicMock

def test_my_event_worker_emits_event():
    # 1. Maak een instantie van de worker
    worker = MyEventWorker(params={})
    
    # 2. Mock de geïnjecteerde 'emit'-methode
    worker.emit = MagicMock()
    
    # 3. Voer de businesslogica uit die een event moet triggeren
    context = create_event_triggering_context()
    worker.process(context)
    
    # 4. Valideer dat 'emit' is aangeroepen met de juiste argumenten
    worker.emit.assert_called_once_with("MyCustomEvent", expected_payload)
```

Deze aanpak zorgt ervoor dat de unit tests van de worker volledig geïsoleerd blijven van de complexiteit van de `PersistorFactory` of de `EventBus`.

### **8.7.3. Integratietests**

Testen de samenwerking tussen de service laag componenten en het Assembly Team.

```python
# tests/integration/test_opportunity_pipeline.py
def test_full_opportunity_pipeline():
    """Test complete flow: Context → Opportunity → Planning."""
    
    # Setup
    blueprint = load_test_blueprint('simple_fvg_strategy.yaml')
    engine = assemble_engine(blueprint)
    
    # Execute one tick
    context = create_test_context()
    engine.process_tick(context)
    
    # Verify operator execution
    assert engine.context_operator.executed
    assert engine.opportunity_operator.executed
    assert engine.planning_operator.executed
    
    # Verify signals generated
    signals = engine.get_generated_signals()
    assert len(signals) > 0
    
    # Verify plans created
    plans = engine.get_created_plans()
    assert len(plans) > 0
    assert plans[0].opportunity_id == signals[0].opportunity_id
```

### **8.7.4. End-to-End Tests**

Een klein aantal tests die via [`run_backtest_cli.py`](../../run_backtest_cli.py) een volledige Operation draaien op een vaste dataset en controleren of het eindresultaat (de PnL) exact overeenkomt met een vooraf berekende waarde.

```python
# tests/e2e/test_full_backtest.py
def test_fvg_strategy_reproducible_results():
    """Test that strategy produces consistent results."""
    
    result = run_backtest(
        strategy='tests/fixtures/fvg_strategy.yaml',
        data='tests/fixtures/btc_eur_2024.parquet',
        start_date='2024-01-01',
        end_date='2024-01-31'
    )
    
    # Verify reproducibility
    assert result.total_pnl == pytest.approx(1250.50, abs=0.01)
    assert result.total_trades == 23
    assert result.win_rate == pytest.approx(0.652, abs=0.001)
```

---

## **8.8. Logging & Traceability**

### **8.8.1. Gelaagde Logging Strategie**

Logging is een multi-inzetbare tool, geen eenheidsworst. We onderscheiden drie lagen:

**Laag 1: stdio (De Console)**
* **Doel:** Alleen voor *initiële, basic development* van een geïsoleerde plugin. Gebruik print() voor de snelle, "vuile" check. Dit is vluchtig en wordt niet bewaard.

**Laag 2: Gestructureerde Logs (JSON)**
* **Doel:** De primaire output voor **backtests en paper trading**. Dit is de *databron* voor analyse.
* **Implementatie:** Een logging.FileHandler die log-records als gestructureerde JSON-objecten wegschrijft naar een logbestand.
* **Principe:** De console blijft schoon. De *echte* output is het log-bestand.

**Laag 3: De "Log Explorer" (Web UI)**
* **Doel:** De primaire interface voor **analyse en debugging**.
* **Implementatie:** Een tool in de frontend die het JSON-logbestand inleest en interactief presenteert, waardoor je kunt filteren op plugin_name of een Causale ID.

### **8.8.2. Traceability met Causale IDs** ✨ **V3 UPGRADE**

**V2 (Oud):** Elk Signal DTO kreeg een simpele `correlation_id` (UUID).

**V3 (Nieuw):** Vier getypeerde causale IDs voor complete "waarom"-analyse:

```python
# 1. OpportunityID - Waarom werd deze trade geopend?
signal = Signal(
    opportunity_id=uuid4(),  # ← Root cause
    timestamp=...,
    signal_type='fvg_entry'
)

# 2. TradeID - Primaire identifier
plan = TradePlan(
    trade_id=uuid4(),
    opportunity_id=signal.opportunity_id,  # ← Causale link!
    ...
)

# 3. ThreatID - Waarom werd deze trade aangepast/gesloten?
threat = CriticalEvent(
    threat_id=uuid4(),
    threat_type='MAX_DRAWDOWN_BREACHED'
)

# 4. ScheduledID - Waarom gebeurde dit nu?
scheduled = ScheduledEvent(
    scheduled_id=uuid4(),
    schedule_name='weekly_dca'
)
```

**Gebruik in StrategyJournal:**

```json
{
  "journal_entries": [
    {
      "timestamp": "2025-10-14T10:00:00Z",
      "event_type": "OPPORTUNITY_DETECTED",
      "opportunity_id": "uuid-abc-123",
      "signal_type": "fvg_entry",
      "metadata": {"gap_size": 8.5}
    },
    {
      "timestamp": "2025-10-14T10:00:05Z",
      "event_type": "TRADE_OPENED",
      "trade_id": "uuid-def-456",
      "opportunity_id": "uuid-abc-123",  // ← Link!
      "entry_price": 50100.0
    },
    {
      "timestamp": "2025-10-14T11:30:00Z",
      "event_type": "TRADE_MODIFIED",
      "trade_id": "uuid-def-456",
      "threat_id": "uuid-ghi-789",  // ← Why modified?
      "modification": "stop_moved_to_breakeven"
    },
    {
      "timestamp": "2025-10-14T14:00:00Z",
      "event_type": "TRADE_CLOSED",
      "trade_id": "uuid-def-456",
      "closure_reason": "take_profit_hit",
      "pnl": 125.00
    }
  ]
}
```

**Analytische Queries:**

```python
# Vind alle trades van een specifieke opportunity
journal.filter(opportunity_id="uuid-abc-123")

# Vind alle trades gesloten door een threat
journal.filter(has_threat_id=True)

# Analyseer rejection rate per threat type
journal.aggregate_rejections_by_threat_type()

# Trace volledige levenscyclus van één trade
journal.trace_trade_lifecycle(trade_id="uuid-def-456")
```

### **8.8.3. Log Explorer UI**

**Features:**
- Multi-dimensionale filtering (worker, event type, causale ID)
- Timeline visualisatie
- Correlation ID tracer
- Export naar CSV/JSON
- Real-time tail mode (live trading)

**Filter UI:**

```
┌────────────────────────────────────────────────────────┐
│ Log Explorer                                            │
├────────────────────────────────────────────────────────┤
│ Filters:                                                │
│ Worker:        [All Workers              ▼]            │
│ Event Type:    [All Events               ▼]            │
│ Opportunity ID: [___________________________]          │
│ Threat ID:      [___________________________]          │
│ Trade ID:       [___________________________]          │
│ Time Range:     [2025-10-14] to [2025-10-14]          │
│                                                         │
│ [Apply Filters] [Clear] [Export]                       │
├────────────────────────────────────────────────────────┤
│ Results: 1,247 entries                                  │
│                                                         │
│ 10:00:00 | fvg_detector       | OPPORTUNITY_DETECTED  │
│          | opportunity_id: uuid-abc-123                │
│          | [View Details] [Trace Lifecycle]            │
│                                                         │
│ 10:00:05 | limit_entry_planner | TRADE_OPENED         │
│          | trade_id: uuid-def-456                      │
│          | opportunity_id: uuid-abc-123 ← LINK         │
│          | [View Details] [Trace Lifecycle]            │
│                                                         │
│ 11:30:00 | max_drawdown_monitor | THREAT_DETECTED     │
│          | threat_id: uuid-ghi-789                     │
│          | [View Details] [See Affected Trades]        │
│                                                         │
│ ...                                                     │
└────────────────────────────────────────────────────────┘
```

---

## **8.9. Samenvatting: De V3 Verbeteringen**

### **8.9.1. Wat is er Nieuw?**

| Aspect | V2 | V3 |
|--------|----|----|
| **Worker Taxonomie** | 4 categorieën | 5 categorieën + 27 sub-types |
| **Plugin Capabilities** | Gemengd | Opt-in via base class hierarchy |
| **Event System** | Geen | 3 abstractieniveaus (Implicit → Predefined → Custom) |
| **Causale IDs** | Simpele correlation_id | 4 getypeerde IDs (Opportunity, Trade, Threat, Scheduled) |
| **Event Debugging** | Geen | Validator, Topology Viewer, Timeline |
| **Strategy Builder** | Basic | Met operator configuratie preview |
| **Trade Explorer** | Simpel | Met causale reconstructie |
| **Plugin IDE** | Template generator | Met capability selector & event wizard |

### **8.9.2. Kernvoordelen**

✅ **Progressive Complexity** - Start simpel, voeg toe wat nodig is  
✅ **Event Debugging** - Complete toolset voor event-driven debugging  
✅ **Causale Traceability** - Volledige "waarom"-analyse per trade  
✅ **Visual Feedback** - Real-time preview en validatie tijdens development  
✅ **Guided Development** - Beslisbomen en wizards voor elke stap  
✅ **Testability** - Pure functies, dependency injection, mock support

---

## **8.10. Gerelateerde Documenten**

Voor diepere technische details:

- **Plugin Anatomie:** [`4_DE_PLUGIN_ANATOMIE.md`](4_DE_PLUGIN_ANATOMIE.md)
- **Event Architectuur:** [`1_BUS_COMMUNICATION_ARCHITECTURE.md`](1_BUS_COMMUNICATION_ARCHITECTURE.md)
- **Worker Taxonomie:** [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md#24-het-worker-ecosysteem-5-gespecialiseerde-rollen)
- **Analytische Pijplijn:** [`5_DE_WORKFLOW_ORKESTRATIE.md`](5_DE_WORKFLOW_ORKESTRATIE.md)
- **Plugin IDE Bijlage:** [`D_BIJLAGE_PLUGIN_IDE.md`](D_BIJLAGE_PLUGIN_IDE.md)

---

**Einde Document - 8_DEVELOPMENT_STRATEGY v3.0**

*"Van rigide templates naar intelligente begeleiding - waar ontwikkeling intuïtief wordt zonder complexiteit te verliezen."*