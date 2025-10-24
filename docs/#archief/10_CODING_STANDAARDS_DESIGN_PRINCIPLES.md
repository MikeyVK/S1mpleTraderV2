# **10. Coding Standaarden & Design Principles**

**Status:** Definitief
Dit document beschrijft de verplichte standaarden en best practices voor het schrijven van alle code binnen het S1mpleTrader-project.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Code Kwaliteit & Stijl](#101-code-kwaliteit--stijl)
3. [Contract-Gedreven Ontwikkeling](#102-contract-gedreven-ontwikkeling)
4. [Dependency Injection Principes](#103-dependency-injection-principes)
5. [Configuratie-Gedreven Design](#104-configuratie-gedreven-design)
6. [Gelaagde Logging & Traceability](#105-gelaagde-logging--traceability)
7. [Testen als Voorwaarde](#106-testen-als-voorwaarde)
8. [Overige Standaarden](#107-overige-standaarden)
9. [Design Principles & Kernconcepten](#108-design-principles--kernconcepten)

---

## **Executive Summary**

Dit document legt de fundering voor een consistente, leesbare, onderhoudbare en robuuste codebase voor S1mpleTrader. Het naleven van deze standaarden is niet optioneel en is cruciaal voor het succes van het project.

### **🎯 Kernprincipes**

**1. Strikte Code Kwaliteit en Stijl**
-   Alle code is **PEP 8 compliant** met een maximale regellengte van 100 tekens.
-   **Volledige type hinting** is verplicht.
-   **Engelse docstrings** in Google Style zijn de standaard voor alle bestanden, klassen en functies.

**2. Contract-Gedreven Ontwikkeling**
-   Alle data die tussen componenten wordt uitgewisseld, wordt ingekapseld in **Pydantic BaseModels**.
-   Uitwisselbare componenten erven van **abstracte basisklassen (Interfaces)**.

**3. Dependency Injection als Kernpatroon**
-   **Constructor Injection** is de standaard voor alle dependencies.
-   Componenten zijn afhankelijk van **abstracties (interfaces)**, niet van concrete implementaties.
-   Een **Gecentraliseerd Factory Model** (`PersistorFactory`, `EventAdapterFactory`, `OperatorFactory`) beheert de creatie van complexe objecten.

**4. Scheiding van ROL en CAPABILITIES**
-   De **ROL** van een worker (zijn architecturale doel) wordt bepaald door de keuze van de basisklasse (`StandardWorker` of `EventDrivenWorker`).
-   De **CAPABILITIES** (extra vaardigheden zoals `state` en `events`) worden expliciet aangevraagd in het `manifest.yaml` en dynamisch geïnjecteerd.

**5. Configuratie-Gedreven Design**
-   Het principe **"YAML is intelligentie, code is mechanica"** is leidend. Het gedrag van het systeem, met name van de operators, wordt gedefinieerd in configuratie (`operators.yaml`), niet in de code.

### **🔑 Design Patterns**

-   **SOLID**: De principes van Single Responsibility, Open/Closed, Dependency Inversion, etc., worden strikt toegepast.
-   **Factory Pattern**: Voor het creëren van complexe, geconfigureerde objecten.
-   **Adapter Pattern**: Om plugins "bus-agnostisch" te maken.
-   **CQRS (Command Query Responsibility Segregation)**: Een strikte scheiding tussen operaties die data lezen (Queries) en operaties die de staat veranderen (Commands).

---

## **10.1. Code Kwaliteit & Stijl**

### **10.1.1. Fundamenten**

*   **PEP 8 Compliant:** Alle Python-code moet strikt voldoen aan de [PEP 8](https://peps.python.org/pep-0008/) stijlgids. Een linter wordt gebruikt om dit te handhaven.
    *   **Regellengte:** Maximaal 100 tekens.
    *   **Naamgeving:** snake\_case voor variabelen, functies en modules; PascalCase voor klassen.
*   **Volledige Type Hinting:** Alle functies, methodes, en variabelen moeten volledig en correct getypeerd zijn. We streven naar een 100% getypeerde codebase om runtime-fouten te minimaliseren.
*   **Commentaar in het Engels:** Al het commentaar in de code (\# ...) en docstrings moeten in het Engels zijn voor universele leesbaarheid en onderhoudbaarheid.

### **10.1.2. Gestructureerde Docstrings**

Elk bestand, elke klasse en elke functie moet een duidelijke docstring hebben.

*   **Bestands-Header Docstring:** Elk .py-bestand begint met een gestandaardiseerde header die de inhoud en de plaats in de architectuur beschrijft.
    ```python
    # backend/assembly/component_builder.py  
    """  
    Contains the ComponentBuilder, responsible for assembling and instantiating  
    all required Operator and Worker components for a given strategy_link.

    @layer: Backend (Assembly)  
    @dependencies: [PyYAML, Pydantic]  
    @responsibilities:  
        - Reads the strategy_blueprint.yaml.  
        - Validates the workforce configuration.  
        - Instantiates all required plugin workers and operators.  
    """
    ```

*   **Imports:** Alle imports staan bovenaan het bestand. Het is van belang dat deze in de juiste volgorde staan. We zullen hiervoor ten alle tijden een onderverdeling gebruiken in de volgende drie groepen en volgorde:
    *   **1. Standard Library Imports**
    *   **2. Third-Party Imports**
    *   **3. Our Application Imports**
        Alle imports zullen absoluut zijn en opbouwen vanaf de project root.

Indien mogelijk worden imports gegroepeerd om lange regels te voorkomen en te blijven voldoen aan de PEP 8.

*   **Functie & Methode Docstrings (Google Style):** Voor alle functies en methodes hanteren we de **Google Style Python Docstrings**. Dit is een leesbare en gestructureerde manier om parameters, return-waarden en voorbeelden te documenteren.
    ```python
    def process_data(df: pd.DataFrame, length: int = 14) -> pd.DataFrame:  
        """Calculates an indicator and adds it as a new column.

        Args:  
            df (pd.DataFrame): The input DataFrame with OHLCV data.  
            length (int, optional): The lookback period for the indicator.  
                Defaults to 14.

        Returns:  
            pd.DataFrame: The DataFrame with the new indicator column added.  
        """  
        # ... function logic ...  
        return df
    ```

### **10.1.3. Naamgevingsconventies**

Naast de algemene [PEP 8]-richtlijnen hanteren we een aantal strikte, aanvullende conventies om de leesbaarheid en de architectonische zuiverheid van de code te vergroten.

*   **Interfaces (Contracten):**
    *   **Principe:** Elke abstracte klasse (ABC) of Protocol die een contract definieert, moet worden voorafgegaan door een hoofdletter I.
    *   **Doel:** Dit maakt een onmiddellijk en ondubbelzinnig onderscheid tussen een abstract contract en een concrete implementatie.
    *   Voorbeeld:
        ```python
        # Het contract (de abstractie)  
        class IAPIConnector(Protocol):
            ...  
        # De concrete implementatie  
        class KrakenAPIConnector(IAPIConnector):
            ...  
        ```

*   **Interne Attributen en Methodes:**
    *   **Principe:** Attributen of methodes die niet bedoeld zijn voor gebruik buiten de klasse, moeten worden voorafgegaan door een enkele underscore (\_).
    *   **Doel:** Dit communiceert duidelijk de publieke API van een klasse.
    *   Voorbeeld:
        ```python
        class AnalysisOperator:  
            def __init__(self):  
                self._app_config = ... # Intern  
            def run_pipeline(self): # Publiek  
                self._prepare_workers() # Intern

            def _prepare_workers(self):  
                ...  
        ```

## **10.2. Contract-Gedreven Ontwikkeling**

### **10.2.1. Pydantic voor alle Data-Structuren**

*   **Principe:** Alle data die tussen componenten wordt doorgegeven, moet worden ingekapseld in een **Pydantic BaseModel**. Dit geldt voor DTO's, configuraties en plugin-parameters.
*   **Voordeel:** Dit garandeert dat data van het juiste type en de juiste structuur is *voordat* het wordt verwerkt.

### **10.2.2. Abstracte Basisklassen (Interfaces)**

*   **Principe:** Componenten die uitwisselbaar moeten zijn (zoals plugins), moeten erven van een gemeenschappelijke abstracte basisklasse (ABC) die een consistent contract afdwingt.

## **10.3. Dependency Injection Principes** ⭐

De S1mpleTrader-architectuur is gebouwd op strikte dependency injection principes om testbaarheid, flexibiliteit en onderhoudbaarheid te maximaliseren.

### **10.3.1. Constructor Injection als Standaard**

Alle dependencies worden geïnjecteerd via de constructor, nooit via property setters of method parameters.

**Goed voorbeeld:**
```python
# backend/core/operators/base_operator.py
class BaseOperator:
    """Operator met geïnjecteerde dependencies."""
    
    def __init__(
        self,
        config: OperatorConfig,
        component_builder: ComponentBuilder,
        event_bus: EventBus,
        persistor_factory: PersistorFactory
    ):
        self.config = config
        self._component_builder = component_builder
        self._event_bus = event_bus
        self._persistor_factory = persistor_factory
```

**Slecht voorbeeld:**
```python
# ❌ NIET DOEN: Dependencies via properties
class BadOperator:
    def __init__(self, config: OperatorConfig):
        self.config = config
        self.event_bus = None  # ❌ Wordt later gezet
    
    def set_event_bus(self, bus: EventBus):  # ❌ Setter pattern
        self.event_bus = bus
```

### **10.3.2. ROL-definitie en Capability-injectie**

Componenten hangen af van abstracties ([`IStatePersistor`](../../backend/core/interfaces/persistors.py:IStatePersistor), [`IJournalPersistor`](../../backend/core/interfaces/persistors.py:IJournalPersistor), [`IEventHandler`](../../backend/core/interfaces/event_handler.py:IEventHandler)), niet van concrete implementaties. De architectuur scheidt de **ROL** van een worker (hoe deze wordt aangeroepen) van zijn **CAPABILITIES** (extra vaardigheden).

1.  **De ROL wordt bepaald door de basisklasse:**
    *   `StandardWorker`: Doet mee aan de georkestreerde pijplijn en implementeert de `process()` methode.
    *   `EventDrivenWorker`: Reageert autonoom op events van de EventBus.

2.  **CAPABILITIES worden aangevraagd in het manifest en geïnjecteerd door de `WorkerBuilder`.**

Een worker vraagt een capability aan, en de `WorkerBuilder` injecteert de benodigde dependency (die een interface implementeert) in de constructor.

**Voorbeeld: Worker die State en Event-capabilities aanvraagt**

Een worker kan zowel een `StandardWorker` zijn als stateful en event-aware willen zijn. Hij erft alleen van `StandardWorker` en de rest wordt geconfigureerd.

**`manifest.yaml`**
```yaml
# manifest.yaml
name: "MyStatefulEventfulWorker"
# ...
capabilities:
  state:
    enabled: true
    state_dto: "dtos.state_dto.MyState"
  events:
    enabled: true # Let op: dit is een StandardWorker die OOK events kan publishen
    publishes:
      - as_event: "MyWorkDoneEvent"
```
**`worker.py` (De implementatie is nu heel schoon)**
```python
# plugins/my_worker/worker.py
from backend.core.base_worker import StandardWorker
from backend.core.interfaces.persistors import IStatePersistor
from backend.core.interfaces.event_handler import IEventHandler

class MyStatefulEventfulWorker(StandardWorker):
    """
    Worker met state en event capabilities, geïnjecteerd via de constructor.
    De ROL (StandardWorker) is gedefinieerd door de klasse.
    De CAPABILITIES (state, events) zijn geconfigureerd in het manifest.
    """
    def __init__(
        self,
        params: Any,
        state_persistor: IStatePersistor,  # ← Geïnjecteerd door WorkerBuilder
        event_handler: IEventHandler      # ← Geïnjecteerd door WorkerBuilder
    ):
        super().__init__(params)
        self._state_persistor = state_persistor
        self._event_handler = event_handler
        self._state = state_persistor.load()

    def process(self, context: Any, **kwargs) -> Any:
        # Doe werk...
        self._state.counter += 1
        self.commit_state()
        self.emit("MyWorkDoneEvent", {"counter": self._state.counter})
        return context

    def commit_state(self) -> None:
        """Schrijft de state weg via de geïnjecteerde persistor."""
        self._state_persistor.save_atomic(self._state)

    def emit(self, event_name: str, payload: Any) -> None:
        """Publiceert een event via de geïnjecteerde handler."""
        self._event_handler.publish(event_name, payload)
```

### **10.3.3. Gecentraliseerd Factory Model voor Complexe Objecten**

Complexe object-constructie gebeurt via **gespecialiseerde, gecentraliseerde factories**. Elke factory heeft één enkele verantwoordelijkheid. Andere componenten (zoals de `WorkerBuilder`) worden "klanten" van deze factories en bevatten zelf geen bouwlogica meer.

*   `PersistorFactory`: De **enige** bron voor het creëren van `IStatePersistor` en `IJournalPersistor` instanties.
*   `EventAdapterFactory`: De **enige** bron voor het creëren van `IEventHandler` (EventAdapter) instanties.
*   `OperatorFactory`: Creëert `BaseOperator` instanties op basis van configuratie.

**EventAdapterFactory Voorbeeld:**
```python
# backend/assembly/event_adapter_factory.py
from backend.core.interfaces.event_handler import IEventHandler
from backend.core.event_bus import EventBus
from .plugin_event_adapter import PluginEventAdapter

class EventAdapterFactory:
    """
    Gespecialiseerde factory voor het creëren van event adapters.
    Dit is de enige plek die weet hoe een IEventHandler wordt gebouwd.
    """
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    def create_event_handler_for_component(
        self,
        target_component: Any,
        wiring_instructions: List[WiringInstruction]
    ) -> IEventHandler:
        """Creëert en configureert een adapter voor een specifieke component."""
        adapter = PluginEventAdapter(
            event_bus=self._event_bus,
            target_component=target_component
        )
        adapter.apply_wirings(wiring_instructions)
        return adapter
```
**OperatorFactory Voorbeeld (Klant van andere componenten):**
```python
# backend/assembly/operator_factory.py
from backend.core.operators.base_operator import BaseOperator

class OperatorFactory:
    """Factory voor het creëren van operators op basis van configuratie."""
    def __init__(
        self,
        config_loader: ConfigLoader,
        worker_builder: WorkerBuilder, # ← Let op: geen 'component_builder' meer
        event_bus: EventBus,
        persistor_factory: PersistorFactory
    ):
        self._config_loader = config_loader
        self._worker_builder = worker_builder
        self._event_bus = event_bus
        self._persistor_factory = persistor_factory

    def create_operator(self, operator_id: str) -> BaseOperator:
        """Creëert een operator instance op basis van operators.yaml."""
        config = self._config_loader.load_operator_config(operator_id)
        
        # Bereid de workforce voor (het nieuwe "Geprepareerde Workforce Model")
        workforce_dto = self._worker_builder.build_workforce_for_operator(config)
        
        # De Operator krijgt alleen de standard_workers en is "dom"
        return BaseOperator(
            config=config,
            workers=workforce_dto.standard_workers, # ← Geprepareerde lijst!
            event_bus=self._event_bus
        )
```

### **10.3.4. "Plugins zijn slim, infrastructuur is dom" Principe**

Plugins bevatten business logica, infrastructuur componenten (operators, persistors) zijn generieke executors.

**Goed voorbeeld - Slimme Plugin:**
```python
# plugins/opportunity_workers/fvg_detector/worker.py
from backend.core.base_worker import BaseWorker

class FVGDetector(BaseWorker):
    """Smart: bevat FVG detectie logica."""
    
    def process(self, context: TradingContext) -> List[Signal]:
        signals = []
        
        # Business logica: wat IS een FVG?
        for i in range(len(context.enriched_df) - 3):
            if self._is_fvg(context.enriched_df, i):
                signals.append(Signal(
                    opportunity_id=uuid4(),
                    timestamp=context.enriched_df.index[i],
                    signal_type='fvg_entry'
                ))
        
        return signals
    
    def _is_fvg(self, df, i):
        # Pure business logica
        return (df['low'].iloc[i+2] > df['high'].iloc[i])
```

**Goed voorbeeld - Domme Infrastructuur:**
```python
# backend/core/operators/base_operator.py
class BaseOperator:
    """Dumb: voert alleen uit volgens configuratie."""
    
    def run(self, context: Any, **kwargs) -> Any:
        """Generieke executie - gedrag bepaald door config."""
        workforce = self._component_builder.get_workforce(...)
        
        # Delegeer naar execution strategy (uit configuratie)
        if self.config.execution_strategy == ExecutionStrategy.SEQUENTIAL:
            return self._execute_sequential(workforce, context)
        elif self.config.execution_strategy == ExecutionStrategy.PARALLEL:
            return self._execute_parallel(workforce, context)
        # etc...
```

### **10.3.5. Dependency Injection in Tests**

Tests moeten gemakkelijk mock dependencies kunnen injecteren.

```python
# tests/test_base_stateful_worker.py
def test_stateful_worker_commits_state():
    # Arrange: Create mock persistor
    mock_persistor = MockStatePersistor()
    worker = TrailingStopManager(
        params={"trail_percent": 0.02},
        state_persistor=mock_persistor  # ← Injecteer mock
    )
    
    # Act
    context = create_test_context(current_price=50000)
    worker.process(context)
    
    # Assert
    assert mock_persistor.save_called
    assert mock_persistor.saved_data['high_water_mark'] == 50000
```

## **10.4. Configuratie-Gedreven Design** ⭐

"**YAML is intelligentie, code is mechanica**"

### **10.4.1. Operators.yaml als Perfecte Scheiding**

Het [`operators.yaml`](../../config/operators.yaml) bestand is het perfecte voorbeeld van configuratie-gedreven design - het volledige gedrag van operators wordt gedefinieerd zonder code te wijzigen.

**Configuratie definieert gedrag:**
```yaml
# config/operators.yaml
operators:
  - operator_id: "ContextOperator"
    manages_worker_type: "ContextWorker"
    execution_strategy: "SEQUENTIAL"      # ← Gedrag in configuratie
    aggregation_strategy: "CHAIN_THROUGH" # ← Niet in code!
    
  - operator_id: "OpportunityOperator"
    manages_worker_type: "OpportunityWorker"
    execution_strategy: "PARALLEL"
    aggregation_strategy: "COLLECT_ALL"
```

**Code is generieke executor:**
```python
# backend/core/operators/base_operator.py
class BaseOperator:
    """Generieke operator - gedrag via configuratie."""
    
    def run(self, context: Any) -> Any:
        # Lees configuratie
        strategy = self.config.execution_strategy
        
        # Voer uit volgens configuratie
        if strategy == ExecutionStrategy.SEQUENTIAL:
            return self._execute_sequential(...)
        elif strategy == ExecutionStrategy.PARALLEL:
            return self._execute_parallel(...)
```

### **10.4.2. Validatie via Pydantic Schemas**

Alle configuratie wordt gevalideerd door Pydantic schemas voordat executie begint.

**OperatorConfig Schema:**
```python
# backend/dtos/config/operator_config.py
from pydantic import BaseModel, Field
from backend.core.enums import ExecutionStrategy, AggregationStrategy

class OperatorConfig(BaseModel):
    """Configuration schema for a single operator."""
    
    operator_id: str = Field(
        ...,
        description="Unique identifier for this operator"
    )
    manages_worker_type: str = Field(
        ...,
        description="The worker type this operator manages"
    )
    execution_strategy: ExecutionStrategy = Field(
        ...,
        description="How workers are executed (SEQUENTIAL/PARALLEL/EVENT_DRIVEN)"
    )
    aggregation_strategy: AggregationStrategy = Field(
        ...,
        description="How worker outputs are combined"
    )

class OperatorSuiteConfig(BaseModel):
    """Configuration schema for all operators."""
    
    operators: List[OperatorConfig] = Field(
        ...,
        description="List of operator configurations"
    )
```

**ExecutionStrategy en AggregationStrategy Enums:**
```python
# backend/core/enums.py
class ExecutionStrategy(str, Enum):
    """How workers are executed."""
    SEQUENTIAL = "SEQUENTIAL"  # One by one, chained
    PARALLEL = "PARALLEL"      # All at once, collect results
    EVENT_DRIVEN = "EVENT_DRIVEN"  # React to events

class AggregationStrategy(str, Enum):
    """How worker outputs are combined."""
    CHAIN_THROUGH = "CHAIN_THROUGH"  # Output N → Input N+1
    COLLECT_ALL = "COLLECT_ALL"      # Collect all in list
    NONE = "NONE"                     # No aggregation
```

### **10.4.3. Best Practices voor Configuratie Design**

✅ **DO's:**
-   Definieer gedrag in YAML, niet in code
-   Gebruik Pydantic voor alle configuratie validatie
-   Maak configuratie zelf-documenterend met `description` fields
-   Test configuratie-wijzigingen zonder code te wijzigen

❌ **DON'Ts:**
-   Hard-code gedrag dat via configuratie zou kunnen
-   Valideer configuratie niet met Pydantic
-   Maak configuratie te complex - begin simpel
-   Skip configuratie documentatie

**Voorbeeld van Perfecte Scheiding:**
```yaml
# config/operators.yaml - Intelligence
- operator_id: "PlanningOperator"
  execution_strategy: "SEQUENTIAL"  # ← Business beslissing
  rationale: >
    Planning moet sequentieel - exit planning heeft entry nodig,
    sizing heeft stop loss afstand nodig.
```

```python
# backend/core/operators/base_operator.py - Mechanics
class BaseOperator:
    """Dumb executor - intelligence in config."""
    
    def run(self, context: Any) -> Any:
        # Pure mechanica - geen business logica
        if self.config.execution_strategy == ExecutionStrategy.SEQUENTIAL:
            return self._execute_sequential(...)
```

## **10.5. Gelaagde Logging & Traceability**

### **10.5.1. Drie Lagen van Logging**

1.  **Laag 1: stdio (Console via print()):** Uitsluitend voor snelle, lokale, vluchtige debugging. Mag nooit gecommit worden.
2.  **Laag 2: Gestructureerde JSON-logs:** De standaard output voor alle runs, bedoeld voor analyse.
3.  **Laag 3: De Web UI (Log Explorer):** De primaire interface voor het analyseren en debuggen van runs.

### **10.5.2. Traceability via Causaal ID Framework**

Het systeem maakt gebruik van een rijk causaal framework.

```python
from uuid import uuid4

# OpportunityID - "Waarom werd deze trade overwogen?"
signal = Signal(
    opportunity_id=uuid4(),
    timestamp=...,
    signal_type='fvg_entry'
)

# TradeID met causale link - "Waarom werd deze trade geopend?"
plan = TradePlan(
    trade_id=uuid4(),
    opportunity_id=signal.opportunity_id,  # ← Causale link!
    entry_price=50000.0
)

# ThreatID - "Waarom werd deze trade gesloten?"
threat = CriticalEvent(
    threat_id=uuid4(),
    threat_type='MAX_DRAWDOWN_BREACHED'
)
```

## **10.6. Testen als Voorwaarde**

### **10.6.1. De Testfilosofie: Elk .py Bestand Heeft een Test**

De "Testen als Voorwaarde"-filosofie wordt uitgebreid naar **alle** Python bestanden in het project, inclusief de architecturale contracten zelf (Schema's, DTOs en Interfaces). Dit garandeert de robuustheid van de "Contract-Gedreven Architectuur" vanaf de basis.

**Kernprincipe:** Geen enkel .py bestand is compleet zonder een corresponderend test bestand. Dit geldt voor:
- **Worker implementaties** (`worker.py` → `tests/test_worker.py`)
- **Configuratie schemas** (`*_schema.py` → `tests/unit/config/schemas/test_*_schema.py`)
- **Data Transfer Objects** (`*.py` in `dtos/` → `tests/unit/dtos/test_*.py`)
- **Interface definities** (`*.py` in `interfaces/` → abstracte testklassen)
- **Infrastructuur componenten** (operators, services, factories)

**Motivatie:**
In een Contract-Gedreven Architectuur zijn de contracten (Pydantic-modellen en interfaces) de meest kritieke onderdelen van de codebase. Fouten of onduidelijkheden in deze contracten leiden onvermijdelijk tot onverwachte runtime-fouten in de componenten die ze gebruiken.

### **10.6.2. Teststrategie per Type**

#### **10.6.2.1. Testen van Configuratie Schema's**

**Doel:** Garanderen dat het schema robuust is tegen zowel geldige als ongeldige configuratie-data.

**Wat te testen:**
- **Happy Path:** Kan het schema succesvol parsen met een correct en volledig YAML-voorbeeld?
- **Default Values:** Worden optionele velden correct gevuld met standaardwaarden als ze ontbreken?
- **Validatie Fouten:** Werpt het schema een ValidationError op bij incorrecte data (verkeerd type, ongeldige enum-waarde, ontbrekend verplicht veld)?

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

#### **10.6.2.2. Testen van Data Transfer Objects (DTOs)**

**Doel:** Verifiëren dat de "vervoerscontainers" voor data correct functioneren.

**Wat te testen:**
- **Happy Path:** Kan de DTO succesvol worden aangemaakt met geldige data?
- **Standaardwaarden & Factories:** Worden velden met default_factory (bijvoorbeeld uuid4) correct geïnitialiseerd?
- **Type Coercion:** Converteert Pydantic data correct (bijvoorbeeld een str naar een datetime) waar van toepassing?

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

#### **10.6.2.3. Testen van Interface Contracten**

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

# Als we later een DatabasePersistor maken, voegen we simpelweg toe:
# class TestDatabasePersistor(AbstractTestIStatePersistor):
#     def get_persistor_instance(self, path):
#         return DatabasePersistor(connection_string="...")
```

Deze aanpak garandeert dat elke nieuwe implementatie van een interface automatisch volledig getest wordt.

### **10.6.3. Worker Testing**

*   **Principe:** Code zonder tests wordt beschouwd als onvolledig.
*   **Implementatie:** Elke plugin is **verplicht** om een tests/test\_worker.py-bestand te bevatten. Continue Integratie (CI) voert alle tests automatisch uit na elke push.

### **10.6.4. Testing Patterns voor Dependency Injection**

```python
# tests/test_event_aware_worker.py
def test_event_aware_worker_publishes_events():
    # Arrange: Mock event handler
    mock_handler = MockEventHandler()
    worker = DCAOpportunityScorer(
        params={"score_regime": True},
        event_handler=mock_handler  # ← Inject mock
    )
    
    # Act
    context = create_test_context()
    signals = worker.process(context)
    
    # Assert
    assert len(mock_handler.published_events) == 1
    assert mock_handler.published_events[0][0] == "dca_opportunity_scored"
```

## **10.7. Overige Standaarden**

*   **Internationalisatie (i18n):**
    *   **Principe:** *Alle* tekst die direct of indirect aan een gebruiker kan worden getoond, moet via de internationalisatie-laag lopen. Hardgecodeerde, gebruikersgerichte strings in de Python-code zijn niet toegestaan.
    *   **Implementatie:** Een centrale Translator-klasse laadt YAML-bestanden uit de /locales map. Code gebruikt vertaalsleutels in "dot-notation" (bv. log.backtest.complete).
    *   **Scope van de Regel:** Deze regel is van toepassing op, maar niet beperkt tot, de volgende onderdelen:
        1.  Log Berichten: Alle log-berichten die bedoeld zijn om de gebruiker te informeren over de voortgang of status van de applicatie (voornamelijk INFO-niveau en hoger). Foutmeldingen voor ontwikkelaars (DEBUG-niveau) mogen wel hardcoded zijn.
            ```python
            # Correct
            logger.info('run.starting', pair=pair_name)
            # Incorrect
            logger.info(f'Starting run for {pair_name}...')
            ```
        2.  Pydantic Veldbeschrijvingen: Alle description velden binnen Pydantic-modellen (DTO's, configuratie-schema's). Deze beschrijvingen kunnen direct in de UI of in documentatie worden getoond.
            ```python
            # Correct
            equity: float = Field(..., description="ledger_state.equity.desc")
            # Incorrect
            equity: float = Field(..., description="The total current value...")
            ```
        3.  **Plugin Manifesten:** Alle beschrijvende velden in een plugin\_manifest.yaml, zoals description en display\_name. Een PluginQueryService moet deze velden door de Translator halen voordat ze naar de frontend worden gestuurd.
    *   **Interactie met Logger:** De Translator wordt één keer geïnitialiseerd en geïnjecteerd in de LogFormatter. De formatter is de enige component binnen het logsysteem die sleutels vertaalt naar leesbare berichten. Componenten die direct output genereren (zoals UI Presenters) krijgen de Translator ook apart geïnjecteerd.

### **10.7.1. Structuur van i18n Dotted Labels**

Om de locales/\*.yaml bestanden georganiseerd en onderhoudbaar te houden, hanteren we een strikte, hiërarchische structuur voor alle vertaalsleutels. De structuur volgt over het algemeen het pad van de component of het datamodel waar de tekst wordt gebruikt.

*   **Principe:** component\_of\_laag.specifieke\_context.naam\_van\_de\_tekst

**Voorbeelden van de Structuur:**

1.  Log Berichten:
    De sleutel begint met de naam van de module of de belangrijkste klasse waarin de log wordt aangeroepen.
    **Structuur:** component\_name.actie\_of\_gebeurtenis
    **Voorbeelden:**
    ```yaml
    # Voor backend/assembly/plugin_registry.py  
    plugin_registry:  
      scan_start: "Scanning for plugins in '{path}'..."  
      scan_complete: "Scan complete. Found {count} valid plugins."

    # Voor services/operators/analysis_operator.py  
    analysis_operator:  
      run_start: "AnalysisOperator run starting..."  
      critical_event: "Critical event detected: {event_type}"
    ```

2.  Pydantic Veldbeschrijvingen (description):
    De sleutel weerspiegelt het pad naar het veld binnen het DTO of schema. De sleutel eindigt altijd op .desc om aan te geven dat het een beschrijving is.
    **Structuur:** schema\_naam.veld\_naam.desc
    **Voorbeelden:**
    ```yaml
    # Voor backend/dtos/ledger_state.py  
    ledger_state:  
      equity:  
        desc: "The total current value of the ledger."  
      available_cash:  
        desc: "The amount of cash available for new positions."

    # Voor een plugin's schema.py  
    ema_detector_params:  
      period:  
        desc: "The lookback period for the EMA calculation."
    ```

3.  Plugin Manifesten (plugin\_manifest.yaml):
    Voor de beschrijvende velden van een plugin gebruiken we een structuur die de plugin uniek identificeert.
    **Structuur:** plugins.plugin\_naam.veld\_naam
    **Voorbeelden:**
    ```yaml
    plugins:  
      ema_detector:  
        display_name: "EMA Detector"  
        description: "Calculates and adds an Exponential Moving Average."  
      fvg_detector:  
        display_name: "FVG Detector"  
        description: "Detects a Fair Value Gap after a Market Structure Shift."
    ```

*   **Configuratie Formaat:** YAML is de standaard voor alle door mensen geschreven configuratie. JSON wordt gebruikt voor machine-naar-machine data-uitwisseling.

## **10.8. Design Principles & Kernconcepten**

De architectuur is gebouwd op de **SOLID**\-principes en een aantal kern-ontwerppatronen die de vier kernprincipes (Plugin First, Scheiding van Zorgen, Configuratie-gedreven, Contract-gedreven) tot leven brengen.

### **10.8.1. De Synergie: Configuratie- & Contract-gedreven Executie**

Het meest krachtige concept is de combinatie van configuratie- en contract-gedreven werken. De code is de motor; **de configuratie is de bestuurder, en de contracten zijn de verkeersregels die zorgen dat de bestuurder binnen de lijntjes blijft.**

*   **Configuratie-gedreven:** De *volledige samenstelling* van een strategie (welke plugins, in welke volgorde, met welke parameters) wordt gedefinieerd in een strategy\_blueprint.yaml. Dit maakt het mogelijk om strategieën drastisch te wijzigen zonder één regel code aan te passen.
*   **Contract-gedreven:** Elk stukje configuratie en data wordt gevalideerd door een strikt **Pydantic-schema**. Dit werkt op twee niveaus:
    1.  **Algemene Schema's:** De hoofdstructuur van een operation.yaml wordt gevalideerd door een algemeen schema. Dit contract dwingt af dat er bijvoorbeeld altijd een strategy\_links sectie aanwezig is.
    2.  **Plugin-Specifieke Schema's:** De parameters voor een specifieke plugin (bv. de length van een EMA-indicator) worden gevalideerd door de Pydantic-klasse in de schema.py van *die ene plugin*.

Bij het starten van een Operation, leest de applicatie de YAML-bestanden en bouwt een set gevalideerde configuratie-objecten. Als een parameter ontbreekt, een verkeerd type heeft, of een plugin wordt aangeroepen die niet bestaat, faalt de applicatie *onmiddellijk* met een duidelijke foutmelding. Dit voorkomt onvoorspelbare runtime-fouten en maakt het systeem extreem robuust en voorspelbaar.

### **10.8.2. SOLID in de Praktijk**

Voorbeelden met worker categorieën en [`BaseOperator`](../../backend/core/operators/base_operator.py).

*   **SRP (Single Responsibility Principle):** Elke klasse heeft één duidelijke taak.
    *   Een [`FVGDetector`](../../plugins/signal_generators/fvg_entry_detector/worker.py) ([`OpportunityWorker`](../../backend/core/base_worker.py:OpportunityWorker)) detecteert alleen Fair Value Gaps. Het transformeren naar een trade plan gebeurt in een aparte [`LimitEntryPlanner`](../../plugins/entry_planners/) ([`PlanningWorker`](../../backend/core/base_worker.py:PlanningWorker)).
    *   [`BaseOperator`](../../backend/core/operators/base_operator.py) heeft één verantwoordelijkheid: het uitvoeren van een workforce volgens zijn configuratie. De *intelligentie* (welke execution strategy) zit in [`operators.yaml`](../../config/operators.yaml).

*   **OCP (Open/Closed Principle):** Uitbreidbaar zonder bestaande code te wijzigen.
    *   Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe exit\_planner-plugin ([`PlanningWorker`](../../backend/core/base_worker.py:PlanningWorker)); de [`PlanningOperator`](../../backend/core/operators/base_operator.py) hoeft hiervoor niet aangepast te worden.
    *   Wil je een nieuwe execution strategy? Voeg deze toe aan [`ExecutionStrategy`](../../backend/core/enums.py:ExecutionStrategy) enum en implementeer de logica in [`BaseOperator._execute_custom()`](../../backend/core/operators/base_operator.py) - alle operators krijgen automatisch deze capability.

*   **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.
    *   De Operations-service hangt af van de [`IAPIConnector`](../../backend/core/interfaces/connectors.py:IAPIConnector)-interface, niet van de specifieke KrakenAPIConnector.
    *   Een worker die state nodig heeft (ongeacht zijn ROL), hangt af van de [`IStatePersistor`](../../backend/core/interfaces/persistors.py:IStatePersistor)-interface, niet van `JsonPersistor`. De `WorkerBuilder` injecteert de concrete persistor op basis van de manifest-configuratie. Testing met een `MockPersistor` is hierdoor triviaal.

### **10.8.3. Kernpatronen**

Nieuwe factories en patterns.

*   **Factory Pattern:** Het Assembly Team gebruikt factories om componenten te creëren:
    *   [`ComponentBuilder`](../../backend/assembly/component_builder.py) - Centraliseert het ontdekken, valideren en creëren van alle plugins
    *   [`OperatorFactory`](../../backend/assembly/operator_factory.py) - Creëert operators op basis van [`operators.yaml`](../../config/operators.yaml)
    *   [`PersistorFactory`](../../backend/assembly/persistor_factory.py) - Creëert gespecialiseerde persistors voor data, state en journaling

**OperatorFactory Voorbeeld:**
```python
# backend/assembly/operator_factory.py
class OperatorFactory:
    """Creates BaseOperator instances based on operators.yaml configuration."""
    
    def create_operator(self, operator_id: str) -> BaseOperator:
        """Factory method - creates configured operator."""
        config = self._load_operator_config(operator_id)
        
        return BaseOperator(
            config=config,
            component_builder=self._component_builder,
            event_bus=self._event_bus,
            persistor_factory=self._persistor_factory
        )
```

**PersistorFactory Voorbeeld:**
```python
# backend/assembly/persistor_factory.py
class PersistorFactory:
    """Creates specialized persistors for different data types."""
    
    def create_state_persistor(self, worker_id: str) -> IStatePersistor:
        """Creates atomic persistor for worker state."""
        return JsonPersistor(
            path=f"state/{worker_id}/state.json",
            mode="atomic"  # Crash-safe writes
        )
    
    def create_journal_persistor(self, strategy_id: str) -> IJournalPersistor:
        """Creates append-only persistor for strategy journal."""
        return JsonPersistor(
            path=f"journals/{strategy_id}/journal.json",
            mode="append"  # Historical log
        )
```

*   **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.

*   **Adapter Pattern:** [`PluginEventAdapter`](../../backend/assembly/plugin_event_adapter.py) maakt plugins bus-agnostisch door events te vertalen tussen plugin API en EventBus.

**PluginEventAdapter Voorbeeld:**
```python
# backend/assembly/plugin_event_adapter.py
class PluginEventAdapter:
    """Adapts plugin event API to EventBus, keeping plugins bus-agnostic."""
    
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
    
    def publish(self, event_name: str, payload: Any) -> None:
        """Adapter method - translates plugin.emit() to bus.publish()."""
        self._event_bus.publish(event_name, payload)
    
    def subscribe(self, event_name: str, handler: Callable) -> None:
        """Adapter method - translates plugin.on_event() to bus.subscribe()."""
        self._event_bus.subscribe(event_name, handler)
```

*   **DTO's (Data Transfer Objects):** Pydantic-modellen zorgen voor een voorspelbare en type-veilige dataflow tussen alle componenten.

**DTO Updates:**
```python
# backend/dtos/pipeline/signal.py
from pydantic import BaseModel, Field
from uuid import UUID

class Signal(BaseModel):
    """Base signal DTO for opportunity detection."""
    
    opportunity_id: UUID = Field(
        ...,
        description="Unique ID for tracing this opportunity through the pipeline"
    )
    timestamp: datetime
    asset: str
    direction: str  # 'long' or 'short'
    signal_type: str

# backend/dtos/execution/critical_event.py
class CriticalEvent(BaseModel):
    """Critical event DTO for threat detection."""
    
    threat_id: UUID = Field(
        ...,
        description="Unique ID for tracing this threat"
    )
    threat_type: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    details: Dict[str, Any]

# backend/dtos/pipeline/trade_plan.py
class TradePlan(BaseModel):
    """Complete trade plan DTO."""
    
    trade_id: UUID = Field(
        ...,
        description="Unique ID for this trade"
    )
    opportunity_id: UUID = Field(
        ...,
        description="Causally linked to the opportunity that triggered this plan"
    )
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
```

### **10.8.4. Event-Driven Design Patterns** ⭐

Patterns voor event-aware workflows.

#### **10.8.4.1. Event Publishing Best Practices**

**Simpele API - Bus Agnostisch:**
```python
# plugins/opportunity_workers/dca_opportunity_scorer/worker.py
from backend.core.base_worker import BaseEventAwareWorker

class DCAOpportunityScorer(BaseEventAwareWorker):
    """Event-aware worker - publishes scores."""
    
    def process(self, context: TradingContext) -> List[Signal]:
        score = self._calculate_score(context)
        
        signal = Signal(
            opportunity_id=uuid4(),
            timestamp=context.current_timestamp,
            metadata={'opportunity_score': score}
        )
        
        # Simple API - no EventBus coupling
        self.emit("dca_opportunity_scored", signal)
        
        return [signal]
```

#### **10.8.4.2. Event Chain Design**

**Fan-Out Pattern - Één event triggert meerdere workers:**
```yaml
# strategy_blueprint.yaml
opportunity_workers:
  - plugin: "multi_timeframe_analyzer"
    publishes:
      - event: "htf_bullish"
      - event: "htf_bearish"
      - event: "htf_neutral"

planning_workers:
  entry_planning:
    - plugin: "aggressive_entry"
      triggers: ["htf_bullish"]  # Alleen bij bullish HTF
    
    - plugin: "conservative_entry"
      triggers: ["htf_neutral"]  # Alleen bij neutral HTF
```

**Fan-In Pattern - Meerdere events → één worker:**
```yaml
# strategy_blueprint.yaml
planning_workers:
  entry_planning:
    - plugin: "adaptive_dca_planner"
      triggers:
        - "dca_opportunity_scored"  # From OpportunityWorker
        - "dca_risk_assessed"       # From ThreatWorker
      requires_all: true  # Wait for BOTH events
```

#### **10.8.4.3. Bus-Agnostische Worker Implementatie**

Workers communiceren via de [`IEventHandler`](../../backend/core/interfaces/event_handler.py:IEventHandler) interface, nooit direct met de EventBus. De `WorkerBuilder` gebruikt de `EventAdapterFactory` om een correct geconfigureerde handler te injecteren.

**Worker implementatie (ROL & Capability Model):**
```python
# Een EventDrivenWorker is van nature bus-agnostisch
class MyCustomEventWorker(EventDrivenWorker):
    """Bus-agnostische event-driven worker."""
    def __init__(self, params: Any, event_handler: IEventHandler):
        super().__init__(params)
        self._event_handler = event_handler # Interface, niet EventBus!

    # Deze methodes worden aangeroepen door de adapter,
    # op basis van 'wirings' in het manifest.
    def on_some_trigger(self, payload: Any) -> None:
        # ... doe werk ...
        self.emit("work_is_done", {"status": "success"})

    def emit(self, event_name: str, payload: Any) -> None:
        """Publiceert via adapter - worker kent de bus niet."""
        self._event_handler.publish(event_name, payload)
```
**Adapter injectie via de WorkerBuilder (Gecentraliseerd Factory Model):**
```python
# backend/assembly/worker_builder.py
class WorkerBuilder:
    """
    Gebruikt gespecialiseerde factories om capabilities te injecteren.
    """
    def __init__(
        self,
        event_adapter_factory: EventAdapterFactory, # ← Geïnjecteerd!
        persistor_factory: PersistorFactory         # ← Geïnjecteerd!
    ):
        self._event_adapter_factory = event_adapter_factory
        self._persistor_factory = persistor_factory

    def _build_worker(self, manifest, params) -> BaseWorker:
        # ... (laad WorkerClass, etc.) ...
        
        injected_dependencies = {"params": params}
        
        # Heeft deze worker state nodig?
        if manifest.capabilities.state.enabled:
            state_persistor = self._persistor_factory.create_state_persistor(...)
            injected_dependencies["state_persistor"] = state_persistor
            
        # Heeft deze worker events nodig?
        if manifest.capabilities.events.enabled:
            # Vraag de specialist om een adapter te bouwen
            event_handler = self._event_adapter_factory.create_event_handler_for_component(...)
            injected_dependencies["event_handler"] = event_handler

        # De worker wordt geïnstantieerd met alle benodigde dependencies
        worker_instance = WorkerClass(**injected_dependencies)
        return worker_instance
```

#### **10.8.4.4. Event Docstring Voorbeeld**

```python
# plugins/opportunity_workers/dca_opportunity_scorer/worker.py
class DCAOpportunityScorer(BaseEventAwareWorker):
    """
    Scores DCA opportunities based on multiple market factors.
    
    This worker is event-driven and publishes its results for downstream
    consumers to react to.
    
    Events:
        Subscribes to:
            - "on_schedule:weekly_dca": Triggered by scheduler for weekly evaluation
        
        Publishes:
            - "dca_opportunity_scored": Emitted when opportunity score is calculated
              Payload: Signal with metadata['opportunity_score']
    
    Args:
        params: Configuration parameters including scoring weights
        event_handler: Event adapter for bus-agnostic communication
    
    Example:
        ```yaml
        # In strategy_blueprint.yaml
        opportunity_workers:
          - plugin: "dca_opportunity_scorer"
            triggers:
              - "on_schedule:weekly_dca"
            publishes:
              - event: "dca_opportunity_scored"
                payload_type: "Signal"
            params:
              score_regime: true
              score_price_zone: true
        ```
    """
    
    def process(self, context: TradingContext) -> List[Signal]:
        """
        Calculates opportunity score and publishes result.
        
        Args:
            context: Current trading context with enriched data
        
        Returns:
            List of Signal DTOs with opportunity scores
        """
        score = self._calculate_score(context)
        
        signal = Signal(
            opportunity_id=uuid4(),
            timestamp=context.current_timestamp,
            asset=context.asset_pair,
            direction='long',
            signal_type='dca_opportunity',
            metadata={'opportunity_score': score}
        )
        
        # Publish for downstream consumers
        self.emit("dca_opportunity_scored", signal)
        
        return [signal]
```

### **10.8.5. CQRS (Command Query Responsibility Segregation)**

*   **Principe:** We hanteren een strikte scheiding tussen operaties die data lezen (Queries) en operaties die de staat van de applicatie veranderen (Commands). Een methode mag óf data retourneren, óf data wijzigen, maar nooit beide tegelijk. Dit principe voorkomt onverwachte bijeffecten en maakt het gedrag van het systeem glashelder en voorspelbaar.
*   **Implementatie in de Service Laag:** Dit principe is het meest expliciet doorgevoerd in de architectuur van onze data-services, waar we een duidelijke scheiding hebben tussen *lezers* en *schrijvers*:
    1.  **Query Services (Lezers):**
        *   **Naamgeving:** Services die uitsluitend data lezen, krijgen de QueryService-suffix (bv. PluginQueryService).
        *   **Methodes:** Alle publieke methodes in een Query Service zijn "vragen" en beginnen met het get\_ prefix (bv. get\_coverage).
        *   **Contract:** De DTO's die deze methodes accepteren, krijgen de Query-suffix (bv. CoverageQuery).
    2.  **Command Services (Schrijvers):**
        *   **Naamgeving:** Services die de staat van de data veranderen, krijgen de CommandService-suffix (bv. DataCommandService).
        *   **Methodes:** Alle publieke methodes in een Command Service zijn "opdrachten" en hebben een actieve, werkwoordelijke naam die de actie beschrijft (bv. synchronize, fetch\_period).
        *   **Contract:** De DTO's die deze methodes accepteren, krijgen de Command-suffix (bv. SynchronizationCommand).
*   **Scope:** Deze CQRS-naamgevingsconventie is de standaard voor alle services binnen de Service-laag die direct interacteren met de staat van data of het systeem. Het naleven van deze conventie is verplicht om de voorspelbaarheid en onderhoudbaarheid van de codebase te garanderen.

---

**Voor meer details over de architectuur, zie:**
-   [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md) - Complete architectuur
-   [`3_DE_CONFIGURATIE_TREIN.md`](3_DE_CONFIGURATIE_TREIN.md) - Configuratie-gedreven design
-   [`4_DE_PLUGIN_ANATOMIE.md`](4_DE_PLUGIN_ANATOMIE.md) - Plugin development guide

**Einde Document**