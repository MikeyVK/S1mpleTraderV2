# **Migratie Map: V2 → V3 Concepten & Terminologie**

**Versie:** 3.0  
**Status:** Definitief  
**Doel:** Centrale referentie voor alle paradigma-shifts en concept-mappings tussen V2 en V3

---

## **1. Worker Taxonomie: 4 → 5 Categorieën**

### **1.1 Hoofdcategorieën Mapping**

| V2 Concept | V3 Concept | Rationale |
|------------|------------|-----------|
| [`ContextWorker`](backend/core/base_worker.py) | [`ContextWorker`](backend/core/base_worker.py) | ✅ Ongewijzigd - "De Cartograaf" |
| [`AnalysisWorker`](backend/core/base_worker.py) | **→ GESPLITST** | ❌ Te breed - bevatte 2 verantwoordelijkheden |
| ↳ Signal Generation | [`OpportunityWorker`](backend/core/base_worker.py) | ✨ Nieuw - "De Verkenner" (detecteert kansen) |
| ↳ Planning Logic | [`PlanningWorker`](backend/core/base_worker.py) | ✨ Nieuw - "De Strateeg" (maakt plannen) |
| [`MonitorWorker`](backend/core/base_worker.py) | [`ThreatWorker`](backend/core/base_worker.py) | 🔄 Hernoemd - "De Waakhond" (betere dualiteit) |
| [`ExecutionWorker`](backend/core/base_worker.py) | [`ExecutionWorker`](backend/core/base_worker.py) | ✅ Verduidelijkt - "De Uitvoerder" |

### **1.2 Enum Mapping**

#### WorkerType Enum

```python
# V2 (DEPRECATED)
class WorkerType(str, Enum):
    CONTEXT_WORKER = "context_worker"
    ANALYSIS_WORKER = "analysis_worker"      # ← DEPRECATED
    MONITOR_WORKER = "monitor_worker"        # ← DEPRECATED
    EXECUTION_WORKER = "execution_worker"

# V3 (CURRENT)
class WorkerType(str, Enum):
    CONTEXT_WORKER = "context_worker"
    OPPORTUNITY_WORKER = "opportunity_worker"  # ← NIEUW
    THREAT_WORKER = "threat_worker"            # ← NIEUW (was MONITOR_WORKER)
    PLANNING_WORKER = "planning_worker"        # ← NIEUW
    EXECUTION_WORKER = "execution_worker"
    
    # Backwards compatibility aliases
    ANALYSIS_WORKER = "opportunity_worker"     # ← Wijst naar nieuwe naam
    MONITOR_WORKER = "threat_worker"           # ← Wijst naar nieuwe naam
```

### **1.3 Phase Enums → Sub-Type Enums**

#### AnalysisPhase → OpportunityType & PlanningPhase

| V2: AnalysisPhase | V3: Nieuwe Categorie | V3: Sub-Type |
|-------------------|---------------------|--------------|
| `signal_generation` | [`OpportunityWorker`](backend/core/base_worker.py) | [`OpportunityType.TECHNICAL_PATTERN`](backend/core/enums.py) |
| `signal_refinement` | [`OpportunityWorker`](backend/core/base_worker.py) | [`OpportunityType.TECHNICAL_PATTERN`](backend/core/enums.py) |
| `entry_planning` | [`PlanningWorker`](backend/core/base_worker.py) | [`PlanningPhase.ENTRY_PLANNING`](backend/core/enums.py) |
| `exit_planning` | [`PlanningWorker`](backend/core/base_worker.py) | [`PlanningPhase.EXIT_PLANNING`](backend/core/enums.py) |
| `size_planning` | [`PlanningWorker`](backend/core/base_worker.py) | [`PlanningPhase.SIZE_PLANNING`](backend/core/enums.py) |
| `order_routing` | [`PlanningWorker`](backend/core/base_worker.py) | [`PlanningPhase.ORDER_ROUTING`](backend/core/enums.py) |

#### ContextPhase → ContextType

| V2: ContextPhase | V3: ContextType |
|------------------|-----------------|
| `regime_context` | [`ContextType.REGIME_CLASSIFICATION`](backend/core/enums.py) |
| `structural_context` | [`ContextType.STRUCTURAL_ANALYSIS`](backend/core/enums.py) |

