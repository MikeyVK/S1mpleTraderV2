# **Aanpassing 1 (Geconsolideerd): Het Uniforme "Manifest-Gedreven Capability Model"**

Versie: 3.2  
Status: Definitief Amendement  
Dit document formaliseert de overstap naar een uniform, expliciet en veilig model voor het definiëren van plugin-vaardigheden. Het vervangt een eerdere, onduidelijke architectuur van "marker" basisklassen door een zuivere scheiding tussen de **ROL** van een worker (gedefinieerd via overerving) en zijn **CAPABILITIES** (geconfigureerd in het manifest.yaml).

### **1. Omschrijving van de Wijziging**

Samenvatting:  
Deze wijziging introduceert een fundamentele architecturale scheiding. De vorige aanpak, waarbij klassen als BaseStatefulWorker en BaseEventAwareWorker zowel de rol als de vaardigheden van een worker impliceerden, wordt vervangen. In het nieuwe model wordt de architectuur als volgt gedefinieerd:

1. **De ROL van een worker is Declaratief:** Een ontwikkelaar maakt een expliciete, architecturale keuze door zijn klasse te laten erven van een van de twee abstracte basisklassen:  
   * **StandardWorker:** Voor een worker die deelneemt aan de georkestreerde, "top-down" pijplijn (aangeroepen via process()).  
   * **EventDrivenWorker:** Voor een worker die autonoom en "bottom-up" reageert op events van de EventBus.  
2. **De CAPABILITIES van een worker zijn Geconfigureerd:** Alle *extra vaardigheden* (state, journaling, network, etc.) worden uitsluitend gedeclareerd in een centrale capabilities-sectie binnen het manifest.yaml.

De WorkerBuilder leest deze combinatie van ROL (via de klasse) en CAPABILITIES (via het manifest) en injecteert de benodigde functionaliteit dynamisch in de worker-instantie.

Rationale (De "Waarom"):  
Dit model lost een aantal fundamentele problemen van de vorige aanpak op:

1. **Zuivere Scheiding van Verantwoordelijkheden:** De ROL (hoe een worker wordt geactiveerd) is nu gescheiden van zijn CAPABILITIES (wat een worker extra kan doen). Dit voorkomt "gespleten persoonlijkheden" en maakt de intentie van de ontwikkelaar ondubbelzinnig.  
2. **Declaratieve Validatie:** De architecturale regels (bv. "een StandardWorker moet een process-methode hebben") worden nu afgedwongen door Python's abstracte klassen, wat eleganter en robuuster is dan imperatieve code in een orkestrator.  
3. **Single Source of Truth:** Het manifest.yaml wordt de enige bron van waarheid over de *behoeften* (capabilities) van een plugin, terwijl de keuze voor de basisklasse de *rol* van de plugin binnen de architectuur definieert.  
4. **Veiligheid & Least Privilege:** Permissies zijn logisch geïntegreerd in de capabilities, waardoor een plugin zonder capabilities 100% "sandboxed" blijft.

### **2. De capabilities Structuur in manifest.yaml**

De capabilities-sectie wordt de centrale hub voor alle speciale vaardigheden die een worker, ongeacht zijn ROL, kan aanvragen.

# manifest.yaml  
capabilities:  
  # Capability voor STATEFULNESS  
  state:  
    enabled: true  
    state_dto: "dtos.state_dto.MyWorkerState"

  # Capability voor EVENT-DRIVEN GEDRAG (voor EventDrivenWorker)  
  # Deze vlag is nu redundant, omdat de basisklasse de rol al definieert,  
  # maar we behouden het voor explicietheid en filtering.  
  events:  
    enabled: true  
    publishes:  
      - payload_dto: "MyCustomSignal"  
        as_event: "MyCustomEventFired"  
    wirings:  
      - listens_to: "SomeTriggerEvent"  
        invokes:  
          method: "on_some_trigger"

  # ... (andere capabilities zoals journaling, network, filesystem) ...

### **3. Technische Implementatie & Gevolgen**

De Rol van de WorkerBuilder (Nu een "Contract-Valideerder"):  
De WorkerBuilder valideert of de code van de ontwikkelaar overeenkomt met de configuratie:

1. Lees het manifest.  
2. Classificeer de *intentie* op basis van capabilities.events.enabled.  
3. Controleer of de *implementatie* (de gekozen basisklasse) overeenkomt met de intentie.  
4. Instantieer de klasse. Python's ABC-mechanisme werpt een TypeError op als de ontwikkelaar het contract van de ROL heeft geschonden.  
5. Injecteer de aangevraagde CAPABILITIES (state, emit, etc.).

