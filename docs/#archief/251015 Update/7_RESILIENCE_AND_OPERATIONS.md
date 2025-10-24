# **7. Robuustheid & Operationele Betrouwbaarheid**

Versie: 3.0 (Architectuur Blauwdruk v5)  
Status: Definitief  
Dit document beschrijft de strategieën en architectonische patronen die S1mpleTrader V2 veerkrachtig maken tegen technische fouten. Deze principes zijn essentieel voor de betrouwbaarheid van het systeem, met name in een live trading-omgeving waar kapitaal op het spel staat.

---

## **7.1. De Persistence Suite Architectuur (SHIFT 3)**

Een fundamentele architectonische shift in V3 is de unificatie van alle data-persistentie via een consistent, interface-gedreven model. Dit elimineert de ad-hoc benaderingen van V2 en introduceert een gelaagde, ontkoppelde architectuur gebaseerd op het **Dependency Inversion Principle**.

### **7.1.1. Filosofie: Uniformiteit, Ontkoppeling en Specialisatie**

De kernfilosofie bestaat uit drie pijlers:

* **Uniformiteit:** Alle interacties met de persistence-laag verlopen via een centrale [`PersistorFactory`](backend/assembly/persistor_factory.py).  
* **Ontkoppeling:** Componenten zijn afhankelijk van **abstracte interfaces** ([`Protocol`](backend/core/interfaces/persistors.py)), niet van concrete implementaties. Dit maakt het systeem flexibel, testbaar en uitbreidbaar.  
* **Specialisatie (SRP):** We erkennen dat verschillende soorten data verschillende opslagbehoeften hebben. Daarom definiëren we gespecialiseerde interfaces voor elk type data.

### **7.1.2. De Drie Persistentie Interfaces**

We identificeren drie fundamenteel verschillende soorten data, elk met een eigen interface:

#### **1. IDataPersistor: Marktdata Persistentie**

```python
# backend/core/interfaces/persistors.py
class IDataPersistor(Protocol):
    """Interface voor grote volumes tijdreeksdata (OHLCV, trades)."""
    
    def save_trades(self, pair: str, trades: List[TradeTick]) -> None:
        """Slaat trade data op in geoptimaliseerd formaat."""
        ...
    
    def get_data_coverage(self, pair: str) -> List[DataCoverage]:
        """Retourneert beschikbare dataranges."""
        ...
```

* **Doel:** Grote volumes, sterk gestructureerde, kolom-georiënteerde tijdreeksdata.  
* **Implementatie:** [`ParquetPersistor`](backend/data/persistors/parquet_persistor.py), geoptimaliseerd voor snelle analytische queries op grote datasets.  
* **Use Case:** OHLCV data, trade ticks, historische marktdata voor backtesting.

#### **2. IStatePersistor: Plugin State Persistentie**

```python
# backend/core/interfaces/persistors.py
class IStatePersistor(Protocol):
    """Interface voor transactionele, atomische state-opslag."""
    
    def save_state(self, plugin_id: str, state: Dict[str, Any]) -> None:
        """Slaat plugin state op met atomische garanties."""
        ...
    
    def load_state(self, plugin_id: str) -> Dict[str, Any]:
        """Laadt plugin state met crash recovery."""
        ...
```

* **Doel:** Kleine, transactionele, read-write data die **absolute atomische consistentie** vereist.  
* **Implementatie:** Een instantie van [`JsonPersistor`](backend/data/persistors/json_persistor.py), die robuuste journaling-logica implementeert (`.journal`, `fsync`, `rename`).  
* **Use Case:** Interne staat van stateful plugins (counters, accumulators, cached calculations).

#### **3. IJournalPersistor: Strategy Journal Persistentie**

```python
# backend/core/interfaces/persistors.py
class IJournalPersistor(Protocol):
    """Interface voor append-only historische journaling."""
    
    def append(self, strategy_id: str, entries: List[Dict[str, Any]]) -> None:
        """Voegt entries toe aan het strategie-journaal."""
        ...
    
    def read_entries(self, strategy_id: str, 
                     start_time: datetime, 
                     end_time: datetime) -> List[Dict[str, Any]]:
        """Leest journal entries voor analyse."""
        ...
```

* **Doel:** Semi-gestructureerde, **append-only**, historische logdata die causale reconstructie mogelijk maakt.  
* **Implementatie:** Een *andere* instantie van dezelfde [`JsonPersistor`](backend/data/persistors/json_persistor.py), geconfigureerd voor append-only schrijven.  
* **Use Case:** Volledige causale geschiedenis van beslissingen, inclusief **afgewezen kansen** en threat-interventies.

### **7.1.3. PersistorFactory: De Centrale Builder**

De [`PersistorFactory`](backend/assembly/persistor_factory.py) is de "hoofdaannemer" die alle persistor-instanties creëert en beheert:

```python
# backend/assembly/persistor_factory.py
class PersistorFactory:
    """
    Centraal punt voor het creëren van alle persistor-instanties.
    Implementeert het Factory Pattern met Dependency Injection.
    """
    
    def __init__(self, config: PlatformConfig):
        self._config = config
        self._state_persistor: IStatePersistor | None = None
        self._journal_persistor: IJournalPersistor | None = None
        self._data_persistor: IDataPersistor | None = None
    
    def get_state_persistor(self) -> IStatePersistor:
        """Retourneert de plugin state persistor (JsonPersistor instantie 1)."""
        if not self._state_persistor:
            self._state_persistor = JsonPersistor(
                base_path=self._config.paths.state_directory,
                mode="transactional"  # Atomic writes met journaling
            )
        return self._state_persistor
    
    def get_journal_persistor(self) -> IJournalPersistor:
        """Retourneert de strategy journal persistor (JsonPersistor instantie 2)."""
        if not self._journal_persistor:
            self._journal_persistor = JsonPersistor(
                base_path=self._config.paths.journal_directory,
                mode="append_only"  # Geen overwrites, alleen appends
            )
        return self._journal_persistor
    
    def get_data_persistor(self) -> IDataPersistor:
        """Retourneert de market data persistor (ParquetPersistor)."""
        if not self._data_persistor:
            self._data_persistor = ParquetPersistor(
                base_path=self._config.paths.market_data_directory
            )
        return self._data_persistor
```

**Cruciaal design detail:** De factory maakt **twee aparte instanties** van dezelfde `JsonPersistor`-klasse aan, elk met:
- **Gescheiden opslagpaden** (state/ vs journal/)
- **Verschillende configuraties** (transactional vs append_only)
- **Geïsoleerde verantwoordelijkheden** (atomische state vs historische log)

### **7.1.4. Dependency Injection in de Praktijk**

Componenten ontvangen hun persistor-dependencies via constructor injection, georkestreerd door de `WorkerBuilder`. De builder leest het `manifest.yaml` van een plugin om te bepalen welke `capabilities` deze nodig heeft.

**WorkerBuilder Integratie:**

De `WorkerBuilder` fungeert als de centrale "assemblagelijn". Het inspecteert de `capabilities`-sectie van het manifest en injecteert de correcte persistor-interface als de capability is aangevraagd.

```python
# backend/assembly/worker_builder.py
class WorkerBuilder:
    """Bouwt worker instances met de juiste dependencies."""

    def __init__(self, persistor_factory: PersistorFactory):
        self._persistor_factory = persistor_factory

    def build_worker(self, manifest: dict, params: dict) -> BaseWorker:
        """Creëert een worker en injecteert capabilities op basis van het manifest."""
        
        worker_class = self._load_worker_class(manifest['identification']['name'])
        
        # Instantieer de basis-worker
        worker_instance = worker_class(params)
        
        # Lees de capabilities en injecteer dependencies
        capabilities = manifest.get('capabilities', {})
        
        if capabilities.get('state', {}).get('enabled'):
            state_persistor = self._persistor_factory.get_state_persistor()
            
            # Dynamische injectie van de state-property en commit-methode
            self._inject_state_capability(
                worker_instance,
                state_persistor,
                manifest['identification']['name']
            )
            
        if capabilities.get('journaling', {}).get('enabled'):
            journal_persistor = self._persistor_factory.get_journal_persistor()
            
            # Dynamische injectie van de log_entries-methode
            self._inject_journaling_capability(worker_instance, journal_persistor)
            
        # ... (injectie voor andere capabilities zoals 'events')
            
        return worker_instance
```

**Voorbeeld van een Worker die State Gebruikt:**

De worker-klasse zelf blijft een simpele `StandardWorker` of `EventDrivenWorker`. Het erft geen speciale state-functionaliteit. De `self.state` property en `self.commit_state()` methode worden dynamisch aan de instantie toegevoegd door de `WorkerBuilder`.

```python
# Een worker die state nodig heeft, vraagt dit aan in zijn manifest.
# De code zelf blijft simpel en focust op businesslogica.

from backend.core.base_worker import StandardWorker

class TrailingStopManager(StandardWorker):
    """
    Beheert trailing stops. De state-functionaliteit wordt
    automatisch geïnjecteerd door de WorkerBuilder.
    """
    def process(self, context: TradingContext) -> None:
        current_price = context.current_price
        
        # De 'self.state' property is beschikbaar omdat de capability
        # is aangevraagd in manifest.yaml.
        high_water_mark = self.state.get('high_water_mark', current_price)
        
        if current_price > high_water_mark:
            self.state['high_water_mark'] = current_price
            
            # De 'self.commit_state()' methode is ook geïnjecteerd.
            self.commit_state()
```

Deze aanpak ontkoppelt de businesslogica van de worker volledig van de implementatiedetails van persistentie, wat de worker extreem testbaar en herbruikbaar maakt.

### **7.1.5. Rationale: Waarom Deze Architectuur?**

Deze architectuur lost drie kritieke V2 problemen op:

1. **Inconsistentie Eliminatie:** V2 had verschillende benaderingen per data-type (direct Parquet, custom per plugin, via service-laag). V3 uniformeert via interfaces.

2. **Testbaarheid:** Door dependency injection kunnen we in tests eenvoudig mock-persistors injecteren zonder het bestandssysteem te raken.

3. **Code Hergebruik:** De `JsonPersistor`-klasse wordt hergebruikt voor zowel state als journal, maar met verschillende configuraties. Dit respecteert het DRY-principe zonder Single Responsibility te schenden.

4. **Flexibiliteit:** We kunnen morgen een `DatabaseStatePersistor` introduceren zonder dat een enkele plugin hoeft te veranderen—ze zijn gekoppeld aan de interface, niet de implementatie.

---

## **7.2. Het Traceability Framework (SHIFT 5)**

V3 introduceert een fundamentele shift van simpele tracking naar **causale analyse**. Waar V2 een enkele `CorrelationID` gebruikte voor flow-tracking, implementeert V3 een rijk framework van **getypeerde, semantische IDs** die de volledige causale keten van elke trade-beslissing vastleggen.