### **1.4 Sub-Type Taxonomie (NIEUW in V3)**

#### ContextType (7 sub-categorieën)
- [`REGIME_CLASSIFICATION`](backend/core/enums.py:ContextType) - Markt regime & conditie
- [`STRUCTURAL_ANALYSIS`](backend/core/enums.py:ContextType) - Technische structuur
- [`INDICATOR_CALCULATION`](backend/core/enums.py:ContextType) - Indicatoren & berekeningen
- [`MICROSTRUCTURE_ANALYSIS`](backend/core/enums.py:ContextType) - Orderbook & microstructuur
- [`TEMPORAL_CONTEXT`](backend/core/enums.py:ContextType) - Temporele context (sessies, killzones)
- [`SENTIMENT_ENRICHMENT`](backend/core/enums.py:ContextType) - Sentiment & alternatieve data
- [`FUNDAMENTAL_ENRICHMENT`](backend/core/enums.py:ContextType) - On-chain & fundamentele data

#### OpportunityType (7 sub-categorieën)
- [`TECHNICAL_PATTERN`](backend/core/enums.py:OpportunityType) - Technische patroon herkenning
- [`MOMENTUM_SIGNAL`](backend/core/enums.py:OpportunityType) - Momentum & trend following
- [`MEAN_REVERSION`](backend/core/enums.py:OpportunityType) - Mean reversion strategieën
- [`STATISTICAL_ARBITRAGE`](backend/core/enums.py:OpportunityType) - Arbitrage & statistical
- [`EVENT_DRIVEN`](backend/core/enums.py:OpportunityType) - Event-driven signalen
- [`SENTIMENT_SIGNAL`](backend/core/enums.py:OpportunityType) - Sentiment-driven signalen
- [`ML_PREDICTION`](backend/core/enums.py:OpportunityType) - Machine learning predictions

#### ThreatType (5 sub-categorieën)
- [`PORTFOLIO_RISK`](backend/core/enums.py:ThreatType) - Portfolio & financieel risico
- [`MARKET_RISK`](backend/core/enums.py:ThreatType) - Markt risico & volatiliteit
- [`SYSTEM_HEALTH`](backend/core/enums.py:ThreatType) - Systeem & technische gezondheid
- [`STRATEGY_PERFORMANCE`](backend/core/enums.py:ThreatType) - Strategie performance
- [`EXTERNAL_EVENT`](backend/core/enums.py:ThreatType) - Externe events

#### PlanningPhase (4 sub-categorieën)
- [`ENTRY_PLANNING`](backend/core/enums.py:PlanningPhase) - Entry planning
- [`EXIT_PLANNING`](backend/core/enums.py:PlanningPhase) - Exit planning (stops & targets)
- [`SIZE_PLANNING`](backend/core/enums.py:PlanningPhase) - Position sizing
- [`ORDER_ROUTING`](backend/core/enums.py:PlanningPhase) - Order routing & execution tactics

#### ExecutionType (4 sub-categorieën)
- [`TRADE_INITIATION`](backend/core/enums.py:ExecutionType) - Trade initiatie
- [`POSITION_MANAGEMENT`](backend/core/enums.py:ExecutionType) - Actieve position management
- [`RISK_SAFETY`](backend/core/enums.py:ExecutionType) - Risk & safety management
- [`OPERATIONAL`](backend/core/enums.py:ExecutionType) - Operationele & geplande taken

---

## **2. Traceability Framework: CorrelationID → Causale IDs**

### **2.1 Conceptuele Shift**

| V2 Concept | V3 Concept | Rationale |
|------------|------------|-----------|
| **CorrelationID** | **Causaal ID Framework** | Van simpele tracking naar causale analyse |
| Simpele UUID tracking | Getypeerde, semantische IDs | Waarom-vraag beantwoorden |
| Eén ID per flow | Meerdere causale IDs per trade | Volledige causale keten |

### **2.2 ID Type Mapping**

