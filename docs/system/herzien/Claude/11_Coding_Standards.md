# Hoofdstuk 11: Coding Standards & Design Principles

**Status:** Definitief  
**Versie:** 4.0

---

## 11.1. Code Kwaliteit

### PEP 8 Compliance

- **Regellengte**: Maximum 100 karakters
- **Naamgeving**: 
  - `snake_case` voor functies, variabelen, modules
  - `PascalCase` voor classes
  - `UPPER_CASE` voor constanten
- **Type Hinting**: Verplicht voor alle functies en variabelen
- **Docstrings**: Google Style, Engels

### Imports Structuur

```python
# backend/core/strategy_journal.py
"""
Append-only causal log of all events.

@layer: Backend (Core)
@dependencies: [backend.core.interfaces, backend.dtos.state]
"""

# 1. Standard Library
from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID

# 2. Third-Party
from pydantic import BaseModel

# 3. Our Application (absolute paths from project root)
from backend.core.interfaces.persistors import IJournalPersistor
from backend.dtos.state.journal_entry import JournalEntry
```

---

## 11.2. Contract-Gedreven Ontwikkeling

### Pydantic voor Alle Data

**Regel**: Alle data tussen componenten = Pydantic BaseModel

```python
# ✅ GOED: Type-safe DTO
class EMAOutputDTO(BaseModel):
    ema_20: float
    ema_50: float
    timestamp: datetime

# ❌ FOUT: Primitieve dict
result = {'ema_20': 50.0, 'ema_50': 49.0}
```

### Interface-Based Dependencies

**Regel**: Dependency op abstractie, niet concrete implementatie

```python
# ✅ GOED: Interface dependency
class MyWorker(StandardWorker):
    context_provider: ITradingContextProvider  # Interface
    state_provider: IStateProvider

# ❌ FOUT: Concrete dependency
class BadWorker(StandardWorker):
    context_provider: TradingContextProvider  # Concrete class
```

---

## 11.3. Dependency Injection

### Constructor Injection (Standaard)

```python
# ✅ GOED: Constructor injection
class EMADetector(StandardWorker):
    def __init__(self, params, **providers):
        super().__init__(params)
        self.context_provider = providers['context_provider']
        self.ohlcv_provider = providers['ohlcv_provider']

# ❌ FOUT: Property setters
class BadWorker(StandardWorker):
    def __init__(self, params):
        self.context_provider = None  # Wordt later gezet
    
    def set_context_provider(self, provider):
        self.context_provider = provider
```

### Factory Pattern

**Regel**: Complexe objecten via factories, niet direct constructors

```python
# ✅ GOED: Via factory
worker = worker_factory.build_from_spec(worker_spec)

# ❌ FOUT: Direct instantiëren
worker = EMADetector(params)
worker.context_provider = ...  # Manual wiring
```

---

## 11.4. DTO Best Practices

### Immutability

```python
# ✅ GOED: Frozen DTO
class EMAOutputDTO(BaseModel):
    ema_20: float
    ema_50: float
    
    class Config:
        frozen = True  # Immutable

# ❌ FOUT: Mutable DTO
class BadDTO(BaseModel):
    value: float  # Kan gewijzigd worden
```

### Validation

```python
# ✅ GOED: Field validation
class MyParams(BaseModel):
    period: int = Field(
        ...,
        ge=5,
        le=200,
        description="params.my_worker.period.desc"
    )
    
    @validator('period')
    def validate_period(cls, v):
        if v % 2 == 0:
            raise ValueError("Period must be odd")
        return v

# ❌ FOUT: Geen validatie
class BadParams(BaseModel):
    period: int  # Geen grenzen, geen checks
```

---

## 11.5. Point-in-Time Principe

### Provider Gebruik

