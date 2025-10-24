# Testing Strategie: 100% Dekking

**Versie:** 3.0
**Status:** Definitief

Dit document beschrijft de teststrategie voor S1mpleTrader, die is ontworpen om de robuustheid en betrouwbaarheid van het systeem te garanderen.

---

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [De Testfilosofie: Elk .py Bestand Heeft een Test](#de-testfilosofie-elk-py-bestand-heeft-een-test)
3. [Teststrategie per Type](#teststrategie-per-type)
4. [Testen van Workers met Capabilities](#testen-van-workers-met-capabilities)
5. [Test Categorieën](#test-categorieën)
6. [Test Fixtures](#test-fixtures)

---

## **Executive Summary**

De teststrategie van S1mpleTrader is gebaseerd op het principe **"Testen als Voorwaarde"**. Geen enkele component wordt als "klaar" beschouwd zonder succesvolle, geautomatiseerde tests.

### **Kernkenmerken**

**1. 100% Test Mirror**
- Elk `.py` bestand in de codebase heeft een corresponderend testbestand in de `tests/` directory.
- Dit geldt voor workers, schemas, DTOs, interfaces en alle infrastructuurcomponenten.

**2. Gelaagde Teststrategie**
- **Unit Tests:** Testen individuele componenten in isolatie.
- **Integratietests:** Testen de samenwerking tussen componenten.
- **End-to-End Tests:** Valideren complete backtest-reproductie.

**3. Contract-Gedreven Testen**
- Tests voor Pydantic schemas valideren happy paths, default values en validation errors.
- Abstracte testklassen voor interfaces dwingen correcte implementatie af.

**4. Dependency Injection voor Testbaarheid**
- Mock objecten worden geïnjecteerd voor het testen van componenten in isolatie.
- Workers blijven eenvoudig te testen, zelfs met complexe capabilities.

---

## **De Testfilosofie: Elk .py Bestand Heeft een Test**

De "Testen als Voorwaarde"-filosofie wordt uitgebreid naar **alle** Python bestanden in het project, inclusief de architecturale contracten zelf (Schema's, DTOs en Interfaces).

**Kernprincipe:** Geen enkel .py bestand is compleet zonder een corresponderend test bestand.

---

## **Teststrategie per Type**

### **Testen van Configuratie Schema's**

**Doel:** Garanderen dat het schema robuust is tegen zowel geldige als ongeldige configuratie-data.

**Wat te testen:**
- **Happy Path:** Succesvol parsen met correcte data.
- **Default Values:** Correcte invulling van optionele velden.
- **Validatie Fouten:** `ValidationError` bij incorrecte data.

### **Testen van Data Transfer Objects (DTOs)**

**Doel:** Verifiëren dat de "vervoerscontainers" voor data correct functioneren.

**Wat te testen:**
- **Happy Path:** Succesvolle creatie met geldige data.
- **Standaardwaarden & Factories:** Correcte initialisatie van `default_factory` velden.
- **Type Coercion:** Correcte dataconversie.

### **Testen van Interface Contracten**

**Doel:** Afdwingen dat concrete klassen zich aan het gedefinieerde gedrag van een interface houden.

**Strategie:**
- Schrijf een **abstracte testklasse** die de *verwachtingen* van de interface test.
- Maak voor **elke concrete implementatie** een testklasse die erft van de abstracte testklasse.

---

## **Testen van Workers met Capabilities**

Omdat capabilities dynamisch worden geïnjecteerd, blijven de workers zelf eenvoudig te testen. We hoeven alleen de geïnjecteerde methodes te mocken.

**Testen van een `state`-capability worker:**

```python
# tests/test_stateful_worker.py
from unittest.mock import MagicMock

def test_my_stateful_worker_updates_state():
    worker = MyStatefulWorker(params={})
    worker.state = {} # Start met een lege state dictionary
    worker.commit_state = MagicMock() # Mock de commit-methode

    context = create_test_context()
    worker.process(context)

    assert worker.state['counter'] == 1
    worker.commit_state.assert_called_once()
```

---

## **Test Categorieën**

**Unit Tests** (`tests/unit/`):
- Test individuele componenten in isolatie
- Mock alle dependencies
- Focus op business logic

**Integration Tests** (`tests/integration/`):
- Test samenwerking tussen componenten
- Minimale mocking
- Focus op dataflow

**Plugin Tests** (`plugins/*/tests/`):
- Co-located met plugin code
- Test plugin business logic
- 100% coverage vereist

---

## **Test Fixtures**

**tests/fixtures/mock_persistors.py**:
```python
# tests/fixtures/mock_persistors.py
class MockStatePersistor:
    def __init__(self):
        self.state = {}
        self.save_called = False
        self.saved_data = None

    def load(self) -> Dict[str, Any]:
        return self.state.copy()

    def save_atomic(self, state: Dict[str, Any]) -> None:
        self.state = state.copy()
        self.saved_data = state.copy()
        self.save_called = True
```

---

## **Referenties**

- **[Coding Standards](01_Coding_Standards.md)** - Dependency injection patterns
- **[Plugin Anatomy](03_Development/01_Plugin_Anatomy.md)** - Testen van plugins

---

**Einde Document**