| V3 ID Type | Gegenereerd Door | Doel | Gebruik |
|------------|------------------|------|---------|
| **TradeID** | [`PlanningWorker`](backend/core/base_worker.py) / [`ExecutionWorker`](backend/core/base_worker.py) | Ankerpunt trade lifecycle | Primaire sleutel in [`StrategyJournal`](backend/core/strategy_journal.py) |
| **OpportunityID** | [`OpportunityWorker`](backend/core/base_worker.py) | Reden voor opening | Causal link: "Waarom is trade geopend?" |
| **ThreatID** | [`ThreatWorker`](backend/core/base_worker.py) | Reden voor ingreep | Causal link: "Waarom is trade gesloten/aangepast?" |
| **ScheduledID** | Scheduler | Tijd-gedreven reden | Causal link: "Waarom is actie nu uitgevoerd?" |

### **2.3 DTO Updates**

#### Signal DTOs

```python
# V2
class Signal(BaseModel):
    correlation_id: UUID  # ← Simpele tracking

# V3
class OpportunitySignal(BaseModel):
    opportunity_id: UUID  # ← Getypeerde, semantische ID
    # ... rest van velden
```

---

## **3. Ledger/Journal Scheiding: Gecombineerd → Gescheiden**

### **3.1 Conceptuele Scheiding**

| Aspect | V2: Portfolio/StrategyLedger | V3: StrategyLedger | V3: StrategyJournal |
|--------|------------------------------|--------------------|--------------------|
| **Doel** | Staat + Geschiedenis | ✅ **Alleen Staat** | ✅ **Alleen Geschiedenis** |
| **Data Type** | Read-Write | Read-Write | Append-Only |
| **Inhoud** | Posities + Historie | Alleen actuele posities | Volledige causale geschiedenis |
| **Performance** | Traag (veel data) | ⚡ Snel (minimale data) | Analyseerbaar |
| **Causal IDs** | Nee | Nee | ✅ Ja |
| **Afgewezen Kansen** | Nee | Nee | ✅ Ja |

### **3.2 Data Mapping**

#### StrategyLedger (Operationele Staat)

```python
# V2: Bevatte alles
{
    "positions": [...],
    "trade_history": [...],      # ← Verplaatst naar Journal
    "performance_metrics": [...], # ← Verplaatst naar Journal
    "causal_data": [...]         # ← Nieuw in Journal
}

# V3: Alleen staat
{
    "capital": 10000.0,
    "open_positions": [...],     # Alleen actieve posities
    "closed_positions": [...],   # Recente gesloten (voor context)
    "unrealized_pnl": 150.0,
    "realized_pnl": 250.0
}
```

#### StrategyJournal (Historische Log)

```python
# V3: Nieuw - Volledige geschiedenis
{
    "journal_entries": [
        {
            "timestamp": "2025-10-14T10:00:00Z",
            "event_type": "OPPORTUNITY_DETECTED",
            "opportunity_id": "uuid-123",
            "details": {...}
        },
        {
            "timestamp": "2025-10-14T10:00:05Z",
            "event_type": "OPPORTUNITY_REJECTED",  # ← Nieuw: afgewezen kansen
            "opportunity_id": "uuid-123",
            "rejection_reason": {
                "threat_id": "uuid-456",
                "threat_type": "MAX_DRAWDOWN_BREACHED"
            }
        },
        {
            "timestamp": "2025-10-14T10:05:00Z",
            "event_type": "TRADE_OPENED",
            "trade_id": "uuid-789",
            "opportunity_id": "uuid-124",  # ← Causale link
            "details": {...}
        }
    ]
}
```

---

## **4. Operator Architectuur: Hard-Coded → Data-Driven**

### **4.1 Structurele Shift**

| V2 Concept | V3 Concept | Impact |
|------------|------------|--------|
| 5 aparte Operator-klassen | 1 [`BaseOperator`](backend/core/operators/base_operator.py) | DRY, flexibiliteit |
| Hard-coded orkestratie | [`operators.yaml`](config/operators.yaml) configuratie | Aanpasbaar zonder code |
| Impliciete strategieën | Expliciete ExecutionStrategy & AggregationStrategy | Duidelijkheid |

### **4.2 Class Mapping**

