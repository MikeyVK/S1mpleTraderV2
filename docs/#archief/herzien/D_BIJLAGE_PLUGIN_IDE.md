# **Bijlage D: De Plugin Development Experience & IDE**

**Versie:** 3.0
**Status:** Definitief
Dit document beschrijft de architectuur en de gebruikerservaring (UX) voor de web-based Integrated Development Environment (IDE) voor plugins binnen S1mpleTrader.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Kernfilosofie: De Glijdende Schaal van Abstractie](#d1-kernfilosofie-de-glijdende-schaal-van-abstractie)
3. [De MVP: De "Intelligente Plugin Generator"](#d2-de-mvp-de-intelligente-plugin-generator)
4. [De Glijdende Schaal Visualisatie](#d3-de-glijdende-schaal-visualisatie)
5. [Plugin Browser & Discovery](#d4-plugin-browser--discovery)
6. [Event Configuration Wizard](#d5-event-configuration-wizard)
7. [Event Topology Viewer](#d6-event-topology-viewer)
8. [De Toekomstvisie: Gelaagde Web IDE](#d7-de-toekomstvisie-gelaagde-web-ide)
9. [UX/UI Mockups](#d8-uxui-mockups)
10. [Architectuur voor Plugin Internationalisatie](#d9-architectuur-voor-plugin-internationalisatie)

---

## **Executive Summary**

Dit document schetst de visie voor de S1mpleTrader Plugin IDE, een web-based ontwikkelomgeving die is ontworpen om het creëren van plugins te transformeren van een technische taak naar een intuïtief, creatief proces. De kernfilosofie is de **"glijdende schaal van abstractie"**, die complexiteit volledig opt-in maakt.

### **🎯 Kernkenmerken**

**1. Glijdende Schaal van Abstractie**
-   De IDE ondersteunt meerdere niveaus van complexiteit, van een "no-code" visuele bouwer tot een "pro-code" embedded editor, waardoor het toegankelijk is voor zowel niet-programmeurs als ervaren ontwikkelaars.

**2. Scheiding van ROL en CAPABILITIES**
-   De IDE begeleidt de ontwikkelaar bij het maken van de cruciale architecturale keuze voor de **ROL** van een worker (`StandardWorker` vs. `EventDrivenWorker`) en het selecteren van de benodigde **CAPABILITIES** (`state`, `events`, `journaling`) via een visuele matrix.

**3. Intelligente Plugin Generator (MVP)**
-   Een multi-step wizard die de ontwikkelaar door het creatieproces leidt, van basisidentificatie tot het definiëren van dependencies en event-configuraties.
-   De wizard genereert context-bewuste boilerplate-code, inclusief docstrings, type hints en `TODO`-commentaren die zijn afgestemd op de gekozen ROL en CAPABILITIES.

**4. Geavanceerde Discovery & Debugging Tools**
-   Een verbeterde **Plugin Browser** met multi-dimensionale filtering (op type, sub-categorie, capabilities, etc.) en een visueel badge-systeem.
-   Een **Event Topology Viewer** en **Causale ID Tracer** bieden diepgaand inzicht in de event-gedreven workflows en de beslissingsketen van trades.

### **🔑 Design Principes**

✅ **Progressive Disclosure** - Begin simpel, onthul complexiteit alleen wanneer nodig.
✅ **Visuele Feedback** - Toon direct de architecturale impact van elke keuze.
✅ **Guided Exploration** - Help de gebruiker de juiste tools en abstractieniveaus te kiezen.
✅ **"Fail Fast" Validatie** - Valideer configuraties en event-chains tijdens het ontwerpproces, niet pas tijdens runtime.

---

## **D.1. Kernfilosofie: De Glijdende Schaal van Abstractie**

### **D.1.1. Paradigma: Opt-in Complexiteit**

De fundamentele uitdaging van elk plugin-systeem is de balans tussen gebruiksgemak en de kracht van code. S1mpleTrader lost dit op met een **"glijdende schaal van abstractie"** - een modulair systeem waarbij complexiteit volledig opt-in is.

**De Drie Dimensies van Complexiteit:**

1.  **Worker Taxonomie** - Van simpel naar gespecialiseerd
    *   5 hoofdcategorieën ([`ContextWorker`](../../backend/core/base_worker.py), [`OpportunityWorker`](../../backend/core/base_worker.py), [`ThreatWorker`](../../backend/core/base_worker.py), [`PlanningWorker`](../../backend/core/base_worker.py), [`ExecutionWorker`](../../backend/core/base_worker.py))
    *   27 sub-categorieën voor fijnmazige classificatie
    *   Duidelijke "Single Responsibility" per type

2.  **ROL & Capabilities** - De scheiding van *Hoe* en *Wat*
    *   **ROL (Declaratief via Klasse):** De ontwikkelaar kiest de fundamentele ROL van de worker. Dit bepaalt *hoe* de worker wordt aangeroepen.
        *   `StandardWorker`: Neemt deel aan de georkestreerde pijplijn.
        *   `EventDrivenWorker`: Reageert autonoom op events.
    *   **CAPABILITIES (Configuratief via Manifest):** De ontwikkelaar "zet" extra vaardigheden aan in het `manifest.yaml`. Dit bepaalt *wat* de worker extra kan.
        *   `state`: Voor intern geheugen.
        *   `events`: Om te publiceren of te reageren op custom events.
        *   `journaling`: Om bij te dragen aan het strategy journal.

3.  **Event-Driven Workflows** - Van impliciete pijplijn naar custom events
    *   **Niveau 1:** Impliciete pijplijnen (95% van gebruik) - "Het werkt gewoon"
    *   **Niveau 2:** Predefined triggers (opt-in) - Gebruik standaard triggers
    *   **Niveau 3:** Custom event chains (expert mode) - Volledige controle

### **D.1.2. Kernprincipes**

1.  **Progressive Disclosure:** Begin simpel, onthul complexiteit alleen wanneer nodig
2.  **Visuele Feedback:** Toon direct de impact van keuzes op architectuur
3.  **Guided Exploration:** Help de gebruiker de juiste abstractieniveau te kiezen
4.  **Fail-Fast Validatie:** Valideer tijdens design-time, niet runtime

---

## **D.2. De MVP: De "Intelligente Plugin Generator"**

De eerste, meest cruciale stap is het bouwen van een Minimum Viable Product (MVP) dat het grootste pijnpunt voor de ontwikkelaar oplost: het handmatig aanmaken van de repetitieve boilerplate-code.

### **D.2.1. De "Nieuwe Plugin" Wizard**

Het hart van de MVP is een intelligent, multi-step formulier dat de ontwikkelaar door de creatie van een nieuwe plugin leidt.

#### **Step 1: Basis Identificatie**

**Velden:**

*   **Display Naam**
    *   **UI Element:** Tekstveld
    *   **Voorbeeld:** `Smart DCA Opportunity Scorer`
    *   **Validatie:** Uniek binnen project

*   **Technische Naam**
    *   **UI Element:** *Read-only* tekstveld (auto-gegenereerd)
    *   **Voorbeeld:** `smart_dca_opportunity_scorer`
    *   **Logica:** Automatisch `snake_case` conversie

*   **Beschrijving & Auteur**
    *   **UI Element:** Textarea & tekstveld
    *   **Doel:** Verrijken [`manifest.yaml`](../../plugins/) en docstrings

#### **Step 2: Worker Type Selector - 5+27 Taxonomie**

**UI Element:** Hierarchische dropdown met visuele icons

**Niveau 1: Hoofdcategorie (5 opties)**

| Icon | Categorie | Beschrijving | Populair |
|------|-----------|--------------|----------|
| 🗺️ | [`ContextWorker`](../../backend/core/enums.py:WorkerType) | "De Cartograaf" - Verrijk marktdata met context | ⭐⭐⭐ |
| 🔍 | [`OpportunityWorker`](../../backend/core/enums.py:WorkerType) | "De Verkenner" - Herken handelskansen | ⭐⭐⭐⭐⭐ |
| 🛡️ | [`ThreatWorker`](../../backend/core/enums.py:WorkerType) | "De Waakhond" - Detecteer risico's | ⭐⭐⭐ |
| 🎯 | [`PlanningWorker`](../../backend/core/enums.py:WorkerType) | "De Strateeg" - Transformeer kansen naar plannen | ⭐⭐⭐⭐ |
| ⚡ | [`ExecutionWorker`](../../backend/core/enums.py:WorkerType) | "De Uitvoerder" - Voer uit en beheer | ⭐⭐ |

**Niveau 2: Sub-categorie (dynamisch op basis van keuze)**

*Voorbeeld voor OpportunityWorker:*

```
OpportunityWorker ▼
├─ Technical Pattern         ⭐⭐⭐⭐⭐  (FVG's, breakouts)
├─ Momentum Signal          ⭐⭐⭐⭐   (Trend following)
├─ Mean Reversion           ⭐⭐⭐    (Oversold/overbought)
├─ Statistical Arbitrage    ⭐⭐     (Pair trading)
├─ Event Driven            ⭐⭐     (News-based)
├─ Sentiment Signal        ⭐       (Fear/greed)
└─ ML Prediction           ⭐       (Model predictions)
```

**Visuele Feedback:**
-   Rechts toont een "Preview Card" de geselecteerde combinatie
-   Icon + naam + beschrijving + "Typische use cases" lijst
-   Link naar voorbeelden: "Bekijk 12 bestaande plugins van dit type"

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

1.  **Triggers** - Wanneer moet deze plugin draaien?
    -   Dropdown: Predefined triggers
    -   Custom event input met autocomplete
    
2.  **Publishes** - Wat publiceert deze plugin?
    -   Event naam + DTO type selector
    -   Validatie: uniek binnen project

3.  **Advanced**
    -   `requires_all` checkbox (wacht op alle triggers)
    -   Event chain preview diagram

**Zie [D.5 Event Configuration Wizard](#d5-event-configuration-wizard) voor details.**

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
-   Autocomplete van vaak gebruikte kolommen
-   Real-time validatie tegen platform capabilities
-   Waarschuwing als verplichte data niet standaard beschikbaar is

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

-   [`manifest.yaml`](../../plugins/)
-   [`worker.py`](../../plugins/) (skeleton met TODOs)
-   [`schema.py`](../../plugins/)
-   [`tests/test_worker.py`](../../plugins/)

**Actions:**
-   [← Back] [Generate Plugin] [Generate & Open in Editor]

### **D.2.2. De Template Engine - Intelligente Code Generatie**

De backend [`PluginCreator`](../../backend/assembly/plugin_creator.py) genereert niet alleen statische boilerplate, maar **context-aware code** op basis van alle wizard keuzes.

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
    
    See docs/system/4_DE_PLUGIN_ANATOMIE.md for BaseEventAwareWorker guide.
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

1.  **Context-Aware Imports:** Alleen nodige imports op basis van capabilities
2.  **Inline Documentation:** Gegenereerde code bevat contextuele TODOs en voorbeelden
3.  **Type Hints:** Volledige type annotations voor IDE support
4.  **Example Code:** Commentaar met concrete voorbeelden relevant voor gekozen type

---

## **D.3. De Glijdende Schaal Visualisatie**

### **D.3.1. Concept: De ROL & Capability Keuzematrix**

Een interactieve visualisatie die de quant helpt de juiste combinatie van ROL en CAPABILITIES te kiezen. Dit is geen lineaire ladder meer, maar een matrix.

### **D.3.2. UI Layout: De Keuzematrix**
```
┌───────────────────────────────────────────────────────────────┐
│  🎯 Bepaal de Architectuur van je Plugin                      │
│                                                                │
│  Volg de 2 stappen om de juiste setup te kiezen:               │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│  Stap 1: Kies de fundamentele ROL                              │
│                                                                │
│  ┌──────────────────────────┐   ┌──────────────────────────┐ │
│  │  StandardWorker       ✓  │   │  EventDrivenWorker       │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━  │   │  ━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │  • Onderdeel van de       │   │  • Autonoom & reactief    │ │
│  │    standaard pijplijn.    │   │  • Reageert op events.    │ │
│  │  • Implementeert          │   │  • Geen process()       │ │
│  │    process().           │   │    methode.             │ │
│  └──────────────────────────┘   └──────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│  Stap 2: Voeg benodigde CAPABILITIES toe                       │
│                                                                │
│  Jouw Gekozen ROL: StandardWorker                             │
│                                                                │
│  [ ] 🔧 State Persistence                                    │
│      Voegt state_persistor toe aan __init__.               │
│      Nodig voor intern "geheugen".                           │
│                                                                │
│  [ ] 📡 Event Communication                                  │
│      Voegt event_handler toe aan __init__.                 │
│      Nodig om custom events te publiceren/ontvangen.         │
│                                                                │
│  [ ] 📖 Historical Journaling                                │
│      Voegt journal_persistor toe aan __init__.             │
│      Nodig om te schrijven naar het strategy journal.        │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│  Jouw Selectie:                                                │
│  • ROL: StandardWorker                                        │
│  • Capabilities: [State, Events]                              │
│  • Resultaat: Een StandardWorker klasse die een             │
│    state_persistor en event_handler geïnjecteerd krijgt.  │
│                                                                │
│  [Bekijk Code Voorbeelden] [Bekijk Testing Guide]            │
└───────────────────────────────────────────────────────────────┘
```

### **D.3.3. Interactive Features**

1.  **Live Code Comparison:**
    -   Click op elk niveau toont side-by-side code comparison
    -   "Wat is het verschil?" tussen niveau N en N+1

2.  **Dependency Preview:**
    -   Visuele "web" van wat elk niveau vereist
    -   Testing complexity indicator

3.  **Performance Impact:**
    -   Geschatte performance overhead per niveau
    -   Memory footprint indicator

4.  **Similar Plugins:**
    -   "12 plugins gebruiken dit niveau" → bekijk voorbeelden

---

## **D.4. Plugin Browser & Discovery**

### **D.4.1. Enhanced Search & Filtering**

De Plugin Browser krijgt een complete overhaul met multi-dimensionale filtering.

**UI Layout:**

```
┌───────────────────────────────────────────────────────────────┐
│  🔍 Plugin Browser                            [+ New Plugin]   │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Search: [_________________________]  [Clear Filters]         │
│                                                                │
│  ┌─ Filters ────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  Worker Type:                                            │ │
│  │  ☑ Context (12)    ☑ Opportunity (23)   ☐ Threat (8)   │ │
│  │  ☑ Planning (15)   ☐ Execution (6)                      │ │
│  │                                                           │ │
│  │  Sub-Category:                       [Show All ▼]       │ │
│  │  ☑ Technical Pattern (8)                                │ │
│  │  ☑ Momentum Signal (5)                                  │ │
│  │  ☐ Mean Reversion (3)                                   │ │
│  │  ...                                                     │ │
│  │                                                           │ │
│  │  Capabilities:                                           │ │
│  │  ☐ State Persistence   ☐ Event Aware   ☐ Journaling    │ │
│  │                                                           │ │
│  │  Event Topology:                                         │ │
│  │  ☐ Publishers Only     ☐ Subscribers Only               │ │
│  │  ☐ Both                                                  │ │
│  │                                                           │ │
│  │  Status:                                                 │ │
│  │  ☑ Active   ☐ Deprecated   ☐ Experimental              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─ Results (38 plugins) ──────────────────────────────────┐ │
│  │                                                           │ │
│  │  📊 ema_detector                                         │ │
│  │  Context / Indicator Calculation                         │ │
│  │  Badges: [BaseWorker] [DataFrame Only]                  │ │
│  │  "Calculates EMA indicators for technical analysis"     │ │
│  │  Dependencies: close → ema_20, ema_50                   │ │
│  │  [View] [Edit] [Clone]                                  │ │
│  │  ─────────────────────────────────────────────────────── │ │
│  │                                                           │ │
│  │  🔍 fvg_detector                                         │ │
│  │  Opportunity / Technical Pattern                         │ │
│  │  Badges: [BaseWorker] [Pure Logic] [Popular ⭐⭐⭐⭐⭐]   │ │
│  │  "Detects Fair Value Gaps for entry opportunities"      │ │
│  │  Dependencies: high, low, close → Signals               │ │
│  │  [View] [Edit] [Clone]                                  │ │
│  │  ─────────────────────────────────────────────────────── │ │
│  │                                                           │ │
│  │  📡 adaptive_dca_planner                                 │ │
│  │  Planning / Entry Planning                               │ │
│  │  Badges: [Event-Aware 📡] [Complex ⚠️]                  │ │
│  │  "Smart DCA planner using event coordination"           │ │
│  │  Events: Listens[2] Publishes[1]                       │ │
│  │  [View] [Edit] [Clone] [→ Event Topology]              │ │
│  │  ─────────────────────────────────────────────────────── │ │
│  │                                                           │ │
│  │  ... (more results)                                      │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### **D.4.2. Badge System**

Visuele badges voor snelle herkenning:

| Badge | Betekenis |
|-------|-----------|
| 🔧 `[BaseWorker]` | Pure, stateless |
| ⚙️ `[Stateful]` | Uses state persistence |
| 📡 `[Event-Aware]` | Participates in events |
| 📖 `[Journaling]` | Logs to journal |
| ⚠️ `[Complex]` | Multiple capabilities |
| 🆕 `[New]` | Created < 7 days ago |
| ⭐ `[Popular]` | Used in > 5 strategies |
| 🧪 `[Experimental]` | Beta/testing phase |
| ⚠️ `[Deprecated]` | Being phased out |

### **D.4.3. Quick Actions**

-   **View:** Bekijk volledige details + dependencies graph
-   **Edit:** Open in editor (lokale IDE of web IDE)
-   **Clone:** Maak kopie als startpunt voor nieuwe plugin
-   **Event Topology:** (alleen voor event-aware) → Opens visualizer

### **D.4.4. Dependency Graph Visualizer**

Click op "View" → "Dependencies" tab:

```
┌───────────────────────────────────────────────────────────────┐
│  Dependency Graph: adaptive_dca_planner                        │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│         ┌─────────────────────┐                               │
│         │  TradingContext     │                               │
│         │  (from Environment) │                               │
│         └──────────┬──────────┘                               │
│                    │                                           │
│              ┌─────┴─────┐                                     │
│              ▼           ▼                                     │
│    ┌─────────────┐  ┌──────────────┐                         │
│    │ dca_        │  │ dca_risk_    │                         │
│    │ opportunity_│  │ assessor     │                         │
│    │ scorer      │  │              │                         │
│    └──────┬──────┘  └──────┬───────┘                         │
│           │                │                                   │
│           │ event:         │ event:                           │
│           │ dca_opport...  │ dca_risk...                      │
│           │                │                                   │
│           └────────┬───────┘                                   │
│                    ▼                                           │
│         ┌──────────────────────┐                              │
│         │ adaptive_dca_planner │ ◀── YOU ARE HERE            │
│         │ (requires_all: true) │                              │
│         └──────────┬───────────┘                              │
│                    │                                           │
│                    │ event: dca_plan_ready                     │
│                    ▼                                           │
│         ┌──────────────────────┐                              │
│         │ default_plan_        │                              │
│         │ executor             │                              │
│         └──────────────────────┘                              │
│                                                                │
│  Legend:                                                       │
│  ━━━ Data flow   ⚡ Event trigger   ● Required   ○ Optional  │
└───────────────────────────────────────────────────────────────┘
```

---

## **D.5. Event Configuration Wizard**

### **D.5.1. Concept: Guided Event Setup**

Voor plugins die [`BaseEventAwareWorker`](../../backend/core/base_worker.py) gebruiken, is event configuratie cruciaal maar complex. De wizard maakt dit toegankelijk via een 3-niveau benadering.

### **D.5.2. Niveau 1: Predefined Triggers (Simpel)**

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

### **D.5.3. Niveau 2: Custom Events (Intermediate)**

**UI:**

```
┌───────────────────────────────────────────────────────────────┐
│  📢 Step 2: Welke events publiceert deze plugin?              │
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

### **D.5.4. Niveau 3: Event Chain Preview (Advanced)**

**UI:** Visual event flow builder

```
┌───────────────────────────────────────────────────────────────┐
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

1.  **Real-time Validation:** Event chain validator runs tijdens configuratie
2.  **Subscriber Discovery:** Toont automatisch welke plugins luisteren
3.  **Impact Analysis:** "2 downstream plugins will be affected"
4.  **Cycle Detection:** Visuele waarschuwing bij circular dependencies

---

## **D.6. Event Topology Viewer**

### **D.6.1. Standalone Event Debugging Tool**

Toegankelijk via:
-   Plugin Browser → Event-aware plugin → [Event Topology]
-   Top menu → Tools → Event Topology Viewer

**Purpose:** Visueel debuggen en begrijpen van complexe event chains.

### **D.6.2. UI Layout**
```
┌───────────────────────────────────────────────────────────────┐
│  Event Topology Viewer                                         │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Strategy: mss_fvg_strategy                    [Export PNG]   │
│                                                                │
│  Filters:                                                      │
│  Worker Type: [All Types          ▼]                          │
│  Event Name:  [___________________]                           │
│  [Show System Events] [Show Custom Events]                    │
│                                                                │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│                    VISUAL EVENT GRAPH                          │
│                                                                │
│    ┌──────────────┐                                           │
│    │ Environment  │                                           │
│    └──────┬───────┘                                           │
│           │ ContextReady                                       │
│           ▼                                                    │
│    ┌──────────────────────────────────────────┐              │
│    │ ContextOperator                           │              │
│    │ ├─ ema_detector                          │              │
│    │ └─ market_structure_detector             │              │
│    └──────┬───────────────────────────────────┘              │
│           │ ContextEnriched                                    │
│        ┌──┴────────────┬─────────────────┐                    │
│        ▼               ▼                 ▼                     │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────┐             │
│  │Opportunity  │ │Threat       │ │Scheduler   │             │
│  │Operator     │ │Operator     │ │            │             │
│  │ fvg_det...  │ │ max_dd...   │ │weekly_dca  │             │
│  └──────┬──────┘ └──────┬──────┘ └──────┬─────┘             │
│         │               │               │                     │
│         │SignalsGen.    │ThreatsDetect. │WEEKLY_DCA_TICK     │
│         └───────┬───────┴────────┬──────┘                     │
│                 ▼                ▼                             │
│         ┌───────────────────────────────┐                     │
│         │ PlanningOperator               │                     │
│         │ ├─ entry: limit_entry_planner │                     │
│         │ ├─ exit:  liquidity_target    │                     │
│         │ ├─ size:  fixed_risk_sizer    │                     │
│         │ └─ route: default_router      │                     │
│         └───────────┬───────────────────┘                     │
│                     │ PlansReady                               │
│                     ▼                                          │
│         ┌───────────────────────────┐                         │
│         │ ExecutionOperator          │                         │
│         │   default_plan_executor    │                         │
│         └────────────────────────────┘                         │
│                                                                │
│  Click on any node for details                                │
│  Click on any edge to see event payload schema                │
│                                                                │
├───────────────────────────────────────────────────────────────┤
│  Details Panel:                                                │
│  Selected: fvg_detector (OpportunityWorker)                   │
│                                                                │
│  Triggers:                                                     │
│  └─ ContextEnriched (implicit)                                │
│                                                                │
│  Publishes:                                                    │
│  └─ (none - uses implicit pipeline)                           │
│                                                                │
│  Dependencies:                                                 │
│  Requires: high, low, close                                   │
│  Provides: Signal (opportunity_id, timestamp, ...)            │
│                                                                │
│  [View Source] [Edit Plugin]                                  │
└───────────────────────────────────────────────────────────────┘
```

### **D.6.3. Interactive Features**

1.  **Hover Effects:**
    -   Hover over node → Highlight dependencies
    -   Hover over edge → Show payload DTO schema

2.  **Click Actions:**
    -   Click node → Show detailed panel
    -   Double-click node → Open plugin editor
    -   Click edge → Show event contract details

3.  **Layout Algorithms:**
    -   Hierarchical (default)
    -   Force-directed
    -   Circular
    -   Timeline (chronological flow)

4.  **Export Options:**
    -   PNG/SVG voor documentatie
    -   JSON voor programmatic analysis
    -   PlantUML voor diagrammen

---

## **D.7. De Toekomstvisie: Gelaagde Web IDE**

Na de MVP wordt de Web IDE uitgebreid tot een volwaardige ontwikkelomgeving door de volgende drie lagen van abstractie aan te bieden.

### **Laag 1: De "No-Code" Strategie Bouwer**

*   **Concept:** Visueel canvas met drag-and-drop LEGO-blokjes
*   **Interface:** Block-based programming (zoals Scratch/Blockly)
*   **Voorbeeld:** `[EMA(10)]` → `[Kruist Boven]` → `[EMA(50)]` → `[Genereer Long Signaal]`
*   **Testen:** Scenario-bouwer met "Gegeven X, verwacht Y"
*   **Doelgroep:** Quants zonder programmeerervaring

### **Laag 2: De "Low-Code" Scripting Helper**

*   **Concept:** "Mad Libs" benadering - vul alleen kernlogica in
*   **Interface:** Formulier met Python expression fields
*   **Abstractie:** Platform abstraheert DTO's en interfaces compleet
*   **Testen:** Test Data Generator UI + Assertie Helper
*   **Doelgroep:** Gemiddelde quant met basis Python kennis

### **Laag 3: De "Pro-Code" Embedded IDE**

*   **Concept:** Volledige Monaco Editor (VS Code engine) in browser
*   **Features:**
    -   Syntax highlighting
    -   IntelliSense voor S1mpleTrader-specifieke code
    -   Real-time linting (Pylint/Mypy)
    -   Integrated terminal
    -   Git integration
*   **Testen:** Handmatig pytest schrijven in tabblad
*   **Doelgroep:** Ervaren ontwikkelaars

---

## **D.8. UX/UI Mockups**

### **D.8.1. Plugin Creator - Main Wizard**

```
╔═══════════════════════════════════════════════════════════════╗
║ 🆕 Create New Plugin                            [Step 2 of 6] ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  Worker Type Selection                                        ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │                                                          │ ║
║  │  [🗺️ ContextWorker    ]  [🔍 OpportunityWorker ✓]      │ ║
║  │                                                          │ ║
║  │  [🛡️ ThreatWorker     ]  [🎯 PlanningWorker    ]       │ ║
║  │                                                          │ ║
║  │  [⚡ ExecutionWorker  ]                                 │ ║
║  │                                                          │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                                ║
║  Sub-Category (7 options):                                    ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                ║
║  ● Technical Pattern      ⭐⭐⭐⭐⭐                            ║
║    Perfect for: FVG's, breakouts, divergences                ║
║                                                                ║
║  ○ Momentum Signal        ⭐⭐⭐⭐                              ║
║    Perfect for: Trend following, momentum breakouts          ║
║                                                                ║
║  ○ Mean Reversion         ⭐⭐⭐                                ║
║    Perfect for: Oversold/overbought, range bounce            ║
║                                                                ║
║  ○ Statistical Arbitrage  ⭐⭐                                  ║
║  ○ Event Driven          ⭐⭐                                  ║
║  ○ Sentiment Signal      ⭐                                    ║
║  ○ ML Prediction         ⭐                                    ║
║                                                                ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ Preview:                                                 │ ║
║  │                                                          │ ║
║  │ 🔍 OpportunityWorker - Technical Pattern                │ ║
║  │                                                          │ ║
║  │ This worker type is responsible for detecting trading   │ ║
║  │ opportunities based on technical chart patterns.         │ ║
║  │                                                          │ ║
║  │ Common examples:                                         │ ║
║  │ • FVG (Fair Value Gap) detector                         │ ║
║  │ • Breakout scanner                                      │ ║
║  │ • Divergence finder                                     │ ║
║  │                                                          │ ║
║  │ [→ View 8 existing plugins of this type]                │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                                ║
║  [← Previous]  [Cancel]              [Next: Capabilities →]   ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

### **D.8.2. Capability Selector**

```
╔═══════════════════════════════════════════════════════════════╗
║ 🔧 Select Capabilities                          [Step 3 of 6] ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  ℹ️ Tip: 90% of plugins don't need any of these!             ║
║     Start simple with BaseWorker and add complexity later.    ║
║                                                                ║
║  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║  ┃ ⚙️  State Persistence                               ℹ️  ┃ ║
║  ┃ [ ] Enable state management                            ┃ ║
║  ┃                                                         ┃ ║
║  ┃ Does your plugin need to remember information between  ┃ ║
║  ┃ ticks? Examples:                                        ┃ ║
║  ┃ • Track high water mark (trailing stops)              ┃ ║
║  ┃ • Learn/adapt parameters over time                    ┃ ║
║  ┃ • Maintain position history                           ┃ ║
║  ┃                                                         ┃ ║
║  ┃ Base Class: BaseStatefulWorker                         ┃ ║
║  ┃ Complexity: +2 ⭐                                       ┃ ║
║  ┃                                                         ┃ ║
║  ┃ [Show Code Example]                                    ┃ ║
║  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                ║
║  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║  ┃ 📡 Event Communication                              ℹ️  ┃ ║
║  ┃ [✓] Enable event communication                         ┃ ║
║  ┃                                                         ┃ ║
║  ┃ Does your plugin need to coordinate with other plugins ┃ ║
║  ┃ via events? Examples:                                   ┃ ║
║  ┃ • Wait for multiple signals before acting             ┃ ║
║  ┃ • Publish custom events for downstream workers        ┃ ║
║  ┃ • React to scheduled triggers                         ┃ ║
║  ┃                                                         ┃ ║
║  ┃ Base Class: BaseEventAwareWorker                       ┃ ║
║  ┃ Complexity: +3 ⭐                                       ┃ ║
║  ┃                                                         ┃ ║
║  ┃ [→ Configure Events]  ← Opens Event Wizard            ┃ ║
║  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                ║
║  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║  ┃ 📖 Historical Journaling                            ℹ️  ┃ ║
║  ┃ [ ] Enable strategy journaling                         ┃ ║
║  ┃                                                         ┃ ║
║  ┃ Should this plugin write to the strategy journal?      ┃ ║
║  ┃ Examples:                                               ┃ ║
║  ┃ • Log decision rationale (why rejected?)              ┃ ║
║  ┃ • Create audit trail                                  ┃ ║
║  ┃ • Research & debugging                                ┃ ║
║  ┃                                                         ┃ ║
║  ┃ Base Class: BaseJournalingWorker                       ┃ ║
║  ┃ Complexity: +1 ⭐                                       ┃ ║
║  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ Your Selection:                                          │ ║
║  │                                                          │ ║
║  │ Base Class: BaseEventAwareWorker                        │ ║
║  │ Total Complexity: 3 ⭐ (Medium)                          │ ║
║  │                                                          │ ║
║  │ You will have access to:                                │ ║
║  │ • self.emit(event_name, payload)                        │ ║
║  │ • def on_event(event_name, payload)                     │ ║
║  │                                                          │ ║
║  │ Event configuration required in manifest.yaml           │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                                ║
║  [← Previous]  [Cancel]              [Next: Events →]         ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

### **D.8.3. Event Configuration UI**

```
╔═══════════════════════════════════════════════════════════════╗
║ 📡 Configure Events                             [Step 4 of 6] ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  Tab: [Triggers ✓] [Publishes] [Advanced]                    ║
║                                                                ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                ║
║  When should this plugin run?                                 ║
║                                                                ║
║  Selected Triggers:                                           ║
║                                                                ║
║  ┌───────────────────────────────────────────────────────┐   ║
║  │ 1. on_schedule:weekly_dca                             │   ║
║  │    Source: Scheduler (schedule.yaml)                  │   ║
║  │    [✗ Remove]                                         │   ║
║  └───────────────────────────────────────────────────────┘   ║
║                                                                ║
║  Add Trigger:                                                 ║
║  ┌─────────────────────────────────────────────┐             ║
║  │ Predefined Triggers           ▼             │             ║
║  │ ─────────────────────────────────────────── │             ║
║  │ on_context_ready                            │             ║
║  │ on_signal_generated                         │             ║
║  │ on_ledger_update                            │             ║
║  │ on_position_opened                          │             ║
║  │ on_position_closed                          │             ║
║  │ on_schedule:weekly_dca              ✓       │             ║
║  │ ─────────────────────────────────────────── │             ║
║  │ Or enter custom event name:                 │             ║
║  │ [________________________]  [Add]           │             ║
║  └─────────────────────────────────────────────┘             ║
║                                                                ║
║  ⚙️ Trigger Behavior:                                         ║
║  [ ] Wait for all triggers (requires_all: true)              ║
║      When checked, plugin waits until ALL triggers fire      ║
║      before executing. Useful for coordination.              ║
║                                                                ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ Preview:                                                 │ ║
║  │                                                          │ ║
║  │ on_schedule:weekly_dca                                  │ ║
║  │        │                                                 │ ║
║  │        ▼                                                 │ ║
║  │ adaptive_dca_planner.process()                          │ ║
║  │                                                          │ ║
║  │ This plugin will run every Monday at 10:00              │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                                ║
║  [← Previous]  [Cancel]              [Next: Publishes →]      ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

### **D.8.4. Plugin Browser**

```
╔═══════════════════════════════════════════════════════════════╗
║ 🔍 Plugin Browser                             [+ New Plugin]  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  Search: [fvg_________________]  🔍  [Clear]  [⚙️ Filters]    ║
║                                                                ║
║  ┌─ Active Filters ───────────────────────────────────────┐  ║
║  │ Worker Type: Opportunity (23)  [✗]                      │  ║
║  │ Sub-Category: Technical Pattern (8)  [✗]               │  ║
║  └──────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌─ Results (1 plugin) ──────────────────────────────────┐   ║
║  │                                                         │   ║
║  │  ┌─────────────────────────────────────────────────┐  │   ║
║  │  │ 🔍 fvg_detector                    ⭐⭐⭐⭐⭐      │  │   ║
║  │  │ ─────────────────────────────────────────────── │  │   ║
║  │  │ OpportunityWorker / Technical Pattern          │  │   ║
║  │  │                                                 │  │   ║
║  │  │ Badges: [BaseWorker] [Pure Logic] [Popular]   │  │   ║
║  │  │                                                 │  │   ║
║  │  │ "Detects Fair Value Gaps for entry opport..."  │  │   ║
║  │  │                                                 │  │   ║
║  │  │ Dependencies:                                   │  │   ║
║  │  │ Requires: high, low, close                     │  │   ║
║  │  │ Produces: Signal (opportunity_id, ...)         │  │   ║
║  │  │                                                 │  │   ║
║  │  │ Used in: 12 strategies                         │  │   ║
║  │  │ Last updated: 3 days ago                       │  │   ║
║  │  │                                                 │  │   ║
║  │  │ [📖 View Details] [✏️ Edit] [📋 Clone]         │  │   ║
║  │  └─────────────────────────────────────────────────┘  │   ║
║  │                                                         │   ║
║  └─────────────────────────────────────────────────────────┘   ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## **D.9. Architectuur voor Plugin Internationalisatie**

### **D.9.1. Geïntegreerde i18n Workflow**

Om een uitwisselbaar ecosysteem te ondersteunen, faciliteert de IDE automatisch meertalige plugins.

**Structuur:**
```
plugins/fvg_detector/
├── manifest.yaml
├── worker.py
├── schema.py
└── locales/
    ├── en.yaml
    └── nl.yaml
```

**Abstractie in de IDE:**

1.  **Parameter Wizard:** Bij het definiëren van parameters in [`schema.py`](../../plugins/), vraagt de IDE om:
    -   Technical field name: `threshold`
    -   Display label (EN): `Entry Threshold`
    -   Display label (NL): `Instap Drempel`
    -   Help text (EN): `Minimum score to trigger entry`
    -   Help text (NL): `Minimale score om in te stappen`

2.  **Auto-generatie:** Het systeem genereert automatisch:
    ```yaml
    # locales/en.yaml
    parameters:
      threshold:
        label: "Entry Threshold"
        help: "Minimum score to trigger entry"
    
    # locales/nl.yaml
    parameters:
      threshold:
        label: "Instap Drempel"
        help: "Minimale score om in te stappen"
    ```

3.  **Visueel Context:** Context visualisaties (grafieken, lijnen) worden op dezelfde manier behandeld

**Resultaat:** De quant vult simpele tekstvelden in, het platform zorgt automatisch voor volledige i18n-infrastructuur.

---

## **D.10. Samenvatting & Roadmap**

### **D.10.1. MVP Features**

✅ **Intelligente Plugin Generator**
-   5 worker types + 27 sub-categorieën selector
-   Capability matrix met visual feedback
-   Event configuration wizard (3 niveaus)
-   Smart dependency builder
-   Context-aware code generation

✅ **Glijdende Schaal Visualisatie**
-   Interactive complexity ladder
-   Decision tree helper
-   Live code comparison
-   Similar plugins discovery

✅ **Enhanced Plugin Browser**
-   Multi-dimensionale filtering
-   Badge system
-   Dependency graph viewer
-   Event topology preview

✅ **Event Tooling**
-   Event configuration wizard
-   Event chain validation preview
-   Predefined triggers library
-   Custom event builder

### **D.10.2. Future Enhancements**

**Phase 2: No-Code Builder**
-   Visual block programming interface
-   Drag-and-drop strategy canvas
-   Auto-generated tests

**Phase 3: Low-Code Helper**
-   Expression-based logic builder
-   Template library
-   Guided testing UI

**Phase 4: Pro-Code IDE**
-   Full Monaco editor integration
-   IntelliSense voor S1mpleTrader
-   Integrated debugging
-   Git workflow

### **D.10.3. Cross-References**

Voor diepere technische details:
-   **Plugin Anatomie:** [`4_DE_PLUGIN_ANATOMIE.md`](4_DE_PLUGIN_ANATOMIE.md)
-   **Event Architectuur:** [`1_BUS_COMMUNICATION_ARCHITECTURE.md`](1_BUS_COMMUNICATION_ARCHITECTURE.md)
-   **Worker Taxonomie:** [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md#24-het-worker-ecosysteem-5-gespecialiseerde-rollen)
-   **Base Worker Hierarchie:** [`backend/core/base_worker.py`](../../backend/core/base_worker.py)

---

**Einde Document - D_BIJLAGE_PLUGIN_IDE**

---
