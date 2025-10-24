# Development Workflow: Process & Tooling

**Versie:** 3.0
**Status:** Definitief

Dit document beschrijft de methodiek, de workflow en de tooling voor het ontwikkelen, testen en debuggen van het S1mpleTrader-ecosysteem, gebaseerd op UI-gedreven flow configuratie en manifest-gedreven capabilities.

---

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

## **Referenties**

- **[Plugin Anatomy](01_Plugin_Anatomy.md)** - Plugin structuur en capabilities
- **[Worker Ecosystem](02_Core_Concepts/01_Worker_Ecosystem.md)** - Worker types en sub-categorieën
- **[Event Architecture](02_Core_Concepts/02_Event_Architecture.md)** - Event system en debugging
- **[Configuration Hierarchy](02_Core_Concepts/03_Configuration_Hierarchy.md)** - YAML configuratie
- **[Traceability Framework](02_Core_Concepts/04_Traceability_Framework.md)** - Causale IDs en logging
- **[IDE Features](03_IDE_Features.md)** - UI/UX tooling voor development

---

**Einde Document**

*"Van rigide templates naar intelligente begeleiding - waar ontwikkeling intuïtief wordt zonder complexiteit te verliezen."*