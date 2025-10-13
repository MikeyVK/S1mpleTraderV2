# S1mpleTrader V2: De Verfijnde Worker Taxonomie V3

**Versie:** 3.0  
**Status:** Definitief  
**Datum:** 2025-10-13  
**Auteur:** Architectonische Brainstorm Sessie

---

## Inhoudsopgave

1. [Executive Summary](#1-executive-summary)
2. [De Quant's Mentale Model](#2-de-quants-mentale-model)
3. [De 5 Worker Categorieën](#3-de-5-worker-categorieën)
4. [Sub-Categorieën per Worker Type](#4-sub-categorieën-per-worker-type)
5. [Event-Driven Architectuur](#5-event-driven-architectuur)
6. [Worker Base Classes](#6-worker-base-classes)
7. [Concrete Use Cases](#7-concrete-use-cases)
8. [Migratie Strategie](#8-migratie-strategie)
9. [Implementatie Roadmap](#9-implementatie-roadmap)

---

## 1. Executive Summary

### 1.1 Waarom Deze Verfijning?

De oorspronkelijke worker taxonomie combineerde twee fundamenteel verschillende concepten in de `AnalysisWorker` categorie:
- **Pure analyse** (patroonherkenning, signaal generatie)
- **Trade constructie** (entry/exit planning, sizing, routing)

Deze verfijning scheidt deze concepten en introduceert een **5-categorieën taxonomie** die:

✅ **Conceptueel zuiver** is - elke categorie heeft één duidelijke verantwoordelijkheid  
✅ **Intuïtief** aansluit bij hoe een quant denkt over strategievorming  
✅ **Flexibel** genoeg is voor diverse trading methodologieën  
✅ **Event-driven** kracht biedt met opt-in complexiteit  
✅ **Backwards compatible** is met bestaande architectuur

### 1.2 De Kernveranderingen

| Aspect | Oud (V2) | Nieuw (V3) |
|--------|----------|------------|
| **Hoofdcategorieën** | 4 (Context, Analysis, Monitor, Execution) | 5 (Context, Opportunity, Threat, Planning, Execution) |
| **AnalysisWorker** | Bevat analyse + planning | Gesplitst in Opportunity + Planning |
| **MonitorWorker** | Generieke naam | Hernoemd naar ThreatWorker (duidelijker) |
| **Event Model** | Impliciete pijplijn | Drie niveaus: Impliciet / Predefined / Custom |
| **Sub-categorieën** | Beperkt | Uitgebreid (26 sub-types totaal) |

---

## 2. De Quant's Mentale Model

### 2.1 De Vier Fasen van Strategievorming

Een quant doorloopt mentaal vier fasen bij het ontwikkelen van een trading strategie:

#### **Fase 1: BEGRIJPEN ("Wat gebeurt er?")**
De quant interpreteert de markt door data te contextualiseren:
- *"Is de markt trending of ranging?"* → Regime classificatie
- *"Waar zijn de belangrijke structuren?"* → Support/resistance, swing points
- *"Wat is de volatiliteit?"* → ATR, Bollinger Bands
- *"Wat is het sentiment?"* → Volume analyse, orderbook diepte

**Kernkenmerk:** Objectief en beschrijvend. De data wordt verrijkt, niet gefilterd.

#### **Fase 2: HERKENNEN ("Zie ik een kans?")**
De quant herkent patronen die mogelijk tot een trade kunnen leiden:
- *"Is er een FVG na een MSS?"* → Patroonherkenning
- *"Is het volume hoog genoeg?"* → Validatie/filtering
- *"Klopt de timing met mijn theorie?"* → Bevestiging

**Kernkenmerk:** Analytisch en probabilistisch. Er ontstaat een "handelsidee" maar nog geen concreet plan.

#### **Fase 3: BESLISSEN ("Wat ga ik doen?")**
Het idee transformeert naar een uitvoerbaar plan:

**3A: PLANNEN (De "Wat als ik trade?" fase)**
- *"Waar stap ik in?"* → Entry planning
- *"Waar plaats ik mijn stop?"* → Risk management
- *"Hoeveel risico neem ik?"* → Position sizing
- *"Hoe voer ik dit technisch uit?"* → Order routing

**3B: MANAGEN (De "Ik ben nu in een trade" fase)**
- *"Moet ik mijn stop aanpassen?"* → Trailing stops
- *"Neem ik gedeeltelijk winst?"* → Profit taking
- *"Is er een reden om eruit te stappen?"* → Exit management

**Kernkenmerk:** Deterministisch en regelgebaseerd. Gegeven een situatie, is de actie voorspelbaar.

#### **Fase 4: BEWAKEN ("Gaat alles nog goed?")**
Parallel aan alles loopt de observatie:
- *"Heb ik te veel drawdown?"* → Portfolio monitoring
- *"Werkt mijn connectie nog?"* → System health
- *"Is er breaking news?"* → Market events

**Kernkenmerk:** Reactief en informatief. Er wordt niet gehandeld, maar gesignaleerd.

### 2.2 Mapping naar Worker Categorieën

```
Fase 1: BEGRIJPEN    → ContextWorker
Fase 2: HERKENNEN    → OpportunityWorker
Fase 3A: PLANNEN     → PlanningWorker
Fase 3B: MANAGEN     → ExecutionWorker
Fase 4: BEWAKEN      → ThreatWorker (parallel)
```

---

## 3. De 5 Worker Categorieën

### 3.1 ContextWorker - "De Cartograaf"

**Single Responsibility:** Het in kaart brengen en verrijken van de markt met objectieve, beschrijvende context.

**Wat doet deze worker:**
- Transformeert ruwe data naar bruikbare informatie
- Voegt indicatoren, structuren en classificaties toe
- Verrijkt ZONDER te filteren of te oordelen

**Data bronnen:**
- Trade ticks & OHLCV candles
- Orderbook snapshots
- News feeds & sentiment data
- Fear & Greed indices
- Social media (Twitter, Reddit)
- On-chain data (voor crypto)

**Output:** Een verrijkte `TradingContext` met een complete "kaart" van de markt.

**Voorbeelden:**
- `EMADetector` - berekent moving averages
- `MarketStructureDetector` - identificeert swing highs/lows
- `ADXRegimeClassifier` - classificeert trending vs ranging
- `NewsSentimentEnricher` - voegt sentiment scores toe
- `OrderbookImbalanceCalculator` - analyseert bid/ask ratio's

**Kernprincipe:** **Objectief en beschrijvend** - "Dit is wat er is"

---

### 3.2 OpportunityWorker - "De Verkenner"

**Single Responsibility:** Het herkennen van handelskansen op basis van patronen, theorieën en strategieën.

**Wat doet deze worker:**
- Scant de verrijkte context op zoek naar kansen
- Herkent patronen die passen bij een handelsstrategie
- Genereert "handelsideeën" zonder concrete plannen

**Diversiteit in benaderingen:**
- **Technische analyse:** FVG's, breakouts, divergenties
- **Fundamentele triggers:** "Buy the rumour, sell the news"
- **Sentiment-driven:** Extreme fear/greed levels
- **Statistical arbitrage:** Mean reversion, correlation breaks
- **Machine learning:** Pattern recognition models

**Output:** Een `Signal` DTO - een abstract handelsidee.

**Voorbeelden:**
- `FVGEntryDetector` - detecteert Fair Value Gaps
- `BreakoutScanner` - herkent structurele doorbraken
- `RumourBuySignalGenerator` - reageert op nieuws
- `MeanReversionDetector` - identificeert oversold/overbought
- `MLPatternRecognizer` - gebruikt trained models

**Kernprincipe:** **Probabilistisch en creatief** - "Ik zie een mogelijkheid"

---

### 3.3 ThreatWorker - "De Waakhond"

**Single Responsibility:** Het detecteren van risico's, bedreigingen en afwijkingen in de operatie.

**Wat doet deze worker:**
- Monitort de staat van ledgers (aggregated & strategy)
- Observeert de context voor gevaarlijke situaties
- Publiceert waarschuwende events, handelt NOOIT zelf

**Focus op risico's:**
- **Portfolio risico's:** Drawdown, exposure, correlation
- **Markt risico's:** Extreme volatiliteit, liquiditeit droogte
- **Systeem risico's:** Connectie problemen, data gaps
- **Strategische risico's:** Underperformance, parameter drift

**Output:** Strategische events (bijv. `MAX_DRAWDOWN_BREACHED`, `HIGH_VOLATILITY_DETECTED`)

**Voorbeelden:**
- `MaxDrawdownMonitor` - bewaakt portfolio drawdown
- `VolatilitySpikeDetector` - detecteert abnormale volatiliteit
- `ConnectionHealthMonitor` - controleert API verbindingen
- `CorrelationBreakMonitor` - detecteert onverwachte correlaties
- `LiquidityDroughtDetector` - waarschuwt voor lage liquiditeit

**Kernprincipe:** **Defensief en informatief** - "Let op, hier is een risico"

**Naamgeving Rationale:**
De naam "ThreatWorker" is gekozen boven "MonitorWorker" omdat:
- Het de **dualiteit** met OpportunityWorker benadrukt (kansen vs bedreigingen)
- Het **duidelijker** communiceert wat de worker doet (risico's detecteren)
- Het **intuïtiever** is voor een quant die denkt in termen van "opportunities and threats"

---

### 3.4 PlanningWorker - "De Strateeg"

**Single Responsibility:** Het transformeren van handelskansen naar concrete, uitvoerbare plannen.

**Wat doet deze worker:**
- Neemt een `Signal` van de OpportunityWorker
- Luistert naar events van de ThreatWorker
- Bepaalt de precieze entry, exit, size en routing

**De vier planningsfasen:**
1. **Entry Planning** - "Waar stap ik in?"
2. **Exit Planning** - "Waar plaats ik mijn stops en targets?"
3. **Size Planning** - "Hoeveel risico neem ik?"
4. **Order Routing** - "Hoe voer ik dit technisch uit?"

**Output:** Een `RoutedTradePlan` - een volledig uitgewerkt plan.

**Voorbeelden:**
- `LimitEntryPlanner` - bepaalt limit order prijzen
- `LiquidityTargetExitPlanner` - plaatst stops bij liquidity zones
- `FixedRiskSizer` - berekent positiegrootte op basis van risico%
- `TWAPRouter` - verdeelt orders over tijd
- `IcebergOrderRouter` - verbergt grote orders

**Kernprincipe:** **Deterministisch en tactisch** - "Gegeven deze kans, dit is het plan"

---

### 3.5 ExecutionWorker - "De Uitvoerder"

**Single Responsibility:** Het uitvoeren en actief beheren van trades en operationele taken.

**Wat doet deze worker:**
- Voert plannen uit via de ExecutionEnvironment
- Beheert actieve posities dynamisch
- Reageert op triggers (tijd, events, markt)

**Drie sub-domeinen:**
1. **Trade Execution** - Het initiëren van trades
2. **Position Management** - Het beheren van lopende posities
3. **Operational Tasks** - Geplande, operationele acties

**Output:** Directe acties in de markt of op het systeem.

**Voorbeelden:**
- `DefaultPlanExecutor` - voert een RoutedTradePlan uit
- `TrailingStopManager` - past stops dynamisch aan
- `PartialProfitTaker` - neemt gedeeltelijk winst
- `EmergencyExitAgent` - forceert exits bij kritieke events
- `DCARebalancer` - voert periodieke rebalancing uit

**Kernprincipe:** **Actief en deterministisch** - "Ik voer uit en beheer"

---

### 3.6 De Dataflow: Hoe Werken Ze Samen?

```
┌─────────────────────────────────────────────────────────────┐
│  RUWE DATA (Ticks, OHLCV, News, Orderbook, etc.)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   1. ContextWorker            │
         │   "Ik breng in kaart"         │
         └───────────┬───────────────────┘
                     │ TradingContext (verrijkt)
                     ├──────────────┬────────────────┐
                     ▼              ▼                ▼
         ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
         │ 2. Opportunity  │  │ 3. Threat    │  │              │
         │    Worker       │  │    Worker    │  │  (Parallel)  │
         │ "Ik zie kansen" │  │ "Ik zie      │  │              │
         │                 │  │  risico's"   │  │              │
         └────────┬────────┘  └──────┬───────┘  └──────────────┘
                  │                  │
                  │ Signal           │ Events (warnings)
                  │                  │
                  └────────┬─────────┘
                           ▼
                 ┌──────────────────────┐
                 │  4. PlanningWorker   │
                 │  "Ik maak een plan"  │
                 │  (gebruikt 2 & 3)    │
                 └──────────┬───────────┘
                            │ RoutedTradePlan
                            ▼
                 ┌──────────────────────┐
                 │  5. ExecutionWorker  │
                 │  "Ik voer uit"       │
                 └──────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  MARKT        │
                    └───────────────┘
```

---

## 4. Sub-Categorieën per Worker Type

### 4.1 ContextType (7 sub-categorieën)

```python
class ContextType(str, Enum):
    """
    Sub-categorieën voor ContextWorker plugins.
    Georganiseerd naar type data-verrijking en abstractieniveau.
    """
    
    # Markt Regime & Conditie
    REGIME_CLASSIFICATION = "regime_classification"
    # Voorbeelden: ADX trend filter, volatility regime classifier
    
    # Technische Structuur
    STRUCTURAL_ANALYSIS = "structural_analysis"  
    # Voorbeelden: Market structure detector, swing point identifier
    
    # Indicatoren & Berekeningen
    INDICATOR_CALCULATION = "indicator_calculation"
    # Voorbeelden: EMA, RSI, MACD, Bollinger Bands
    
    # Orderbook & Microstructuur
    MICROSTRUCTURE_ANALYSIS = "microstructure_analysis"
    # Voorbeelden: Orderbook imbalance, bid-ask spread analyzer
    
    # Temporele Context
    TEMPORAL_CONTEXT = "temporal_context"
    # Voorbeelden: Session analyzer, time-of-day patterns, killzones
    
    # Sentiment & Alternatieve Data
    SENTIMENT_ENRICHMENT = "sentiment_enrichment"
    # Voorbeelden: News sentiment, social media analysis, fear & greed
    
    # On-chain & Fundamentele Data
    FUNDAMENTAL_ENRICHMENT = "fundamental_enrichment"
    # Voorbeelden: On-chain metrics, earnings data, economic indicators
```

**Rationale:** Deze indeling volgt de **bron en aard van de data**, wat intuïtief is voor een quant die denkt: "Ik wil sentiment toevoegen" of "Ik wil structuur analyseren".

---

### 4.2 OpportunityType (7 sub-categorieën)

```python
class OpportunityType(str, Enum):
    """
    Sub-categorieën voor OpportunityWorker plugins.
    Georganiseerd naar handelsstrategie type en theoretische basis.
    """
    
    # Technische Patroon Herkenning
    TECHNICAL_PATTERN = "technical_pattern"
    # Voorbeelden: FVG detector, breakout scanner, divergence finder
    
    # Momentum & Trend Following
    MOMENTUM_SIGNAL = "momentum_signal"
    # Voorbeelden: Trend continuation, momentum breakout
    
    # Mean Reversion
    MEAN_REVERSION = "mean_reversion"
    # Voorbeelden: Oversold/overbought, range bounce
    
    # Arbitrage & Statistical
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    # Voorbeelden: Pair trading, correlation breaks
    
    # Event-Driven
    EVENT_DRIVEN = "event_driven"
    # Voorbeelden: News-based signals, "buy the rumour"
    
    # Sentiment-Driven
    SENTIMENT_SIGNAL = "sentiment_signal"
    # Voorbeelden: Extreme fear/greed, social sentiment spikes
    
    # Machine Learning
    ML_PREDICTION = "ml_prediction"
    # Voorbeelden: Trained model predictions, pattern recognition AI
```

**Rationale:** Deze indeling volgt **strategische benaderingen** die een quant herkent uit de literatuur en praktijk.

---

### 4.3 ThreatType (5 sub-categorieën)

```python
class ThreatType(str, Enum):
    """
    Sub-categorieën voor ThreatWorker plugins.
    Georganiseerd naar domein van risico dat wordt gemonitord.
    """
    
    # Portfolio & Financieel Risico
    PORTFOLIO_RISK = "portfolio_risk"
    # Voorbeelden: Max drawdown monitor, exposure monitor, correlation risk
    
    # Markt Risico & Volatiliteit
    MARKET_RISK = "market_risk"
    # Voorbeelden: Volatility spike detector, liquidity drought detector
    
    # Systeem & Technische Gezondheid
    SYSTEM_HEALTH = "system_health"
    # Voorbeelden: Connection monitor, data gap detector, latency monitor
    
    # Strategie Performance
    STRATEGY_PERFORMANCE = "strategy_performance"
    # Voorbeelden: Win rate degradation, parameter drift detector
    
    # Externe Events
    EXTERNAL_EVENT = "external_event"
    # Voorbeelden: Breaking news monitor, regulatory change detector
```

**Rationale:** Deze indeling volgt de **bron van het risico**, wat helpt bij het organiseren van risk management.

---

### 4.4 PlanningPhase (4 sub-categorieën)

```python
class PlanningPhase(str, Enum):
    """
    Sub-categorieën voor PlanningWorker plugins.
    Georganiseerd naar planningsfase in de trade lifecycle.
    """
    
    # Entry Planning
    ENTRY_PLANNING = "entry_planning"
    # Voorbeelden: Limit entry planner, market entry planner, TWAP entry
    
    # Exit Planning (Stop Loss & Take Profit)
    EXIT_PLANNING = "exit_planning"
    # Voorbeelden: Liquidity target exit, ATR-based stops, fixed R:R
    
    # Position Sizing
    SIZE_PLANNING = "size_planning"
    # Voorbeelden: Fixed risk sizer, Kelly criterion, volatility-based sizing
    
    # Order Routing & Execution Tactics
    ORDER_ROUTING = "order_routing"
    # Voorbeelden: Default router, iceberg orders, smart order routing
```

**Rationale:** Deze indeling volgt de **natuurlijke volgorde** van trade planning die elke quant doorloopt.

---

### 4.5 ExecutionType (4 sub-categorieën)

```python
class ExecutionType(str, Enum):
    """
    Sub-categorieën voor ExecutionWorker plugins.
    Georganiseerd naar type actie en lifecycle fase.
    """
    
    # Trade Initiatie
    TRADE_INITIATION = "trade_initiation"
    # Voorbeelden: Plan executor, manual trade executor
    
    # Actieve Position Management
    POSITION_MANAGEMENT = "position_management"
    # Voorbeelden: Trailing stop manager, partial profit taker, scale-in/out
    
    # Risk & Safety Management
    RISK_SAFETY = "risk_safety"
    # Voorbeelden: Emergency exit agent, circuit breaker, forced liquidation
    
    # Operationele & Geplande Taken
    OPERATIONAL = "operational"
    # Voorbeelden: DCA rebalancer, scheduled rebalancing, portfolio cleanup
```

**Rationale:** Deze indeling volgt de **aard van de actie** - van initiatie tot beheer tot noodmaatregelen.

---

### 4.6 Overzichtstabel

| Worker Categorie | Sub-Categorie Enum | Aantal Sub-Types | Organisatie Principe |
|------------------|-------------------|------------------|---------------------|
| **ContextWorker** | `ContextType` | 7 | Type data-verrijking |
| **OpportunityWorker** | `OpportunityType` | 7 | Strategische benadering |
| **ThreatWorker** | `ThreatType` | 5 | Domein van risico |
| **PlanningWorker** | `PlanningPhase` | 4 | Planningsfase |
| **ExecutionWorker** | `ExecutionType` | 4 | Type actie |

**Totaal:** 5 hoofdcategorieën, 27 sub-categorieën

---

## 5. Event-Driven Architectuur

### 5.1 Het Probleem: Complexiteit vs Flexibiliteit

Een volledig event-driven systeem biedt maximale flexibiliteit, maar introduceert complexiteit:
- Quants moeten events begrijpen
- Event chains moeten worden gemanaged
- Debugging wordt moeilijker

**Oplossing:** Drie abstractie niveaus die progressieve complexiteit bieden.

---

### 5.2 Niveau 1: Impliciete Pijplijnen (95% van gebruik)

**Voor wie:** Standaard quant die een lineaire strategie wil bouwen.

**Hoe het werkt:** De quant definieert workers, het systeem genereert automatisch de event chain.

**Voorbeeld:**
```yaml
# strategy_blueprint.yaml
workforce:
  context_workers:
    - plugin: "ema_detector"
    - plugin: "market_structure_detector"
  
  opportunity_workers:
    - plugin: "fvg_detector"
  
  planning_workers:
    entry_planning:
      - plugin: "limit_entry_planner"
    exit_planning:
      - plugin: "liquidity_target_exit"
    size_planning:
      - plugin: "fixed_risk_sizer"
    order_routing:
      - plugin: "default_router"
  
  execution_workers:
    trade_initiation:
      - plugin: "default_plan_executor"
```

**Automatisch gegenereerde event flow:**
```
MarketDataReceived 
  → ContextReady 
  → SignalGenerated 
  → PlanReady 
  → ExecutionApproved
```

**Voordelen:**
- ✅ Geen event management nodig
- ✅ Duidelijke, lineaire flow
- ✅ "Het werkt gewoon"

---

### 5.3 Niveau 2: Predefined Triggers (Opt-in)

**Voor wie:** Quant die specifieke workers op specifieke momenten wil activeren.

**Hoe het werkt:** Gebruik predefined trigger namen voor common use cases.

**Voorbeeld:**
```yaml
# strategy_blueprint.yaml
workforce:
  context_workers:
    - plugin: "ema_detector"
  
  opportunity_workers:
    - plugin: "fvg_detector"
  
  # Threat monitoring (parallel aan main flow)
  threat_workers:
    - plugin: "max_drawdown_monitor"
      triggers:
        - "on_ledger_update"  # Predefined trigger
    
    - plugin: "news_event_monitor"
      triggers:
        - "on_context_ready"  # Check bij elke nieuwe context
```

**Predefined Triggers:**
```python
PREDEFINED_TRIGGERS = {
    "on_context_ready": "Wanneer context klaar is",
    "on_signal_generated": "Wanneer een signaal is gegenereerd",
    "on_ledger_update": "Wanneer ledger verandert",
    "on_position_opened": "Wanneer een positie wordt geopend",
    "on_position_closed": "Wanneer een positie wordt gesloten",
    "on_schedule": "Tijd-gebaseerd (via scheduler)",
}
```

**Voordelen:**
- ✅ Meer controle waar nodig
- ✅ Geen custom event namen
- ✅ Duidelijke, gedocumenteerde opties

---

### 5.4 Niveau 3: Custom Event Chains (Expert Mode)

**Voor wie:** Geavanceerde quant die complexe, event-driven workflows wil bouwen.

**Hoe het werkt:** Definieer custom events en hun routing expliciet.

**Voorbeeld: Smart DCA**
```yaml
# strategy_blueprint.yaml (ADVANCED)
workforce:
  context_workers:
    - plugin: "regime_classifier"
    - plugin: "premium_discount_detector"
  
  opportunity_workers:
    - plugin: "dca_opportunity_scorer"
      triggers:
        - "on_schedule:weekly_dca"  # Scheduler event
      publishes:
        - event: "dca_opportunity_scored"
          payload_type: "Signal"
  
  threat_workers:
    - plugin: "dca_risk_assessor"
      triggers:
        - "on_schedule:weekly_dca"
      publishes:
        - event: "dca_risk_assessed"
          payload_type: "CriticalEvent"
  
  planning_workers:
    entry_planning:
      - plugin: "adaptive_dca_planner"
        triggers:
          - "dca_opportunity_scored"
          - "dca_risk_assessed"
        requires_all: true  # Wacht op beide events
        publishes:
          - event: "dca_plan_ready"
            payload_type: "TradePlan"
  
  execution_workers:
    operational:
      - plugin: "dca_plan_executor"
        triggers:
          - "dca_plan_ready"
```

**Event Flow:**
```
Scheduler → WEEKLY_DCA_TICK
         ↓
    ┌────┴────┐
    ▼         ▼
Opportunity  Threat
  Scorer    Assessor
    │         │
    ▼         ▼
dca_opportunity_scored  dca_risk_assessed
         │         │
         └────┬────┘
              ▼
      Adaptive DCA Planner
              ▼
        dca_plan_ready
              ▼
       DCA Plan Executor
```

**Voordelen:**
- ✅ Volledige controle
- ✅ Complexe workflows mogelijk
- ✅ Opt-in: alleen als nodig

---

### 5.5 Event Chain Validatie

Het systeem valideert automatisch event chains:

```python
# ComponentBuilder (pseudo-code)
def _validate_event_chain(self, blueprint):
    """Controleert of alle events correct zijn gedefinieerd."""
    
    # Check 1: Alle triggers hebben een publisher
    for worker in blueprint.all_workers():
        for trigger in worker.triggers:
            if not self._has_publisher(trigger, blueprint):
                raise ValidationError(
                    f"Worker '{worker.name}' luistert naar event '{trigger}', "
                    f"maar geen enkele worker publiceert dit event!"
                )
    
    # Check 2: Geen circular dependencies
    if self._has_circular_dependency(blueprint):
        raise ValidationError("Circular event dependency detected!")
    
    # Check 3: Alle publishes hebben een subscriber
    for worker in blueprint.all_workers():
        for event in worker.publishes:
            if not self._has_subscriber(event, blueprint):
                logger.warning(
                    f"Worker '{worker.name}' publiceert event '{event}', "
                    f"maar niemand luistert ernaar. Is dit intentioneel?"
                )
```

---

### 5.6 De Scheduler: Event Source

De Scheduler is **geen worker**, maar een **Event Source** die tijd-gebaseerde events publiceert:

```yaml
# schedule.yaml
schedules:
  - name: "weekly_dca"
    cron: "0 10 * * 1"  # Elke maandag 10:00
    event: "WEEKLY_DCA_TICK"
  
  - name: "eod_check"
    cron: "0 22 * * *"  # Elke dag 22:00
    event: "END_OF_DAY_TICK"
```

**Workflow:**
```
Scheduler → Event → Operator → Worker(s)
```

**Primaire target:** `ExecutionWorker.OPERATIONAL`

---

## 6. Worker Base Classes

### 6.1 Ontwerpprincipe: Opt-in Capabilities

Workers kunnen verschillende capabilities hebben, maar alleen als ze die nodig hebben:

```
BaseWorker (90%)
    ├─ Pure, stateless functie
    └─ Geen dependencies
    
BaseStatefulWorker (5%)
    ├─ Automatisch state persistence
    └─ Crash recovery via journaling
    
BaseEventAwareWorker (5%)
    ├─ Event ontvangst via on_event()
    └─ Event publicatie via self.emit()
    
BaseStatefulEventAwareWorker (Zeldzaam)
    └─ Combinatie van beide
```

---

### 6.2 BaseWorker (Simpel, 90% van plugins)

```python
# backend/core/base_worker.py
from abc import ABC, abstractmethod
from typing import Any

class BaseWorker(ABC):
    """
    Pure, stateless worker.
    
    Dit is de standaard base class voor de meeste plugins.
    Geen state, geen events, alleen pure business logica.
    """
    
    def __init__(self, params: Any):
        """
        Args:
            params: Pydantic model met plugin configuratie
        """
        self.params = params
    
    @abstractmethod
    def process(self, context: TradingContext) -> Any:
        """
        Hoofdmethode die de business logica bevat.
        
        Args:
            context: De volledige trading context
            
        Returns:
            Plugin-specifieke output (Signal, TradePlan, etc.)
        """
        raise NotImplementedError
```

**Gebruik:**
```python
# plugins/opportunity_workers/fvg_detector/worker.py
class FVGDetector(BaseWorker):
    """Detecteert Fair Value Gaps."""
    
    def process(self, context: TradingContext) -> List[Signal]:
        signals = []
        
        for i in range(len(context.enriched_df) - 3):
            if self._is_fvg(context.enriched_df, i):
                signals.append(Signal(
                    correlation_id=uuid4(),
                    timestamp=context.enriched_df.index[i],
                    asset=context.asset_pair,
                    direction='long',
                    signal_type='fvg_entry'
                ))
        
        return signals
    
    def _is_fvg(self, df, i):
        # Pure business logica
        pass
```

---

### 6.3 BaseStatefulWorker (Voor state persistence)

```python
class BaseStatefulWorker(BaseWorker):
    """
    Worker met automatisch state management.
    
    Gebruikt atomic writes (journal → fsync → rename) voor crash recovery.
    De ontwikkelaar hoeft alleen self.state te lezen/schrijven en
    self.commit_state() aan te roepen.
    """
    
    def __init__(self, params: Any, state_path: str):
        """
        Args:
            params: Plugin configuratie
            state_path: Directory voor state opslag
        """
        super().__init__(params)
        self._state_path = state_path
        self._state = self._load_state()  # Automatisch laden met recovery
    
    @property
    def state(self) -> Dict[str, Any]:
        """
        Toegang tot state (read/write).
        
        Example:
            self.state['counter'] += 1
            self.state['last_price'] = 50000.0
        """
        return self._state
    
    def commit_state(self) -> None:
        """
        Veilig opslaan met atomic writes.
        
        Workflow:
        1. Schrijf naar state.json.journal
        2. Voer os.fsync() uit
        3. Voer os.rename() uit
        
        Example:
            self.state['counter'] += 1
            self.commit_state()  # Veilig opgeslagen
        """
        self._save_state_atomic(self._state)
    
    def _load_state(self) -> Dict[str, Any]:
        """
        Herstel-logica met journal recovery.
        
        Workflow:
        1. Check of .journal bestand bestaat
        2. Zo ja: rename naar .json (crash recovery)
        3. Laad state.json
        4. Return state of empty dict
        """
        journal_file = os.path.join(self._state_path, "state.json.journal")
        state_file = os.path.join(self._state_path, "state.json")
        
        # Crash recovery
        if os.path.exists(journal_file):
            os.rename(journal_file, state_file)
        
        # Laad state
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        
        return {}
    
    def _save_state_atomic(self, state: Dict[str, Any]) -> None:
        """Atomic write implementatie."""
        journal_file = os.path.join(self._state_path, "state.json.journal")
        state_file = os.path.join(self._state_path, "state.json")
        
        # 1. Schrijf naar journal
        with open(journal_file, 'w') as f:
            json.dump(state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # 2. Force write to disk
        
        # 3. Atomic rename
        os.rename(journal_file, state_file)
```

**Gebruik:**
```python
# plugins/execution_workers/trailing_stop_manager/worker.py
class TrailingStopManager(BaseStatefulWorker):
    """Beheert trailing stops met state persistence."""
    
    def process(self, context: TradingContext) -> None:
        current_price = context.current_price
        
        # Lees state
        high_water_mark = self.state.get('high_water_mark', current_price)
        
        # Update state
        if current_price > high_water_mark:
            self.state['high_water_mark'] = current_price
            self.commit_state()  # Veilig opgeslagen
        
        # Business logica
        new_stop = high_water_mark * (1 - self.params.trail_percent)
        self._update_stop_loss(new_stop)
```

---

### 6.4 BaseEventAwareWorker (Voor event interactie)

```python
from typing import Optional, Any, Callable
from abc import ABC

class IEventHandler(ABC):
    """
    Abstracte interface voor event publicatie.
    
    Workers gebruiken deze interface, niet de concrete EventBus.
    Dit maakt workers testbaar en herbruikbaar.
    """
    
    @abstractmethod
    def publish(self, event_name: str, payload: Any) -> None:
        """Publiceer een event."""
        raise NotImplementedError


class BaseEventAwareWorker(BaseWorker):
    """
    Worker die events kan ontvangen en publiceren via abstractie.
    
    De worker kent GEEN concrete EventBus, alleen een interface.
    De Operator injecteert een EventHandler tijdens initialisatie.
    """
    
    def __init__(self, params: Any):
        super().__init__(params)
        self._event_handler: Optional[IEventHandler] = None
    
    def set_event_handler(self, handler: IEventHandler) -> None:
        """
        Wordt aangeroepen door de Operator tijdens setup.
        Plugin ontwikkelaar hoeft dit nooit aan te raken.
        
        Args:
            handler: Event handler interface
        """
        self._event_handler = handler
    
    def emit(self, event_name: str, payload: Any) -> None:
        """
        Simpele API voor plugin om events te publiceren.
        
        Args:
            event_name: Naam van het event (zoals gedefinieerd in manifest)
            payload: DTO object om te publiceren
        
        Example:
            signal = Signal(...)
            self.emit("dca_opportunity_scored", signal)
        """
        if self._event_handler:
            self._event_handler.publish(event_name, payload)
        else:
            logger.warning(
                f"Worker '{self.__class__.__name__}' tried to emit event "
                f"'{event_name}' but no event handler is configured."
            )
    
    def on_event(self, event_name: str, payload: Any) -> None:
        """
        Override deze methode om events te ontvangen.
        
        De Operator roept deze methode aan wanneer een relevant event
        binnenkomt (zoals gedefinieerd in het manifest).
        
        Args:
            event_name: Naam van het ontvangen event
            payload: DTO object van het event
        
        Example:
            def on_event(self, event_name, payload):
                if event_name == "dca_opportunity_scored":
                    self._opportunity_score = payload.metadata['score']
                elif event_name == "dca_risk_assessed":
                    self._risk_level = payload.metadata['risk_level']
        """
        pass  # Default: doe niets
```

**Gebruik:**
```python
# plugins/opportunity_workers/dca_opportunity_scorer/worker.py
class DCAOpportunityScorer(BaseEventAwareWorker):
    """Event-aware worker die opportunity scores publiceert."""
    
    def process(self, context: TradingContext) -> List[Signal]:
        score = self._calculate_score(context)
        
        signal = Signal(
            correlation_id=uuid4(),
            timestamp=context.current_timestamp,
            asset=context.asset_pair,
            direction='long',
            signal_type='dca_opportunity',
            metadata={'opportunity_score': score}
        )
        
        # Publiceer event (simpele API)
        self.emit("dca_opportunity_scored", signal)
        
        return [signal]
    
    def _calculate_score(self, context: TradingContext) -> float:
        """Pure business logica."""
        score = 50
        regime = context.enriched_df['regime'].iloc[-1]
        if regime == 'bullish':
            score += 20
        # ... rest van logica
        return score
```

**Gebruik (ontvangen):**
```python
# plugins/planning_workers/adaptive_dca_planner/worker.py
class AdaptiveDCAPlanner(BaseEventAwareWorker):
    """Event-aware planner die reageert op opportunity en risk events."""
    
    def __init__(self, params):
        super().__init__(params)
        self._opportunity_score: Optional[float] = None
        self._risk_level: Optional[str] = None
    
    def on_event(self, event_name: str, payload: Any) -> None:
        """Operator roept dit aan voor relevante events."""
        if event_name == "dca_opportunity_scored":
            self._opportunity_score = payload.metadata['opportunity_score']
        
        elif event_name == "dca_risk_assessed":
            self._risk_level = payload.metadata['risk_level']
    
    def process(self, signal: Signal, context: TradingContext) -> Optional[TradePlan]:
        """Pure business logica."""
        if self._opportunity_score is None or self._risk_level is None:
            return None  # Nog niet klaar
        
        amount = self._calculate_amount(
            self._opportunity_score,
            self._risk_level
        )
        
        if amount == 0:
            return None
        
        plan = TradePlan(...)
        
        # Optioneel: publiceer dat plan klaar is
        self.emit("dca_plan_ready", plan)
        
        return plan
```

---

### 6.5 BaseStatefulEventAwareWorker (Combinatie)

```python
class BaseStatefulEventAwareWorker(BaseStatefulWorker, BaseEventAwareWorker):
    """
    Worker die ZOWEL state persistence ALS event interactie nodig heeft.
    
    Combineert beide capabilities via multiple inheritance.
    """
    
    def __init__(self, params: Any, state_path: str):
        BaseStatefulWorker.__init__(self, params, state_path)
        BaseEventAwareWorker.__init__(self, params)
```

**Gebruik:**
```python
class ComplexWorker(BaseStatefulEventAwareWorker):
    """Worker met state + events."""
    
    def on_event(self, event_name: str, payload: Any):
        # Update state op basis van event
        self.state['last_event'] = event_name
        self.state['event_count'] = self.state.get('event_count', 0) + 1
        self.commit_state()
    
    def process(self, context: TradingContext):
        # Gebruik state
        event_count = self.state.get('event_count', 0)
        
        # Business logica
        result = self._calculate(event_count)
        
        # Publiceer event
        self.emit("result_ready", result)
        
        return result
```

---

### 6.6 Testing: Voor & Na

**VOOR (zonder base classes):**
```python
def test_dca_scorer():
    # Complex: mock EventBus nodig
    mock_bus = MockEventBus()
    scorer = DCAOpportunityScorer(params, mock_bus)
    
    context = create_test_context()
    signals = scorer.process(context)
    
    # Moet bus calls verifiëren
    assert mock_bus.published_events[0] == ("dca_opportunity_scored", signals[0])
```

**NA (met BaseEventAwareWorker):**
```python
def test_dca_scorer():
    # Simpel: geen bus nodig
    scorer = DCAOpportunityScorer(params)
    
    # Optioneel: mock handler voor event verificatie
    mock_handler = MockEventHandler()
    scorer.set_event_handler(mock_handler)
    
    context = create_test_context()
    signals = scorer.process(context)
    
    # Verifieer business logica
    assert signals[0].metadata['opportunity_score'] == 75
    
    # Optioneel: verifieer event
    assert mock_handler.emitted_events[0] == ("dca_opportunity_scored", signals[0])
```

---

## 7. Concrete Use Cases

### 7.1 ICT/SMC Strategie

**Methodologie:** Smart Money Concepts met focus op market structure, liquidity zones en Fair Value Gaps.

**Worker Mapping:**

```yaml
# strategy_blueprint.yaml
name: "ICT_FVG_Liquidity_Sweep"
version: "1.0.0"

workforce:
  # === CONTEXT: Bouw de ICT "kaart" ===
  context_workers:
    # Structurele analyse
    - plugin: "market_structure_detector"
      subtype: "structural_analysis"
      params:
        detect_bos: true
        detect_choch: true
    
    - plugin: "liquidity_zone_mapper"
      subtype: "structural_analysis"
      params:
        map_buy_side_liquidity: true
        map_sell_side_liquidity: true
    
    - plugin: "order_block_identifier"
      subtype: "structural_analysis"
    
    # Indicatoren
    - plugin: "premium_discount_calculator"
      subtype: "indicator_calculation"
      params:
        fibonacci_levels: [0.5, 0.618, 0.786]
    
    - plugin: "session_analyzer"
      subtype: "temporal_context"
      params:
        london_session: true
        new_york_session: true
        killzones: true
    
    # Regime
    - plugin: "higher_timeframe_bias"
      subtype: "regime_classification"
      params:
        timeframes: ["4H", "Daily", "Weekly"]
  
  # === OPPORTUNITY: Detecteer ICT setups ===
  opportunity_workers:
    - plugin: "fvg_detector"
      subtype: "technical_pattern"
      params:
        min_gap_size: 5
        require_structure_break: true
    
    - plugin: "optimal_trade_entry_finder"
      subtype: "technical_pattern"
      params:
        look_for_ote: true
        require_order_block: true
    
    - plugin: "liquidity_sweep_detector"
      subtype: "momentum_signal"
      params:
        detect_stop_hunts: true
  
  # === THREAT: Monitor risico's ===
  threat_workers:
    - plugin: "max_drawdown_monitor"
      subtype: "portfolio_risk"
      params:
        max_daily_drawdown: 2.0
    
    - plugin: "news_event_monitor"
      subtype: "market_risk"
      params:
        high_impact_events: true
        pause_trading_minutes_before: 30
    
    - plugin: "economic_calendar_monitor"
      subtype: "external_event"
      params:
        track_fomc: true
        track_nfp: true
  
  # === PLANNING: Construeer het trade plan ===
  planning_workers:
    entry_planning:
      - plugin: "limit_entry_at_fvg"
        params:
          entry_at_fvg_midpoint: true
    
    exit_planning:
      - plugin: "liquidity_target_exit"
        params:
          target_opposite_liquidity: true
          stop_below_order_block: true
      
      - plugin: "atr_based_stops"
        params:
          atr_multiplier: 1.5
    
    size_planning:
      - plugin: "fixed_risk_sizer"
        params:
          risk_per_trade_percent: 1.0
    
    order_routing:
      - plugin: "limit_order_router"
  
  # === EXECUTION: Voer uit en beheer ===
  execution_workers:
    trade_initiation:
      - plugin: "default_plan_executor"
    
    position_management:
      - plugin: "partial_profit_taker"
        params:
          take_50_percent_at_first_target: true
          move_stop_to_breakeven: true
      
      - plugin: "trailing_stop_manager"
        params:
          trail_after_first_target: true
          trail_by_structure: true
    
    risk_safety:
      - plugin: "emergency_exit_on_news"
        params:
          exit_all_on_high_impact_news: true
```

**Validatie:**
- ✅ Alle ICT concepten passen in de taxonomie
- ✅ Market structure → STRUCTURAL_ANALYSIS
- ✅ Liquidity zones → STRUCTURAL_ANALYSIS
- ✅ FVG's → TECHNICAL_PATTERN
- ✅ Sessions/Killzones → TEMPORAL_CONTEXT
- ✅ Premium/Discount → INDICATOR_CALCULATION

---

### 7.2 Smart DCA (Event-Driven)

**Doel:** Dollar Cost Averaging die intelligent reageert op marktcondities en risico's.

**Worker Mapping:**

```yaml
# strategy_blueprint.yaml
name: "Smart_DCA_BTC"
version: "1.0.0"

workforce:
  # === CONTEXT ===
  context_workers:
    - plugin: "regime_classifier"
      subtype: "regime_classification"
    
    - plugin: "premium_discount_detector"
      subtype: "indicator_calculation"
    
    - plugin: "volatility_percentile_calculator"
      subtype: "indicator_calculation"
  
  # === OPPORTUNITY (Event-Aware) ===
  opportunity_workers:
    - plugin: "dca_opportunity_scorer"
      subtype: "technical_pattern"
      triggers:
        - "on_schedule:weekly_dca"
      publishes:
        - event: "dca_opportunity_scored"
          payload_type: "Signal"
      params:
        score_regime: true
        score_price_zone: true
        score_volatility: true
  
  # === THREAT (Event-Aware) ===
  threat_workers:
    - plugin: "dca_risk_assessor"
      subtype: "portfolio_risk"
      triggers:
        - "on_schedule:weekly_dca"
      publishes:
        - event: "dca_risk_assessed"
          payload_type: "CriticalEvent"
      params:
        max_drawdown_for_dca: 15.0
        max_volatility_percentile: 95
  
  # === PLANNING (Event-Aware) ===
  planning_workers:
    entry_planning:
      - plugin: "adaptive_dca_planner"
        triggers:
          - "dca_opportunity_scored"
          - "dca_risk_assessed"
        requires_all: true
        publishes:
          - event: "dca_plan_ready"
            payload_type: "TradePlan"
        params:
          base_amount: 1000
          min_amount: 500
          max_amount: 2000
  
  # === EXECUTION ===
  execution_workers:
    operational:
      - plugin: "dca_plan_executor"
        triggers:
          - "dca_plan_ready"
```

**Scheduler Configuratie:**
```yaml
# schedule.yaml
schedules:
  - name: "weekly_dca"
    cron: "0 10 * * 1"  # Elke maandag 10:00
    event: "WEEKLY_DCA_TICK"
```

**Event Flow:**
```
Scheduler → WEEKLY_DCA_TICK
         ↓
    ┌────┴────┐
    ▼         ▼
Opportunity  Threat
  Scorer    Assessor
    │         │
    ▼         ▼
dca_opportunity_scored  dca_risk_assessed
         │         │
         └────┬────┘
              ▼
      Adaptive DCA Planner
              ▼
        dca_plan_ready
              ▼
       DCA Plan Executor
```

**Beslissingsmatrix:**

| Opportunity Score | Risk Level | Action |
|-------------------|------------|--------|
| 80+ | LOW | Max amount (€2000) |
| 60-79 | LOW | Base amount (€1000) |
| <60 | LOW | Min amount (€500) |
| 70+ | MEDIUM | Base amount (€1000) |
| <70 | MEDIUM | Min amount (€500) |
| Any | HIGH | Skip |

**Validatie:**
- ✅ Complexe, event-driven workflow
- ✅ Workers blijven simpel en testbaar
- ✅ Intelligentie komt van compositie
- ✅ Geen event logica in plugin code

---

### 7.3 Andere Methodologieën

**Wyckoff:**
```
Context: STRUCTURAL_ANALYSIS (accumulation/distribution phases)
         INDICATOR_CALCULATION (volume analysis)
Opportunity: TECHNICAL_PATTERN (spring, upthrust)
✅ Past perfect
```

**Elliott Wave:**
```
Context: STRUCTURAL_ANALYSIS (wave counting)
         INDICATOR_CALCULATION (fibonacci retracements)
Opportunity: TECHNICAL_PATTERN (wave 3 detection)
✅ Past perfect
```

**Volume Profile:**
```
Context: MICROSTRUCTURE_ANALYSIS (volume at price)
         STRUCTURAL_ANALYSIS (value areas)
Opportunity: TECHNICAL_PATTERN (POC bounces)
✅ Past perfect
```

**ML-Driven:**
```
Context: Alle types (rijke feature set)
Opportunity: ML_PREDICTION + STATISTICAL_ARBITRAGE
Threat: STRATEGY_PERFORMANCE (drift detection)
Planning: Dynamische sizing op basis van confidence
✅ Past perfect
```

---

## 8. Migratie Strategie

### 8.1 Backwards Compatibility

**Principe:** Bestaande code blijft werken, nieuwe features zijn opt-in.

**Strategie:**
1. Introduceer nieuwe enums als aliases
2. Deprecate oude namen met warnings
3. Verwijder oude namen in V3.0

---

### 8.2 WorkerType Enum

**Huidig (V2):**
```python
class WorkerType(str, Enum):
    CONTEXT_WORKER = "context_worker"
    ANALYSIS_WORKER = "analysis_worker"
    MONITOR_WORKER = "monitor_worker"
    EXECUTION_WORKER = "execution_worker"
```

**Nieuw (V3):**
```python
class WorkerType(str, Enum):
    """
    De 5 fundamentele worker categorieën in de V3 architectuur.
    """
    CONTEXT_WORKER = "context_worker"
    OPPORTUNITY_WORKER = "opportunity_worker"  # NIEUW
    THREAT_WORKER = "threat_worker"            # NIEUW (was MONITOR_WORKER)
    PLANNING_WORKER = "planning_worker"        # NIEUW
    EXECUTION_WORKER = "execution_worker"
    
    # Backwards compatibility aliases (DEPRECATED)
    ANALYSIS_WORKER = "opportunity_worker"  # Alias voor OPPORTUNITY_WORKER
    MONITOR_WORKER = "threat_worker"        # Alias voor THREAT_WORKER
```

**Deprecation Warnings:**
```python
def __new__(cls, value):
    obj = str.__new__(cls, value)
    obj._value_ = value
    
    # Emit deprecation warning voor oude namen
    if value in ["analysis_worker", "monitor_worker"]:
        warnings.warn(
            f"WorkerType.{value.upper()} is deprecated. "
            f"Use WorkerType.OPPORTUNITY_WORKER or WorkerType.THREAT_WORKER instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    return obj
```

---

### 8.3 Phase Enums Mapping

**Oude AnalysisPhase → Nieuwe Taxonomie:**

```python
# Mapping voor automatische migratie
PHASE_MIGRATION_MAP = {
    # Oude AnalysisPhase → Nieuwe categorieën
    "signal_generation": ("opportunity_worker", "technical_pattern"),
    "signal_refinement": ("opportunity_worker", "technical_pattern"),
    "entry_planning": ("planning_worker", "entry_planning"),
    "exit_planning": ("planning_worker", "exit_planning"),
    "size_planning": ("planning_worker", "size_planning"),
    "order_routing": ("planning_worker", "order_routing"),
    
    # Oude ContextPhase → Nieuwe sub-types
    "regime_context": ("context_worker", "regime_classification"),
    "structural_context": ("context_worker", "structural_analysis"),
}
```

**Automatische Migratie:**
```python
def migrate_blueprint(old_blueprint: dict) -> dict:
    """Migreert een V2 blueprint naar V3 formaat."""
    new_blueprint = old_blueprint.copy()
    
    # Migreer analysis_workers naar opportunity + planning
    if "analysis_workers" in old_blueprint:
        opportunity_workers = []
        planning_workers = {
            "entry_planning": [],
            "exit_planning": [],
            "size_planning": [],
            "order_routing": []
        }
        
        for worker in old_blueprint["analysis_workers"]:
            phase = worker.get("phase")
            
            if phase in ["signal_generation", "signal_refinement"]:
                opportunity_workers.append(worker)
            elif phase == "entry_planning":
                planning_workers["entry_planning"].append(worker)
            elif phase == "exit_planning":
                planning_workers["exit_planning"].append(worker)
            elif phase == "size_planning":
                planning_workers["size_planning"].append(worker)
            elif phase == "order_routing":
                planning_workers["order_routing"].append(worker)
        
        new_blueprint["opportunity_workers"] = opportunity_workers
        new_blueprint["planning_workers"] = planning_workers
        del new_blueprint["analysis_workers"]
    
    # Hernoem monitor_workers naar threat_workers
    if "monitor_workers" in old_blueprint:
        new_blueprint["threat_workers"] = old_blueprint["monitor_workers"]
        del new_blueprint["monitor_workers"]
    
    return new_blueprint
```

---

### 8.4 Plugin Manifest Migratie

**Oud Manifest (V2):**
```yaml
identification:
  name: "fvg_detector"
  type: "analysis_worker"
  phase: "signal_generation"
```

**Nieuw Manifest (V3):**
```yaml
identification:
  name: "fvg_detector"
  type: "opportunity_worker"
  subtype: "technical_pattern"
```

**Automatische Conversie:**
```python
def migrate_manifest(old_manifest: dict) -> dict:
    """Migreert een V2 manifest naar V3 formaat."""
    new_manifest = old_manifest.copy()
    
    worker_type = old_manifest["identification"]["type"]
    phase = old_manifest["identification"].get("phase")
    
    if worker_type == "analysis_worker" and phase:
        new_type, new_subtype = PHASE_MIGRATION_MAP.get(phase, (worker_type, None))
        new_manifest["identification"]["type"] = new_type
        if new_subtype:
            new_manifest["identification"]["subtype"] = new_subtype
        del new_manifest["identification"]["phase"]
    
    elif worker_type == "monitor_worker":
        new_manifest["identification"]["type"] = "threat_worker"
    
    return new_manifest
```

---

### 8.5 Migratie Timeline

**Phase 1: V2.5 (Transitie Release)**
- Introduceer nieuwe enums met aliases
- Emit deprecation warnings
- Automatische migratie van blueprints
- Documentatie update

**Phase 2: V2.9 (Final Warning)**
- Verhoog warning level naar error in test mode
- Update alle voorbeelden naar nieuwe syntax
- Migratie tool voor bestaande plugins

**Phase 3: V3.0 (Clean Break)**
- Verwijder oude enums
- Verwijder backwards compatibility code
- Alleen nieuwe syntax ondersteund

---

## 9. Implementatie Roadmap

### 9.1 Phase 1: Core Taxonomie (MVP)

**Doel:** Implementeer de 5 worker categorieën met backwards compatibility.

**Taken:**
1. ✅ Update `enums.py` met nieuwe WorkerType en sub-type enums
2. ✅ Implementeer backwards compatibility aliases
3. ✅ Update ComponentBuilder voor nieuwe categorieën
4. ✅ Migratie tool voor bestaande blueprints
5. ✅ Update documentatie

**Deliverables:**
- Nieuwe enum definities
- Migratie scripts
- Updated ComponentBuilder
- Migratie guide

**Tijdsinschatting:** 2 weken

---

### 9.2 Phase 2: Event Abstractie

**Doel:** Implementeer BaseEventAwareWorker en event routing.

**Taken:**
1. ✅ Implementeer IEventHandler interface
2. ✅ Implementeer BaseEventAwareWorker
3. ✅ Update Operators voor event routing
4. ✅ Implementeer event chain validatie
5. ✅ Automatische event chain generatie

**Deliverables:**
- BaseEventAwareWorker class
- Updated Operators
- Event chain validator
- Event routing tests

**Tijdsinschatting:** 3 weken

---

### 9.3 Phase 3: UI/UX

**Doel:** Maak de nieuwe taxonomie toegankelijk via de UI.

**Taken:**
1. ✅ Plugin Browser met sub-categorie filtering
2. ✅ Event Flow Visualizer
3. ✅ Geavanceerde modus toggle
4. ✅ Editable wiring_map interface
5. ✅ Interactive event debugging

**Deliverables:**
- Updated Strategy Builder UI
- Event Flow Visualizer component
- Advanced mode interface
- Event debugging tools

**Tijdsinschatting:** 4 weken

---

### 9.4 Phase 4: Documentatie & Voorbeelden

**Doel:** Complete documentatie en voorbeeldstrategieën.

**Taken:**
1. ✅ Beginner tutorial (geen events)
2. ✅ Intermediate guide (predefined triggers)
3. ✅ Advanced guide (custom events)
4. ✅ ICT/SMC voorbeeld strategie
5. ✅ Smart DCA voorbeeld strategie
6. ✅ Plugin development guide

**Deliverables:**
- Complete documentatie set
- 5+ voorbeeld strategieën
- Video tutorials
- Plugin development templates

**Tijdsinschatting:** 2 weken

---

### 9.5 Totale Timeline

**Total:** ~11 weken (2.75 maanden)

**Milestones:**
- Week 2: Core taxonomie klaar
- Week 5: Event abstractie klaar
- Week 9: UI/UX klaar
- Week 11: Documentatie & voorbeelden klaar

---

## 10. Conclusie

### 10.1 Wat We Hebben Bereikt

Deze verfijning biedt:

1. **Conceptuele Zuiverheid**
   - Elke categorie heeft één duidelijke verantwoordelijkheid
   - Geen overlap tussen categorieën
   - Duidelijke scheiding tussen analyse en planning

2. **Intuïtieve Naamgeving**
   - Sluit aan bij quant's mentale model
   - OpportunityWorker vs ThreatWorker (dualiteit)
   - PlanningWorker (brug tussen analyse en executie)

3. **Flexibiliteit**
   - Ondersteunt diverse trading methodologieën
   - Event-driven workflows mogelijk
   - Opt-in complexiteit

4. **Schaalbaarheid**
   - Van simpel naar complex zonder refactoring
   - Progressieve complexiteit (3 niveaus)
   - Uitbreidbaar met nieuwe sub-types

5. **Backwards Compatibility**
   - Bestaande code blijft werken
   - Automatische migratie mogelijk
   - Geleidelijke transitie

6. **Toekomstbestendig**
   - Event-driven foundation
   - Flexibele architectuur
   - Ruimte voor groei

---

### 10.2 Kernprincipes Behouden

✅ **Plugin First** - Alle logica in plugins  
✅ **Configuratie-gedreven** - YAML definieert gedrag  
✅ **Contract-gedreven** - Pydantic validatie  
✅ **Event-driven** - Opt-in complexiteit  
✅ **Testbaar** - Pure functies, mock interfaces  
✅ **Herbruikbaar** - Bus-agnostische plugins

---

### 10.3 Volgende Stappen

1. **Review & Approval**
   - Review deze documentatie met het team
   - Goedkeuring voor implementatie
   - Prioritering van phases

2. **Implementatie Start**
   - Begin met Phase 1 (Core Taxonomie)
   - Setup development branch
   - Create implementation tickets

3. **Community Feedback**
   - Share met early adopters
   - Gather feedback op taxonomie
   - Iterate op basis van feedback

---

## Appendix A: Volledige Enum Definities

```python
# backend/core/enums.py
"""
Contains application-wide enumerations for the V3 worker taxonomy.

@layer: Core
@version: 3.0 (V3 Architecture)
"""
from enum import Enum
import warnings

# === V3 ARCHITECTURE: WORKER TYPES (ROLES) ===

class WorkerType(str, Enum):
    """
    The 5 fundamental worker categories in the V3 architecture.
    
    Each represents a distinct functional role in the trading system:
    - CONTEXT_WORKER: Enriches raw market data with analytical context
    - OPPORTUNITY_WORKER: Recognizes trading opportunities (patterns, signals)
    - THREAT_WORKER: Detects risks and threats in the operation
    - PLANNING_WORKER: Transforms opportunities into executable plans
    - EXECUTION_WORKER: Executes plans and manages positions
    """
    CONTEXT_WORKER = "context_worker"
    OPPORTUNITY_WORKER = "opportunity_worker"
    THREAT_WORKER = "threat_worker"
    PLANNING_WORKER = "planning_worker"
    EXECUTION_WORKER = "execution_worker"
    
    # Backwards compatibility aliases (DEPRECATED in V3)
    ANALYSIS_WORKER = "opportunity_worker"
    MONITOR_WORKER = "threat_worker"


# === V3 ARCHITECTURE: SUB-CATEGORIES ===

class ContextType(str, Enum):
    """
    Sub-categories for ContextWorker plugins.
    Organized by type of data enrichment.
    """
    REGIME_CLASSIFICATION = "regime_classification"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    INDICATOR_CALCULATION = "indicator_calculation"
    MICROSTRUCTURE_ANALYSIS = "microstructure_analysis"
    TEMPORAL_CONTEXT = "temporal_context"
    SENTIMENT_ENRICHMENT = "sentiment_enrichment"
    FUNDAMENTAL_ENRICHMENT = "fundamental_enrichment"


class OpportunityType(str, Enum):
    """
    Sub-categories for OpportunityWorker plugins.
    Organized by trading strategy type.
    """
    TECHNICAL_PATTERN = "technical_pattern"
    MOMENTUM_SIGNAL = "momentum_signal"
    MEAN_REVERSION = "mean_reversion"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    EVENT_DRIVEN = "event_driven"
    SENTIMENT_SIGNAL = "sentiment_signal"
    ML_PREDICTION = "ml_prediction"


class ThreatType(str, Enum):
    """
    Sub-categories for ThreatWorker plugins.
    Organized by risk domain.
    """
    PORTFOLIO_RISK = "portfolio_risk"
    MARKET_RISK = "market_risk"
    SYSTEM_HEALTH = "system_health"
    STRATEGY_PERFORMANCE = "strategy_performance"
    EXTERNAL_EVENT = "external_event"


class PlanningPhase(str, Enum):
    """
    Sub-categories for PlanningWorker plugins.
    Organized by planning phase in trade lifecycle.
    """
    ENTRY_PLANNING = "entry_planning"
    EXIT_PLANNING = "exit_planning"
    SIZE_PLANNING = "size_planning"
    ORDER_ROUTING = "order_routing"


class ExecutionType(str, Enum):
    """
    Sub-categories for ExecutionWorker plugins.
    Organized by action type.
    """
    TRADE_INITIATION = "trade_initiation"
    POSITION_MANAGEMENT = "position_management"
    RISK_SAFETY = "risk_safety"
    OPERATIONAL = "operational"


# === PREDEFINED EVENT TRIGGERS ===

class PredefinedTrigger(str, Enum):
    """
    Predefined trigger names for common use cases.
    These can be used in plugin manifests without custom event chains.
    """
    ON_CONTEXT_READY = "on_context_ready"
    ON_SIGNAL_GENERATED = "on_signal_generated"
    ON_LEDGER_UPDATE = "on_ledger_update"
    ON_POSITION_OPENED = "on_position_opened"
    ON_POSITION_CLOSED = "on_position_closed"
    ON_SCHEDULE = "on_schedule"


# === EXECUTION ENVIRONMENTS ===

class EnvironmentType(str, Enum):
    """
    The three execution environment types.
    """
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


# === V2 COMPATIBILITY (DEPRECATED) ===

class AnalysisPhase(str, Enum):
    """
    DEPRECATED: V2 phase-based pipeline enum.
    
    Use OpportunityType and PlanningPhase instead.
    Will be removed in V3.0.
    """
    SIGNAL_GENERATION = "signal_generation"
    SIGNAL_REFINEMENT = "signal_refinement"
    ENTRY_PLANNING = "entry_planning"
    EXIT_PLANNING = "exit_planning"
    SIZE_PLANNING = "size_planning"
    ORDER_ROUTING = "order_routing"


class ContextPhase(str, Enum):
    """
    DEPRECATED: V2 context phase enum.
    
    Use ContextType instead.
    Will be removed in V3.0.
    """
    REGIME_CONTEXT = "regime_context"
    STRUCTURAL_CONTEXT = "structural_context"
```

---

## Appendix B: Plugin Manifest Template

```yaml
# plugin_manifest.yaml (V3 Template)

identification:
  name: "my_plugin"
  display_name: "My Plugin"
  type: "opportunity_worker"  # context_worker, opportunity_worker, threat_worker, planning_worker, execution_worker
  subtype: "technical_pattern"  # Sub-categorie (zie enums)
  version: "1.0.0"
  description: "plugins.my_plugin.description"  # i18n key
  author: "Your Name"

# Event configuratie (OPTIONEEL - alleen voor event-aware workers)
event_config:
  # Wanneer moet deze worker worden aangeroepen?
  triggers:
    - "on_context_ready"  # Predefined trigger
    - "custom_event_name"  # Custom event
  
  # Wat publiceert deze worker?
  publishes:
    - event_name: "my_custom_event"
      payload_type: "Signal"
      description: "Published when pattern is detected"

# Dependencies
dependencies:
  # Verplichte DataFrame kolommen
  requires: ['close', 'volume']
  
  # Geproduceerde DataFrame kolommen
  provides: ['my_indicator']
  
  # Verplichte rijke data
  requires_context: []
  
  # Optionele rijke data
  uses: []

# Permissions (OPTIONEEL)
permissions:
  network_access: []
  filesystem_access: []
```

---

## Appendix C: Strategy Blueprint Template

```yaml
# strategy_blueprint.yaml (V3 Template)

name: "My Strategy"
version: "1.0.0"
description: "Strategy description"

workforce:
  # === CONTEXT: Prepare the market ===
  context_workers:
    - plugin: "ema_detector"
      subtype: "indicator_calculation"
      params:
        period: 20
    
    - plugin: "market_structure_detector"
      subtype: "structural_analysis"
  
  # === OPPORTUNITY: Detect chances ===
  opportunity_workers:
    - plugin: "fvg_detector"
      subtype: "technical_pattern"
      params:
        min_gap_size: 5
  
  # === THREAT: Monitor risks (OPTIONEEL) ===
  threat_workers:
    - plugin: "max_drawdown_monitor"
      subtype: "portfolio_risk"
      triggers:
        - "on_ledger_update"
      params:
        max_drawdown_percent: 10.0
  
  # === PLANNING: Make the plan ===
  planning_workers:
    entry_planning:
      - plugin: "limit_entry_planner"
    
    exit_planning:
      - plugin: "liquidity_target_exit"
    
    size_planning:
      - plugin: "fixed_risk_sizer"
        params:
          risk_per_trade_percent: 1.0
    
    order_routing:
      - plugin: "default_router"
  
  # === EXECUTION: Execute and manage ===
  execution_workers:
    trade_initiation:
      - plugin: "default_plan_executor"
    
    position_management:
      - plugin: "trailing_stop_manager"
        params:
          trail_percent: 2.0
```

---

**Einde Documentatie**

---

**Versie Historie:**
- V1.0 (2025-10-13): Initiële versie
- V2.0 (2025-10-13): Toegevoegd event-driven architectuur
- V3.0 (2025-10-13): Definitieve versie met volledige use cases en migratie strategie