### **7.2.1. Van Tracking naar Causale Reconstructie**

**Het Probleem met V2:**
```python
# V2: Simpele tracking
class Signal:
    correlation_id: UUID  # Wat betekent dit? Welke relatie?
```

Deze benadering kon flows tracken ("deze events horen bij elkaar"), maar kon niet beantwoorden:
- **Waarom** werd deze trade geopend?
- **Waarom** werd deze trade gesloten?
- Welke opportunity werd afgewezen en door welke threat?

**De V3 Oplossing:**
```python
# V3: Causale ID Framework
class TradeEntry:
    trade_id: UUID           # Ankerpunt: unieke trade identifier
    opportunity_id: UUID     # WAAROM geopend: link naar detecterende opportunity
    approved_at: datetime
    
class TradeExit:
    trade_id: UUID           # Zelfde ankerpunt
    threat_id: UUID          # WAAROM gesloten: link naar triggende threat
    closed_at: datetime
```

### **7.2.2. De Vier Causale ID Types**

| ID Type | Gegenereerd Door | Semantische Betekenis | Primair Gebruik |
|---------|------------------|----------------------|-----------------|
| **TradeID** | [`PlanningWorker`](backend/core/base_worker.py) of [`ExecutionWorker`](backend/core/base_worker.py) | Ankerpunt van de trade lifecycle | Primaire sleutel in alle trade-gerelateerde records |
| **OpportunityID** | [`OpportunityWorker`](backend/core/base_worker.py) | "Reden voor opening" | Causale link: "Deze trade werd geopend omdat opportunity X werd gedetecteerd" |
| **ThreatID** | [`ThreatWorker`](backend/core/base_worker.py) | "Reden voor ingreep" | Causale link: "Deze trade werd gesloten/aangepast omdat threat Y werd gedetecteerd" |
| **ScheduledID** | Scheduler | "Reden gebaseerd op tijd" | Causale link: "Deze actie werd uitgevoerd omdat het geplande moment Z werd bereikt" |

### **7.2.3. Causale Reconstructie: Complete Workflow**

#### **Stap 1: Opportunity Detection**

```python
# plugins/fvg_detector/worker.py (OpportunityWorker)
class FVGDetector(BaseOpportunityWorker):
    
    def process(self, context: TradingContext) -> List[OpportunitySignal]:
        """Detecteert Fair Value Gaps."""
        
        if self._detect_bullish_fvg(context.ohlcv_df):
            # Genereer unieke OpportunityID
            opportunity_id = uuid.uuid4()
            
            signal = OpportunitySignal(
                opportunity_id=opportunity_id,  # ← Causaal ankerpunt
                opportunity_type=OpportunityType.TECHNICAL_PATTERN,
                direction=Direction.LONG,
                detected_at=context.timestamp,
                confidence=0.85,
                metadata={
                    "pattern": "bullish_fvg",
                    "gap_size": 0.0023
                }
            )
            
            return [signal]
        
        return []
```

#### **Stap 2: Threat Assessment**

```python
# plugins/drawdown_monitor/worker.py (ThreatWorker)
class DrawdownMonitor(BaseThreatWorker):
    
    def process(self, context: TradingContext) -> List[ThreatSignal]:
        """Monitort portfolio drawdown."""
        
        current_dd = self._calculate_drawdown(context.portfolio_state)
        
        if current_dd > self.config['max_drawdown']:
            # Genereer unieke ThreatID
            threat_id = uuid.uuid4()
            
            threat = ThreatSignal(
                threat_id=threat_id,  # ← Causaal ankerpunt
                threat_type=ThreatType.PORTFOLIO_RISK,
                severity=Severity.HIGH,
                detected_at=context.timestamp,
                metadata={
                    "current_drawdown": current_dd,
                    "threshold": self.config['max_drawdown']
                }
            )
            
            return [threat]
        
        return []
```

#### **Stap 3: Risk Governor (met Journaling)**

```python
# plugins/risk_governor/worker.py (ExecutionWorker + BaseJournalingWorker)
class RiskGovernor(BaseJournalingWorker, BaseExecutionWorker):
    
    def process(self, 
                opportunity: OpportunitySignal,
                active_threats: List[ThreatSignal],
                context: TradingContext) -> OpportunitySignal | None:
        """
        Keurt opportunities goed of af. LOGT ALLE beslissingen.
        """
        
        if active_threats:
            # REJECTION: Log de causale keten
            rejection_entry = {
                "event_type": "OPPORTUNITY_REJECTED",
                "opportunity_id": str(opportunity.opportunity_id),  # ← Causale link
                "threat_id": str(active_threats[0].threat_id),      # ← Causale link
                "rejection_reason": {
                    "threat_type": active_threats[0].threat_type.value,
                    "severity": active_threats[0].severity.value,
                    "details": active_threats[0].metadata
                },
                "opportunity_details": {
                    "pattern": opportunity.metadata.get("pattern"),
                    "confidence": opportunity.confidence
                }
            }
            
            # Log naar StrategyJournal
            self.log_entries([rejection_entry], context)
            
            return None  # Opportunity wordt NIET doorgegeven
        
        # APPROVAL: Log de goedkeuring
        approval_entry = {
            "event_type": "OPPORTUNITY_APPROVED",
            "opportunity_id": str(opportunity.opportunity_id),
            "approved_for_planning": True
        }
        
        self.log_entries([approval_entry], context)
        
        return opportunity  # Opportunity gaat door naar Planning
```

#### **Stap 4: Trade Planning & Execution**

