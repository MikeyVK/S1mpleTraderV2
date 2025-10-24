# Hoofdstuk 4: Plugin Anatomie

**Status:** Definitief  
**Versie:** 4.0

---

## 4.1. De Plugin als Zelfstandige Eenheid

Een plugin is een **volledig zelfstandige, testbare eenheid** van businesslogica. De mappenstructuur maakt dit mogelijk:

```
plugins/<worker_category>/<sub_type>/<plugin_name>/
├── manifest.yaml          # Identiteit & contracten
├── worker.py             # Businesslogica
├── schema.py             # Parameter validatie
├── dtos/                 # Output DTOs (optioneel)
│   └── my_output_dto.py
└── tests/
    └── test_worker.py    # Verplichte tests
```

---

## 4.2. Manifest.yaml: De Complete Plugin Specificatie

Het [`manifest.yaml`](plugins/*/manifest.yaml) is de **Single Source of Truth** voor alles wat het platform over een plugin moet weten.

### 4.2.1. Identificatie

```yaml
# manifest.yaml
identification:
  name: "ema_detector"                    # Technische naam (snake_case)
  display_name: "EMA Detector"           # UI naam
  type: "context_worker"                 # Een van de 5 categorieën
  subtype: "indicator_calculation"       # Een van de 27 sub-types
  version: "1.0.0"                       # Semantische versie
  description: "Berekent EMA indicatoren"
  author: "S1mpleTrader Team"
```

**Worker Types** (5 categorieën):
- `context_worker` - Verrijkt data met context
- `opportunity_worker` - Detecteert handelskansen
- `threat_worker` - Detecteert risico's
- `planning_worker` - Maakt trade plannen
- `execution_worker` - Voert uit en beheert

### 4.2.2. Data Contracten (DTO-Centric)

```yaml
# Data dependencies voor Point-in-Time model
requires_capability:
  - "ohlcv_window"           # Platform provider
  - "state_persistence"      # State provider

requires_dtos:
  # DTOs die deze worker uit Tick Cache nodig heeft
  - dto_type: "MarketStructureDTO"
    expected_path: "backend.dto_reg.s1mple.market_structure_detector.v1_0_0.structure_dto"

produces_dtos:
  # DTOs die deze worker in Tick Cache plaatst
  - dto_type: "EMAOutputDTO"
    local_path: "dtos/ema_output_dto.py"
    description: "EMA waarden voor verschillende periodes"
```

**Verschil met oude model**:
- ❌ GEEN `requires: ['close', 'high']` (DataFrame kolommen)
- ❌ GEEN `provides: ['ema_20', 'ema_50']` (DataFrame kolommen)
- ✅ WEL `requires_dtos` en `produces_dtos` (expliciete DTOs)

### 4.2.3. Capabilities

```yaml
capabilities:
  # State persistence
  state:
    enabled: true
    state_dto: "dtos.state_dto.EMAState"
  
  # Event communication (alleen voor event-aware workers)
  events:
    enabled: true
    publishes:
      - event_name: "EMA_CROSS_DETECTED"
        description: "Published when EMAs cross"
    wirings:
      - listens_to: "SCHEDULE_TICK"
        invokes:
          method: "on_scheduled_check"
  
  # Journaling
  journaling:
    enabled: false  # Deze worker logt niet
```

---

## 4.3. Worker.py: De Twee Basisklassen

Plugin developers kiezen **expliciet** tussen twee architecturale rollen:

### StandardWorker (90% van plugins)

**Voor**: Workers in de standaard, georkestreerde pipeline.

```python
# plugins/context_workers/indicator_calculation/ema_detector/worker.py
from backend.core.base_worker import StandardWorker
from backend.core.interfaces.context_provider import ITradingContextProvider
from backend.core.interfaces.ohlcv_provider import IOhlcvProvider
from backend.shared_dtos.disposition_envelope import DispositionEnvelope
from .dtos.ema_output_dto import EMAOutputDTO

class EMADetector(StandardWorker):
    """
    ContextWorker - Indicator Calculation
    
    Berekent EMA indicatoren voor technische analyse.
    """
    
    # Type hints voor geïnjecteerde providers
    context_provider: ITradingContextProvider
    ohlcv_provider: IOhlcvProvider
    
    def __init__(self, params, **providers):
        """
        Args:
            params: Gevalideerde parameters uit schema.py
            **providers: Geïnjecteerde platform providers
        """
        super().__init__(params)
        self.context_provider = providers['context_provider']
        self.ohlcv_provider = providers['ohlcv_provider']
    
    def process(self) -> DispositionEnvelope:
        """
        Verplichte methode voor StandardWorker.
        
        Returns:
            DispositionEnvelope met flow control instructie
        """
        # 1. Haal basis context
        base_ctx = self.context_provider.get_base_context()
        
        # 2. Haal OHLCV data (Point-in-Time)
        df = self.ohlcv_provider.get_window(
            timestamp=base_ctx.timestamp,
            lookback=200
        )
        
        # 3. Bereken EMA
        ema_20 = df['close'].ewm(span=self.params.period_fast).mean().iloc[-1]
        ema_50 = df['close'].ewm(span=self.params.period_slow).mean().iloc[-1]
        
        # 4. Creëer output DTO
        result = EMAOutputDTO(
            ema_20=float(ema_20),
            ema_50=float(ema_50),
            timestamp=base_ctx.timestamp
        )
        
        # 5. Plaats in Tick Cache
        self.context_provider.set_result_dto(self, result)
        
        # 6. Continue flow
        return DispositionEnvelope(disposition="CONTINUE")
```

### EventDrivenWorker (10% van plugins)

**Voor**: Autonome workers die reageren op events.

```python
# plugins/threat_workers/external_event/news_monitor/worker.py
from backend.core.base_worker import EventDrivenWorker
from backend.shared_dtos.disposition_envelope import DispositionEnvelope
from backend.dtos.execution.critical_event import CriticalEventDTO

class NewsMonitor(EventDrivenWorker):
    """
    ThreatWorker - External Event
    
    Monitort nieuws voor high-impact events.
    GEEN process() methode - alleen event handlers.
    """
    
    context_provider: ITradingContextProvider
    state_provider: IStateProvider
    
    def __init__(self, params, **providers):
        super().__init__(params)
        self.context_provider = providers['context_provider']
        self.state_provider = providers['state_provider']
    
    def on_news(self, news_event: NewsEventDTO) -> DispositionEnvelope:
        """
        Event handler - aangeroepen bij NEWS_RECEIVED.
        
        Methode naam komt uit manifest.wirings.
        """
        # Analyseer nieuws
        if news_event.impact == "HIGH":
            # Publiceer noodsignaal
            threat = CriticalEventDTO(
                threat_id=uuid4(),
                threat_type="HIGH_IMPACT_NEWS",
                severity="CRITICAL",
                details={"headline": news_event.headline}
            )
            
            return DispositionEnvelope(
                disposition="PUBLISH",
                event_name="EMERGENCY_HALT_TRADING",
                event_payload=threat
            )
        
        # Geen bedreiging
        return DispositionEnvelope(disposition="STOP")
```

---

## 4.4. Schema.py: Parameter Validatie

Elk plugin definieert zijn configureerbare parameters via Pydantic.

```python
# plugins/context_workers/indicator_calculation/ema_detector/schema.py
from pydantic import BaseModel, Field

class EMADetectorParams(BaseModel):
    """Parameter schema voor EMA Detector."""
    
    period_fast: int = Field(
        default=20,
        ge=5,
        le=200,
        description="params.ema_detector.period_fast.desc"
    )
    
    period_slow: int = Field(
        default=50,
        ge=10,
        le=500,
        description="params.ema_detector.period_slow.desc"
    )
    
    def validate_periods(self):
        """Custom validatie: slow > fast."""
        if self.period_slow <= self.period_fast:
            raise ValueError("period_slow must be > period_fast")
```

**Gebruik in strategy_blueprint.yaml**:

```yaml
workforce:
  context_workers:
    - instance_id: "ema_main"
      plugin: "ema_detector"
      params:
        period_fast: 20
        period_slow: 50
```

---

## 4.5. DTO Definitie & Enrollment

### Lokale DTO Definitie

Plugin definieert output DTOs lokaal:

```python
# plugins/context_workers/indicator_calculation/ema_detector/dtos/ema_output_dto.py
from pydantic import BaseModel
from datetime import datetime

class EMAOutputDTO(BaseModel):
    """Output DTO voor EMA berekeningen."""
    
    ema_20: float
    ema_50: float
    ema_200: float = 0.0  # Optioneel
    timestamp: datetime
    
    class Config:
        frozen = True  # Immutable
```

### Enrollment Proces

Wanneer de plugin wordt "enrolled" via de Plugin IDE:

1. **IDE detecteert** DTOs in `dtos/` folder
2. **Platform kopieert** naar centraal register:
   ```
   backend/dto_reg/s1mple/ema_detector/v1_0_0/ema_output_dto.py
   ```
3. **Platform registreert** in DTO Registry
4. **Andere plugins** kunnen nu importeren:
   ```python
   from backend.dto_reg.s1mple.ema_detector.v1_0_0.ema_output_dto import EMAOutputDTO
   ```

### Versioning

DTOs zijn **versie-specifiek** gekoppeld aan plugin versie:

```
backend/dto_reg/s1mple/ema_detector/
├── v1_0_0/
│   └── ema_output_dto.py
├── v1_1_0/
│   └── ema_output_dto.py  # Backwards compatible wijziging
└── v2_0_0/
    └── ema_output_dto.py  # Breaking change
```

**Dependency management**: DependencyValidator checkt tijdens bootstrap of gevraagde DTO versie beschikbaar is.

---

## 4.6. Testing Requirements

### Verplichte Test Structuur

```python
# plugins/context_workers/indicator_calculation/ema_detector/tests/test_worker.py
import pytest
from unittest.mock import MagicMock
from ..worker import EMADetector
from ..dtos.ema_output_dto import EMAOutputDTO
from backend.shared_dtos.disposition_envelope import DispositionEnvelope

@pytest.fixture
def mock_providers():
    """Mock all required providers."""
    
    # Mock context provider
    context_provider = MagicMock()
    context_provider.get_base_context.return_value = BaseContextDTO(
        timestamp=datetime(2024, 1, 1, 10, 0),
        current_price=50000.0
    )
    
    # Mock OHLCV provider
    ohlcv_provider = MagicMock()
    ohlcv_provider.get_window.return_value = create_test_dataframe()
    
    return {
        'context_provider': context_provider,
        'ohlcv_provider': ohlcv_provider
    }

def test_ema_detector_calculates_correctly(mock_providers):
    """Test EMA calculation logic."""
    
    # Arrange
    params = {'period_fast': 20, 'period_slow': 50}
    worker = EMADetector(params, **mock_providers)
    
    # Act
    result = worker.process()
    
    # Assert
    assert isinstance(result, DispositionEnvelope)
    assert result.disposition == "CONTINUE"
    
    # Verify DTO was placed in cache
    mock_providers['context_provider'].set_result_dto.assert_called_once()
    call_args = mock_providers['context_provider'].set_result_dto.call_args
    
    produced_dto = call_args[0][1]
    assert isinstance(produced_dto, EMAOutputDTO)
    assert produced_dto.ema_20 > 0
    assert produced_dto.ema_50 > 0
    assert produced_dto.ema_50 > produced_dto.ema_20  # Slow > Fast

def test_ema_detector_respects_point_in_time(mock_providers):
    """Test that worker requests data with correct timestamp."""
    
    # Arrange
    params = {'period_fast': 20, 'period_slow': 50}
    worker = EMADetector(params, **mock_providers)
    
    # Act
    worker.process()
    
    # Assert - check OHLCV was requested with correct timestamp
    mock_providers['ohlcv_provider'].get_window.assert_called_once()
    call_kwargs = mock_providers['ohlcv_provider'].get_window.call_args[1]
    
    assert 'timestamp' in call_kwargs
    assert call_kwargs['timestamp'] == datetime(2024, 1, 1, 10, 0)
```

**Test Coverage Requirements**:
- ✅ Happy path (normale werking)
- ✅ Edge cases (lege data, extreme waarden)
- ✅ Parameter validatie
- ✅ DTO structuur validatie
- ✅ Point-in-Time correctheid
- ✅ Provider interactie

---

## 4.7. Plugin Development Checklist

### Minimale Plugin (Pure ContextWorker)

```
☐ Creëer plugin directory structuur
☐ Schrijf manifest.yaml
  ☐ identification (type, subtype)
  ☐ requires_capability
  ☐ produces_dtos
☐ Schrijf schema.py (parameter model)
☐ Schrijf worker.py
  ☐ Inherit van StandardWorker
  ☐ Implementeer process() methode
  ☐ Gebruik providers via self.<provider>
  ☐ Return DispositionEnvelope
☐ Definieer output DTO in dtos/
☐ Schrijf tests/test_worker.py
  ☐ Test met gemockte providers
  ☐ Verify DTO output
  ☐ Verify Point-in-Time
☐ Run pytest - 100% pass vereist
```

### Event-Aware Plugin (Toegevoegd)

```
☐ Alle stappen van minimale plugin
☐ Plus:
  ☐ Inherit van EventDrivenWorker
  ☐ manifest.capabilities.events.enabled = true
  ☐ Declareer publishes in manifest
  ☐ Declareer wirings in manifest
  ☐ Implementeer event handler methoden
  ☐ Test event publicatie
  ☐ Test event ontvangst
```

---

## 4.8. Complete Plugin Voorbeeld

### Manifest

```yaml
# plugins/opportunity_workers/technical_pattern/ema_cross_detector/manifest.yaml
identification:
  name: "ema_cross_detector"
  display_name: "EMA Cross Detector"
  type: "opportunity_worker"
  subtype: "technical_pattern"
  version: "1.0.0"
  description: "Detecteert EMA kruisingen als entry signalen"
  author: "Trading Team"

requires_capability:
  - "state_persistence"  # Voor het bijhouden van vorige waarden

requires_dtos:
  - dto_type: "EMAOutputDTO"
    expected_path: "backend.dto_reg.s1mple.ema_detector.v1_0_0.ema_output_dto"

produces_dtos: []  # Geen intermediaire DTOs

capabilities:
  state:
    enabled: true
    state_dto: "dtos.cross_state_dto.CrossStateDTO"
  
  events:
    enabled: false  # Geen custom events
  
  journaling:
    enabled: false
```

### Schema

```python
# schema.py
from pydantic import BaseModel, Field

class EMACrossDetectorParams(BaseModel):
    """Parameters voor EMA Cross Detector."""
    
    min_separation: float = Field(
        default=0.001,
        ge=0.0,
        le=0.1,
        description="params.ema_cross.min_separation.desc"
    )
    
    require_volume_confirmation: bool = Field(
        default=True,
        description="params.ema_cross.require_volume.desc"
    )
```

### State DTO

```python
# dtos/cross_state_dto.py
from pydantic import BaseModel

class CrossStateDTO(BaseModel):
    """Interne state voor cross detectie."""
    
    last_ema_20: float = 0.0
    last_ema_50: float = 0.0
    last_cross_type: str = ""  # 'bullish' of 'bearish'
```

### Worker Implementatie

```python
# worker.py
from backend.core.base_worker import StandardWorker
from backend.dtos.pipeline.signal import OpportunitySignalDTO
from backend.shared_dtos.disposition_envelope import DispositionEnvelope
from backend.dto_reg.s1mple.ema_detector.v1_0_0.ema_output_dto import EMAOutputDTO
from .schema import EMACrossDetectorParams
from .dtos.cross_state_dto import CrossStateDTO

class EMACrossDetector(StandardWorker):
    """Detecteert EMA kruisingen."""
    
    params: EMACrossDetectorParams
    context_provider: ITradingContextProvider
    state_provider: IStateProvider
    
    def process(self) -> DispositionEnvelope:
        """Detecteer EMA cross."""
        
        # 1. Haal basis context
        base_ctx = self.context_provider.get_base_context()
        
        # 2. Haal required DTOs uit cache
        required_dtos = self.context_provider.get_required_dtos(self)
        ema_dto = required_dtos[EMAOutputDTO]
        
        # 3. Haal vorige state
        state = self.state_provider.get() or CrossStateDTO()
        
        # 4. Detecteer cross
        cross_detected = False
        cross_type = ""
        
        if state.last_ema_20 > 0:  # Niet eerste run
            # Bullish cross: fast kruist boven slow
            if (state.last_ema_20 < state.last_ema_50 and 
                ema_dto.ema_20 > ema_dto.ema_50):
                
                separation = abs(ema_dto.ema_20 - ema_dto.ema_50) / ema_dto.ema_50
                if separation >= self.params.min_separation:
                    cross_detected = True
                    cross_type = "bullish"
            
            # Bearish cross: fast kruist onder slow
            elif (state.last_ema_20 > state.last_ema_50 and 
                  ema_dto.ema_20 < ema_dto.ema_50):
                
                separation = abs(ema_dto.ema_20 - ema_dto.ema_50) / ema_dto.ema_50
                if separation >= self.params.min_separation:
                    cross_detected = True
                    cross_type = "bearish"
        
        # 5. Update state
        state.last_ema_20 = ema_dto.ema_20
        state.last_ema_50 = ema_dto.ema_50
        state.last_cross_type = cross_type
        self.state_provider.set(state)
        
        # 6. Publiceer indien cross gedetecteerd
        if cross_detected:
            signal = OpportunitySignalDTO(
                opportunity_id=uuid4(),
                timestamp=base_ctx.timestamp,
                asset=base_ctx.asset_pair,
                signal_type=f"ema_cross_{cross_type}",
                confidence=0.75,
                metadata={
                    'ema_20': ema_dto.ema_20,
                    'ema_50': ema_dto.ema_50,
                    'separation': separation
                }
            )
            
            return DispositionEnvelope(
                disposition="PUBLISH",
                event_name="SIGNAL_GENERATED",
                event_payload=signal
            )
        
        # Geen cross
        return DispositionEnvelope(disposition="STOP")
```

### Test

```python
# tests/test_worker.py
from unittest.mock import MagicMock
from ..worker import EMACrossDetector
from ..dtos.cross_state_dto import CrossStateDTO
from backend.dto_reg.s1mple.ema_detector.v1_0_0.ema_output_dto import EMAOutputDTO

def test_detects_bullish_cross():
    """Test bullish EMA cross detection."""
    
    # Mock providers
    context_provider = MagicMock()
    context_provider.get_base_context.return_value = BaseContextDTO(
        timestamp=datetime.now(),
        current_price=50000.0
    )
    context_provider.get_required_dtos.return_value = {
        EMAOutputDTO: EMAOutputDTO(
            ema_20=50100.0,  # Fast boven slow
            ema_50=50000.0,
            timestamp=datetime.now()
        )
    }
    
    state_provider = MagicMock()
    # Vorige state: fast onder slow
    state_provider.get.return_value = CrossStateDTO(
        last_ema_20=49900.0,
        last_ema_50=50000.0,
        last_cross_type=""
    )
    
    # Test
    worker = EMACrossDetector(
        params={'min_separation': 0.001},
        context_provider=context_provider,
        state_provider=state_provider
    )
    
    result = worker.process()
    
    # Verify
    assert result.disposition == "PUBLISH"
    assert result.event_name == "SIGNAL_GENERATED"
    assert result.event_payload.signal_type == "ema_cross_bullish"
    
    # Verify state updated
    state_provider.set.assert_called_once()
```

---

## 4.9. Plugin Categorieën & Sub-Types

Elke plugin behoort tot één van de **5 hoofdcategorieën** en één van de **27 sub-types**:

### ContextWorker (7 sub-types)

| Sub-Type | Doel | Voorbeelden |
|----------|------|-------------|
| `regime_classification` | Markt regime bepalen | ADX filter, Volatility regime |
| `structural_analysis` | Technische structuren | Market structure, Liquidity zones |
| `indicator_calculation` | Indicatoren berekenen | EMA, RSI, ATR, MACD |
| `microstructure_analysis` | Orderbook analyse | Imbalance detector |
| `temporal_context` | Tijd-gebaseerde context | Session analyzer, Killzones |
| `sentiment_enrichment` | Sentiment data | News sentiment, Fear & Greed |
| `fundamental_enrichment` | Fundamentele data | On-chain metrics, Earnings |

### OpportunityWorker (7 sub-types)

| Sub-Type | Doel | Voorbeelden |
|----------|------|-------------|
| `technical_pattern` | Patroonherkenning | FVG, Breakouts, Divergences |
| `momentum_signal` | Momentum signalen | Trend continuation |
| `mean_reversion` | Mean reversion | Oversold bounce |
| `statistical_arbitrage` | Arbitrage | Pair trading |
| `event_driven` | Nieuws-gebaseerd | News reactions |
| `sentiment_signal` | Sentiment extremen | Fear/Greed signals |
| `ml_prediction` | ML voorspellingen | Model predictions |

### ThreatWorker (5 sub-types)

| Sub-Type | Doel | Voorbeelden |
|----------|------|-------------|
| `portfolio_risk` | Portfolio risico | Max drawdown, Exposure |
| `market_risk` | Markt risico | Volatility spikes, Liquidity |
| `system_health` | Systeem gezondheid | Connection monitor |
| `strategy_performance` | Performance monitoring | Win rate degradation |
| `external_event` | Externe events | Breaking news |

### PlanningWorker (4 sub-types)

| Sub-Type | Doel | Voorbeelden |
|----------|------|-------------|
| `entry_planning` | Entry bepalen | Limit entry, Market entry |
| `exit_planning` | Stops/targets bepalen | Liquidity targets, ATR stops |
| `size_planning` | Position sizing | Fixed risk, Kelly criterion |
| `order_routing` | Order routing | Limit router, Iceberg |

### ExecutionWorker (4 sub-types)

| Sub-Type | Doel | Voorbeelden |
|----------|------|-------------|
| `trade_initiation` | Trades initiëren | Plan executor |
| `position_management` | Posities beheren | Trailing stops, Profit taker |
| `risk_safety` | Noodmaatregelen | Emergency exit, Circuit breaker |
| `operational` | Geplande taken | DCA executor, Rebalancer |

---

## 4.10. Best Practices

### DO's ✅

- **Expliciet declareren**: Alle data dependencies in manifest
- **Type-safe**: Gebruik DTOs voor alle data
- **Point-in-Time**: Request data altijd met timestamp
- **Immutable DTOs**: Gebruik `frozen=True` in Config
- **Test providers**: Mock alle providers in tests
- **Validate params**: Gebruik Pydantic validators
- **Document DTOs**: Duidelijke docstrings

### DON'Ts ❌

- **Geen globals**: Nooit globale state
- **Geen side-effects**: Alleen via providers
- **Geen hardcoded paths**: Gebruik centraal DTO register
- **Geen primitives in cache**: Altijd DTOs
- **Geen toekomst data**: Respecteer Point-in-Time
- **Geen EventBus direct**: Alleen via DispositionEnvelope
- **Geen tests skippen**: 100% coverage vereist

---

**Einde Hoofdstuk 4**

Dit hoofdstuk beschrijft de complete anatomie van een plugin in de nieuwe architectuur, met focus op DTO-centric data flow, expliciete contracten en maximale testbaarheid.