| V2 Class | V3 Equivalent |
|----------|---------------|
| [`ContextOrchestrator`](services/) | [`BaseOperator`](backend/core/operators/base_operator.py) instance (config: ContextOperator) |
| [`AnalysisOperator`](services/) | **→ GESPLITST** |
| ↳ Signal fase | [`BaseOperator`](backend/core/operators/base_operator.py) instance (config: OpportunityOperator) |
| ↳ Planning fase | [`BaseOperator`](backend/core/operators/base_operator.py) instance (config: PlanningOperator) |
| [`MonitorOperator`](services/) | [`BaseOperator`](backend/core/operators/base_operator.py) instance (config: ThreatOperator) |
| [`ExecutionHandler`](services/) | [`BaseOperator`](backend/core/operators/base_operator.py) instance (config: ExecutionOperator) |

### **4.3 Configuratie Schema**

```yaml
# config/operators.yaml (NIEUW)
operators:
  - operator_id: "ContextOperator"
    manages_worker_type: "ContextWorker"
    execution_strategy: "SEQUENTIAL"      # ← Was hard-coded
    aggregation_strategy: "CHAIN_THROUGH" # ← Was hard-coded
  
  - operator_id: "OpportunityOperator"
    manages_worker_type: "OpportunityWorker"
    execution_strategy: "PARALLEL"        # ← Was hard-coded
    aggregation_strategy: "COLLECT_ALL"   # ← Was hard-coded
  
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

### **4.4 Execution & Aggregation Strategies**

#### ExecutionStrategy Enum

```python
class ExecutionStrategy(str, Enum):
    SEQUENTIAL = "sequential"      # Workers één voor één
    PARALLEL = "parallel"          # Workers tegelijkertijd
    EVENT_DRIVEN = "event_driven"  # Op basis van events
```

#### AggregationStrategy Enum

```python
class AggregationStrategy(str, Enum):
    COLLECT_ALL = "collect_all"      # Verzamel alle resultaten
    CHAIN_THROUGH = "chain_through"  # Output → volgende input
    NONE = "none"                    # Geen aggregatie
```

---

## **5. Persistence Suite: Ad-hoc → Unified Architecture**

### **5.1 Conceptuele Unificatie**

| Aspect | V2 | V3 |
|--------|----|----|
| **Architectuur** | Ad-hoc, inconsistent | Unified, interface-driven |
| **Factory Pattern** | Geen | [`PersistorFactory`](backend/assembly/persistor_factory.py) |
| **Interfaces** | Impliciete contracts | Expliciete Protocol interfaces |
| **State Persistence** | Custom per plugin | Generiek via [`IStatePersistor`](backend/core/interfaces/persistors.py:IStatePersistor) |
| **Journal Persistence** | Via service-laag | Direct via [`IJournalPersistor`](backend/core/interfaces/persistors.py:IJournalPersistor) |

### **5.2 Interface Mapping**

| Data Type | V2 Benadering | V3 Interface | V3 Implementatie |
|-----------|---------------|--------------|------------------|
| **Marktdata** | Direct Parquet | [`IDataPersistor`](backend/core/interfaces/persistors.py:IDataPersistor) | [`ParquetPersistor`](backend/data/persistors/parquet_persistor.py) |
| **Plugin State** | Custom per plugin | [`IStatePersistor`](backend/core/interfaces/persistors.py:IStatePersistor) | [`JsonPersistor`](backend/data/persistors/json_persistor.py) (atomic writes) |
| **Strategy Journal** | Via JournalAdapter | [`IJournalPersistor`](backend/core/interfaces/persistors.py:IJournalPersistor) | [`JsonPersistor`](backend/data/persistors/json_persistor.py) (append-only) |

### **5.3 Dependency Injection Pattern**

```python
# V2: Direct koppeling
class MyWorker:
    def __init__(self):
        self.file_path = "state.json"  # ← Hard-coded
        self.state = self._load()       # ← Custom logica

# V3: Interface injection
class MyWorker(BaseStatefulWorker):
    def __init__(self, state_persistor: IStatePersistor):
        self._state_persistor = state_persistor  # ← Geïnjecteerd
        # Geen custom logica nodig