```python
# plugins/entry_planner/worker.py (PlanningWorker)
class EntryPlanner(BasePlanningWorker):
    
    def process(self, 
                opportunity: OpportunitySignal,
                context: TradingContext) -> TradePlan:
        """Creëert een concrete trade plan."""
        
        # Genereer unieke TradeID
        trade_id = uuid.uuid4()
        
        plan = TradePlan(
            trade_id=trade_id,                      # ← Nieuwe ankerpunt
            opportunity_id=opportunity.opportunity_id,  # ← Causale link terug
            entry_price=self._calculate_entry(context),
            stop_loss=self._calculate_stop(context),
            take_profit=self._calculate_target(context),
            position_size=self._calculate_size(context)
        )
        
        return plan

# plugins/trade_executor/worker.py (ExecutionWorker)
class TradeExecutor(BaseJournalingWorker, BaseExecutionWorker):
    
    def process(self, 
                plan: TradePlan,
                context: TradingContext) -> ExecutionResult:
        """Voert de trade uit en logt."""
        
        result = self._execute_order(plan)
        
        # Log de trade opening met COMPLETE causale context
        opening_entry = {
            "event_type": "TRADE_OPENED",
            "trade_id": str(plan.trade_id),              # ← Primaire ankerpunt
            "opportunity_id": str(plan.opportunity_id),  # ← "Waarom geopend"
            "execution_details": {
                "entry_price": result.fill_price,
                "position_size": result.filled_quantity,
                "slippage": result.slippage
            },
            "plan_details": {
                "stop_loss": plan.stop_loss,
                "take_profit": plan.take_profit
            }
        }
        
        self.log_entries([opening_entry], context)
        
        return result
```

#### **Stap 5: Position Monitoring & Exit**

```python
# plugins/stop_manager/worker.py (ExecutionWorker)
class StopManager(BaseJournalingWorker, BaseExecutionWorker):
    
    def process(self,
                active_positions: List[Position],
                active_threats: List[ThreatSignal],
                context: TradingContext) -> List[ExecutionDirective]:
        """Monitort stops en sluit posities bij threats."""
        
        directives = []
        
        for position in active_positions:
            # Check of er een threat is die deze positie bedreigt
            relevant_threat = self._find_relevant_threat(position, active_threats)
            
            if relevant_threat:
                # CLOSE POSITION met causale documentatie
                close_directive = ExecutionDirective(
                    action=Action.CLOSE_POSITION,
                    trade_id=position.trade_id,
                    reason="threat_triggered"
                )
                directives.append(close_directive)
                
                # Log de EXIT met complete causale context
                exit_entry = {
                    "event_type": "TRADE_CLOSED",
                    "trade_id": str(position.trade_id),         # ← Ankerpunt
                    "threat_id": str(relevant_threat.threat_id), # ← "Waarom gesloten"
                    "close_reason": "threat_intervention",
                    "threat_details": {
                        "threat_type": relevant_threat.threat_type.value,
                        "severity": relevant_threat.severity.value
                    },
                    "performance": {
                        "pnl": position.unrealized_pnl,
                        "return_pct": position.return_percentage
                    }
                }
                
                self.log_entries([exit_entry], context)
        
        return directives
```

### **7.2.4. Causale Reconstructie: Praktische Use Cases**

#### **Use Case 1: "Waarom werd deze verliezende trade geopend?"**

```sql
-- Query op StrategyJournal
SELECT 
    t.trade_id,
    t.opportunity_id,
    o.pattern,
    o.confidence,
    t.final_pnl
FROM trade_openings t
JOIN opportunity_detections o ON t.opportunity_id = o.opportunity_id
WHERE t.final_pnl < 0
ORDER BY t.final_pnl ASC
LIMIT 10;
```

**Resultaat:** We kunnen exact zien welk patroon (FVG, MSS, etc.) en met welke confidence elke verliezende trade werd geopend.

#### **Use Case 2: "Hoeveel kansen werden gemist door risk management?"**

```python
# Analysis script
rejected_opportunities = journal.query(event_type="OPPORTUNITY_REJECTED")

rejection_by_threat = defaultdict(list)
for rejection in rejected_opportunities:
    threat_type = rejection['rejection_reason']['threat_type']
    rejection_by_threat[threat_type].append(rejection)

# Output:
# PORTFOLIO_RISK: 23 opportunities rejected (max drawdown breach)
# MARKET_RISK: 15 opportunities rejected (high volatility)
# SYSTEM_HEALTH: 2 opportunities rejected (connection issues)
```

#### **Use Case 3: "Complete lifecycle van een trade"**

```python
def reconstruct_trade_lifecycle(journal: StrategyJournal, trade_id: UUID) -> dict:
    """Reconstrueert de complete causale geschiedenis van een trade."""
    
    # Stap 1: Vind de opening
    opening = journal.query(
        event_type="TRADE_OPENED",
        trade_id=trade_id
    )[0]
    
    # Stap 2: Vind de oorspronkelijke opportunity
    opportunity = journal.query(
        event_type="OPPORTUNITY_DETECTED",
        opportunity_id=opening['opportunity_id']
    )[0]
    
    # Stap 3: Vind de exit
    closing = journal.query(
        event_type="TRADE_CLOSED",
        trade_id=trade_id
    )[0]
    
    # Stap 4: Vind de threat die de exit triggerde
    threat = journal.query(
        event_type="THREAT_DETECTED",
        threat_id=closing['threat_id']
    )[0]
    
    return {
        "trade_summary": {
            "trade_id": trade_id,
            "pnl": closing['performance']['pnl']
        },
        "opening_cause": {
            "pattern": opportunity['metadata']['pattern'],
            "confidence": opportunity['confidence'],
            "detected_at": opportunity['timestamp']
        },
        "closing_cause": {
            "threat_type": threat['threat_type'],
            "severity": threat['severity'],
            "triggered_at": threat['timestamp']
        }
    }
```

