# S1mpleTrader V4.0 Architectuur - Quick Start

**Versie:** 4.0  
**Laatst bijgewerkt:** 2025-10-23

---

## 📚 Start Hier

Welkom bij de S1mpleTrader V4.0 architectuur documentatie. Deze README helpt je snel op weg.

### Voor Nieuwe Developers

**Minimale leeslijst** (30 minuten):

1. **[INDEX.md](INDEX.md)** - Overzicht en navigatie
2. **[Hoofddocument - Voorwoord](../S1mpleTrader%20V2%20Architectuur%20-%20Herzien.md#voorwoord-de-drie-fundamentele-paradigmas)** - De 3 paradigma's
3. **[H3: Data Landschap](H3_Het_Data_Landschap.md)** - Hoe data werkt (Point-in-Time)
4. **[H4: Plugin Anatomie](H4_Plugin_Anatomie.md)** - Hoe een plugin bouwen
5. **[H5: Worker Ecosysteem](H5_Worker_Ecosysteem.md)** - Welk worker type kiezen

**Je bent nu klaar om je eerste plugin te bouwen!**

### Voor Architects

**Volledige leeslijst** (2 uur):

1. Lees alle hoofdstukken in volgorde
2. Focus op H1 (Communicatie), H2 (Configuratie), H6 (Workflow)
3. Bestudeer sequence diagrams en code voorbeelden
4. Lees [Bijlage A: Terminologie](Bijlage_A_Terminologie.md) voor deprecated terms

---

## 🎯 De Drie Paradigma's (Essentie)

### 1. Platgeslagen Event-Driven Netwerk

**Wat**: Geen Operators, alleen EventAdapters  
**Waarom**: Maximale transparantie en flexibiliteit  
**Lees**: [H1: Communicatie](H1_Communicatie_Architectuur.md)

### 2. Point-in-Time DTO-Gedreven Data

**Wat**: Data via ITradingContextProvider & Tick Cache, niet via enriched_df  
**Waarom**: Geen data-lekkage, type-safe, expliciet  
**Lees**: [H3: Data Landschap](../S1mpleTrader%20V2%20Architectuur%20-%20Herzien.md#hoofdstuk-3-het-data-landschap-point-in-time-architectuur)

### 3. BuildSpec-Gedreven Bootstrap

**Wat**: ConfigTranslator → BuildSpecs → Factories  
**Waarom**: Scheiding config complexiteit en runtime simpliciteit  
**Lees**: [H2: Configuratielagen](../S1mpleTrader%20V2%20Architectuur%20-%20Herzien.md#hoofdstuk-2-de-drie-configuratielagen--buildspecs)

---

## 🔧 Snelle Concepten

### Worker Types (Kies je type)

```
ContextWorker     → Verrijkt data met context (EMA, Market Structure)
OpportunityWorker → Detecteert kansen (FVG, Breakouts)
ThreatWorker      → Detecteert risico's (Drawdown, Volatility)
PlanningWorker    → Maakt trade plannen (Entry, Exit, Size, Routing)
ExecutionWorker   → Voert uit en beheert (Trade init, Position mgmt)
```

**Lees**: [H5: Worker Ecosysteem](H5_Worker_Ecosysteem.md)

### Base Classes (Kies je rol)

```python
StandardWorker      # 90% - Voor georkestreerde pipeline
                    # MOET process() implementeren

EventDrivenWorker   # 10% - Voor autonome, event-based workers
                    # GEEN process() - alleen event handlers
```

**Lees**: [H4: Plugin Anatomie](H4_Plugin_Anatomie.md#43-workerpy-de-twee-basisklassen)

### DispositionEnvelope (Return type)

```python
# Continue flow, data in cache
return DispositionEnvelope(disposition="CONTINUE")

# Publiceer event op EventBus
return DispositionEnvelope(
    disposition="PUBLISH",
    event_name="SIGNAL_GENERATED",
    event_payload=signal_dto
)

# Stop deze flow-tak
return DispositionEnvelope(disposition="STOP")
```

**Lees**: [H3: DispositionEnvelope](../S1mpleTrader%20V2%20Architectuur%20-%20Herzien.md#35-dispositionenvelope-flow-control)

---

## 📖 Documentatie Structuur

### Kern Documenten

| Document | Beschrijving | Moet Lezen |
|----------|-------------|------------|
| [INDEX.md](INDEX.md) | Navigatie en overzicht | ⭐⭐⭐ |
| [Hoofddocument](../S1mpleTrader%20V2%20Architectuur%20-%20Herzien.md) | Voorwoord + H2 + H3 | ⭐⭐⭐ |
| [H1: Communicatie](H1_Communicatie_Architectuur.md) | EventAdapter model | ⭐⭐⭐ |
| [H4: Plugin Anatomie](H4_Plugin_Anatomie.md) | Plugin structuur | ⭐⭐⭐ |
| [H5: Worker Ecosysteem](H5_Worker_Ecosysteem.md) | 5 categorieën | ⭐⭐⭐ |
| [H6: Workflow](H6_Workflow_Orkestratie.md) | Flow orkestratie | ⭐⭐ |
| [H7: Frontend](H7_Frontend_Integration.md) | UI integratie | ⭐⭐ |
| [H8: Robuustheid](H8_Robuustheid_Operations.md) | Operations | ⭐⭐ |
| [H9: Development](H9_Development_Strategy.md) | Dev workflow | ⭐⭐ |
| [H10: Meta Workflows](H10_Meta_Workflows.md) | Optimization | ⭐ |
| [H11: Standards](H11_Coding_Standards.md) | Coding rules | ⭐⭐⭐ |
| [Bijlage A](Bijlage_A_Terminologie.md) | Terminologie | ⭐⭐ |

---

## 🚀 Quick Start: Eerste Plugin

### 1. Kies Worker Type

Wat wil je bouwen?
- Data verrijken? → `ContextWorker`
- Kansen detecteren? → `OpportunityWorker`
- Risico's monitoren? → `ThreatWorker`
- Plannen maken? → `PlanningWorker`
- Uitvoeren? → `ExecutionWorker`

### 2. Gebruik Plugin IDE

```bash
# Open Plugin IDE in browser
python run_web.py

# Navigeer naar: Plugin Development → New Plugin
# Volg wizard voor scaffolding
```

### 3. Implementeer Process()

```python
# Voor StandardWorker
class MyWorker(StandardWorker):
    context_provider: ITradingContextProvider
    
    def process(self) -> DispositionEnvelope:
        # 1. Haal data
        base_ctx = self.context_provider.get_base_context()
        
        # 2. Verwerk
        result = self._calculate(base_ctx)
        
        # 3. Output
        self.context_provider.set_result_dto(self, result)
        return DispositionEnvelope(disposition="CONTINUE")
```

### 4. Test

```python
# tests/test_worker.py
def test_my_worker(mock_providers):
    worker = MyWorker(params={}, **mock_providers)
    result = worker.process()
    
    assert result.disposition == "CONTINUE"
    mock_providers['context_provider'].set_result_dto.assert_called_once()
```

### 5. Enroll & Use

```bash
# Run tests
pytest plugins/my_worker/tests/

# Enrollment (via UI of CLI)
python tools/enroll_plugin.py --plugin my_worker

# Gebruik in Strategy Builder UI
```

---

## 🎓 Veelgestelde Vragen

### "Wat is het verschil met V3.0?"

**V3.0 had**:
- BaseOperator klasse en Operator laag
- operators.yaml configuratie
- enriched_df in TradingContext
- Impliciete data doorgifte

**V4.0 heeft**:
- Platgeslagen EventAdapter model
- UI-gegenereerde strategy_wiring_map
- Point-in-Time DTOs via ITradingContextProvider
- Expliciete data via DispositionEnvelope

**Lees**: [Bijlage A: Deprecated Terms](Bijlage_A_Terminologie.md#deprecated-terminologie)

### "Hoe werkt data-uitwisseling nu?"

1. Worker vraagt DTOs op via `context_provider.get_required_dtos()`
2. Worker plaatst output via `context_provider.set_result_dto()`
3. DTOs leven in tijdelijke Tick Cache (alleen tijdens tick)
4. Volgende worker haalt DTOs op uit cache

**Lees**: [H3: Data Landschap](../S1mpleTrader%20V2%20Architectuur%20-%20Herzien.md#hoofdstuk-3-het-data-landschap-point-in-time-architectuur)

### "Wat is een DispositionEnvelope?"

Een standaard return type voor workers die flow control aanstuurt:

```python
CONTINUE - Ga door, data in cache
PUBLISH  - Publiceer event op EventBus
STOP     - Stop deze flow-tak
```

**Lees**: [H3: DispositionEnvelope](../S1mpleTrader%20V2%20Architectuur%20-%20Herzien.md#35-dispositionenvelope-flow-control)

### "Hoe configureer ik de workflow?"

Via de **Strategy Builder UI**:
1. Drag workers naar canvas
2. Positioneer serieel (onder elkaar) of parallel (naast elkaar)
3. UI genereert automatisch strategy_wiring_map.yaml
4. Validatie gebeurt real-time

**Lees**: [H7: Frontend Integration](H7_Frontend_Integration.md)

### "Wanneer gebruik ik EventDrivenWorker?"

Gebruik EventDrivenWorker als:
- Worker moet reageren op **scheduled events** (weekly DCA)
- Worker moet op **meerdere triggers** wachten (fan-in)
- Worker opereert **autonoom** (news monitor)

Anders: gebruik StandardWorker (90% van gevallen)

**Lees**: [H4: Base Classes](H4_Plugin_Anatomie.md#43-workerpy-de-twee-basisklassen)

---

## 🛠️ Tools & Commands

### Development

```bash
# Start Web UI (Plugin IDE + Strategy Builder)
python run_web.py

# Run backtest CLI
python run_backtest_cli.py --operation my_operation

# Validate configuration
python tools/validate_config.py --strategy ict_smc_strategy

# Validate event chains
python tools/validate_event_chains.py --strategy ict_smc_strategy
```

### Testing

```bash
# Run all tests
pytest

# Test one plugin
pytest plugins/my_plugin/tests/

# Test with coverage
pytest --cov=backend --cov=plugins

# Integration tests
pytest tests/integration/
```

---

## 📦 Repository Structuur

```
S1mpleTraderV2/
├── backend/
│   ├── core/              # EventBus, TickCacheManager, base_worker.py
│   ├── assembly/          # Factories, Validators, EventAdapter
│   ├── config/            # ConfigLoader, ConfigTranslator
│   ├── dtos/              # Systeem DTOs
│   └── dto_reg/           # Centraal DTO register
├── config/
│   ├── platform.yaml
│   ├── operation.yaml
│   ├── platform_wiring_map.yaml
│   └── runs/
│       ├── strategy_blueprint.yaml
│       └── strategy_wiring_map.yaml  # UI-gegenereerd
├── plugins/
│   ├── context_workers/
│   ├── opportunity_workers/
│   ├── threat_workers/
│   ├── planning_workers/
│   └── execution_workers/
├── services/
│   └── operation_service.py  # Levenscyclus manager
├── docs/
│   └── system/
│       └── herzien/       # Deze documentatie
└── tests/
```

---

## 🔗 Externe Resources

- **Originele documentatie**: `docs/system/S1mpleTrader V2 Architectuur.md` (V3.0)
- **Addenda**: `docs/system/addendums/` (achtergrond voor V4.0 wijzigingen)
- **Code voorbeelden**: Zie elk hoofdstuk voor complete code samples

---

## ⚡ Quick Reference Cards

### Plugin Manifest Template

```yaml
identification:
  name: "my_worker"
  type: "context_worker"  # of opportunity/threat/planning/execution
  subtype: "indicator_calculation"  # zie H5 voor alle sub-types
  
requires_capability:
  - "ohlcv_window"
  
requires_dtos:
  - dto_type: "SomeDTO"
    expected_path: "backend.dto_reg.vendor.plugin.version.dto"
    
produces_dtos:
  - dto_type: "MyOutputDTO"
    local_path: "dtos/my_output_dto.py"
    
capabilities:
  state: {enabled: false}
  events: {enabled: false}
  journaling: {enabled: false}
```

### Worker Template

```python
from backend.core.base_worker import StandardWorker
from backend.shared_dtos.disposition_envelope import DispositionEnvelope

class MyWorker(StandardWorker):
    context_provider: ITradingContextProvider
    ohlcv_provider: IOhlcvProvider
    
    def process(self) -> DispositionEnvelope:
        # 1. Get data
        base_ctx = self.context_provider.get_base_context()
        df = self.ohlcv_provider.get_window(base_ctx.timestamp, 200)
        
        # 2. Calculate
        result_dto = self._calculate(df)
        
        # 3. Output
        self.context_provider.set_result_dto(self, result_dto)
        return DispositionEnvelope(disposition="CONTINUE")
```

### Test Template

```python
from unittest.mock import MagicMock

def test_my_worker():
    # Mock providers
    providers = {
        'context_provider': MagicMock(),
        'ohlcv_provider': MagicMock()
    }
    
    # Test
    worker = MyWorker(params={}, **providers)
    result = worker.process()
    
    # Verify
    assert result.disposition == "CONTINUE"
```

---

## 📞 Support

Voor vragen of problemen:
1. Check [INDEX.md](INDEX.md) voor navigatie
2. Zoek in [Bijlage A: Terminologie](Bijlage_A_Terminologie.md)
3. Raadpleeg relevant hoofdstuk
4. Contact development team

---

## 🗺️ Navigatie Map

```
START HERE (README) → INDEX → Voorwoord (3 paradigma's)
                                    ↓
                            Kies je pad:
                                    ↓
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            Plugin Dev      Strategy Dev     Architect
                ↓               ↓               ↓
            H4 + H5         H6 + H7         H1 + H2 + H3
```

---

**Veel succes met S1mpleTrader V4.0!** 🚀