```

---

## **6. Plugin Capabilities: Mixed → Three-Tier Model**

### **6.1 Capability Scheiding**

| Capability | V2 | V3 Base Class | Injection |
|------------|----|--------------|-----------| 
| **Pure Logic** | [`BaseWorker`](backend/core/base_worker.py) | [`BaseWorker`](backend/core/base_worker.py) | Geen (90% van plugins) |
| **State Management** | Custom per plugin | [`BaseStatefulWorker`](backend/core/base_worker.py:BaseStatefulWorker) | [`IStatePersistor`](backend/core/interfaces/persistors.py:IStatePersistor) (5%) |
| **Event Awareness** | Via EventBus | [`BaseEventAwareWorker`](backend/core/base_worker.py:BaseEventAwareWorker) | [`IEventHandler`](backend/core/interfaces/event_handler.py:IEventHandler) (5%) |
| **Journaling** | Via JournalAdapter | [`BaseJournalingWorker`](backend/core/base_worker.py:BaseJournalingWorker) | [`IJournalPersistor`](backend/core/interfaces/persistors.py:IJournalPersistor) (zeldzaam) |

### **6.2 API Mapping**

#### State Management

```python
# V2: Custom implementatie
class MyWorker:
    def save_state(self):
        with open("state.json", "w") as f:
            json.dump(self.state, f)  # ← Niet crash-safe

# V3: Gestandaardiseerd
class MyWorker(BaseStatefulWorker):
    def process(self, context):
        self.state['counter'] += 1
        self.commit_state()  # ← Atomic writes (journal → fsync → rename)
```

#### Event Handling

```python
# V2: Direct EventBus koppeling
class MyWorker:
    def __init__(self, event_bus):
        self.event_bus = event_bus  # ← Tight coupling
    
    def publish(self, event):
        self.event_bus.publish(event)  # ← Niet testbaar

# V3: Interface abstraction
class MyWorker(BaseEventAwareWorker):
    def process(self, context):
        signal = Signal(...)
        self.emit("my_event", signal)  # ← Testbaar, herbruikbaar
```

#### Journaling

```python
# V2: Via service-laag
class MyWorker:
    def process(self, context):
        # Geen directe journaling
        pass

# V3: Direct journaling
class MyWorker(BaseJournalingWorker):
    def process(self, opportunity, threats, context):
        if threats:
            entry = {
                "event_type": "OPPORTUNITY_REJECTED",
                "opportunity_id": opportunity.opportunity_id,
                "rejection_reason": {"threat_id": threats[0].threat_id}
            }
            self.log_entries([entry], context)  # ← Direct, ontkoppeld
```

---

## **7. ExecutionEnvironment Rol: MarketSnapshot → TradingContext**

### **7.1 Verantwoordelijkheid Shift**

| Aspect | V2 | V3 |
|--------|----|----|
| **Output DTO** | [`MarketSnapshot`](backend/dtos/market/market_snapshot.py) | [`TradingContext`](backend/dtos/state/trading_context.py) |
| **strategy_link_id** | Toegevoegd door ContextOperator | ✅ Toegevoegd door ExecutionEnvironment |
| **Context Creatie** | In ContextOperator | ✅ In ExecutionEnvironment |
| **ContextOperator Rol** | Special case (context builder) | Standaard operator (verrijkt bestaande context) |

### **7.2 Dataflow Mapping**

```python
# V2: ExecutionEnvironment → MarketSnapshot
class BacktestEnvironment:
    def tick(self):
        snapshot = MarketSnapshot(
            timestamp=...,
            ohlcv=...
            # Geen strategy_link_id
        )
        self.event_bus.publish("MarketDataReceived", snapshot)

# V2: ContextOperator moet speciale logica hebben
class ContextOperator:
    def on_market_data(self, snapshot):
        context = TradingContext(
            timestamp=snapshot.timestamp,
            ohlcv_df=snapshot.ohlcv,
            strategy_link_id=self._get_strategy_id()  # ← Speciale logica
        )
        # Verrijk context...

# V3: ExecutionEnvironment → TradingContext (compleet)
class BacktestEnvironment:
    def tick(self):
        context = TradingContext(
            timestamp=...,
            ohlcv_df=...,
            strategy_link_id=self.strategy_link_id  # ← Direct beschikbaar
        )
        self.event_bus.publish("ContextReady", context)

# V3: ContextOperator is nu standaard
class BaseOperator:  # Geconfigureerd als ContextOperator
    def run(self, context: TradingContext):
        # Verrijk het bestaande context object
        # Geen speciale logica nodig