**Output:**
```json
{
    "trade_summary": {
        "trade_id": "a3f2...",
        "pnl": -45.23
    },
    "opening_cause": {
        "pattern": "bullish_fvg",
        "confidence": 0.85,
        "detected_at": "2025-10-14T10:00:00Z"
    },
    "closing_cause": {
        "threat_type": "MARKET_RISK",
        "severity": "HIGH",
        "triggered_at": "2025-10-14T10:15:23Z"
    }
}
```

### **7.2.5. Traceability in het StrategyJournal**

Alle causale IDs worden persistent gemaakt in het [`StrategyJournal`](backend/core/strategy_journal.py):

```json
{
    "strategy_id": "mss_fvg_strategy",
    "journal_entries": [
        {
            "timestamp": "2025-10-14T10:00:00Z",
            "event_type": "OPPORTUNITY_DETECTED",
            "opportunity_id": "a1b2c3...",
            "opportunity_type": "TECHNICAL_PATTERN",
            "metadata": {"pattern": "bullish_fvg"}
        },
        {
            "timestamp": "2025-10-14T10:00:01Z",
            "event_type": "THREAT_DETECTED",
            "threat_id": "d4e5f6...",
            "threat_type": "PORTFOLIO_RISK",
            "metadata": {"current_drawdown": 0.15}
        },
        {
            "timestamp": "2025-10-14T10:00:02Z",
            "event_type": "OPPORTUNITY_REJECTED",
            "opportunity_id": "a1b2c3...",
            "threat_id": "d4e5f6...",
            "rejection_reason": "max_drawdown_exceeded"
        }
    ]
}
```

---

## **7.3. Journaling Architectuur: Ledger vs Journal Scheiding**

V3 introduceert een strikte conceptuele en architectonische scheiding tussen **operationele staat** en **historische log**.

### **7.3.1. StrategyLedger: Operationele Staat (Snel & Minimaal)**

De [`StrategyLedger`](backend/core/strategy_ledger.py) is de **real-time, read-write cache** van de huidige operationele staat:

```python
# backend/core/strategy_ledger.py
class StrategyLedger:
    """
    Bevat ALLEEN de actuele operationele staat van een strategie.
    Geoptimaliseerd voor snelle read/write operaties tijdens trading.
    """
    
    def __init__(self):
        self.capital: float = 10000.0
        self.open_positions: List[Position] = []
        self.closed_positions: List[Position] = []  # Alleen recent (laatste 10)
        self.unrealized_pnl: float = 0.0
        self.realized_pnl: float = 0.0
        
        # GEEN historische data
        # GEEN causale IDs
        # GEEN afgewezen opportunities
```

**Karakteristieken:**
- **Performance:** ⚡ Extreem snel (minimale data in geheugen)
- **Volatiliteit:** Hoge mutatie-frequentie (elke tick)
- **Retentie:** Alleen actuele + recente closed positions
- **Persistentie:** Via [`IStatePersistor`](backend/core/interfaces/persistors.py:IStatePersistor) met atomische writes

### **7.3.2. StrategyJournal: Historische Log (Rijk & Immutable)**

Het [`StrategyJournal`](backend/core/strategy_journal.py) is de **append-only, historische log** van alle beslissingen:

```python
# backend/core/strategy_journal.py
class StrategyJournal:
    """
    Bevat de VOLLEDIGE historische log van alle events, beslissingen,
    en causale relaties. Append-only, immutable na schrijven.
    """
    
    def __init__(self, journal_persistor: IJournalPersistor):
        self._persistor = journal_persistor
    
    def log_event(self, event: JournalEntry) -> None:
        """Voegt een event toe aan het immutable journal."""
        self._persistor.append(
            strategy_id=event.strategy_id,
            entries=[event.to_dict()]
        )
```

**Karakteristieken:**
- **Performance:** Geoptimaliseerd voor batch-writes, niet voor real-time queries
- **Volledigheid:** Bevat ALLE events, inclusief:
  - ✅ Gedetecteerde opportunities
  - ✅ Gedetecteerde threats
  - ✅ **Afgewezen opportunities** (met reden)
  - ✅ Goedgekeurde opportunities
  - ✅ Trade openings (met causale OpportunityID)
  - ✅ Trade closings (met causale ThreatID)
- **Immutability:** Entries worden NOOIT gewijzigd na schrijven
- **Persistentie:** Via [`IJournalPersistor`](backend/core/interfaces/persistors.py:IJournalPersistor) in append-only mode

### **7.3.3. Journaling via de 'journaling' Capability**

Plugins krijgen directe, maar ontkoppelde, toegang tot het `StrategyJournal` door de `journaling` capability aan te vragen in hun `manifest.yaml`. Dit vervangt de oude `BaseJournalingWorker`.

**De Rol van de WorkerBuilder:**

Als de `WorkerBuilder` de `journaling: enabled: true` vlag in het manifest van een worker ziet, voert het de volgende stappen uit:

1.  Het vraagt de singleton `IJournalPersistor`-instantie op bij de `PersistorFactory`.
2.  Het injecteert dynamisch een `log_entries`-methode in de worker-instantie. Deze methode fungeert als een-interface die de aanroep delegeert naar de `IJournalPersistor`.