### **3.1 De Rol van Abstracte Basisklassen voor ROL-Definitie (NIEUWE SECTIE)**

Om de architecturale ROL op een elegante, declaratieve manier af te dwingen, introduceren we twee specifieke, abstracte basisklassen. Een ontwikkelaar **moet** een van deze twee kiezen.

**De BaseWorker-hiërarchie:**

# backend/core/base_worker.py  
from abc import ABC, abstractmethod

# Dit is de absolute basis, bevat alleen de __init__  
class BaseWorker(ABC):  
    def __init__(self, params: Any):  
        self.params = params

# 1. Het contract voor de ROL: Standaard Worker  
class StandardWorker(BaseWorker, ABC):  
    """  
    Definieert de ROL van een worker die deelneemt aan de georkestreerde  
    pijplijn (SEQUENTIAL/PARALLEL). Deze klasse dwingt de implementatie  
    van een 'process'-methode af.  
    """  
    @abstractmethod  
    def process(self, context: Any, **kwargs) -> Any:  
        """  
        De kernlogica voor een standaard worker. MOET geïmplementeerd worden.  
        """  
        raise NotImplementedError

# 2. Het contract voor de ROL: Event-Driven Worker  
class EventDrivenWorker(BaseWorker, ABC):  
    """  
    Definieert de ROL van een worker die uitsluitend reageert op events  
    van de EventBus. Deze klasse heeft bewust GEEN 'process'-methode.  
    """  
    # Deze klasse is leeg. Zijn doel is om als ROL-definitie te dienen.  
    pass

Afdwingen via de WorkerBuilder:  
De WorkerBuilder voert een simpele, maar krachtige, validatie uit:

1. **Classificatie:** Bepaal de bedoelde ROL (Standaard of Event-Driven) op basis van capabilities.events.enabled in het manifest.  
2. **Type Check:** Controleer of de geladen worker-klasse daadwerkelijk van de juiste basisklasse erft.  
   * **Als** de ROL "Standaard" is, controleer issubclass(WorkerClass, StandardWorker).  
   * **Als** de ROL "Event-Driven" is, controleer issubclass(WorkerClass, EventDrivenWorker).  
3. **Foutafhandeling:** Als de check faalt, stopt het systeem met een duidelijke ConfigurationError.  
   * **Foutmelding:** *"Architectural Mismatch in 'MyWorker': Manifest declareert dit als een Event-Driven worker, maar de klasse erft niet van 'EventDrivenWorker'. Pas de basisklasse in worker.py aan."*

Resultaat:  
De verantwoordelijkheid voor het contract van de ROL ligt nu waar hij hoort: bij de ontwikkelaar die de klasse schrijft. De WorkerBuilder hoeft alleen te controleren of de ontwikkelaar zich aan de regels houdt.

### **4. Bijgewerkte Plugin Template Mapstructuur**

De mappenstructuur blijft ongewijzigd, maar de inhoud van worker.py zal nu altijd beginnen met from ... import StandardWorker of from ... import EventDrivenWorker.

plugins/[plugin_naam]/  
├── manifest.yaml  
├── schema.py  
├── worker.py  
├── dtos/  
│   ├── __init__.py  
│   ├── state_dto.py  
│   └── event_dtos.py  
├── tests/  
│   └── test_worker.py  
└── visualization_dto.py

### **5. Lijst van Geraakte Documenten**

De implementatie van dit model vereist aanpassingen in de volgende documenten om consistentie te waarborgen:

1. 0_S1MPLETRADER_V2_DEVELOPMENT.md  
2. 1_BUS_COMMUNICATION_ARCHITECTURE.md  
3. 2_ARCHITECTURE.md  
4. 3_DE_CONFIGURATIE_TREIN.md  
5. 4_DE_PLUGIN_ANATOMIE.md  
6. 5_DE_WORKFLOW_ORKESTRATIE.md  
7. 6_FRONTEND_INTEGRATION.md  
8. 7_RESILIENCE_AND_OPERATIONS.md  
9. 8_DEVELOPMENT_STRATEGY.md  
10. 10_CODING_STANDAARDS_DESIGN_PRINCIPLES.md  
11. A_BIJLAGE_TERMINOLOGIE.md  
12. D_BIJLAGE_PLUGIN_IDE.md  
13. V3_COMPLETE_SYSTEM_DESIGN.md