```

---

## **8. Configuration Files: Nieuwe & Gewijzigde**

### **8.1 Nieuwe Configuratiebestanden**

| Bestand | Doel | Versie |
|---------|------|--------|
| [`config/operators.yaml`](config/operators.yaml) | Operator gedrag configuratie | V3 |
| [`config/schedule.yaml`](config/schedule.yaml) | Tijd-gebaseerde event scheduling | V3 |

### **8.2 Herbenoemde Configuratiebestanden**

| V2 Naam | V3 Naam | Wijziging |
|---------|---------|-----------|
| `run_blueprint.yaml` | [`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml) | Herbenaming + structuurwijziging |
| `portfolio.yaml` | [`operation.yaml`](config/operation.yaml) | Herbenaming + conceptuele shift |

### **8.3 strategy_blueprint.yaml Structuurwijziging**

```yaml
# V2: 4 worker categorieën
workforce:
  context_workers: [...]
  analysis_workers: [...]    # ← Bevat alles (signals + planning)
  monitor_workers: [...]
  execution_workers: [...]

# V3: 5 worker categorieën met sub-structuur
workforce:
  context_workers: [...]
  
  opportunity_workers: [...]  # ← Alleen signal detection
  
  threat_workers: [...]       # ← Hernoemd van monitor_workers
  
  planning_workers:           # ← Nieuw, gestructureerd
    entry_planning: [...]
    exit_planning: [...]
    size_planning: [...]
    order_routing: [...]
  
  execution_workers:
    trade_initiation: [...]
    position_management: [...]
    risk_safety: [...]
    operational: [...]
```

---

## **9. Terminologie Updates**

### **9.1 Core Termen**

| V2 Term | V3 Term | Context |
|---------|---------|---------|
| "Analytische Pijplijn" | "Worker Ecosysteem" | Fundamentele conceptuele shift |
| "9-Fasen Trechter" | "5-Categorie Workflow" | Worker taxonomie |
| "CorrelationID" | "Causale ID Framework" | Traceability |
| "Portfolio" | "Operation" | Strategisch niveau |
| "Run Blueprint" | "Strategy Blueprint" | Configuratie naam |
| "Monitor" | "Threat Detection" | Worker rol verduidelijking |

### **9.2 Component Termen**

| V2 Term | V3 Term | Rationale |
|---------|---------|-----------|
| "ContextOrchestrator" | "ContextOperator" | Consistente naamgeving |
| "AnalysisOperator" | "OpportunityOperator" + "PlanningOperator" | Scheiding verantwoordelijkheden |
| "MonitorOperator" | "ThreatOperator" | Betere semantiek |
| "ExecutionHandler" | "ExecutionOperator" | Consistente naamgeving |
| "StrategyEngine" | `[VERWIJDERD]` | Verantwoordelijkheid verdeeld over Operators |
| "JournalAdapter" | `[VERWIJDERD]` | Direct journaling via BaseJournalingWorker |

---

## **10. Migratie Checklist**

### **10.1 Code Migratie**

- [ ] Update [`backend/core/enums.py`](backend/core/enums.py) met nieuwe WorkerType enum
- [ ] Voeg sub-type enums toe (ContextType, OpportunityType, etc.)
- [ ] Implementeer [`BaseOperator`](backend/core/operators/base_operator.py)
- [ ] Creëer [`OperatorFactory`](backend/assembly/operator_factory.py)
- [ ] Implementeer Persistence Suite interfaces
- [ ] Update [`BaseWorker`](backend/core/base_worker.py) hierarchy (Stateful, EventAware, Journaling)
- [ ] Pas [`ExecutionEnvironment`](backend/environments/) aan voor TradingContext output

### **10.2 Configuratie Migratie**

- [ ] Creëer [`config/operators.yaml`](config/operators.yaml)
- [ ] Hernoem `run_blueprint.yaml` → `strategy_blueprint.yaml`
- [ ] Update blueprint structuur (4 → 5 categorieën)
- [ ] Hernoem `portfolio.yaml` → `operation.yaml`
- [ ] Voeg [`config/schedule.yaml`](config/schedule.yaml) toe indien nodig

### **10.3 Plugin Migratie**

- [ ] Update plugin manifests (`type` + `subtype` fields)
- [ ] Migreer signal generation plugins → OpportunityWorker
- [ ] Migreer planning logic → PlanningWorker
- [ ] Hernoem MonitorWorker plugins → ThreatWorker
- [ ] Update naar nieuwe base classes waar nodig