**Voorbeeld van een Worker die Journaling Gebruikt:**

De worker-code blijft gefocust op de businesslogica. De ontwikkelaar hoeft alleen te weten dat hij `self.log_entries()` kan aanroepen.

```python
# plugins/risk_governor/worker.py
from backend.core.base_worker import StandardWorker

class RiskGovernor(StandardWorker):
    """
    Keurt opportunities goed of af en LOGT ALLE beslissingen.
    De 'log_entries' methode is dynamisch geïnjecteerd.
    """
    def process(self,
                opportunity: OpportunitySignal,
                active_threats: List[ThreatSignal],
                context: TradingContext) -> OpportunitySignal | None:
        
        if active_threats:
            # REJECTION: Formuleer de journal entry
            rejection_entry = {
                "event_type": "OPPORTUNITY_REJECTED",
                "opportunity_id": str(opportunity.opportunity_id),
                "threat_id": str(active_threats[0].threat_id),
                # ... overige details
            }
            
            # Log naar StrategyJournal via de geïnjecteerde methode
            self.log_entries([rejection_entry], context)
            
            return None # Opportunity wordt afgewezen
        
        # ... (logica voor goedkeuring)
        
        return opportunity
```

**Filosofie: "De Plugin als Intelligente Bron"**

Deze architectuur behoudt het kernprincipe:

-   De **plugin** is de enige die de semantische inhoud en rationale van zijn beslissingen kent en formuleert de journal entries.
-   De **`log_entries`-methode** (geïnjecteerd) is de gestandaardiseerde, ontkoppelde interface naar de persistence-laag.
-   De **persistor** is "dom" en slaat simpelweg op wat hij via de interface ontvangt.

### **7.3.4. Event-to-Journal Mapping**

Alle belangrijke events worden gelogd met rijke causale context:

| Event Type | Worker Type | Journaled Data | Causale IDs |
|------------|-------------|----------------|-------------|
| **OPPORTUNITY_DETECTED** | OpportunityWorker | Pattern, confidence, market conditions | `opportunity_id` (nieuw) |
| **THREAT_DETECTED** | ThreatWorker | Threat type, severity, trigger values | `threat_id` (nieuw) |
| **OPPORTUNITY_REJECTED** | ExecutionWorker | Rejection reason, threat details | `opportunity_id`, `threat_id` |
| **OPPORTUNITY_APPROVED** | ExecutionWorker | Approval criteria, context | `opportunity_id` |
| **TRADE_OPENED** | ExecutionWorker | Entry details, plan specs | `trade_id` (nieuw), `opportunity_id` |
| **POSITION_ADJUSTED** | ExecutionWorker | Adjustment reason, new parameters | `trade_id`, `threat_id` (optional) |
| **TRADE_CLOSED** | ExecutionWorker | Exit reason, performance metrics | `trade_id`, `threat_id` (optional) |

### **7.3.5. Practical Example: Complete Decision Trail**

```python
# Voorbeeld: Een volledige beslissingsketen in het journal

# Event 1: Opportunity detectie
{
    "timestamp": "2025-10-14T10:00:00.000Z",
    "event_type": "OPPORTUNITY_DETECTED",
    "opportunity_id": "opp_a1b2c3",
    "opportunity_type": "TECHNICAL_PATTERN",
    "worker": "fvg_detector",
    "metadata": {
        "pattern": "bullish_fvg",
        "gap_size": 0.0023,
        "confidence": 0.85,
        "price_level": 61250.00
    }
}

# Event 2: Threat detectie (parallel)
{
    "timestamp": "2025-10-14T10:00:00.050Z",
    "event_type": "THREAT_DETECTED",
    "threat_id": "threat_d4e5f6",
    "threat_type": "PORTFOLIO_RISK",
    "worker": "drawdown_monitor",
    "metadata": {
        "current_drawdown": 0.15,
        "max_allowed": 0.10,
        "severity": "HIGH"
    }
}

# Event 3: Opportunity rejection
{
    "timestamp": "2025-10-14T10:00:00.100Z",
    "event_type": "OPPORTUNITY_REJECTED",
    "opportunity_id": "opp_a1b2c3",  # ← Link terug
    "threat_id": "threat_d4e5f6",     # ← Link naar reden
    "worker": "risk_governor",
    "rejection_reason": {
        "primary": "max_drawdown_exceeded",
        "threat_details": {
            "current_drawdown": 0.15,
            "threshold": 0.10
        },
        "opportunity_details": {
            "pattern": "bullish_fvg",
            "confidence": 0.85
        }
    }
}
```

Deze entry-keten maakt het mogelijk om later te analyseren:
- Hoeveel high-confidence FVG opportunities werden gemist door drawdown limits?
- Wat was de gemiddelde confidence van afgewezen vs uitgevoerde opportunities?
- Welke threat types zijn de meest restrictieve?

---

## **7.4. Integriteit van de Staat: Atomiciteit en Persistentie**

Een trading-systeem is inherent 'stateful'. De huidige staat (open posities, kapitaal, de interne staat van een stateful plugin) is de basis voor toekomstige beslissingen. Het corrumperen van deze staat is catastrofaal.

### **7.4.1. Atomische Schrijfacties (Journaling)**