```python
# ✅ GOED: Respecteert timestamp
class MyWorker(StandardWorker):
    def process(self):
        base_ctx = self.context_provider.get_base_context()
        
        # ALTIJD timestamp meegeven
        df = self.ohlcv_provider.get_window(
            timestamp=base_ctx.timestamp,  # Point-in-Time!
            lookback=200
        )

# ❌ FOUT: Geen timestamp
class BadWorker(StandardWorker):
    def process(self):
        df = self.ohlcv_provider.get_latest()  # Lekkage!
```

### State Access

```python
# ✅ GOED: Via provider
class MyWorker(StandardWorker):
    def process(self):
        state = self.state_provider.get()
        state['counter'] = state.get('counter', 0) + 1
        self.state_provider.set(state)

# ❌ FOUT: Direct attribuut
class BadWorker(StandardWorker):
    def process(self):
        self.counter += 1  # Niet persistent!
```

---

## 11.6. DispositionEnvelope Patterns

### CONTINUE Pattern

```python
# ✅ GOED: Data in cache, continue flow
def process(self):
    result_dto = self._calculate()
    self.context_provider.set_result_dto(self, result_dto)
    return DispositionEnvelope(disposition="CONTINUE")
```

### PUBLISH Pattern

```python
# ✅ GOED: Publiceer signaal
def process(self):
    if self._condition_met():
        signal = OpportunitySignalDTO(...)
        return DispositionEnvelope(
            disposition="PUBLISH",
            event_name="SIGNAL_GENERATED",
            event_payload=signal
        )
    return DispositionEnvelope(disposition="STOP")
```

### STOP Pattern

```python
# ✅ GOED: Geen output, stop flow
def process(self):
    if not self._should_continue():
        return DispositionEnvelope(disposition="STOP")
```

---

## 11.7. Testing Standards

### Test Coverage

**Regel**: 100% test coverage vereist voor enrollment

```python
# tests/test_worker.py
def test_happy_path():
    """Test normale werking."""
    pass

def test_edge_cases():
    """Test edge cases."""
    pass

def test_error_handling():
    """Test error scenarios."""
    pass

def test_point_in_time():
    """Test timestamp correctheid."""
    pass
```

### Mock Providers

```python
# ✅ GOED: Mock alle providers
from unittest.mock import MagicMock

@pytest.fixture
def mock_providers():
    context_provider = MagicMock(spec=ITradingContextProvider)
    context_provider.get_base_context.return_value = BaseContextDTO(...)
    
    ohlcv_provider = MagicMock(spec=IOhlcvProvider)
    ohlcv_provider.get_window.return_value = test_dataframe()
    
    return {
        'context_provider': context_provider,
        'ohlcv_provider': ohlcv_provider
    }

def test_worker(mock_providers):
    worker = MyWorker(params, **mock_providers)
    result = worker.process()
    
    # Verify provider calls
    mock_providers['context_provider'].set_result_dto.assert_called_once()
```

---

## 11.8. Internationalisatie (i18n)

### Translation Keys

**Regel**: Alle user-facing tekst via translation keys

```python
# ✅ GOED: Translation key
description = Field(
    ...,
    description="params.ema_detector.period.desc"
)

# ❌ FOUT: Hardcoded tekst
description = Field(
    ...,
    description="The EMA period in bars"
)
```

### Structuur

```yaml
# locales/nl.yaml
params:
  ema_detector:
    period:
      desc: "De EMA periode in bars"

# locales/en.yaml  
params:
  ema_detector:
    period:
      desc: "The EMA period in bars"
```

---

## 11.9. Error Handling

### Fail Fast Principe

```python
# ✅ GOED: Fail tijdens bootstrap
def validate_config(config):
    if not config.is_valid():
        raise ConfigurationError("Invalid config")
    # Continue alleen als valid

# ❌ FOUT: Silent failures
def bad_validate(config):
    if not config.is_valid():
        logger.warning("Config might be invalid")
        # Gaat toch door!
```

### Informative Errors