### **10.4 Documentatie Migratie**

- [ ] Update [`2_ARCHITECTURE.md`](docs/system/2_ARCHITECTURE.md) naar v3.0
- [ ] Update [`A_BIJLAGE_TEMINOLOGIE.md`](docs/system/A_BIJLAGE_TEMINOLOGIE.md)
- [ ] Herzie alle referenties naar oude worker namen
- [ ] Update diagrammen met nieuwe 5-worker flow

---

## **11. Backwards Compatibility**

### **11.1 Deprecation Strategie**

**Phase 1: V2.5 (Transitie)**
- Nieuwe enums met aliases (ANALYSIS_WORKER → OPPORTUNITY_WORKER)
- Deprecation warnings
- Automatische blueprint migratie

**Phase 2: V2.9 (Final Warning)**
- Verhoogde warning severity
- Migratie tool voor plugins

**Phase 3: V3.0 (Clean Break)**
- Verwijder oude enums
- Alleen nieuwe syntax ondersteund

### **11.2 Auto-Migration Script**

```python
# tools/migrate_v2_to_v3.py (Conceptueel)
def migrate_blueprint(v2_blueprint: dict) -> dict:
    """Migreert V2 blueprint naar V3 formaat."""
    v3_blueprint = v2_blueprint.copy()
    
    # Split analysis_workers
    if "analysis_workers" in v2_blueprint:
        opportunity = []
        planning = {"entry_planning": [], "exit_planning": [], 
                   "size_planning": [], "order_routing": []}
        
        for worker in v2_blueprint["analysis_workers"]:
            phase = worker.get("phase")
            if phase in ["signal_generation", "signal_refinement"]:
                opportunity.append(worker)
            elif phase in planning:
                planning[phase].append(worker)
        
        v3_blueprint["opportunity_workers"] = opportunity
        v3_blueprint["planning_workers"] = planning
        del v3_blueprint["analysis_workers"]
    
    # Rename monitor → threat
    if "monitor_workers" in v2_blueprint:
        v3_blueprint["threat_workers"] = v2_blueprint["monitor_workers"]
        del v3_blueprint["monitor_workers"]
    
    return v3_blueprint
```

---

## **12. Quick Reference: Zoek-en-Vervang Gids**

Voor snelle code updates:

| Zoek (V2) | Vervang met (V3) |
|-----------|------------------|
| `WorkerType.ANALYSIS_WORKER` | `WorkerType.OPPORTUNITY_WORKER` of `WorkerType.PLANNING_WORKER` |
| `WorkerType.MONITOR_WORKER` | `WorkerType.THREAT_WORKER` |
| `AnalysisPhase.SIGNAL_GENERATION` | `OpportunityType.TECHNICAL_PATTERN` |
| `AnalysisPhase.ENTRY_PLANNING` | `PlanningPhase.ENTRY_PLANNING` |
| `correlation_id` | `opportunity_id` / `threat_id` / `trade_id` (context-dependent) |
| `ContextOrchestrator` | `BaseOperator (ContextOperator config)` |
| `AnalysisOperator` | `BaseOperator (OpportunityOperator + PlanningOperator config)` |
| `MonitorOperator` | `BaseOperator (ThreatOperator config)` |
| `ExecutionHandler` | `BaseOperator (ExecutionOperator config)` |

---

**Einde Migratie Map**

**Voor vragen of onduidelijkheden, raadpleeg:**
- [`WORKER_TAXONOMIE_V3.md`](docs/development/251014%20Bijwerken%20documentatie/WORKER_TAXONOMIE_V3.md) - Volledige worker taxonomie uitwerking
- [`Overdrachtsdocument_Verfijningen.md`](docs/development/251014%20Bijwerken%20documentatie/Overdrachtsdocument_%20Verfijningen%20en%20Afwijkingen%20op%20de%20S1mpleTrader%20V2%20Architectuur.md) - Kernafwijkingen samenvatting
- [`S1mpleTrader_V2.1_Finale_Verfijningen.md`](docs/development/251014%20Bijwerken%20documentatie/S1mpleTrader%20V2.1_%20Finale%20Architectonische%20Verfijningen.md) - Architectonische verfijningen