* **Probleem:** Een applicatiecrash of stroomuitval tijdens het schrijven van een state-bestand (bv. state.json voor een stateful ExecutionWorker) kan leiden tot een half geschreven, corrupt bestand, met permanent dataverlies tot gevolg.  
* **Architectonische Oplossing:** We implementeren een **Write-Ahead Log (WAL)** of **Journaling**-patroon, een techniek die door professionele databases wordt gebruikt.  
* **Gedetailleerde Workflow:**  
  1. **Schrijf naar Journaal:** De [`save_state()`](backend/core/base_worker.py:BaseStatefulWorker.save_state)-methode van een stateful plugin schrijft de nieuwe staat **nooit** direct naar state.json. Het serialiseert de data naar een tijdelijk bestand: `state.json.journal`.  
  2. **Forceer Sync naar Schijf:** Na het schrijven roept de methode [`os.fsync()`](https://docs.python.org/3/library/os.html#os.fsync) aan op het `.journal`-bestands-handle. Dit is een cruciale, expliciete instructie aan het besturingssysteem om alle databuffers onmiddellijk naar de fysieke schijf te schrijven.  
  3. **Atomische Hernoeming:** Alleen als de sync succesvol is, wordt de [`os.rename()`](https://docs.python.org/3/library/os.html#os.rename)-operatie uitgevoerd om `state.json.journal` te hernoemen naar `state.json`. Deze rename-operatie is op de meeste moderne bestandssystemen een **atomische handeling**: het slaagt in zijn geheel, of het faalt in zijn geheel.  
  4. **Herstel-Logica:** De [`load_state()`](backend/core/base_worker.py:BaseStatefulWorker.load_state)-methode van de plugin bevat de herstel-logica. Bij het opstarten controleert het: "Bestaat er een `.journal`-bestand?". Zo ja, dan weet het dat de applicatie is gecrasht na stap 2 maar vóór stap 3. De herstelprocedure is dan het voltooien van de rename-operatie.

**Implementatie in JsonPersistor:**

```python
# backend/data/persistors/json_persistor.py
class JsonPersistor:
    """
    Generieke JSON persistor met atomische write garanties.
    Implementeert zowel IStatePersistor als IJournalPersistor.
    """
    
    def save_state(self, plugin_id: str, state: Dict[str, Any]) -> None:
        """Atomische state save via journaling."""
        state_file = self._get_state_path(plugin_id)
        journal_file = f"{state_file}.journal"
        
        # Stap 1: Schrijf naar journal
        with open(journal_file, 'w') as f:
            json.dump(state, f, indent=2)
            f.flush()
            
            # Stap 2: Force sync naar schijf
            os.fsync(f.fileno())
        
        # Stap 3: Atomische rename
        os.rename(journal_file, state_file)
    
    def load_state(self, plugin_id: str) -> Dict[str, Any]:
        """Load met crash recovery."""
        state_file = self._get_state_path(plugin_id)
        journal_file = f"{state_file}.journal"
        
        # Check voor incomplete write (crash recovery)
        if os.path.exists(journal_file):
            logger.warning(f"Detected incomplete write for {plugin_id}, recovering...")
            os.rename(journal_file, state_file)
        
        # Normal load
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        
        return {}  # Empty state voor nieuwe plugin
```

---

## **7.5. Netwerkveerkracht en Staatssynchronisatie**

Een live-systeem is afhankelijk van een stabiele verbinding en moet kunnen omgaan met de onvermijdelijke instabiliteit van het internet. De kernfilosofie is: **de exchange is de enige bron van waarheid.** Ons platform onderhoudt slechts een real-time cache van die waarheid.

* **Architectonische Oplossing:** De verantwoordelijkheid voor het managen van de verbinding en de staatssynchronisatie ligt bij de [`LiveEnvironment`](backend/environments/live_environment.py) en wordt aangestuurd door gespecialiseerde ThreatWorkers en ExecutionWorkers. We gebruiken een tweeledige strategie van "push" en "pull".

### **7.5.1. Mechanisme 1: Real-time Synchronisatie via 'Push' (WebSocket)**

* **Doel:** De interne staat ([`StrategyLedger`](backend/core/strategy_ledger.py)) met minimale latency synchroon houden tijdens de normale operatie.  
* **Componenten:** De [`LiveEnvironment`](backend/environments/live_environment.py) en zijn [`IAPIConnector`](backend/core/interfaces/connectors.py:IAPIConnector).  
* **Proces:**  
  1. De LiveEnvironment zet via de IAPIConnector een **private WebSocket-verbinding** ([`start_user_data_stream()`](backend/core/interfaces/connectors.py:IAPIConnector.start_user_data_stream)) op.  
  2. Wanneer een door S1mpleTrader geplaatste order wordt gevuld, *pusht* de exchange onmiddellijk een `TradeExecuted`-bericht.  
  3. De IAPIConnector vangt dit bericht op en vertaalt het naar een intern `LedgerStateChanged`-event.  
  4. Een ThreatWorker die de LedgerState observeert, wordt geactiveerd door dit event en kan indien nodig andere componenten informeren.

### **7.5.2. Mechanisme 2: Herstel & Verificatie via 'Pull' (State Reconciliation)**

* **Doel:** Het cruciale veiligheidsnet voor periodieke verificatie en, belangrijker nog, voor **herstel na een crash** of netwerkonderbreking.  
* **Componenten:** Een `ReconciliationMonitor` (een ThreatWorker) en de LiveEnvironment.  
* **Proces:**  
  1. **Trigger**: De Scheduler publiceert een periodiek event (bv. `five_minute_reconciliation_tick`) zoals gedefinieerd in [`schedule.yaml`](config/schedule.yaml).  
  2. De ReconciliationMonitor luistert naar dit event en start de [`reconcile_state()`](backend/environments/live_environment.py:LiveEnvironment.reconcile_state)-procedure. Dit gebeurt **altijd** bij het opstarten van een live Operation.  
  3. **Pull**: De monitor instrueert de LiveEnvironment om via de IAPIConnector de REST API van de exchange aan te roepen ([`get_open_orders()`](backend/core/interfaces/connectors.py:IAPIConnector.get_open_orders), [`get_open_positions()`](backend/core/interfaces/connectors.py:IAPIConnector.get_open_positions)) om de "absolute waarheid" op te halen.  
  4. **Vergelijk**: Het vergelijkt deze lijst van "echte" posities en orders met de staat van de StrategyLedgers die het beheert.  
  5. **Corrigeer**: Bij discrepanties wordt de StrategyLedger geforceerd gecorrigeerd om de staat van de exchange te weerspiegelen, en wordt een CRITICAL-waarschuwing gelogd.

### **7.5.3. Verbindingsbeheer & Circuit Breaker**

* **Componenten:** Een `ConnectionMonitor` (ThreatWorker), een `CircuitBreakerWorker` (ExecutionWorker), en de LiveEnvironment's DataSource.  
* **Proces:**  
  1. **Heartbeat & Reconnect**: De DataSource monitort de verbinding. Bij een onderbreking start het een automatisch reconnect-protocol met een **exponential backoff**-algoritme.  
  2. **Event Publicatie**: Als de DataSource na een configureerbaar aantal pogingen geen verbinding kan herstellen, publiceert het een `CONNECTION_LOST`-event.  
  3. De **ConnectionMonitor** vangt dit event op en publiceert een strategisch event, bijvoorbeeld `CONNECTION_UNSTABLE_DETECTED`.  
  4. De **CircuitBreakerWorker** luistert naar `CONNECTION_UNSTABLE_DETECTED` en activeert de **Circuit Breaker**:  
     * Het publiceert een `HALT_NEW_SIGNALS`-event.  
     * Het stuurt een kritieke alert naar de gebruiker.  
     * Het kan (optioneel) proberen alle open posities die door S1mpleTrader worden beheerd, te sluiten door een `EXECUTE_EMERGENCY_EXIT`-event te publiceren.

---

## **7.6. Applicatie Crash Recovery (Supervisor Model)**

* **Probleem:** Het hoofdproces van het platform (de Operations-service) kan crashen door een onverwachte bug.  
* **Architectonische Oplossing:** We scheiden het *starten* van de applicatie van de *applicatie zelf* door middel van een **Supervisor (Watchdog)**-proces, aangestuurd door [`run_supervisor.py`](run_supervisor.py).  
* **Gedetailleerde Workflow:**  
  1. **Entrypoint [`run_supervisor.py`](run_supervisor.py):** Dit is het enige script dat je handmatig start in een live-omgeving.  
  2. **Supervisor Proces:** Dit script start een lichtgewicht "supervisor"-proces dat een *kind-proces* voor de daadwerkelijke Operations-service start en monitort.  
  3. **Herstart & Herstel Cyclus:**  
     * Als het Operations-proces onverwacht stopt, detecteert de Supervisor dit.  
     * De Supervisor start de Operations-service opnieuw.  
     * De *nieuwe* Operations-instantie start in een **"herstelmodus"**:  
       * **Stap A (Plugin State Herstel):** Via de [`WorkerBuilder`](backend/assembly/worker_builder.py) worden alle stateful plugins geladen met hun [`load_state()`](backend/core/base_worker.py:BaseStatefulWorker.load_state)-methodes, die de journaling-logica (zie 7.4.1) gebruiken om een consistente staat te herstellen.  
       * **Stap B (Ledger Herstel):** De **State Reconciliation**-procedure (zie 7.5.2) wordt onmiddellijk uitgevoerd om alle StrategyLedgers te synchroniseren met de exchange.  
       * **Stap C (Hervatting):** Alleen als beide stappen succesvol zijn, gaat de Operation verder met de normale-tick verwerking.

---

## **7.7. Samenvatting: De Drie Pijlers van Robuustheid**

De robuustheid van S1mpleTrader V2 rust op drie fundamentele architectonische pijlers:

1. **Persistence Suite (SHIFT 3):** Uniform, interface-gedreven model voor alle data-opslag met scheiding van verantwoordelijkheden (marktdata, state, journal) en dependency injection voor testbaarheid.

2. **Traceability Framework (SHIFT 5):** Getypeerde causale IDs (TradeID, OpportunityID, ThreatID, ScheduledID) die complete reconstructie van beslissingsketen mogelijk maken—niet alleen "wat gebeurde" maar "waarom het gebeurde".

3. **Ledger/Journal Scheiding:** Strikte scheiding tussen operationele staat (StrategyLedger: snel, minimaal) en historische log (StrategyJournal: compleet, inclusief afgewezen kansen) met directe journaling via BaseJournalingWorker.

Deze drie pijlers, gecombineerd met de beproefde technieken uit V2 (atomische writes, state reconciliation, circuit breakers), creëren een systeem dat niet alleen betrouwbaar is tijdens normale operaties, maar ook robuust herstelt van crashes, netwerkfouten en andere onverwachte omstandigheden.

**Kernprincipe:** In een trading-systeem is data-integriteit niet optioneel—het is de basis. Elke regel code die met persistentie te maken heeft, moet geschreven zijn met de aanname dat "het volgende moment kan alles crashen".