```python
# ✅ GOED: Duidelijke error
raise MissingDTOError(
    f"Worker '{self.instance_id}' requires DTOs of type "
    f"{required_types} but only {available_types} available in cache"
)

# ❌ FOUT: Vage error
raise ValueError("Missing data")
```

---

## 11.10. SOLID Principles

### Single Responsibility

```python
# ✅ GOED: Eén verantwoordelijkheid
class ConfigTranslator:
    """Vertaalt YAML naar BuildSpecs."""
    def collect_build_specs(self, ...): pass

class WorkerFactory:
    """Bouwt workers uit specs."""
    def build_from_spec(self, ...): pass

# ❌ FOUT: Meerdere verantwoordelijkheden
class BadService:
    """Laadt config EN bouwt workers EN start execution."""
    pass
```

### Dependency Inversion

```python
# ✅ GOED: Hang af van abstractie
class MyWorker:
    def __init__(self, provider: IStateProvider):  # Interface
        self._provider = provider

# ❌ FOUT: Hang af van concrete class
class BadWorker:
    def __init__(self, provider: JsonStatePersistor):  # Concrete
        self._provider = provider
```

---

## 11.11. Naamgevingsconventies

### Interfaces

```python
# ✅ GOED: I prefix
class ITradingContextProvider(Protocol): pass
class IStateProvider(Protocol): pass

# ❌ FOUT: Geen I prefix
class TradingContextProvider(Protocol): pass
```

### Factories

```python
# ✅ GOED: Factory suffix
class WorkerFactory: pass
class PersistorFactory: pass

# ❌ FOUT: Onduidelijke naam
class WorkerBuilder: pass  # Is dit een builder of factory?
```

### Private Members

```python
# ✅ GOED: _ prefix voor internal
class MyClass:
    def __init__(self):
        self._internal_state = {}  # Private
        self.public_api = None     # Public
    
    def _internal_method(self): pass  # Private
    def public_method(self): pass      # Public
```

---

## 11.12. Documentation Standards

### Docstrings

```python
# ✅ GOED: Complete docstring
def process(self, context: TradingContext) -> DispositionEnvelope:
    """
    Process trading context and detect opportunities.
    
    Args:
        context: Current trading context with timestamp
    
    Returns:
        DispositionEnvelope with flow control instruction
    
    Raises:
        MissingDataError: If required DTOs not in cache
    """
    pass
```

### File Headers

```python
# backend/core/strategy_journal.py
"""
Append-only causal log of all events.

@layer: Backend (Core)
@dependencies: [backend.core.interfaces, backend.dtos.state]
@responsibilities:
    - Manages immutable historical log
    - Contains opportunities, threats, trades with causal links
    - Uses IJournalPersistor for persistence
"""
```

---

## 11.13. Quick Reference Checklist

### Voor Elke Plugin

- [ ] Manifest.yaml compleet (type, subtype, dependencies, capabilities)
- [ ] Schema.py met parameter validatie
- [ ] Worker.py met type hints en docstrings
- [ ] DTOs immutable (frozen=True)
- [ ] Providers via constructor injection
- [ ] DispositionEnvelope correct gebruikt
- [ ] Point-in-Time principe gerespecteerd
- [ ] Tests met 100% coverage
- [ ] Translation keys voor alle user-facing tekst
- [ ] Error messages informatief

### Voor Elke Factory

- [ ] Eén verantwoordelijkheid (SRP)
- [ ] build_from_spec() methode
- [ ] Dependencies via constructor
- [ ] Geen business logica
- [ ] Complete error handling

### Voor Elke DTO

- [ ] Pydantic BaseModel
- [ ] frozen=True (indien mogelijk)
- [ ] Field validatie waar nodig
- [ ] Duidelijke docstring
- [ ] Translation keys in descriptions

---

**Einde Hoofdstuk 11**

Dit hoofdstuk beschrijft de coding standards zonder verwijzingen naar het oude Operator model, volledig gericht op de nieuwe platgeslagen, DTO-centric architectuur.