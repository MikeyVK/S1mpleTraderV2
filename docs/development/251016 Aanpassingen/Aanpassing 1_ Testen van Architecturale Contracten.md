# **Aanpassing 1: De Testfilosofie voor Architecturale Contracten**

Versie: 3.1  
Status: Definitief Amendement  
Dit document formaliseert de strategie voor het testen van de architecturale contracten zelf (Schema's, DTOs en Interfaces). Het verankert het principe dat **elk .py bestand, inclusief contractdefinities, een corresponderend testbestand moet hebben** om de robuustheid van de "Contract-Gedreven Architectuur" te garanderen.

### **1\. De Noodzaak van het Testen van Contracten**

In een "Contract-Gedreven Architectuur" zijn de contracten (Pydantic-modellen en interfaces) de meest kritieke onderdelen van de codebase. Fouten of onduidelijkheden in deze contracten leiden onvermijdelijk tot onverwachte runtime-fouten in de componenten die ze gebruiken.

Het testen van contracten heeft drie hoofddoelen:

1. **Validatie van het Contract:** Verifiëren dat het contract (bv. een Pydantic-schema) zich gedraagt zoals verwacht, inclusief validatieregels, standaardwaarden en typeconversies.  
2. **Documentatie via Code:** De tests fungeren als levende, uitvoerbare documentatie die precies laat zien hoe een contract geïnstantieerd en gebruikt moet worden.  
3. **Afdwingen van Implementatie (voor Interfaces):** Verifiëren dat een concrete klasse zich volledig aan het contract van een interface houdt.

### **2\. Teststrategie per Contracttype**

#### **2.1 Testen van Configuratie Schema's (\*\_schema.py)**

**Doel:** Garanderen dat het schema robuust is tegen zowel geldige als ongeldige configuratie-data.

**Wat te testen:**

* **Happy Path:** Kan het schema succesvol parsen met een correct en volledig YAML-voorbeeld?  
* **Default Values:** Worden optionele velden correct gevuld met standaardwaarden als ze ontbreken?  
* **Validatie Fouten:** Werpt het schema een ValidationError op bij incorrecte data (bv. verkeerd type, ongeldige enum-waarde, ontbrekend verplicht veld)?

**Voorbeeld (tests/unit/config/schemas/test\_operators\_schema.py):**

import pytest  
from pydantic import ValidationError

from backend.config.schemas.operators\_schema import OperatorConfig, OperatorSuiteConfig  
from backend.core.enums import ExecutionStrategy, AggregationStrategy

def test\_operator\_config\_happy\_path():  
    """ Tests successful validation with correct data. """  
    data \= {  
        "operator\_id": "TestOperator",  
        "manages\_worker\_type": "ContextWorker",  
        "execution\_strategy": "SEQUENTIAL",  
        "aggregation\_strategy": "CHAIN\_THROUGH"  
    }  
    \# Deze aanroep mag geen error geven  
    config \= OperatorConfig(\*\*data)  
    assert config.operator\_id \== "TestOperator"  
    assert config.execution\_strategy \== ExecutionStrategy.SEQUENTIAL

def test\_operator\_config\_invalid\_strategy():  
    """ Tests that an invalid enum value raises a ValidationError. """  
    data \= {  
        "operator\_id": "TestOperator",  
        "manages\_worker\_type": "ContextWorker",  
        "execution\_strategy": "INVALID\_STRATEGY", \# Deze waarde is fout  
        "aggregation\_strategy": "CHAIN\_THROUGH"  
    }  
    with pytest.raises(ValidationError):  
        OperatorConfig(\*\*data)

#### **2.2 Testen van Data Transfer Objects (DTOs)**

**Doel:** Verifiëren dat de "vervoerscontainers" voor data correct functioneren.

**Wat te testen:**

* **Happy Path:** Kan de DTO succesvol worden aangemaakt met geldige data?  
* **Standaardwaarden & Factories:** Worden velden met default\_factory (bv. uuid4) correct geïnitialiseerd?  
* **Type Coercion:** Converteert Pydantic data correct (bv. een str naar een datetime) waar van toepassing?

**Voorbeeld (tests/unit/dtos/pipeline/test\_signal\_dto.py):**

from uuid import UUID  
from datetime import datetime  
from backend.dtos.pipeline.signal import Signal

def test\_signal\_dto\_creation():  
    """ Tests basic instantiation and default value generation. """  
    now \= datetime.utcnow()  
    signal \= Signal(  
        timestamp=now,  
        asset="BTC/EUR",  
        direction="long",  
        signal\_type="fvg\_entry"  
    )  
      
    assert isinstance(signal.opportunity\_id, UUID) \# Is de default\_factory aangeroepen?  
    assert signal.asset \== "BTC/EUR"

#### **2.3 Testen van Interface Contracten (interfaces/\*.py)**

**Doel:** Afdwingen dat concrete klassen zich aan het gedefinieerde gedrag van een interface houden.

**Wat te testen:**

* We schrijven een **abstracte testklasse** die de *verwachtingen* van de interface test.  
* Vervolgens maken we voor **elke concrete implementatie** een testklasse die erft van de abstracte testklasse.

**Voorbeeld (tests/unit/core/interfaces/test\_persistors.py):**

from abc import ABC, abstractmethod  
import pytest

\# Stap 1: Definieer een abstracte test voor het IStatePersistor contract  
class AbstractTestIStatePersistor(ABC):  
    @abstractmethod  
    def get\_persistor\_instance(self, path):  
        """ Moet een instantie van de te testen persistor teruggeven. """  
        raise NotImplementedError

    def test\_save\_and\_load\_cycle(self, tmp\_path):  
        """ Test de basisfunctionaliteit van opslaan en laden. """  
        persistor \= self.get\_persistor\_instance(tmp\_path / "state.json")  
        test\_data \= {"key": "value", "count": 1}  
          
        persistor.save\_atomic(test\_data)  
        loaded\_data \= persistor.load()  
        assert loaded\_data \== test\_data

\# Stap 2: Maak een CONCRETE testklasse voor JsonPersistor  
from backend.data.persistors.json\_persistor import JsonPersistor

class TestJsonPersistor(AbstractTestIStatePersistor):  
    """ Concrete test voor de JsonPersistor implementatie. """  
    def get\_persistor\_instance(self, path):  
        return JsonPersistor(path=path, mode="atomic")

\# Als we later een DatabasePersistor maken, voegen we simpelweg toe:  
\# class TestDatabasePersistor(AbstractTestIStatePersistor):  
\#     def get\_persistor\_instance(self, path):  
\#         return DatabasePersistor(connection\_string="...")

### **3\. Conclusie**

Het opnemen van alle contracten (Schema's, DTOs en Interfaces) in de testspiegel is een fundamentele pijler van de "Testen als Voorwaarde"-filosofie. Het verhoogt niet alleen de robuustheid van de code, maar dient ook als cruciale, uitvoerbare documentatie die de architectuur versterkt en onderhoudbaar maakt.

### **4\. Lijst van Geraakte Documenten**

De implementatie van dit model vereist aanpassingen in de volgende documenten om consistentie te waarborgen:

1. 8\_DEVELOPMENT\_STRATEGY.md  
2. 10\_CODING\_STANDAARDS\_DESIGN\_PRINCIPLES.md  
3. V3\_COMPLETE\_SYSTEM\_DESIGN.md