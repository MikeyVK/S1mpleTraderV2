# 08_Development_Strategy.md

# **S1mpleTrader: Ontwikkelstrategie & Tooling**

Dit document beschrijft de methodiek, de workflow en de tooling voor het ontwikkelen, testen en debuggen van het S1mpleTrader-ecosysteem, gebaseerd op UI-gedreven flow configuratie en manifest-gedreven capabilities.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Filosofie: Rapid, Lean & Progressive Complexity](#filosofie-rapid-lean--progressive-complexity)
3. [De Supercharged Ontwikkelcyclus](#de-supercharged-ontwikkelcyclus)
4. [Plugin Development Workflow](#plugin-development-workflow)
5. [UI-Gedreven Flow Configuratie](#ui-gedreven-flow-configuratie)
6. [Event Debugging Tools](#event-debugging-tools)
7. [De Tooling in Detail](#de-tooling-in-detail)
8. [Development Workflow per Worker Type](#development-workflow-per-worker-type)
9. [Manifest-Gedreven Development](#manifest-gedreven-development)
10. [Testing Strategieën](#testing-strategieën)
11. [Logging & Traceability](#logging--traceability)

---

## **Executive Summary**

Dit document beschrijft de ontwikkelstrategie voor S1mpleTrader, die is ontworpen om een snelle, efficiënte en data-gedreven ontwikkelomgeving te creëren. De filosofie is gebaseerd op **Rapid, Lean & Progressive Complexity**, waarbij de Web UI de centrale IDE is en de "Bouwen → Meten → Leren"-cyclus wordt geminimaliseerd.

### **Kernkenmerken**

**1. UI-Gedreven Flow Configuratie**
- De volledige workflow, van visuele strategie-constructie in de **Strategy Builder** tot diepgaande analyse in de **Backtesting Hub**, vindt plaats binnen een naadloze, visuele webapplicatie.
- Gebruikers configureren worker flow via drag-and-drop, de UI genereert automatisch de strategy_wiring_map

**2. Manifest-Gedreven Capabilities**
- Workers declareren hun behoeften in manifest.yaml
- Capabilities (state, events, journaling) worden geconfigureerd via manifest
- Geen specialistische base classes meer - alles is configuratie

**3. Geavanceerde Event Debugging Tools**
- S1mpleTrader introduceert een reeks tools voor het debuggen van event-driven workflows, waaronder een **Event Chain Validator** (om de integriteit van de event-stroom bij het opstarten te controleren), een **Event Topology Viewer** (voor visueel inzicht), en een **Causale ID Tracer** (om de volledige beslissingsketen van een trade te reconstrueren).

**4. Gelaagde Teststrategie**
- Een strikte teststrategie met **Unit Tests** (per plugin, geïsoleerd), **Integratietests** (samenwerking tussen componenten), en **End-to-End Tests** (volledige backtest-reproductie) garandeert de robuustheid van het systeem.

### **Design Principes**

✅ **De Gebruiker staat Centraal** - De workflow van de kwantitatieve strateeg is leidend.
✅ **UI-Gedreven Configuratie** - Flow wordt geconfigureerd via visuele interface
✅ **Manifest-Gedreven Development** - Capabilities worden geconfigureerd via YAML
✅ **Snelle Feedback Loop** - Minimaliseer de tijd tussen een idee en het zien van het resultaat.
✅ **Testen als Voorwaarde** - Geen enkele component is "klaar" zonder succesvolle, geautomatiseerde tests.

---

## **Filosofie: Rapid, Lean & Progressive Complexity**

### **Kernprincipes**

We stappen af van een traditionele, op de CLI gerichte workflow. De nieuwe filosofie is gebaseerd op een combinatie van **Lean UX**, **User-Centered Design (UCD)** en **Progressive Complexity**, met als doel een "supercharged" ontwikkelcyclus te creëren.

* **De Gebruiker staat Centraal:** De primaire gebruiker ("De Kwantitatieve Strateeg") en diens workflow bepalen wat we bouwen en in welke volgorde. De Web UI is het centrale instrument.
* **Compact Ontwikkelen:** We bouwen in de kleinst mogelijke, onafhankelijke eenheden (een plugin) en testen deze geïsoleerd.
* **UI-Gedreven Flow:** Flow configuratie gebeurt via visuele interface, niet via code.
* **Manifest-Gedreven Capabilities:** Extra vaardigheden worden geconfigureerd via YAML, niet via base classes.
* **Direct Testen:** Elke plugin wordt vergezeld van unit tests. Geen enkele component wordt als "klaar" beschouwd zonder succesvolle, geautomatiseerde tests.
* **Snelle Feedback Loop (Bouwen → Meten → Leren):** De tijd tussen een idee, een codewijziging en het zien van het visuele resultaat moet minimaal zijn. De Web UI is de motor van deze cyclus.

### **De Scheiding van ROL en CAPABILITIES**

De ontwikkelstrategie van S1mpleTrader is gebouwd op een fundamenteel principe: de strikte scheiding tussen de **ROL** van een worker (zijn architecturale doel) en zijn **CAPABILITIES** (zijn extra vaardigheden). Dit vervangt de oude "complexiteitsniveaus".

**Pijler 1: De ROL Bepaalt de Workflow (Code)**

De ontwikkelaar maakt een expliciete, architecturale keuze door een van de twee basisklassen te kiezen. Dit bepaalt hoe de worker wordt aangeroepen.

- **`StandardWorker` (90% van de gevallen)**
  - **ROL**: Een deelnemer in een door een EventAdapter georkestreerde, voorspelbare pijplijn
  - **Gebruik**: Voor alle lineaire data-transformaties. "Het werkt gewoon."

- **`EventDrivenWorker` (10% van de gevallen)**
  - **ROL**: Een autonome agent die reageert op events en onafhankelijk van een operator-pijplijn functioneert.
  - **Gebruik**: Voor complexe, asynchrone strategieën, monitoring, of wanneer een worker op meerdere triggers moet reageren.

**Pijler 2: CAPABILITIES Bepalen de Vaardigheden (Configuratie)**

Alle extra vaardigheden worden aangevraagd in de `capabilities`-sectie van het `manifest.yaml`. De WorkerBuilder leest dit manifest en injecteert de benodigde functionaliteit dynamisch in de worker-instantie.

```yaml
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
      - event: "dca_opportunity_scored"
        payload_type: "Signal"
    wirings:
      - listens_to: "WEEKLY_DCA_TICK"
        invokes:
          method: "on_weekly_tick"
```

Deze "opt-in" benadering houdt de basis-worker extreem simpel en veilig, en de complexiteit wordt alleen toegevoegd waar het expliciet nodig is.

---

## **De Supercharged Ontwikkelcyclus**

De gehele workflow, van het bouwen van een strategie tot het analyseren van de resultaten, vindt plaats binnen de naadloze, visuele webapplicatie.

### **Fase 1: Visuele Strategie Constructie (De "Strategy Builder")**

**Doel:** Snel en foutloos een nieuwe strategie ([`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml)) samenstellen.

**Updates:**
- Worker type selector met 5 hoofdcategorieën
- Sub-categorie filter met 27 opties
- Capability badges (State, Events, Journaling)
- Event topology preview
- Worker flow configuratie visualisatie

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
4. Voor elke geplaatste plugin genereert de UI automatisch een configuratieformulier op basis van de [`schema.py`](plugins/) van de plugin. Input wordt direct in de browser gevalideerd.
5. **NIEUW:** Event-aware plugins tonen een "⚡ Configure Events" knop voor event setup.
6. **NIEUW:** Real-time event chain validatie tijdens het bouwen.
7. Bij het opslaan wordt de configuratie als YAML op de server aangemaakt.

**Worker Flow Configuratie Visualisatie:**

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

### **Fase 2: Interactieve Analyse (De "Backtesting Hub")**

**Doel:** De gebouwde strategieën rigoureus testen en de resultaten diepgaand analyseren.

**Updates:**
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

### **Fase 3: De Feedback Loop**

**Doel:** Een inzicht uit de analysefase direct omzetten in een verbetering.

**Updates:**
- Event chain aanpassing direct vanuit Trade Explorer
- Plugin capability upgrade suggesties
- A/B testing voor event-driven vs. impliciete workflows

**Proces:** Vanuit de "Trade Explorer" klikt de gebruiker op "Bewerk Strategie". Hij wordt direct teruggebracht naar de "Strategy Builder" met de volledige [`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml) al ingeladen, klaar om een aanpassing te doen. De cyclus begint opnieuw.

---

## **Plugin Development Workflow**

### **De Nieuwe Plugin Wizard - Intelligente Begeleiding**

De Plugin IDE leidt de ontwikkelaar door een gestructureerd proces.

#### **Step 1: Basis Identificatie**

**Velden:**

* **Display Naam**
  * **UI Element:** Tekstveld
  * **Voorbeeld:** `Smart DCA Opportunity Scorer`
  * **Validatie:** Uniek binnen project

* **Technische Naam**
  * **UI Element:** *Read-only* tekstveld (auto-gegenereerd)
  * **Voorbeeld:** `smart_dca_opportunity_scorer`
  * **Logica:** Automatisch `snake_case` conversie

* **Beschrijving & Auteur**
  * **UI Element:** Textarea & tekstveld
  * **Doel:** Verrijken [`manifest.yaml`](plugins/) en docstrings

#### **Step 2: Worker Type Selector - 5+27 Taxonomie**

**UI Element:** Hierarchische dropdown met visuele icons

**Niveau 1: Hoofdcategorie (5 opties)**

| Icon | Categorie | Beschrijving | Populair |
|------|-----------|--------------|----------|
| 🗺️ | ContextWorker | "De Cartograaf" - Verrijk marktdata met context | ⭐⭐⭐ |
| 🔍 | OpportunityWorker | "De Verkenner" - Herken handelskansen | ⭐⭐⭐⭐⭐ |
| 🛡️ | ThreatWorker | "De Waakhond" - Detecteer risico's | ⭐⭐⭐ |
| 🎯 | PlanningWorker | "De Strateeg" - Transformeer kansen naar plannen | ⭐⭐⭐⭐ |
| ⚡ | ExecutionWorker | "De Uitvoerder" - Voer uit en beheer | ⭐⭐ |

**Niveau 2: Sub-categorie (dynamisch op basis van keuze)**

*Voorbeeld voor OpportunityWorker:*

```
OpportunityWorker ▼
├─ Technical Pattern      ⭐⭐⭐⭐⭐  (FVG's, breakouts)
├─ Momentum Signal       ⭐⭐⭐⭐   (Trend following)
├─ Mean Reversion        ⭐⭐⭐    (Oversold/overbought)
├─ Statistical Arbitrage ⭐⭐     (Pair trading)
├─ Event Driven         ⭐⭐     (News-based)
├─ Sentiment Signal     ⭐       (Fear/greed)
└─ ML Prediction        ⭐       (Model predictions)
```

**Visuele Feedback:**
- Rechts toont een "Preview Card" de geselecteerde combinatie
- Icon + naam + beschrijving + "Typische use cases" lijst
- Link naar voorbeelden: "Bekijk 12 bestaande plugins van dit type"

#### **Step 3: Rol & Capability Selector**

Deze stap is cruciaal en reflecteert de kern van de architectuur. De gebruiker definieert eerst de ROL en voegt daarna optionele CAPABILITIES toe.

**UI Element:** Twee-delig interactief formulier.

**Deel 1: Kies de ROL van je Worker**
```
┌─────────────────────────────────────────────────────────┐
│  Wat is de fundamentele ROL van deze plugin?             │
│                                                          │
│  (•) StandardWorker                                     │
│      "Mijn plugin is onderdeel van de standaard,        │
│       stapsgewijze dataverwerkingspijplijn."              │
│      Vereist implementatie van een process() methode.  │
│                                                          │
│  ( ) EventDrivenWorker                                  │
│      "Mijn plugin werkt autonoom en reageert alleen op  │
│       specifieke events van de event bus."               │
│      Heeft geen process() methode.                     │
└─────────────────────────────────────────────────────────┘
```

**Deel 2: Selecteer de benodigde CAPABILITIES**
```
┌─────────────────────────────────────────────────────────┐
│  Welke extra vaardigheden (Capabilities) heeft je nodig? │
│                                                          │
│  ⚠️ Houd het simpel! 90% van de plugins heeft GEEN       │
│     extra capabilities nodig.                            │
│                                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 🔧 State Persistence                            ℹ️ │ │
│  │ [ ] Deze plugin heeft "geheugen" nodig tussen     │ │
│  │     aanroepen.                                    │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 📡 Event Communication                          ℹ️ │ │
│  │ [ ] Deze plugin moet custom events publiceren of  │ │
│  │     hierop reageren.                               │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 📖 Historical Journaling                        ℹ️ │ │
│  │ [ ] Deze plugin schrijft naar het strategy journal. │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  Geselecteerde ROL: StandardWorker                        │
│  Geselecteerde Capabilities: Geen                         │
│  Totale complexiteit: 0 ⭐ (PERFECT! Hou het simpel)      │
└─────────────────────────────────────────────────────────┘
```

**Intelligente Suggesties:**

De wizard analyseert de gekozen worker type/sub-categorie en suggereert welke *capabilities* aangezet moeten worden.

```yaml
# Voorbeeld: TrailingStopManager (ExecutionWorker + Position Management)
Suggestie: ✅ Activeer "State Persistence"
Reden: "Position management workers hebben doorgaans state nodig om bijvoorbeeld een high-water mark bij te houden."
```

#### **Step 4: Event Configuration (Conditioneel)**

**Zichtbaar alleen als:** "Event Communication" capability is geselecteerd.

**UI Tabs:**

1. **Triggers** - Wanneer moet deze plugin draaien?
   - Dropdown: Predefined triggers
   - Custom event input met autocomplete
   
2. **Publishes** - Wat publiceert deze plugin?
   - Event naam + DTO type selector
   - Validatie: uniek binnen project

3. **Advanced**
   - `requires_all` checkbox (wacht op alle triggers)
   - Event chain preview diagram

**Zie [Event Configuration Wizard](#event-configuration-wizard) voor details.**

#### **Step 5: Dependencies (Data Contract)**

**UI Element:** Smart dependency builder

```
┌─────────────────────────────────────────────────────────┐
│  Welke data heeft deze plugin nodig?                     │
│                                                          │
│  📊 DataFrame Kolommen:                                  │
│  ┌──────────────────────────────────────────┐          │
│  │ Requires (verplicht):                     │          │
│  │  [+] close                                │          │
│  │  [+] volume                               │          │
│  │  [Add Column]                             │          │
│  │                                            │          │
│  │ Provides (output):                        │          │
│  │  [+] opportunity_score                    │          │
│  │  [Add Column]                             │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  🎯 Rijke Context Data:                                  │
│  ┌──────────────────────────────────────────┐          │
│  │ Requires Context (verplicht):             │          │
│  │  [ ] orderbook_snapshot                   │          │
│  │  [ ] tick_by_tick_volume                  │          │
│  │                                            │          │
│  │ Uses (optioneel):                         │          │
│  │  [ ] news_sentiment                       │          │
│  │  [ ] on_chain_metrics                     │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  ⚠️ Validation:                                          │
│  ✓ All required data is available in default setup      │
└─────────────────────────────────────────────────────────┘
```

**Intelligente Features:**
- Autocomplete van vaak gebruikte kolommen
- Real-time validatie tegen platform capabilities
- Waarschuwing als verplichte data niet standaard beschikbaar is

#### **Step 6: Review & Generate**

**UI:** Split-screen preview

**Links:** Samenvatting van alle keuzes
```
Plugin: Smart DCA Opportunity Scorer
├─ Type: OpportunityWorker / Technical Pattern
├─ Base Class: BaseEventAwareWorker
├─ Events: 
│  ├─ Triggers: on_schedule:weekly_dca
│  └─ Publishes: dca_opportunity_scored (Signal)
├─ Dependencies:
│  ├─ Requires: ['close', 'volume']
│  └─ Provides: ['opportunity_score']
└─ Complexity: 3 ⭐ (Medium)
```

**Rechts:** Live preview van gegenereerde bestanden (tabs)

- [`manifest.yaml`](plugins/)
- [`worker.py`](plugins/) (skeleton met TODOs)
- [`schema.py`](plugins/)
- [`tests/test_worker.py`](plugins/)

**Actions:**
- [← Back] [Generate Plugin] [Generate & Open in Editor]

### **De Template Engine - Intelligente Code Generatie**

De backend [`PluginCreator`](backend/assembly/plugin_creator.py) genereert niet alleen statische boilerplate, maar **context-aware code** op basis van alle wizard keuzes.

**Voorbeeld Gegenereerde `worker.py` (BaseEventAwareWorker):**

```python
# plugins/opportunity_workers/smart_dca_opportunity_scorer/worker.py
"""
Smart DCA Opportunity Scorer

Auto-generated by S1mpleTrader Plugin IDE
Created: 2025-10-14
"""
from backend.core.base_worker import BaseEventAwareWorker
from backend.dtos.pipeline.signal import Signal
from backend.dtos.state.trading_context import TradingContext
from typing import List
from uuid import uuid4

class SmartDcaOpportunityScorer(BaseEventAwareWorker):
    """
    OpportunityWorker - Technical Pattern
    
    TODO: Implement your opportunity detection logic below.
    
    This worker is event-aware and can:
    - React to triggers: on_schedule:weekly_dca
    - Publish events: dca_opportunity_scored (Signal)
    
    See docs/system/4_Plugin_Anatomie.md for BaseEventAwareWorker guide.
    """
    
    def process(self, context: TradingContext) -> List[Signal]:
        """
        Main processing method - called when trigger event fires.
        
        Args:
            context: Trading context with enriched_df containing:
                     - close (required)
                     - volume (required)
        
        Returns:
            List of Signal DTOs with opportunity_score in metadata
        """
        signals = []
        
        # TODO: Implement your opportunity detection logic
        # Example:
        # score = self._calculate_opportunity_score(context)
        # if score > self.params.threshold:
        #     signal = Signal(
        #         opportunity_id=uuid4(),
        #         timestamp=context.current_timestamp,
        #         asset=context.asset_pair,
        #         direction='long',
        #         signal_type='dca_opportunity',
        #         metadata={'opportunity_score': score}
        #     )
        #     
        #     # Publish event for downstream workers
        #     self.emit("dca_opportunity_scored", signal)
        #     
        #     signals.append(signal)
        
        return signals
    
    def _calculate_opportunity_score(self, context: TradingContext) -> float:
        """
        TODO: Implement your scoring logic.
        
        Example factors to consider:
        - Price deviation from MA
        - Volume patterns
        - Market regime
        """
        raise NotImplementedError("Implement your scoring logic")
```

**Key Features van Template Engine:**

1. **Context-Aware Imports:** Alleen nodige imports op basis van capabilities
2. **Inline Documentation:** Gegenereerde code bevat contextuele TODOs en voorbeelden
3. **Type Hints:** Volledige type annotations voor IDE support
4. **Example Code:** Commentaar met concrete voorbeelden relevant voor gekozen type

---

## **UI-Gedreven Flow Configuratie**

### **Concept: Guided Flow Setup**

Voor plugins die EventDrivenWorker gebruiken, is flow configuratie cruciaal maar complex. De wizard maakt dit toegankelijk via een UI-gedreven benadering.

### **Niveau 1: Predefined Triggers (Simpel)**

**UI:**

```
┌───────────────────────────────────────────────────────────────┐
│  Event Configuration: adaptive_dca_planner                     │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  📌 Step 1: Wanneer moet deze plugin draaien?                 │
│                                                                │
│  Kies een of meer triggers:                                   │
│                                                                │
│  Systeem Triggers (Predefined):                               │
│  ☐ on_context_ready      - Na context verrijking             │
│  ☐ on_signal_generated   - Na opportunity detectie           │
│  ☐ on_ledger_update      - Na ledger wijziging               │
│  ☐ on_position_opened    - Na positie opening                │
│  ☐ on_position_closed    - Na positie sluiting               │
│  ☑ on_schedule:weekly_dca - Tijd-gebaseerd (schedule.yaml)   │
│                                                                │
│  [+ Add Custom Event Trigger] → Niveau 2                      │
│                                                                │
│  ⚙️ Advanced:                                                  │
│  ☐ Wait for all triggers (requires_all: true)                │
│     When checked, plugin waits until ALL triggers fire        │
│                                                                │
│  [Next: Configure Published Events →]                         │
└───────────────────────────────────────────────────────────────┘
```

### **Niveau 2: Custom Events (Intermediate)**

**UI:**

```
┌───────────────────────────────────────────────────────────────┐
│  📢 Step 2: Welke events publiceert deze plugin?              │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Published Events:                                             │
│                                                                │
│  ┌───────────────────────────────────────────────────────────┐│
│  │ Event 1:                                                  ││
│  │                                                            ││
│  │ Event Name: [dca_opportunity_scored______________]        ││
│  │             ⚠️ Must be unique and descriptive             ││
│  │                                                            ││
│  │ Payload Type: [Signal                       ▼]           ││
│  │               Options: Signal, TradePlan,                ││
│  │                       CriticalEvent, Custom DTO          ││
│  │                                                            ││
│  │ Description (optional):                                   ││
│  │ [Published when DCA opportunity score is calculated____] ││
│  │                                                            ││
│  │ [Remove Event]                                            ││
│  └───────────────────────────────────────────────────────────┘│
│                                                                │
│  [+ Add Another Event]                                        │
│                                                                │
│  [← Back] [Next: Preview Event Chain →]                       │
└───────────────────────────────────────────────────────────────┘
```

### **Niveau 3: Event Chain Preview (Advanced)**

**UI:** Visual event flow builder

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Step 3: Event Chain Preview & Validation                  │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Your plugin's event flow:                                    │
│                                                                │
│  TRIGGERS (incoming):                                         │
│  ┌────────────────────────────────────────────────┐          │
│  │ on_schedule:weekly_dca                          │          │
│  │ Source: Scheduler (schedule.yaml)              │          │
│  │ Frequency: Every Monday 10:00                  │          │
│  └────────────────────────────────────────────────┘          │
│           │                                                    │
│           ▼                                                    │
│  ┌────────────────────────────────────────────────┐          │
│  │ adaptive_dca_planner.process()                 │ ◀─ YOU   │
│  └────────────────────────────────────────────────┘          │
│           │                                                    │
│           ▼                                                    │
│  PUBLISHES (outgoing):                                        │
│  ┌────────────────────────────────────────────────┐          │
│  │ dca_opportunity_scored (Signal)                │          │
│  │ Subscribers: [2 found ✓]                      │          │
│  │  ├─ dca_risk_assessor                         │          │
│  │  └─ strategy_logger                           │          │
│  └────────────────────────────────────────────────┘          │
│                                                                │
│  Validation Results:                                          │
│  ✓ All triggers have publishers                              │
│  ✓ All published events have subscribers                     │
│  ✓ No circular dependencies detected                         │
│  ✓ Payload DTO types are consistent                          │
│                                                                │
│  [← Back] [Save Configuration]                                │
└───────────────────────────────────────────────────────────────┘
```

**Key Features:**

1. **Real-time Validation:** Event chain validator runs tijdens configuratie
2. **Subscriber Discovery:** Toont automatisch welke plugins luisteren
3. **Impact Analysis:** "2 downstream plugins will be affected"
4. **Cycle Detection:** Visuele waarschuwing bij circular dependencies

---

## **Event Debugging Tools**

### **Event Chain Validator Output**

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

### **Event Topology Viewer**

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
│                    ┌───────────────┐                         │
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
│           ▼             ▼                 ▼               │
│    ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│    │Opportun- │  │ Threat   │  │Scheduler   │          │
│    │ity Op    │  │ Op       │  │            │          │
│    │fvg_det   │  │max_dd    │  │weekly_dca  │          │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│         │             │             │                    │
│         │SignalsGen   │ThreatsDetect│WEEKLY_DCA       │
│         └───────┬──────┴──────┬──────┘                 │
│                 ▼             ▼                         │
│         ┌───────────────────────────┐                  │
│         │ PlanningOperator           │                  │
│         │ • entry: limit_planner    │                  │
│         │ • exit: liquidity_target  │                  │
│         │ • size: fixed_risk        │                  │
│         │ • route: default_router   │                  │
│         └─────────┬─────────────────┘                  │
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
│ └─ (none - uses implicit pipeline)     │
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

### **Causale ID Tracer**

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

### **Event Flow Timeline Visualizer**

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

## **De Tooling in Detail**

### **Gespecialiseerde Entrypoints**

De applicatie kent drie manieren om gestart te worden, elk met een eigen doel:

* **[`run_web.py`](run_web.py) (De IDE):** Het primaire entrypoint voor de ontwikkelaar. Start de FastAPI-server die de Web UI en de bijbehorende API's serveert.
* **[`run_backtest_cli.py`](run_backtest_cli.py) (De Robot):** De "headless" entrypoint voor het uitvoeren van een Operation, ideaal voor automatisering, zoals regressietesten en Continuous Integration (CI/CD) workflows.
* **[`run_supervisor.py`](run_supervisor.py) (De Productie-schakelaar):** De minimalistische, robuuste starter voor de live trading-omgeving, die het Operations-proces monitort.

### **Strategy Builder met Worker Flow Configuratie**

**Enhancement:** Visuele representatie van worker flow strategies.

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

### **Trade Explorer met Causale Reconstructie**

**Enhancement:** Volledige causale chain visualisatie per trade.

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
            Size: 0.1 BTC (1% risk)
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

### **Plugin IDE met Capability Selectors**

**Enhancement:** Visuele capability matrix en real-time complexity feedback.

**Features:**
- Interactive beslisboom voor base class selectie
- Live preview van gegenereerde code
- Event configuration wizard (3 niveaus)
- Automatic manifest.yaml generation
- Test template generation met fixtures
- Real-time event chain validatie

---

## **Development Workflow per Worker Type**

### **ContextWorker Development**

**Karakteristieken:**
- Altijd `BaseWorker` (geen state/events nodig)
- Input: TradingContext met base DataFrame
- Output: Verrijkte TradingContext met extra kolommen
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

### **OpportunityWorker Development**

**Karakteristieken:**
- Meestal `BaseWorker` (95%)
- Soms `BaseEventAwareWorker` voor scheduled/complex flows
- Input: Verrijkte TradingContext
- Output: List van Signal DTOs met opportunity_id
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

capabilities:
  events:
    enabled: true
    triggers:
      - "on_schedule:weekly_dca"
    publishes:
      - event: "dca_opportunity_scored"
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

### **ThreatWorker Development**

**Karakteristieken:**
- Meestal `BaseWorker`
- Vaak gebruikt met predefined triggers (`on_ledger_update`)
- Input: TradingContext en/of StrategyLedger
- Output: Optional CriticalEvent DTO met threat_id
- Parallel execution in operator

**Workflow:**

```python
# manifest.yaml
identification:
  type: "threat_worker"
  subtype: "portfolio_risk"

capabilities:
  events:
    enabled: true
    triggers:
      - "on_ledger_update"

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

### **PlanningWorker Development**

**Karakteristieken:**
- Altijd `BaseWorker` voor standard planning
- `BaseEventAwareWorker` voor complex coordination
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
        # Bepaal entry prijs op basis van signal
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

capabilities:
  events:
    enabled: true
    triggers:
      - "dca_opportunity_scored"
      - "dca_risk_assessed"
    requires_all: true
    publishes:
      - event: "dca_plan_ready"
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

### **ExecutionWorker Development**

**Karakteristieken:**
- `BaseWorker` voor simple execution
- `BaseStatefulWorker` voor position management (state nodig)
- `BaseEventAwareWorker` voor scheduled/emergency actions
- Event-driven execution in operator
- Side effects (market orders, position modifications)

**Workflow (Stateful Position Management):**

```python
# manifest.yaml
identification:
  type: "execution_worker"
  subtype: "position_management"

capabilities:
  state:
    enabled: true

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

## **Manifest-Gedreven Development**

### **Capability Selectie via Manifest**

In plaats van een "beslisboom" voor base classes, presenteert de wizard nu een "capability matrix" die direct het manifest.yaml-bestand aanpast.

```
┌──────────────────────────────────────────────────┐
│ 🔧 CAPABILITIES (manifest.yaml)                  │
│                                                   │
│ [ ] 🔧 State Persistence                        ℹ️  │
│     Voegt 'self.state' en 'self.commit_state()' toe │
│                                                   │
│ [ ] 📡 Event Communication                      ℹ️  │
│     Voegt 'self.emit()' toe en configureert      │
│     'publishes' en 'wirings'.                    │
│                                                   │
│ [ ] 📖 Historical Journaling                    ℹ️  │
│     Voegt 'self.log_entries()' toe.              │
└──────────────────────────────────────────────────┘
```

Wanneer een checkbox wordt aangevinkt, wordt de corresponderende sectie automatisch aan het manifest.yaml toegevoegd, klaar om geconfigureerd te worden.

### **Intelligente Suggesties**

De wizard analyseert de gekozen worker type/sub-categorie en suggereert welke capabilities aangezet moeten worden.

```yaml
# Voorbeeld: TrailingStopManager (ExecutionWorker + Position Management)
Suggestie: ✅ Activeer "State Persistence"
Reden: "Position management workers hebben doorgaans state nodig om bijvoorbeeld een high-water mark bij te houden."
```

---

## **Testing Strategieën**

### **De Testfilosofie: Elk .py Bestand Heeft een Test**

De "Testen als Voorwaarde"-filosofie wordt uitgebreid naar **alle** Python bestanden in het project, inclusief de architecturale contracten zelf (Schema's, DTOs en Interfaces). Dit garandeert de robuustheid van de "Contract-Gedreven Architectuur" vanaf de basis.

**Kernprincipe:** Geen enkel .py bestand is compleet zonder een corresponderend test bestand. Dit geldt voor:
- Worker implementaties (`worker.py` → `tests/test_worker.py`)
- Configuratie schemas (`*_schema.py` → `tests/unit/config/schemas/test_*_schema.py`)
- Data Transfer Objects (`*.py` in `dtos/` → `tests/unit/dtos/test_*.py`)
- Interface definities (`*.py` in `interfaces/` → abstracte testklassen)
- Infrastructuur componenten (operators, services, factories)

### **Testen van Configuratie Schema's**

**Doel:** Garanderen dat het schema robuust is tegen zowel geldige als ongeldige configuratie-data.

**Wat te testen:**
- **Happy Path:** Kan het schema succesvol parsen met een correct en volledig YAML-voorbeeld?
- **Default Values:** Worden optionele velden correct gevuld met standaardwaarden als ze ontbreken?
- **Validatie Fouten:** Werpt het schema een ValidationError op bij incorrecte data?

**Voorbeeld:**
```python
# tests/unit/config/schemas/test_operators_schema.py
import pytest
from pydantic import ValidationError
from backend.config.schemas.operators_schema import OperatorConfig
from backend.core.enums import ExecutionStrategy, AggregationStrategy

def test_operator_config_happy_path():
    """Tests successful validation with correct data."""
    data = {
        "operator_id": "TestOperator",
        "manages_worker_type": "ContextWorker",
        "execution_strategy": "SEQUENTIAL",
        "aggregation_strategy": "CHAIN_THROUGH"
    }
    config = OperatorConfig(**data)
    assert config.operator_id == "TestOperator"
    assert config.execution_strategy == ExecutionStrategy.SEQUENTIAL

def test_operator_config_invalid_strategy():
    """Tests that an invalid enum value raises a ValidationError."""
    data = {
        "operator_id": "TestOperator",
        "manages_worker_type": "ContextWorker",
        "execution_strategy": "INVALID_STRATEGY",
        "aggregation_strategy": "CHAIN_THROUGH"
    }
    with pytest.raises(ValidationError):
        OperatorConfig(**data)
```

### **Testen van Data Transfer Objects (DTOs)**

**Doel:** Verifiëren dat de "vervoerscontainers" voor data correct functioneren.

**Wat te testen:**
- **Happy Path:** Kan de DTO succesvol worden aangemaakt met geldige data?
- **Standaardwaarden & Factories:** Worden velden met default_factory correct geïnitialiseerd?
- **Type Coercion:** Converteert Pydantic data correct waar van toepassing?

**Voorbeeld:**
```python
# tests/unit/dtos/pipeline/test_signal_dto.py
from uuid import UUID
from datetime import datetime
from backend.dtos.pipeline.signal import Signal

def test_signal_dto_creation():
    """Tests basic instantiation and default value generation."""
    now = datetime.utcnow()
    signal = Signal(
        timestamp=now,
        asset="BTC/EUR",
        direction="long",
        signal_type="fvg_entry"
    )
    
    assert isinstance(signal.opportunity_id, UUID)
    assert signal.asset == "BTC/EUR"
```

### **Testen van Interface Contracten**

**Doel:** Afdwingen dat concrete klassen zich aan het gedefinieerde gedrag van een interface houden.

**Strategie:**
- We schrijven een **abstracte testklasse** die de *verwachtingen* van de interface test.
- Vervolgens maken we voor **elke concrete implementatie** een testklasse die erft van de abstracte testklasse.

**Voorbeeld:**
```python
# tests/unit/core/interfaces/test_persistors.py
from abc import ABC, abstractmethod
import pytest

class AbstractTestIStatePersistor(ABC):
    """Abstract test for IStatePersistor contract."""
    
    @abstractmethod
    def get_persistor_instance(self, path):
        """Must return an instance of the persistor to test."""
        raise NotImplementedError
    
    def test_save_and_load_cycle(self, tmp_path):
        """Test basic save and load functionality."""
        persistor = self.get_persistor_instance(tmp_path / "state.json")
        test_data = {"key": "value", "count": 1}
        
        persistor.save_atomic(test_data)
        loaded_data = persistor.load()
        assert loaded_data == test_data

# Concrete test for JsonPersistor
from backend.data.persistors.json_persistor import JsonPersistor

class TestJsonPersistor(AbstractTestIStatePersistor):
    """Concrete test for the JsonPersistor implementation."""
    def get_persistor_instance(self, path):
        return JsonPersistor(path=path, mode="atomic")
```

### **Unit Tests per Plugin**

Elke plugin-map krijgt een [`tests/test_worker.py`](plugins/). Deze test laadt een stukje voorbeeld-data, draait de [`worker.py`](plugins/) erop, en valideert of de output correct is. Dit gebeurt volledig geïsoleerd.

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

### **Testen van Workers met Capabilities**

Omdat capabilities dynamisch worden geïnjecteerd, blijven de workers zelf eenvoudig te testen. We hoeven alleen de geïnjecteerde methodes te mocken.

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

### **Integratietests**

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

### **End-to-End Tests**

Een klein aantal tests die via [`run_backtest_cli.py`](run_backtest_cli.py) een volledige Operation draaien op een vaste dataset en controleren of het eindresultaat (de PnL) exact overeenkomt met een vooraf berekende waarde.

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

## **Logging & Traceability**

### **Gelaagde Logging Strategie**

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

### **Traceability met Causale IDs**

Vier getypeerde causale IDs voor complete "waarom"-analyse:

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

### **Log Explorer UI**

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

## **Samenvatting: De Verbeteringen**

### **Architectuur Kenmerken**

| Aspect | Huidige Implementatie |
|--------|----------------------|
| **Worker Taxonomie** | 5 categorieën + 27 sub-types |
| **Plugin Capabilities** | Opt-in via manifest |
| **Event System** | 3 abstractieniveaus (Implicit → Predefined → Custom) |
| **Causale IDs** | 4 getypeerde IDs (Opportunity, Trade, Threat, Scheduled) |
| **Event Debugging** | Validator, Topology Viewer, Timeline |
| **Strategy Builder** | Met worker flow preview |
| **Trade Explorer** | Met causale reconstructie |
| **Plugin IDE** | Met capability selector & event wizard |

### **Kernvoordelen**

✅ **UI-Gedreven Flow** - Flow configuratie via visuele interface
✅ **Manifest-Gedreven Development** - Capabilities via YAML configuratie
✅ **Event Debugging** - Complete toolset voor event-driven debugging
✅ **Causale Traceability** - Volledige "waarom"-analyse per trade
✅ **Visual Feedback** - Real-time preview en validatie tijdens development
✅ **Guided Development** - Beslisbomen en wizards voor elke stap
✅ **Testability** - Pure functies, dependency injection, mock support

---

## **Gerelateerde Documenten**

Voor diepere technische details:
- **Plugin Anatomie:** [`4_Plugin_Anatomie.md`](4_Plugin_Anatomie.md)
- **Event Architectuur:** [`1_Bus_communicatie_structuur.md`](1_Bus_communicatie_structuur.md)
- **Worker Taxonomie:** [`2_Architectuur_Componenten.md`](2_Architectuur_Componenten.md#worker-ecosysteem-5-gespecialiseerde-rollen)
- **Analytische Pijplijn:** [`5_Workflow_Orkestratie.md`](5_Workflow_Orkestratie.md)
- **Plugin IDE Bijlage:** [`D_BIJLAGE_PLUGIN_IDE.md`](D_BIJLAGE_PLUGIN_IDE.md)

---

**Einde Document - 8_Development_Strategy**

*"Van rigide templates naar intelligente begeleiding - waar ontwikkeling intuïtief wordt zonder complexiteit te verliezen."*

---

**Einde Document**