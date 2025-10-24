# **2. Architectuur & Componenten**

**Status:** Definitief
Dit document beschrijft de architectuur van S1mpleTrader, die een robuuste, flexibele en conceptueel zuivere systeemarchitectuur biedt.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Inleiding: De Evolutie naar V3](#21-inleiding-de-evolutie-naar-v3)
3. [De Configuratie: De Bron van Waarheid](#22-de-configuratie-de-bron-van-waarheid)
4. [De Gelaagde Architectuur](#23-de-gelaagde-architectuur)
5. [Het Worker Ecosysteem: 5 Gespecialiseerde Rollen](#24-het-worker-ecosysteem-5-gespecialiseerde-rollen)
6. [Het Traceability Framework](#25-het-traceability-framework)
7. [De Ledger/Journal Scheiding](#26-de-ledgerjournal-scheiding)
8. [De Data-Gedreven Operator](#27-de-data-gedreven-operator)
9. [De Persistence Suite](#28-de-persistence-suite)
10. [Plugin Capabilities Model](#29-plugin-capabilities-model)
11. [Componenten in Detail](#210-componenten-in-detail)
12. [Dataflow & Orchestratie](#211-dataflow--orchestratie)

---

## **Executive Summary**

De S1mpleTrader-architectuur is ontworpen om de conceptuele zuiverheid, flexibiliteit en analytische kracht van het platform te maximaliseren. Dit wordt bereikt door een doordachte systeemarchitectuur die de kern van het platform vormt.

### **🎯 Architectuur Kernprincipes**

**1. Gespecialiseerde Worker Taxonomie**
- Vijf gespecialiseerde worker-categorieën (`Context`, `Opportunity`, `Threat`, `Planning`, `Execution`) voor een zuiverdere scheiding van verantwoordelijkheden.

**2. Rijk Causaal ID Framework**
- Getypeerde, causale IDs (`OpportunityID`, `ThreatID`, `TradeID`) die een volledige "waarom"-analyse van elke trade mogelijk maken.

**3. Gescheiden Ledger & Journal**
- Splitsing van de state in een snelle, operationele `StrategyLedger` (huidige staat) en een rijke, analytische `StrategyJournal` (volledige, causale geschiedenis), wat zowel de performance als de analysemogelijkheden verbetert.

**4. Data-Gedreven Operator**
- Een enkele, data-gedreven `BaseOperator` wiens gedrag wordt gedicteerd door `operators.yaml`, wat het DRY-principe versterkt.

**5. Unified Persistence Suite**
- Een formele, interface-gedreven architectuur voor data-persistentie (`IDataPersistor`, `IStatePersistor`, `IJournalPersistor`) voor consistentie en betrouwbaarheid.

**6. Manifest-Gedreven Capabilities**
- Een zuivere scheiding tussen de **ROL** van een worker (bepaald door de basisklasse) en zijn **CAPABILITIES** (aangevraagd in het `manifest.yaml`), wat zorgt voor een expliciet en valideerbaar contract.

### **🔑 Design Principes**

✅ **Configuratie-gedreven** - Gedrag wordt gedefinieerd in YAML, niet in code.
✅ **Conceptuele Zuiverheid** - Elke component heeft één duidelijke verantwoordelijkheid (SRP).
✅ **Volledige Traceability** - Elke beslissing in het systeem is volledig herleidbaar.
✅ **Opt-in Complexiteit** - Het systeem is standaard eenvoudig en wordt alleen complexer waar nodig.

---

## **2.1. Inleiding: Architectuur Principes**

De S1mpleTrader-architectuur is ontworpen om het **Single Responsibility Principle (SRP)** te maximaliseren, complexiteit effectief te moduleren, en een intuïtief model te bieden dat aansluit bij hoe een quant denkt over trading.

### **2.1.1. De Fundamentele Architectuur Principes**

De architectuur is gebaseerd op zes kernprincipes die samen een robuuste, flexibele en conceptueel zuivere systeemarchitectuur creëren:

| Principe | Huidige Implementatie | Voordeel |
|----------|---------------------|----------|
| 1. Worker Taxonomie | 5 gespecialiseerde categorieën | Zuiverdere scheiding van verantwoordelijkheden |
| 2. Traceability | Rijk Causaal ID Framework | Volledige "waarom"-analyse mogelijk |
| 3. State Management | Gescheiden Ledger + Journal | Performance & analytische kracht |
| 4. Operator Model | 1 data-gedreven BaseOperator | Flexibiliteit & DRY-principe |
| 5. Persistence | Unified Persistence Suite | Consistentie & betrouwbaarheid |
| 6. Plugin Model | Manifest-Gedreven Capability Model | Zuivere scheiding ROL & CAPABILITIES |

### **2.1.2. Kernprincipes**

De fundamentele principes van het systeem zijn:

✅ **Plugin-First** - Alle businesslogica in plugins
✅ **Configuratie-gedreven** - YAML definieert gedrag
✅ **Contract-gedreven** - Pydantic validatie overal
✅ **Event-driven** - Asynchrone communicatie
✅ **Testbaar** - Pure functies, dependency injection
✅ **Agnostisch** - Platform-onafhankelijke componenten

---

## **2.2. De Configuratie: De Bron van Waarheid**

De S1mpleTrader V3 architectuur blijft fundamenteel **configuratie-gedreven**. YAML-bestanden vormen het complete "draaiboek" dat de operatie van het trading-ecosysteem beschrijft.

### **2.2.1. Configuratie Hiërarchie**

```
config/
├── platform.yaml              # Globale platform settings
├── operators.yaml             # Operator gedrag configuratie
├── schedule.yaml              # Tijd-gebaseerde events
├── connectors.yaml            # Live exchange connecties
├── index.yaml                 # Centrale configuratie index
├── operation.yaml             # Strategisch niveau
└── runs/
    └── strategy_blueprint.yaml # Strategie definitie
```

### **2.2.2. Configuratiebestanden**

#### [`operators.yaml`](../config/operators.yaml) - Operator Gedrag

```yaml
# Definieert het gedrag van elke Operator in het systeem
operators:
  - operator_id: "ContextOperator"
    manages_worker_type: "ContextWorker"
    execution_strategy: "SEQUENTIAL"
    aggregation_strategy: "CHAIN_THROUGH"
  
  - operator_id: "OpportunityOperator"
    manages_worker_type: "OpportunityWorker"
    execution_strategy: "PARALLEL"
    aggregation_strategy: "COLLECT_ALL"
  
  - operator_id: "ThreatOperator"
    manages_worker_type: "ThreatWorker"
    execution_strategy: "PARALLEL"
    aggregation_strategy: "COLLECT_ALL"
  
  - operator_id: "PlanningOperator"
    manages_worker_type: "PlanningWorker"
    execution_strategy: "SEQUENTIAL"
    aggregation_strategy: "CHAIN_THROUGH"
  
  - operator_id: "ExecutionOperator"
    manages_worker_type: "ExecutionWorker"
    execution_strategy: "EVENT_DRIVEN"
    aggregation_strategy: "NONE"
```

#### [`schedule.yaml`](../config/schedule.yaml) - Tijd-gebaseerde Events

```yaml
# Definieert scheduled events voor operationele taken
schedules:
  - name: "weekly_dca"
    cron: "0 10 * * 1"  # Elke maandag 10:00
    event: "WEEKLY_DCA_TICK"
  
  - name: "daily_rebalance"
    cron: "0 22 * * *"  # Elke dag 22:00
    event: "DAILY_REBALANCE_TICK"
```

**→ Voor complete uitwerking van de configuratie-hiërarchie, zie: [`3_DE_CONFIGURATIE_TREIN.md`](3_DE_CONFIGURATIE_TREIN.md)**

---

## **2.3. De Gelaagde Architectuur**

De applicatie behoudt haar strikte drie-lagen architectuur met **eenrichtingsverkeer** van afhankelijkheden:

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND LAAG  (/frontends)                            │
│  "De Gebruikersinterface"                               │
│  - CLI Presenters & Reporters                           │
│  - Web UI (React/TypeScript)                            │
│  - BFF API Layer                                        │
└────────────────────┬────────────────────────────────────┘
                     │ (Communiceert via BFF API)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  SERVICE LAAG  (/services)                              │
│  "De Orkestratielaag"                                   │
│  - Operators (via BaseOperator)                         │
│  - EventBus & EventAdapters                             │
│  - Meta Workflows (Optimization, Variant Testing)       │
└────────────────────┬────────────────────────────────────┘
                     │ (Gebruikt componenten uit backend)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  BACKEND LAAG  (/backend)                               │
│  "De Motor & Gereedschapskist"                          │
│  - Core Components (Workers, DTOs, Interfaces)          │
│  - Assembly Team (Factories, Builders, Registry)        │
│  - Persistence Suite                                    │
│  - ExecutionEnvironments                                │
└─────────────────────────────────────────────────────────┘
```

### **2.3.1. Laag Verantwoordelijkheden**

| Laag | Mag Gebruiken | Mag NIET Gebruiken | Kernverantwoordelijkheid |
|------|---------------|-------------------|--------------------------|
| **Frontend** | Service Laag (via API) | Backend direct, EventBus | Gebruikersinteractie |
| **Service** | Backend, EventBus | Frontend | Workflow orchestratie |
| **Backend** | Eigen componenten | Service Laag, EventBus | Herbruikbare businesslogica |

---

## **2.4. Het Worker Ecosysteem: 5 Gespecialiseerde Rollen**

De architectuur biedt een verfijnd worker-model dat de workflow van een quant intuïtiever weerspiegelt door de verantwoordelijkheden strikter te scheiden.

### **2.4.1. De Vijf Worker Categorieën**

| Vorige Indeling (4 Categorieën) | Huidige Architectuur (5 Categorieën) |
|--------------------------------|-------------------------------------|
| ContextWorker                  | ContextWorker ✓                     |
| AnalysisWorker                 | OpportunityWorker (detectie)        |
|                                | PlanningWorker (planning)           |
| MonitorWorker                  | ThreatWorker (hernoemd)             |
| ExecutionWorker                | ExecutionWorker ✓                   |

### **2.4.2. De 5 Worker Categorieën**
#### **1. ContextWorker - "De Cartograaf"**

**Single Responsibility:** Het in kaart brengen en verrijken van ruwe marktdata met objectieve context.

```python
from backend.core.base_worker import BaseWorker
from backend.dtos.state.trading_context import TradingContext

class EMADetector(BaseWorker):
    """Berekent EMA indicatoren."""
    
    def process(self, context: TradingContext) -> TradingContext:
        # Verrijk DataFrame met EMA kolommen
        context.enriched_df['ema_20'] = context.enriched_df['close'].ewm(span=20).mean()
        context.enriched_df['ema_50'] = context.enriched_df['close'].ewm(span=50).mean()
        return context
```

**Sub-Types:** [`ContextType`](../backend/core/enums.py:ContextType)
-   `REGIME_CLASSIFICATION` - Trending vs ranging
-   `STRUCTURAL_ANALYSIS` - Market structure, swing points
-   `INDICATOR_CALCULATION` - Technical indicators
-   `MICROSTRUCTURE_ANALYSIS` - Orderbook data
-   `TEMPORAL_CONTEXT` - Sessions, killzones
-   `SENTIMENT_ENRICHMENT` - News, social media
-   `FUNDAMENTAL_ENRICHMENT` - On-chain, earnings

**Kernprincipe:** Objectief en beschrijvend - "Dit is wat er is"

**Technische Afbakening:** Een ContextWorker mag nooit een Signal DTO of een OpportunityID genereren. Zijn enige toegestane output is een verrijkt TradingContext-object. Hij voegt data toe aan de "kaart", maar plaatst er geen vlaggen op.

---

#### **2. OpportunityWorker - "De Verkenner"** ✨

**Single Responsibility:** Het herkennen van handelskansen op basis van patronen en strategieën.

```python
from backend.core.base_worker import BaseWorker
from backend.dtos.pipeline.signal import Signal

class FVGDetector(BaseWorker):
    """Detecteert Fair Value Gaps."""
    
    def process(self, context: TradingContext) -> List[Signal]:
        signals = []
        for i in range(len(context.enriched_df) - 3):
            if self._is_fvg(context.enriched_df, i):
                signals.append(Signal(
                    opportunity_id=uuid4(),  # ✨ Causale ID
                    timestamp=context.enriched_df.index[i],
                    asset=context.asset_pair,
                    direction='long',
                    signal_type='fvg_entry'
                ))
        return signals
```

**Sub-Types:** [`OpportunityType`](../backend/core/enums.py:OpportunityType)
-   `TECHNICAL_PATTERN` - FVG's, breakouts, divergenties
-   `MOMENTUM_SIGNAL` - Trend continuation
-   `MEAN_REVERSION` - Oversold/overbought
-   `STATISTICAL_ARBITRAGE` - Pair trading
-   `EVENT_DRIVEN` - News-based signals
-   `SENTIMENT_SIGNAL` - Extreme fear/greed
-   `ML_PREDICTION` - Model predictions

**Kernprincipe:** Probabilistisch en creatief - "Ik zie een mogelijkheid"

**Technische Afbakening:** De OpportunityWorker is de eerste en enige component in de workflow die een OpportunityID mag genereren. Dit is de technische poortwachter die de overgang markeert van objectieve analyse naar subjectieve, strategie-specifieke interpretatie.

---

#### **3. ThreatWorker - "De Waakhond"** 🔄

**Single Responsibility:** Het detecteren van risico's en bedreigingen in de operatie.

```python
from backend.core.base_worker import BaseWorker
from backend.dtos.execution.critical_event import CriticalEvent

class MaxDrawdownMonitor(BaseWorker):
    """Monitort portfolio drawdown."""
    
    def process(self, ledger_state: StrategyLedger) -> Optional[CriticalEvent]:
        current_drawdown = ledger_state.calculate_drawdown()
        
        if current_drawdown > self.params.max_drawdown_percent:
            return CriticalEvent(
                threat_id=uuid4(),  # ✨ Causale ID
                threat_type='MAX_DRAWDOWN_BREACHED',
                severity='HIGH',
                details={'current_drawdown': current_drawdown}
            )
        return None
```

**Sub-Types:** [`ThreatType`](../backend/core/enums.py:ThreatType)
-   `PORTFOLIO_RISK` - Drawdown, exposure, correlation
-   `MARKET_RISK` - Volatility spikes, liquidity drought
-   `SYSTEM_HEALTH` - Connection issues, data gaps
-   `STRATEGY_PERFORMANCE` - Win rate degradation
-   `EXTERNAL_EVENT` - Breaking news, regulatory changes

**Kernprincipe:** Defensief en informatief - "Let op, hier is een risico"

**Naamgeving Rationale:** "Threat" benadrukt dualiteit met "Opportunity" en is duidelijker dan "Monitor"

---

#### **4. PlanningWorker - "De Strateeg"** ✨

**Single Responsibility:** Het transformeren van handelskansen naar concrete, uitvoerbare plannen.

```python
from backend.core.base_worker import BaseWorker
from backend.dtos.pipeline.trade_plan import TradePlan

class LimitEntryPlanner(BaseWorker):
    """Plant limit entry orders."""
    
    def process(self, signal: Signal, context: TradingContext) -> TradePlan:
        # Bepaal entry prijs op basis van signal
        entry_price = self._calculate_entry(signal, context)
        
        return TradePlan(
            trade_id=uuid4(),  # ✨ TradeID voor tracking
            opportunity_id=signal.opportunity_id,  # ✨ Causale link
            entry_price=entry_price,
            entry_type='LIMIT',
            # ... rest van plan
        )
```

**Sub-Types:** [`PlanningPhase`](../backend/core/enums.py:PlanningPhase)
-   `ENTRY_PLANNING` - Waar stap ik in?
-   `EXIT_PLANNING` - Waar plaats ik stops/targets?
-   `SIZE_PLANNING` - Hoeveel risico neem ik?
-   `ORDER_ROUTING` - Hoe voer ik technisch uit?

**Kernprincipe:** Deterministisch en tactisch - "Gegeven deze kans, dit is het plan"

---

#### **5. ExecutionWorker - "De Uitvoerder"**

**Single Responsibility:** Het uitvoeren en actief beheren van trades en operationele taken.

```python
from backend.core.base_worker import BaseWorker

class DefaultPlanExecutor(BaseWorker):
    """Voert trade plannen uit."""
    
    def
process(self, plan: RoutedTradePlan) -> None:
        # Voer plan uit via ExecutionEnvironment
        self.execution_env.execute_trade(plan)
```

**Sub-Types:** [`ExecutionType`](../backend/core/enums.py:ExecutionType)
-   `TRADE_INITIATION` - Het initiëren van trades
-   `POSITION_MANAGEMENT` - Beheer van lopende posities
-   `RISK_SAFETY` - Emergency exits, circuit breakers
-   `OPERATIONAL` - DCA, rebalancing, scheduled tasks

**Kernprincipe:** Actief en deterministisch - "Ik voer uit en beheer"

---

### **2.4.3. De Dataflow: Hoe Werken Ze Samen?**

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
                  │ Signal           │ CriticalEvent (warnings)
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

## **2.5. Het Traceability Framework**

De architectuur biedt een rijk framework van getypeerde, causale IDs die de volledige "waarom"-keten van elke beslissing vastleggen.

### **2.5.1. Het Causale ID Framework**

Het systeem gebruikt vier getypeerde IDs die samen een complete causale keten vormen:

### **2.5.2. Het Causale ID Framework**

V3 introduceert vier getypeerde IDs die samen een complete causale keten vormen:

```python
from uuid import UUID
from backend.dtos.pipeline.signal import Signal
from backend.dtos.pipeline.trade_plan import TradePlan

# 1. OpportunityID - Gegenereerd door OpportunityWorker
signal = Signal(
    opportunity_id=uuid4(),  # ← "Waarom openen?"
    timestamp=...,
    signal_type='fvg_entry'
)

# 2. TradePlan met causale link
plan = TradePlan(
    trade_id=uuid4(),                    # ← "Welke trade?"
    opportunity_id=signal.opportunity_id, # ← Causale link!
    entry_price=50000.0
)

# 3. ThreatID - Gegenereerd door ThreatWorker
threat = CriticalEvent(
    threat_id=uuid4(),     # ← "Waarom ingrijpen?"
    threat_type='MAX_DRAWDOWN_BREACHED'
)

# 4. ScheduledID - Gegenereerd door Scheduler
scheduled_action = ScheduledEvent(
    scheduled_id=uuid4(),  # ← "Waarom nu?"
    schedule_name='weekly_dca'
)
```

### **2.5.3. Gebruik in StrategyJournal**

Het [`StrategyJournal`](../backend/core/strategy_journal.py) legt deze causale links vast:

```json
{
  "journal_entries": [
    {
      "timestamp": "2025-10-14T10:00:00Z",
      "event_type": "OPPORTUNITY_DETECTED",
      "opportunity_id": "uuid-abc-123",
      "signal_type": "fvg_entry",
      "price": 50000.0
    },
    {
      "timestamp": "2025-10-14T10:00:05Z",
      "event_type": "TRADE_OPENED",
      "trade_id": "uuid-def-456",
      "opportunity_id": "uuid-abc-123",  // ← Causale link: waarom geopend
      "entry_price": 50100.0
    },
    {
      "timestamp": "2025-10-14T11:30:00Z",
      "event_type": "TRADE_CLOSED",
      "trade_id": "uuid-def-456",
      "threat_id": "uuid-ghi-789",       // ← Causale link: waarom gesloten
      "closure_reason": "MAX_DRAWDOWN_BREACHED",
      "exit_price": 49500.0
    }
  ]
}
```

**Analytische Kracht:** In de Trade Explorer UI kan nu exact worden gereconstrueerd:
-   "Trade X werd geopend vanwege opportunity Y"
-   "Trade X werd gesloten vanwege threat Z"
-   "Opportunity Q werd afgewezen vanwege threat R"

---

## **2.6. De Ledger/Journal Scheiding**

De architectuur scheidt de operationele staat van de analytische geschiedenis voor maximale performance en SRP.

### **2.6.1. De Gescheiden Componenten**

Het systeem gebruikt twee complementaire componenten voor optimale performance en functionaliteit.

### **2.6.2. De V3 Scheiding**

#### **StrategyLedger - "Het Domme Grootboek"**

**Verantwoordelijkheid:** Alleen actuele, operationele staat voor snelle executie.

```python
# backend/core/strategy_ledger.py
class StrategyLedger:
    """Snelle, operationele state tracking."""
    
    capital: Decimal
    open_positions: List[Position]      # ← Alleen actieve posities
    recently_closed: List[Position]     # ← Voor context (laatste 10)
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    
    # GEEN causale IDs
    # GEEN volledige historie
    # GEEN analytische data
```

**Gebruik:** Door ExecutionWorkers voor snelle beslissingen.

#### **StrategyJournal - "De Intelligente Notulist"**

**Verantwoordelijkheid:** Onveranderlijk, causaal logboek van ALLE gebeurtenissen.

```python
# backend/core/strategy_journal.py (conceptueel)
class StrategyJournal:
    """Append-only, causaal logboek."""
    
    journal_entries: List[JournalEntry]
    
    # Bevat:
    # - Gedetecteerde opportunities (incl. metadata)
    # - Actieve threats
    # - Trade opens/closes met causale links
    # - AFGEWEZEN kansen met redenatie
    # - Parameter wijzigingen
```

**Gebruik:** Door de Trade Explorer UI en performance analyse tools.

### **2.6.3. Dataflow**

```
Plugin (OpportunityWorker)
    ↓
    Detecteert kans
    ↓
    ├─→ Publiceert Signal (workflow)
    └─→ Logt in StrategyJournal (via BaseJournalingWorker)

Plugin (ExecutionWorker)
    ↓
    Opent trade
    ↓
    ├─→ Update StrategyLedger (actuele staat)
    └─→ Logt in StrategyJournal (volledige context + causale ID)

Plugin (ThreatWorker)
    ↓
    Detecteert risico
    ↓
    ├─→ Publiceert CriticalEvent (workflow)
    └─→ Logt in StrategyJournal (threat + severity)
```

---

## **2.7. De Data-Gedreven Operator**

De architectuur gebruikt een generieke `BaseOperator` die zijn gedrag laat dicteren door configuratie.

### **2.7.1. Het "Geprepareerde Workforce Model"**

Dankzij deze nieuwe architectuur is de `BaseOperator` een pure, "domme" uitvoerder geworden. Hij heeft geen kennis van of runtime-logica voor `EventDrivenWorker`-instanties. De classificatie van alle workers gebeurt vooraf in de assembly-laag door de `WorkerBuilder`.

De `OperatorFactory` creëert de `BaseOperator`-instantie en geeft alleen de `StandardWorkers` door die de operator moet orkestreren. De `EventDrivenWorkers` zijn op dat punt al via de `EventAdapterFactory` aan de EventBus gekoppeld en leiden een autonoom leven, volledig buiten de `run`-methode van de operator om.

### **2.7.2. Execution & Aggregation Strategies**

Hoewel een operator in `operators.yaml` geconfigureerd kan worden als `EVENT_DRIVEN`, betekent dit niet dat de `BaseOperator` zelf de event-logica afhandelt. Het dient als een signaal voor de `OperatorFactory` en `ComponentBuilder` over hoe de bijbehorende workers behandeld moeten worden tijdens de setup. De runtime `run`-methode van de operator is hierdoor sterk vereenvoudigd.

#### **Execution Strategies**

| Strategy | Beschrijving | Gebruik |
|---|---|---|
| `SEQUENTIAL` | Workers één voor één, output → input | ContextWorker, PlanningWorker |
| `PARALLEL` | Workers tegelijkertijd, verzamel resultaten | OpportunityWorker, ThreatWorker |

#### **Aggregation Strategies**

| Strategy | Beschrijving | Gebruik |
|---|---|---|
| `COLLECT_ALL` | Verzamel alle niet-None resultaten in lijst | Parallel workers |
| `CHAIN_THROUGH` | Output van worker N → input van worker N+1 | Sequential workers |
| `NONE` | Geen aggregatie, voor side-effects | Typisch voor `EVENT_DRIVEN` workers |

### **2.7.3. Implementatie**

De implementatie van de `BaseOperator` reflecteert deze versimpeling: de `EVENT_DRIVEN`-tak is bewust verwijderd uit de runtime-methode.

```python
# backend/core/operators/base_operator.py
class BaseOperator:
    """Generieke operator die een PRE-GEFILTERDE lijst van workers orkestreert."""
    
    def __init__(self, config: OperatorConfig, workers: List[IWorker], **services):
        self.config = config
        self.workers = workers # Belangrijk: dit zijn ALLEEN standard_workers
        self._services = services
    
    def run(self, context: Any, **kwargs) -> Any:
        """
        Hoofdmethode - delegeert naar strategie.
        De EVENT_DRIVEN tak is hier niet meer nodig.
        """
        if self.config.execution_strategy == ExecutionStrategy.SEQUENTIAL:
            results = self._execute_sequential(self.workers, context)
        elif self.config.execution_strategy == ExecutionStrategy.PARALLEL:
            results = self._execute_parallel(self.workers, context)
        else:
            results = [] # Operator doet niets voor andere strategieën
        
        return self._aggregate(results)
```

### **2.7.4. Voordelen**

✅ **DRY:** Geen duplicatie van orkestratie-logica
✅ **SRP:** Operator focust puur op executie, niet op classificatie
✅ **Flexibiliteit:** Wijzig gedrag via YAML, niet code
✅ **Testbaar:** Eén simpele, voorspelbare component om te testen

---

## **2.8. De Persistence Suite**

De architectuur biedt een formele, geünificeerde architectuur voor alle data-persistentie via de [`PersistorFactory`](../backend/assembly/persistor_factory.py).

### **2.8.1. De Drie Pijlers**

| Data Type | Interface | Implementatie | Gebruik |
|-----------|-----------|---------------|---------|
| **Marktdata** | [`IDataPersistor`](../backend/core/interfaces/persistors.py:IDataPersistor) | [`ParquetPersistor`](../backend/data/persistors/parquet_persistor.py) | Grote tijdreeksen |
| **Plugin State** | [`IStatePersistor`](../backend/core/interfaces/persistors.py:IStatePersistor) | [`JsonPersistor`](../backend/data/persistors/json_persistor.py) (atomic) | Read-write state |
| **Strategy Journal** | [`IJournalPersistor`](../backend/core/interfaces/persistors.py:IJournalPersistor) | [`JsonPersistor`](../backend/data/persistors/json_persistor.py) (append) | Append-only log |

### **2.8.2. Dependency Injection Pattern**

```python
# De PersistorFactory creëert gespecialiseerde persistors
class PersistorFactory:
    def create_data_persistor(self) -> IDataPersistor:
        return ParquetPersistor(...)
    
    def create_state_persistor(self, worker_id: str) -> IStatePersistor:
        return JsonPersistor(
            path=f"state/{worker_id}/state.json",
            mode="atomic"  # Journal → fsync → rename
        )
    
    def create_journal_persistor(self, strategy_id: str) -> IJournalPersistor:
        return JsonPersistor(
            path=f"journals/{strategy_id}/journal.json",
            mode="append"  # Append-only writes
        )
```

### **2.8.3. Atomic Writes voor Crash Recovery**

```python
# JsonPersistor implementeert crash-safe writes
class JsonPersistor:
    def save_atomic(self, data: dict) -> None:
        """Crash-safe write met journaling."""
        # 1. Schrijf naar .journal bestand
        with open(f"{self.path}.journal", 'w') as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())  # 2. Force naar disk
        
        # 3. Atomic rename
        os.rename(f"{self.path}.journal", self.path)
    
    def load_with_recovery(self) -> dict:
        """Herstel van crash."""
        # Als .journal bestaat, herstel eerst
        if os.exists(f"{self.path}.journal"):
            os.rename(f"{self.path}.journal", self.path)
        
        # Laad normale file
        with open(self.path) as f:
            return json.load(f)
```

---

## **2.9. Het "Manifest-Gedreven Capability Model"**

De architectuur biedt een zuivere, expliciete scheiding tussen de **ROL** van een worker en zijn **CAPABILITIES** via het manifest-gedreven model.

### **2.9.1. De Twee Pijlers van de Plugin Architectuur**

#### **Pijler 1: De ROL van een worker is Declaratief**

De ontwikkelaar kiest expliciet een van de twee abstracte basisklassen. Deze keuze definieert de architecturale rol van de worker: hoe hij wordt aangestuurd.

```python
# backend/core/base_worker.py
from abc import ABC, abstractmethod

class BaseWorker(ABC):
    """De absolute basis voor alle workers."""
    def __init__(self, params: Any):
        self.params = params

class StandardWorker(BaseWorker, ABC):
    """
    ROL: Een worker in de georkestreerde pijplijn.
    CONTRACT: MOET een 'process'-methode implementeren.
    """
    @abstractmethod
    def process(self, context: Any, **kwargs) -> Any:
        raise NotImplementedError

class EventDrivenWorker(BaseWorker, ABC):
    """
    ROL: Een autonome worker die reageert op de EventBus.
    CONTRACT: Heeft GEEN 'process'-methode.
    """
    pass
```

#### **Pijler 2: De CAPABILITIES van een worker zijn Geconfigureerd**

Alle extra vaardigheden die een worker nodig heeft, worden uitsluitend gedeclareerd in een centrale `capabilities`-sectie binnen het `manifest.yaml`. Dit is de enige bron van waarheid voor de behoeften van een plugin.

```yaml
# manifest.yaml
capabilities:
  # Capability voor statefulness
  state:
    enabled: true
    state_dto: "dtos.state_dto.MyWorkerState"

  # Capability voor event-interactie
  events:
    enabled: true
    publishes:
      - as_event: "MyCustomEventFired"
        payload_dto: "MyCustomSignal"
    wirings:
      - listens_to: "SomeTriggerEvent"
        invokes:
          method: "on_some_trigger"
  
  # Capability voor journaling
  journaling:
    enabled: true
```

### **2.9.2. De Rol van de WorkerBuilder**

De `WorkerBuilder` fungeert als een "contract-valideerder" en assemblage-lijn:

1.  **Lees Contract:** Inspecteert de **ROL** (basisklasse) en de aangevraagde **CAPABILITIES** (manifest).
2.  **Valideer:** Controleert of de implementatie overeenkomt met de configuratie (bv. een `EventDrivenWorker` moet `events: enabled: true` hebben).
3.  **Verzamel Onderdelen:** Vraagt de benodigde dependencies aan bij gespecialiseerde factories (bv. `PersistorFactory` voor state, `EventAdapterFactory` voor events).
4.  **Injecteer & Bouw:** Instantieert de worker en injecteert de dependencies (`self.state`, `self.emit`, `self.log_entry`, etc.) dynamisch in de worker-instantie.

Dit model zorgt voor maximale duidelijkheid, veiligheid en onderhoudbaarheid. De ontwikkelaar declareert expliciet zijn intenties, en het systeem valideert en faciliteert deze op een robuuste manier.

---

## **2.10. Componenten in Detail**

### **2.10.1. Core Components (Backend Laag)**

#### **ExecutionEnvironment**

**Rol:** De "wereld" waarin een strategie draait (`Backtest`, `Paper`, of `Live`).

**Huidige Implementatie:** Publiceert complete [`TradingContext`](../backend/dtos/state/trading_context.py) met alle relevante context informatie.

```python
class BacktestEnvironment(ExecutionEnvironment):
    def tick(self):
        """Process one historical tick."""
        # V3: Creëer complete context
        context = TradingContext(
            timestamp=self.current_timestamp,
            ohlcv_df=self.get_historical_window(),
            strategy_link_id=self.strategy_link_id,  # ← Toegevoegd hier!
            asset_pair=self.asset_pair
        )
        
        # Publiceer naar ContextOperator
        self.event_bus.publish("ContextReady", context)
```

#### **StrategyLedger**

**Rol:** Operationele staat van één strategie-run (alleen actueel, geen historie).

```python
class StrategyLedger:
    """Snel, operationeel grootboek."""
    strategy_link_id: str
    capital: Decimal
    open_positions: List[Position]
    recently_closed: List[Position]  # Laatste 10 voor context
    unrealized_pnl: Decimal
    realized_pnl: Decimal
```

#### **StrategyJournal**

**Rol:** Onveranderlijk, causaal logboek van alle gebeurtenissen.

```python
class StrategyJournal:
    """Append-only, causaal logboek."""
    strategy_link_id: str
    journal_entries: List[JournalEntry]
    
    # Entries bevatten:
    # - OpportunityID, ThreatID, TradeID, ScheduledID
    # - Timestamps, details, causale links
    # - Afgewezen kansen met redenatie
```

### **2.10.2. Assembly Components**

#### **ComponentBuilder**

**Rol:** Assembleert complete strategy-runs op basis van [`strategy_blueprint.yaml`](../config/runs/strategy_blueprint.yaml).

**Functionaliteit:**
-   Gebruikt [`OperatorFactory`](../backend/assembly/operator_factory.py) voor operators
-   Injecteert persistors in workers
-   Configureert event routing

#### **OperatorFactory**

**Rol:** Creëert [`BaseOperator`](../backend/core/operators/base_operator.py) instanties op basis van [`operators.yaml`](../config/operators.yaml).

```python
class OperatorFactory:
    def create_operator(self, operator_id: str) -> BaseOperator:
        config = self._load_config(operator_id)
        return BaseOperator(
            config=config,
            component_builder=self.component_builder,
            **self.injected_services
        )
```

#### **PersistorFactory**

**Rol:** Creëert gespecialiseerde persistors voor data, state en journaling.

```python
class PersistorFactory:
    def create_state_persistor(self, worker_id: str) -> IStatePersistor:
        return JsonPersistor(path=f"state/{worker_id}/", mode="atomic")
    
    def create_journal_persistor(self, strategy_id: str) -> IJournalPersistor:
        return JsonPersistor(path=f"journals/{strategy_id}/", mode="append")
```

#### **PluginRegistry**

**Rol:** Ontdekt en valideert alle plugins in [`plugins/`](../plugins/) directory.

**Functionaliteit:**
-   Valideert `subtype` field in manifests
-   Ondersteunt event-aware plugins

#### **WorkerBuilder**

**Rol:** Instantieert workers op basis van hun manifest, valideert hun contract en injecteert dependencies via gespecialiseerde factories.

**De "Manifest-Gedreven Assemblagelijn":**

De `WorkerBuilder` opereert als een strikte assemblagelijn. Zijn gedrag wordt volledig gedicteerd door de combinatie van de **ROL** (basisklasse) en de **CAPABILITIES** (manifest) van de te bouwen plugin.

De logica is als volgt:

1.  **Classificeer de worker:** De builder bepaalt de **ROL** (`StandardWorker` of `EventDrivenWorker`) via de basisklasse en leest de aangevraagde `capabilities` uit het manifest.
2.  **Valideer het contract:** Het controleert of de ROL en capabilities consistent zijn.
3.  **Delegeer creatie van dependencies:**
    -   Indien `state: enabled`: Roept de `PersistorFactory` aan om een `IStatePersistor` te creëren en injecteert deze.
    -   Indien `events: enabled`: Vertaalt de `wirings` en `publishes` secties naar `WiringInstruction` DTOs en roept de `EventAdapterFactory` aan om de worker te koppelen aan de EventBus en de `emit`-functie te injecteren.
    -   Indien `journaling: enabled`: Roept de `PersistorFactory` aan om een `IJournalPersistor` te creëren en injecteert deze.
4.  **Assembleer de worker:** De builder instantieert de worker-klasse en injecteert de verzamelde dependencies.

De `WorkerBuilder` neemt nooit zelf beslissingen; het vertaalt en delegeert. Als het manifest sluitend en correct is, slaagt de bouw; zo niet, faalt de bouw met een duidelijke `ConfigurationError`.

---

## **2.11. Dataflow & Orchestratie**

### **2.11.1. Complete Dataflow**

```
┌────────────────────────────────────────────────────────────┐
│  ExecutionEnvironment (Backtest/Paper/Live)                │
│  - Genereert/ontvangt market data                          │
│  - Creëert TradingContext (incl. strategy_link_id)         │
└───────────────────────┬────────────────────────────────────┘
                        │ Publiceert "ContextReady" event
                        │ Payload: TradingContext (ruw)
                        ▼
┌────────────────────────────────────────────────────────────┐
│  BaseOperator (ContextOperator config)                     │
│  - Execution: SEQUENTIAL                                   │
│  - Aggregation: CHAIN_THROUGH                              │
│  ├─→ ContextWorker 1 (verrijkt context)                   │
│  ├─→ ContextWorker 2 (verrijkt verder)                    │
│  └─→ ContextWorker N (finale verrijking)                  │
└───────────────────────┬────────────────────────────────────┘
                        │ Publiceert "ContextEnriched" event
                        │ Payload: TradingContext (verrijkt)
             ┌──────────┴──────────┬─────────────────┐
             ▼                     ▼                 ▼
┌──────────────────────┐  ┌────────────────┐  ┌──────────────┐
│ BaseOperator         │  │ BaseOperator   │  │              │
│ (OpportunityOp)      │  │ (ThreatOp)     │  │  (Parallel)  │
│ - PARALLEL           │  │ - PARALLEL     │  │              │
│ - COLLECT_ALL        │  │ - COLLECT_ALL  │  │              │
│                      │  │                │  │              │
│ OpportunityWorkers   │  │ ThreatWorkers  │  │              │
│ (detecteren kansen)  │  │ (detecteren    │  │              │
│                      │  │  risico's)     │  │              │
└──────────┬───────────┘  └────────┬───────┘  └──────────────┘
           │                       │
           │ List[Signal]          │ List[CriticalEvent]
           │ (+ OpportunityIDs)    │ (+ ThreatIDs)
           └───────────┬───────────┘
                       ▼
           ┌───────────────────────────┐
           │ BaseOperator              │
           │ (PlanningOperator)        │
           │ - SEQUENTIAL              │
           │ - CHAIN_THROUGH           │
           │                           │
           │ ├─→ Entry Planning        │
           │ ├─→ Exit Planning         │
           │ ├─→ Size Planning         │
           │ └─→ Order Routing         │
           └───────────┬───────────────┘
                       │ RoutedTradePlan
                       │ (+ TradeID + causale links)
                       ▼
           ┌───────────────────────────┐
           │ BaseOperator              │
           │ (ExecutionOperator)       │
           │ - EVENT_DRIVEN            │
           │ - NONE                    │
           │                           │
           │ ExecutionWorkers          │
           │ (voeren uit + beheren)    │
           └───────────┬───────────────┘
                       │
                       ├─→ Update StrategyLedger (staat)
                       └─→ Log in StrategyJournal (historie + causaal)
                       │
                       ▼
           ┌───────────────────────────┐
           │ ExecutionEnvironment      │
           │ (Execute in market)       │
           └───────────────────────────┘
```

### **2.11.2. Event Chain**

```
ExecutionEnvironment
    ↓
ContextReady (TradingContext)
    ↓
ContextOperator
    ↓
ContextEnriched (TradingContext)
    ↓
    ├─→ OpportunityOperator → SignalsDetected (List[Signal])
    └─→ ThreatOperator → ThreatsDetected (List[CriticalEvent])
    ↓
PlanningOperator (combines both)
    ↓
PlanReady (RoutedTradePlan)
    ↓
ExecutionOperator
    ↓
    ├─→ LedgerStateChanged (StrategyLedger update)
    └─→ JournalEntryLogged (StrategyJournal append)
```

---

## **2.12. Samenvatting: Architectuur Voordelen**

### **2.12.1. Conceptuele Zuiverheid**

✅ Elke worker heeft één duidelijke verantwoordelijkheid
✅ OpportunityWorker vs ThreatWorker (dualiteit en semantiek)
✅ PlanningWorker overbrugt analyse en executie
✅ Scheiding van operationele staat en analytische geschiedenis

### **2.12.2. Flexibiliteit & Schaalbaarheid**

✅ Data-gedreven operators: wijzig gedrag via YAML
✅ Event-driven workflows mogelijk zonder complexity burden
✅ Opt-in capabilities: gebruik alleen wat je nodig hebt
✅ Unified persistence: consistente interface voor alle storage

### **2.12.3. Analytische Kracht**

✅ Causaal ID framework: volledige "waarom"-analyse
✅ StrategyJournal: afgewezen kansen + complete context
✅ Traceability: reconstructie van complete beslissingsketen
✅ Trade Explorer: visuele analyse van causale links

### **2.12.4. Robuustheid**

✅ Atomic writes: crash-safe state persistence
✅ Dependency injection: testbare, herbruikbare componenten
✅ Interface-driven: flexibele implementaties
✅ Backwards compatibility: geleidelijke migratie mogelijk

---

## **2.13. Gerelateerde Documenten**

Voor diepere uitwerkingen van specifieke onderdelen:

-   **Configuratie:** [`3_DE_CONFIGURATIE_TREIN.md`](3_DE_CONFIGURATIE_TREIN.md)
-   **Worker Taxonomie:** [`WORKER_TAXONOMIE_V3.md`](../development/251014%20Bijwerken%20documentatie/WORKER_TAXONOMIE_V3.md)
-   **Migratie Gids:** [`MIGRATION_MAP.md`](MIGRATION_MAP.md)
-   **Plugin Ontwikkeling:** [`4_DE_PLUGIN_ANATOMIE.md`](4_DE_PLUGIN_ANATOMIE.md)
-   **Terminologie:** [`A_BIJLAGE_TERMINOLOGIE.md`](A_BIJLAGE_TERMINOLOGIE.md)

---

**Einde Architectuur Document**