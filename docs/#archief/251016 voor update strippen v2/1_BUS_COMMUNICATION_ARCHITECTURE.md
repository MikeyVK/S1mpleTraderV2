# **1. S1mpleTrader V2: De Communicatie Architectuur**

Versie: 3.0
Status: Definitief
Dit document beschrijft de communicatie-architectuur van S1mpleTrader V2, gericht op de scheiding tussen business- en communicatielogica via het EventAdapter Patroon.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Visie & Filosofie: Scheiding van Logica](#11-visie--filosofie-scheiding-van-logica)
3. [De Architectuur: Het EventAdapter Patroon](#12-de-architectuur-het-eventadapter-patroon)
4. [NIEUW: PluginEventAdapter Architectuur](#13-nieuw-plugineventadapter-architectuur)
5. [NIEUW: Event Chain Validatie](#14-nieuw-event-chain-validatie)
6. [De Levenscyclus in de Praktijk](#15-de-levenscyclus-in-de-praktijk)
7. [De Event Map: De Grondwet van de Communicatie](#16-de-event-map-de-grondwet-van-de-communicatie)
8. [Event-Driven Architectuur: Drie Niveaus](#17-event-driven-architectuur-drie-niveaus)
9. [De Operator Suite (V3)](#18-de-operator-suite-v3)

---

## **Executive Summary**

Dit document beschrijft de communicatie-architectuur van S1mpleTrader V3, die is gebaseerd op een radicale scheiding tussen businesslogica en communicatielogica. De kern van het ontwerp is het **EventAdapter Patroon**, dat ervoor zorgt dat kerncomponenten zoals Operators en Workers "bus-agnostisch" zijn en geen directe kennis hebben van de EventBus.

### **🎯 Kernkenmerken**

**1. Bus-Agnostische Componenten**
- Businesslogica (Operators, Workers) is volledig geïsoleerd van de communicatielaag.
- Componenten zijn pure Python-klassen die DTOs accepteren en retourneren.

**2. EventAdapter Patroon**
- Generieke "vertalers" (`EventAdapter`) overbruggen de kloof tussen de EventBus en de business-componenten.
- Het gedrag van adapters wordt volledig gedefinieerd in configuratie (`wiring_map.yaml`), niet in code.

**3. Manifest-Gedreven Capabilities**
- De ROL van een worker (`StandardWorker` vs. `EventDrivenWorker`) wordt gescheiden van zijn CAPABILITIES (state, events, journaling), die in het `manifest.yaml` worden aangevraagd.
- De `WorkerBuilder` injecteert dynamisch de benodigde functionaliteit.

**4. "Fail Fast" met Event Chain Validatie**
- Een `EventChainValidator` analyseert de volledige event-stroom bij het opstarten om runtime problemen zoals zwevende events, onbereikbare subscribers en circulaire afhankelijkheden te voorkomen.

**5. Progressive Complexity**
- De architectuur ondersteunt drie niveaus van complexiteit, waardoor het systeem toegankelijk is voor beginners (impliciete pijplijnen) en tegelijkertijd krachtig voor experts (custom event chains).

### **🔑 Design Principes**

✅ **Scheiding van Verantwoordelijkheden** - Businesslogica weet niets van communicatie.
✅ **Configuratie boven Code** - Event-routing en adapter-gedrag worden gedefinieerd in YAML.
✅ **"Fail Fast" Validatie** - Voorkom runtime fouten door validatie tijdens de bootstrap-fase.
✅ **Opt-in Complexiteit** - Begin simpel en voeg event-driven complexiteit alleen toe waar nodig.

---

## **1.1. Visie & Filosofie: Scheiding van Logica**

### **1.1.1. Inleiding & Doel**

Dit document beschrijft de communicatie-architectuur van S1mpleTrader V2. De kern van dit ontwerp is niet simpelweg het gebruik van een event-gedreven model, maar de **radicale scheiding tussen businesslogica en communicatielogica**.

Het doel is een systeem te creëren waarin de componenten die de daadwerkelijke strategie- en businesslogica bevatten (Operators en Workers) volledig puur, agnostisch en onwetend zijn van het communicatiemechanisme (de EventBus).

### **1.1.2. De Filosofie: Bus-Agnostische Componenten**

In deze architectuur is een Operator (bv. de [`OpportunityOperator`](backend/core/operators/base_operator.py)) een pure Python-klasse. Zijn taak is het uitvoeren van een specifieke business-taak: hij accepteert een DTO (Data Transfer Object) als input en retourneert een DTO als output. Hij weet niets van "subscriben" of "publishen".

De volledige verantwoordelijkheid voor de communicatie met de EventBus wordt gedelegeerd aan een generieke tussenlaag: het **EventAdapter Patroon**.

### **1.1.3. Kernprincipe: Event-Driven is OPTIONEEL**

Een fundamenteel principe in V3 is dat **event-driven communicatie optioneel is**. Het systeem ondersteunt drie abstractieniveaus:

1.  **Niveau 1: Impliciete Pijplijnen (95% van gebruik)**
    De quant definieert workers, het systeem genereert automatisch de event chain. Geen event management nodig.

2.  **Niveau 2: Predefined Triggers (Opt-in)**
    Gebruik voorgedefinieerde trigger namen voor common use cases zonder custom events.

3.  **Niveau 3: Custom Event Chains (Expert Mode)**
    Volledige controle met custom events en complexe workflows.

Dit "progressive complexity" model zorgt ervoor dat beginners direct kunnen starten, terwijl experts alle kracht hebben die ze nodig hebben.

---

## **1.2. De Architectuur: Het EventAdapter Patroon**

### **1.2.1. De EventAdapter als Vertaler**

De EventAdapter is een generieke, herbruikbare "vertaler" wiens enige taak het is om een brug te slaan tussen de EventBus en een pure business-component (Operator). Zijn gedrag wordt niet in code, maar in configuratie gedefinieerd via de [`wiring_map.yaml`](config/wiring_map.yaml).

**Voorbeeld van een wiring_map.yaml-regel:**

```yaml
# wiring_map.yaml (Applicatie-niveau routing)
- adapter_id: "OpportunityPipelineAdapter"
  listens_to: "ContextReady"
  invokes:
    component: "OpportunityOperator"
    method: "run_pipeline"
  publishes_result_as: "SignalsGenerated"
```

Deze regel instrueert het systeem om:

1.  Een EventAdapter te creëren.
2.  Deze adapter te laten luisteren naar het `ContextReady`-event.
3.  Wanneer dat event binnenkomt, de [`run_pipeline()`](backend/core/operators/base_operator.py:run_pipeline)-methode van de OpportunityOperator aan te roepen met de event-payload.
4.  Als de methode een resultaat teruggeeft, dit resultaat te publiceren op de bus onder de naam `SignalsGenerated`.

### **1.2.2. De Rol van de EventWiringFactory en EventAdapterFactory**

Tijdens het opstarten van de applicatie leest de EventWiringFactory de volledige wiring_map.yaml. Haar rol is echter niet langer om zelf de adapters te bouwen. Volgens het Gecentraliseerde Factory Model is de EventWiringFactory een "klant" van de gespecialiseerde EventAdapterFactory.

Het proces is als volgt:

De EventWiringFactory leest de wiring_map.yaml.

Voor elke regel vertaalt het de configuratie naar een gestandaardiseerde WiringInstruction DTO.

Het roept vervolgens de centrale EventAdapterFactory aan met deze instructies en de doelcomponent (bv. de OpportunityOperator).

De EventAdapterFactory, de enige specialist die weet hoe een adapter gebouwd moet worden, creëert en configureert de EventAdapter-instantie en abonneert deze op de EventBus.

Deze scheiding van verantwoordelijkheden zorgt ervoor dat de bouwlogica voor adapters op één enkele, onderhoudbare plek is geconcentreerd, wat het DRY (Don't Repeat Yourself) principe versterkt.

---

## **1.3. NIEUW: Het "Manifest-Gedreven Capability Model"**

### **1.3.1. Filosofie: Scheiding van ROL en CAPABILITIES**

**SHIFT 4 (Geconsolideerd): Van Impliciete Basisklassen naar een Expliciet Contract**

In V3 introduceert S1mpleTrader een fundamentele architecturale scheiding die plugins volledig isoleert van de EventBus-implementatie. De oude aanpak, waarbij een klasse als BaseEventAwareWorker zowel de rol als de vaardigheden van een worker impliceerde, wordt vervangen.

De nieuwe kernfilosofie is een zuivere scheiding van verantwoordelijkheden:

De **ROL** van een worker is **Declaratief**: De ontwikkelaar kiest expliciet een van de twee abstracte basisklassen. Deze keuze definieert hoe de worker wordt aangestuurd in de architectuur.

-   **StandardWorker**: Voor een worker die deelneemt aan de georkestreerde, "top-down" pijplijn (aangeroepen via `process()`).
-   **EventDrivenWorker**: Voor een worker die autonoom en "bottom-up" reageert op events van de EventBus.

De **CAPABILITIES** van een worker zijn **Geconfigureerd**: Alle extra vaardigheden (state, journaling, en ook event-gedrag) worden uitsluitend gedeclareerd in een centrale `capabilities`-sectie binnen het `manifest.yaml`.

De `WorkerBuilder` leest deze combinatie van **ROL** (via de klasse) en **CAPABILITIES** (via het manifest) en valideert het contract. Als een worker de `events`-capability aanvraagt, wordt de benodigde `emit`-functionaliteit dynamisch geïnjecteerd door de `EventAdapterFactory`.

### **1.3.2. De Twee Pijlers van de Plugin Architectuur**

#### **Pijler 1: De Configuratie (manifest.yaml) - Het "Capability Paspoort"**

Dit is waar de plugin zijn behoeften en vaardigheden definieert. De `capabilities`-sectie is de enige bron van waarheid voor de extra functionaliteiten die een worker nodig heeft.

```yaml
# plugins/smart_dca_worker/manifest.yaml
capabilities:
  # Capability voor statefulness (optioneel)
  state:
    enabled: true
    state_dto: "dtos.state_dto.MyWorkerState"

  # Capability voor event-interactie
  events:
    enabled: true # Cruciaal: dit activeert de event-gedreven natuur
    publishes:
      # Definieert welke events deze worker MAG publiceren
      - payload_dto: "MyCustomSignal"
        as_event: "MyCustomEventFired"
    wirings:
      # Definieert op welke events deze worker reageert
      - listens_to: "SomeTriggerEvent"
        invokes:
          method: "on_some_trigger"
```

#### **Pijler 2: De ROL Definitie (Abstracte Basisklassen) - Het "Architecturale Contract"**

Een plugin-ontwikkelaar moet een van de volgende twee basisklassen kiezen. Dit dwingt een correcte implementatie af op architecturaal niveau.

```python
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
    pijplijn. Deze klasse dwingt de implementatie van een 'process'-methode af.
    """
    @abstractmethod
    def process(self, context: Any, **kwargs) -> Any:
        raise NotImplementedError

# 2. Het contract voor de ROL: Event-Driven Worker
class EventDrivenWorker(BaseWorker, ABC):
    """
    Definieert de ROL van een worker die uitsluitend reageert op events
    van de EventBus. Deze klasse heeft bewust GEEN 'process'-methode.
    """
    # Deze klasse is leeg. Zijn doel is om als ROL-definitie te dienen.
    pass
```

De `WorkerBuilder` valideert of de gekozen basisklasse overeenkomt met de intentie in het manifest. Een `EventDrivenWorker` die `events: enabled: false` heeft, zal bijvoorbeeld een `ConfigurationError` veroorzaken.

### **1.3.3. De Assemblage: De Rol van de Factories**

De "magie" van het verbinden van de worker met de EventBus gebeurt tijdens de setup-fase, georkestreerd door de componenten in de assembly-laag.

-   **De WorkerBuilder (De Vertaler):** Leest het manifest van een worker. Als `capabilities.events.enabled` true is, classificeert het de worker als event-gedreven. Het vertaalt de `publishes`- en `wirings`-secties naar een lijst van universele `WiringInstruction` DTOs.

-   **De EventAdapterFactory (De Specialist):** Wordt aangeroepen door de `WorkerBuilder`. Het ontvangt de worker-instantie en de lijst met `WiringInstructions`. Zijn taak is om:
    1.  Een `EventAdapter`-instantie te creëren.
    2.  De `emit`-methode van de adapter te "injecteren" in de worker-instantie, zodat de worker `self.emit(...)` kan aanroepen.
    3.  De adapter te abonneren op de juiste events op de EventBus, die de methodes van de worker aanroepen zoals gedefinieerd in de `wirings`.

Dit gecentraliseerde model zorgt ervoor dat de complexe logica voor het bouwen en injecteren van adapters op één plek staat (DRY) en dat elke component een duidelijke, enkele verantwoordelijkheid heeft (SRP).

---

## **1.4. NIEUW: Event Chain Validatie**

### **1.4.1. Het Probleem: Event Chain Integriteit**

In een event-driven systeem kunnen complexe problemen ontstaan:

-   **Orphaned Events:** Een plugin publiceert een event, maar niemand luistert ernaar
-   **Dead-End Events:** Een plugin verwacht een event, maar niemand publiceert het
-   **Circular Dependencies:** Event A triggert B, B triggert C, C triggert A
-   **Type Mismatches:** Een plugin publiceert `Signal`, een ander verwacht `TradePlan`

Deze problemen zijn moeilijk te debuggen tijdens runtime. **Oplossing: Validatie bij startup.**

### **1.4.2. Event Chain Validator**

De [`EventChainValidator`](backend/assembly/event_chain_validator.py) analyseert de volledige event chain tijdens startup:

```python
# backend/assembly/event_chain_validator.py
from typing import Dict, List, Set
from backend.config.schemas import StrategyBlueprint

class EventChainValidator:
    """
    Valideert de integriteit van event chains tijdens startup.
    
    Checks:
    1. Alle triggers hebben een publisher
    2. Geen circular dependencies
    3. Dead-end event detectie (waarschuwing)
    4. Payload DTO type consistency
    """
    
    def validate(self, 
                 blueprint: StrategyBlueprint,
                 wiring_map: Dict,
                 operators_config: Dict) -> ValidationResult:
        """
        Voert volledige validatie uit.
        
        Args:
            blueprint: Strategy blueprint met workforce definitie
            wiring_map: Applicatie-niveau event routing
            operators_config: Operator configuratie
            
        Returns:
            ValidationResult met errors en warnings
        """
        result = ValidationResult()
        
        # Build event graph
        graph = self._build_event_graph(blueprint, wiring_map)
        
        # Check 1: Publisher/Subscriber consistency
        self._validate_publishers_and_subscribers(graph, result)
        
        # Check 2: Circular dependencies
        self._detect_circular_dependencies(graph, result)
        
        # Check 3: Dead-end events
        self._detect_dead_ends(graph, result)
        
        # Check 4: DTO type consistency
        self._validate_payload_types(graph, result)
        
        return result
    
    def _build_event_graph(self, 
                          blueprint: StrategyBlueprint,
                          wiring_map: Dict) -> EventGraph:
        """
        Bouwt een gerichte graaf van alle event relaties.
        
        Nodes: Events
        Edges: Publisher → Event → Subscriber
        """
        graph = EventGraph()
        
        # Parse wiring_map (applicatie-niveau)
        for wire in wiring_map:
            event_name = wire['listens_to']
            result_event = wire.get('publishes_result_as')
            
            if result_event:
                graph.add_edge(event_name, result_event)
        
        # Parse plugin manifests (plugin-niveau)
        for worker_config in blueprint.all_workers():
            manifest = self._load_manifest(worker_config['plugin'])
            
            # Publishes
            for pub in manifest.get('publishes', []):
                graph.add_publisher(pub['event_name'], worker_config['plugin'])
            
            # Listens_to
            for sub in manifest.get('listens_to', []):
                graph.add_subscriber(sub['event_name'], worker_config['plugin'])
        
        return graph
    
    def _validate_publishers_and_subscribers(self,
                                            graph: EventGraph,
                                            result: ValidationResult) -> None:
        """
        Check 1: Alle triggers moeten een publisher hebben.
        """
        for event_name in graph.get_subscribed_events():
            publishers = graph.get_publishers(event_name)
            
            if not publishers:
                result.add_error(
                    f"Event '{event_name}' has subscribers but no publishers! "
                    f"Subscribers: {graph.get_subscribers(event_name)}"
                )
    
    def _detect_circular_dependencies(self,
                                     graph: EventGraph,
                                     result: ValidationResult) -> None:
        """
        Check 2: Detecteer circular dependencies via DFS.
        """
        visited = set()
        rec_stack = set()
        
        def dfs(event: str, path: List[str]) -> None:
            visited.add(event)
            rec_stack.add(event)
            
            for next_event in graph.get_downstream_events(event):
                if next_event not in visited:
                    dfs(next_event, path + [next_event])
                elif next_event in rec_stack:
                    # Circular dependency detected!
                    cycle = path[path.index(next_event):] + [next_event]
                    result.add_error(
                        f"Circular dependency detected: {' → '.join(cycle)}"
                    )
            
            rec_stack.remove(event)
        
        for event in graph.get_all_events():
            if event not in visited:
                dfs(event, [event])
    
    def _detect_dead_ends(self,
                         graph: EventGraph,
                         result: ValidationResult) -> None:
        """
        Check 3: Detecteer events die worden gepubliceerd maar niet gebruikt.
        """
        for event_name in graph.get_published_events():
            subscribers = graph.get_subscribers(event_name)
            
            if not subscribers:
                result.add_warning(
                    f"Event '{event_name}' is published but has no subscribers. "
                    f"Is this intentional?"
                )
    
    def _validate_payload_types(self,
                               graph: EventGraph,
                               result: ValidationResult) -> None:
        """
        Check 4: Valideer dat publishers en subscribers compatibele DTO types gebruiken.
        """
        for event_name in graph.get_all_events():
            publishers = graph.get_publishers_with_types(event_name)
            subscribers = graph.get_subscribers_with_types(event_name)
            
            # Check type consistency
            publisher_types = {p['payload_dto'] for p in publishers}
            
            if len(publisher_types) > 1:
                result.add_error(
                    f"Event '{event_name}' has multiple publishers with "
                    f"different payload types: {publisher_types}"
                )
```

### **1.4.3. Validatie tijdens Bootstrap**

De validatie wordt automatisch uitgevoerd tijdens het opstarten:

```python
# backend/assembly/context_builder.py
class ContextBuilder:
    """Orkestreert de volledige bootstrap fase."""
    
    def bootstrap(self, 
                  blueprint: StrategyBlueprint,
                  platform_config: PlatformConfig) -> BootstrapResult:
        """
        Bootstrap fase met event chain validatie.
        """
        # 1. Load alle configuraties
        wiring_map = self._load_wiring_map()
        operators_config = self._load_operators_config()
        
        # 2. Valideer event chain
        validator = EventChainValidator()
        validation_result = validator.validate(
            blueprint, 
            wiring_map, 
            operators_config
        )
        
        # 3. Stop als er errors zijn
        if validation_result.has_errors():
            raise EventChainValidationError(
                "Event chain validation failed:\n" + 
                "\n".join(validation_result.errors)
            )
        
        # 4. Log warnings
        for warning in validation_result.warnings:
            logger.warning(f"Event chain warning: {warning}")
        
        # 5. Continue met bootstrap...
        components = self._build_components(blueprint)
        
        return BootstrapResult(
            components=components,
            validation_result=validation_result
        )
```

### **1.4.4. Voorbeeld Validatie Output**

```
[INFO] Event Chain Validation Started
[INFO] Building event graph from blueprint and wiring_map...
[INFO] Found 12 events, 8 publishers, 15 subscribers
[✓] Check 1: All triggers have publishers
[✓] Check 2: No circular dependencies detected
[!] Check 3: Dead-end event detected: 'debug_signal_logged' has no subscribers
[✓] Check 4: Payload DTO types are consistent
[WARN] Event 'debug_signal_logged' is published but has no subscribers. Is this intentional?
[SUCCESS] Event chain validation completed with 0 errors, 1 warning
```

---

## **1.5. De Levenscyclus in de Praktijk**

### **1.5.1. De Bootstrap Fase (Het "Bedraden" van het Systeem)**

1.  De gebruiker start een Operation via een entrypoint.
2.  De applicatie laadt de volledige "Configuratie Trein":
    -   [`platform.yaml`](config/platform.yaml)
    -   [`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml)
    -   [`operators.yaml`](config/operators.yaml) (NIEUW in V3)
    -   [`wiring_map.yaml`](config/wiring_map.yaml)
3.  De **[`EventChainValidator`](backend/assembly/event_chain_validator.py)** valideert de event integriteit (NIEUW in V3).
4.  De **[`ComponentBuilder`](backend/assembly/context_builder.py)** instantieert alle benodigde componenten:
    -   5 Operators (Context, Opportunity, Threat, Planning, Execution)
    -   Alle Workers per Operator
    -   PluginEventAdapters voor event-aware workers
5.  De **[`ContextBootstrapper`](backend/assembly/context_builder.py)** zorgt voor het vullen van de initiële, rijke context *voordat* de Operation live gaat.
6.  De **[`EventWiringFactory`](backend/assembly/event_wiring_factory.py)** leest de [`wiring_map.yaml`](config/wiring_map.yaml) en creëert de EventAdapters, die zich abonneren op de EventBus.
7.  Het `OperationStarted`-event wordt gepubliceerd. Het systeem is nu "live".

### **1.5.2. Een Runtime Voorbeeld (De Tick-Loop met 5 Operators)**

**V3 Flow (5 Operators):**

```
1. ExecutionEnvironment publiceert TradingContext
                    ↓
2. ContextOperator verrijkt context
   └→ publiceert ContextReady
                    ↓
        ┌───────────┴───────────┐
        ▼                       ▼
3. OpportunityOperator    ThreatOperator
   (parallelle executie)
   └→ publiceert          └→ publiceert
      SignalsGenerated       ThreatEvents
        │                       │
        └───────────┬───────────┘
                    ▼
4. PlanningOperator (combineert beide)
   └→ publiceert PlansReady
                    ↓
5. ExecutionOperator voert uit
   └→ publiceert ExecutionApproved
```

**Belangrijke Wijziging t.o.v. V2:**
-   **ExecutionEnvironment** publiceert nu direct [`TradingContext`](backend/dtos/state/trading_context.py) in plaats van `MarketSnapshot`
-   **ContextOperator** is nu een standaard operator (verrijkt bestaande context)
-   **OpportunityOperator** en **ThreatOperator** draaien parallel
-   **PlanningOperator** combineert opportunities en threats tot plannen

---

## **1.6. De Event Map: De Grondwet van de Communicatie**

De [`event_map.yaml`](config/event_map.yaml) definieert alle toegestane events en hun contracten.

### **1.6.1. V3 Event Map (5 Operators)**

| Event Naam | Payload (DTO Contract) | Mogelijke Publisher(s) | Mogelijke Subscriber(s) |
|:-----------|:-----------------------|:-----------------------|:------------------------|
| **Operation Lifecycle** | | | |
| `OperationStarted` | [`OperationParameters`](backend/dtos/state/operation_parameters.py) | Operations | EventAdapter (voor ContextOperator), ContextBootstrapper |
| `BootstrapComplete` | [`BootstrapResult`](backend/dtos/state/bootstrap_result.py) | ContextBootstrapper | ExecutionEnvironment |
| `ShutdownRequested` | [`ShutdownSignal`](backend/dtos/execution/shutdown_signal.py) | UI, EventAdapter (van ThreatWorker) | Operations |
| `OperationFinished` | [`OperationSummary`](backend/dtos/state/operation_summary.py) | Operations | ResultLogger, UI |
| --- | --- | --- | --- |
| **Tick Lifecycle (V3: 5 Operators)** | | | |
| `ContextReady` | [`TradingContext`](backend/dtos/state/trading_context.py) | ExecutionEnvironment, EventAdapter (van ContextOperator) | EventAdapter (voor OpportunityOperator, ThreatOperator) |
| `SignalsGenerated` | [`List[OpportunitySignal]`](backend/dtos/pipeline/signal.py) | EventAdapter (van OpportunityOperator) | EventAdapter (voor PlanningOperator) |
| `ThreatsDetected` | [`List[CriticalEvent]`](backend/dtos/execution/critical_event.py) | EventAdapter (van ThreatOperator) | EventAdapter (voor PlanningOperator, ExecutionOperator) |
| `PlansReady` | [`List[RoutedTradePlan]`](backend/dtos/pipeline/routed_trade_plan.py) | EventAdapter (van PlanningOperator) | EventAdapter (voor ExecutionOperator) |
| `ExecutionApproved` | [`List[ExecutionDirective]`](backend/dtos/execution/execution_directive.py) | EventAdapter (van ExecutionOperator) | ExecutionEnvironment |
| --- | --- | --- | --- |
| **State & Monitoring Lifecycle** | | | |
| `LedgerStateChanged` | [`LedgerState`](backend/dtos/state/ledger_state.py) | ExecutionEnvironment | EventAdapter (voor ThreatWorker) |
| `AggregatePortfolioUpdated` | [`AggregateMetrics`](backend/dtos/state/aggregate_metrics.py) | EventAdapter (van ThreatWorker) | UI, EventAdapter (voor ExecutionWorker) |
| --- | --- | --- | --- |
| **Analyse Lifecycle** | | | |
| `BacktestCompleted` | [`BacktestResult`](backend/dtos/state/backtest_result.py) | Operations | ResultLogger, UI |
| --- | --- | --- | --- |
| **Scheduler Events (NIEUW in V3)** | | | |
| `DAILY_MARKET_OPEN_TICK` | [`ScheduledTick`](backend/dtos/state/scheduled_tick.py) | Scheduler | EventAdapter (voor ExecutionWorker) |
| `WEEKLY_DCA_TICK` | [`ScheduledTick`](backend/dtos/state/scheduled_tick.py) | Scheduler | EventAdapter (voor OpportunityWorker, ThreatWorker) |

### **1.6.2. Operator Configuratie (operators.yaml)**

**NIEUW in V3:** Het gedrag van Operators wordt geconfigureerd via [`operators.yaml`](config/operators.yaml):

```yaml
# config/operators.yaml
operators:
  - operator_id: "ContextOperator"
    manages_worker_type: "ContextWorker"
    execution_strategy: "SEQUENTIAL"      # Workers één voor één
    aggregation_strategy: "CHAIN_THROUGH" # Output → volgende input
  
  - operator_id: "OpportunityOperator"
    manages_worker_type: "OpportunityWorker"
    execution_strategy: "PARALLEL"        # Workers tegelijkertijd
    aggregation_strategy: "COLLECT_ALL"   # Verzamel alle signalen
  
  - operator_id: "ThreatOperator"
    manages_worker_type: "ThreatWorker"
    execution_strategy: "PARALLEL"
    aggregation_strategy: "COLLECT_ALL"   # Verzamel alle threats
  
  - operator_id: "PlanningOperator"
    manages_worker_type: "PlanningWorker"
    execution_strategy: "SEQUENTIAL"
    aggregation_strategy: "CHAIN_THROUGH" # Signal → Plan transformatie
  
  - operator_id: "ExecutionOperator"
    manages_worker_type: "ExecutionWorker"
    execution_strategy: "EVENT_DRIVEN"    # Op basis van events
    aggregation_strategy: "NONE"          # Geen aggregatie
```

---

## **1.7. Event-Driven Architectuur: Drie Niveaus**

### **1.7.1. Filosofie: Progressive Complexity**

S1mpleTrader V3 omarmt het principe van **progressive complexity**: beginners kunnen simpel starten, experts krijgen alle kracht die ze nodig hebben.

### **1.7.2. Niveau 1: Impliciete Pijplijnen (95% van gebruik)**

**Voor wie:** Standaard quant die een lineaire strategie wil bouwen.

**Hoe het werkt:** De quant definieert workers, het systeem genereert automatisch de event chain.

**Voorbeeld:**

```yaml
# strategy_blueprint.yaml
workforce:
  context_workers:
    - plugin: "ema_detector"
    - plugin: "market_structure_detector"
  
  opportunity_workers:
    - plugin: "fvg_detector"
  
  planning_workers:
    entry_planning:
      - plugin: "limit_entry_planner"
    exit_planning:
      - plugin: "liquidity_target_exit"
    size_planning:
      - plugin: "fixed_risk_sizer"
    order_routing:
      - plugin: "default_router"
  
  execution_workers:
    trade_initiation:
      - plugin: "default_plan_executor"
```

**Automatisch gegenereerde event flow:**
```
ContextReady → SignalsGenerated → PlansReady → ExecutionApproved
```

**Voordelen:**
-   ✅ Geen event management nodig
-   ✅ Duidelijke, lineaire flow
-   ✅ "Het werkt gewoon"

### **1.7.3. Niveau 2: Predefined Triggers (Opt-in)**

**Voor wie:** Quant die specifieke workers op specifieke momenten wil activeren.

**Voorbeeld:**

```yaml
workforce:
  threat_workers:
    - plugin: "max_drawdown_monitor"
      triggers:
        - "on_ledger_update"  # Predefined trigger
    
    - plugin: "news_event_monitor"
      triggers:
        - "on_context_ready"
```

**Predefined Triggers:**
-   `on_context_ready`: Wanneer context klaar is
-   `on_signal_generated`: Wanneer een signaal is gegenereerd
-   `on_ledger_update`: Wanneer ledger verandert
-   `on_position_opened`: Wanneer een positie wordt geopend
-   `on_position_closed`: Wanneer een positie wordt gesloten
-   `on_schedule`: Tijd-gebaseerd (via scheduler)

### **1.7.4. Niveau 3: Custom Event Chains (Expert Mode)**

**Voor wie:** Geavanceerde quant die complexe, event-driven workflows wil bouwen.

**Voorbeeld: Smart DCA**

```yaml
workforce:
  opportunity_workers:
    - plugin: "dca_opportunity_scorer"
      triggers:
        - "on_schedule:weekly_dca"
      publishes:
        - event: "dca_opportunity_scored"
          payload_type: "Signal"
  
  threat_workers:
    - plugin: "dca_risk_assessor"
      triggers:
        - "on_schedule:weekly_dca"
      publishes:
        - event: "dca_risk_assessed"
          payload_type: "CriticalEvent"
  
  planning_workers:
    entry_planning:
      - plugin: "adaptive_dca_planner"
        triggers:
          - "dca_opportunity_scored"
          - "dca_risk_assessed"
        requires_all: true  # Wacht op beide events
        publishes:
          - event: "dca_plan_ready"
            payload_type: "TradePlan"
```

**Event Flow:**
```
Scheduler → WEEKLY_DCA_TICK
         ↓
    ┌────┴────┐
    ▼         ▼
Opportunity  Threat
  Scorer    Assessor
    │         │
    ▼         ▼
dca_opportunity_scored  dca_risk_assessed
         │         │
         └────┬────┘
              ▼
      Adaptive DCA Planner
              ▼
        dca_plan_ready
```

---

## **1.8. De Operator Suite (V3)**

### **1.8.1. Van 4 naar 5 Operators**

**V2 Model (4 Operators):**
-   ContextOrchestrator
-   AnalysisOperator (bevatte signals + planning)
-   MonitorOperator
-   ExecutionHandler

**V3 Model (5 Operators):**
-   [`ContextOperator`](backend/core/operators/base_operator.py) - "De Cartograaf"
-   [`OpportunityOperator`](backend/core/operators/base_operator.py) - "De Verkenner" (was deel van Analysis)
-   [`ThreatOperator`](backend/core/operators/base_operator.py) - "De Waakhond" (was Monitor)
-   [`PlanningOperator`](backend/core/operators/base_operator.py) - "De Strateeg" (NIEUW, was deel van Analysis)
-   [`ExecutionOperator`](backend/core/operators/base_operator.py) - "De Uitvoerder"

### **1.8.2. Operator Responsibilities**

| Operator | Input | Output | Execution Strategy |
|:---------|:------|:-------|:-------------------|
| **ContextOperator** | [`TradingContext`](backend/dtos/state/trading_context.py) (base) | [`TradingContext`](backend/dtos/state/trading_context.py) (verrijkt) | SEQUENTIAL |
| **OpportunityOperator** | [`TradingContext`](backend/dtos/state/trading_context.py) | [`List[OpportunitySignal]`](backend/dtos/pipeline/signal.py) | PARALLEL |
| **ThreatOperator** | [`TradingContext`](backend/dtos/state/trading_context.py), [`LedgerState`](backend/dtos/state/ledger_state.py) | [`List[CriticalEvent]`](backend/dtos/execution/critical_event.py) | PARALLEL |
| **PlanningOperator** | [`OpportunitySignal`](backend/dtos/pipeline/signal.py), [`List[CriticalEvent]`](backend/dtos/execution/critical_event.py) | [`List[RoutedTradePlan]`](backend/dtos/pipeline/routed_trade_plan.py) | SEQUENTIAL |
| **ExecutionOperator** | [`RoutedTradePlan`](backend/dtos/pipeline/routed_trade_plan.py) | [`List[ExecutionDirective]`](backend/dtos/execution/execution_directive.py) | EVENT_DRIVEN |

### **1.8.3. Data-Driven Operator Configuratie**

**KERNAFWIJKING #3A:** In plaats van 5 hard-coded operator klassen, gebruikt V3 één generieke `BaseOperator` die zijn gedrag volledig baseert op configuratie.

Dankzij het "Geprepareerde Workforce Model" is de `BaseOperator` een pure, "domme" uitvoerder geworden. Hij heeft geen kennis meer van event-gedreven workers. De classificatie van workers gebeurt vooraf door de `WorkerBuilder`, die een `Workforce` DTO teruggeeft met twee gescheiden lijsten: `standard_workers` en `event_driven_workers`.

De `OperatorFactory` geeft alleen de `standard_workers` door aan de constructor van de `BaseOperator`. De `event_driven_workers` zijn op dat punt al via de `EventAdapterFactory` aan de EventBus gekoppeld en leiden een autonoom leven.

De implementatie van de `BaseOperator` is hierdoor extreem simpel en robuust:

```python
# backend/core/operators/base_operator.py
class BaseOperator:
    """
    Generieke operator die een PRE-GEFILTERDE lijst van workers orkestreert
    volgens de meegegeven strategie.
    
    Gedrag wordt bepaald door operators.yaml, niet door code.
    """
    
    def __init__(self,
                 operator_id: str,
                 workers: List[IWorker], # Belangrijk: dit zijn ALLEEN standard_workers
                 execution_strategy: ExecutionStrategy,
                 aggregation_strategy: AggregationStrategy):
        self.operator_id = operator_id
        self.workers = workers
        self.execution_strategy = execution_strategy
        self.aggregation_strategy = aggregation_strategy
    
    def run_pipeline(self, context: TradingContext) -> Any:
        """
        Voert de worker pipeline uit. Let op: er is geen 'EVENT_DRIVEN' tak meer,
        omdat die workers deze operator nooit bereiken.
        """
        if self.execution_strategy == ExecutionStrategy.SEQUENTIAL:
            return self._run_sequential(context)
        elif self.execution_strategy == ExecutionStrategy.PARALLEL:
            return self._run_parallel(context)
        # De 'EVENT_DRIVEN' strategie is geen verantwoordelijkheid meer
        # van de operator's runtime executie.
```

Deze aanpak zorgt voor een zuivere scheiding van verantwoordelijkheden: de assembly-laag is verantwoordelijk voor de voorbereiding en classificatie, terwijl de `BaseOperator` zich puur richt op de operationele uitvoering van zijn georkestreerde pijplijn.

---

## **Conclusie**

S1mpleTrader V3 introduceert een robuuste, flexibele en elegante communicatie-architectuur die:

✅ **Bus-agnostische plugins** - Volledige isolatie via PluginEventAdapter
✅ **Twee-niveaus event routing** - Plugin contracts + applicatie bedrading
✅ **Automatische event chain validatie** - Catch errors tijdens startup
✅ **Progressive complexity** - Van simpel naar expert zonder refactoring
✅ **5-operator model** - Duidelijke scheiding van verantwoordelijkheden
✅ **Data-driven configuratie** - Gedrag in YAML, niet in code

Deze architectuur maakt het mogelijk om complexe, event-driven strategieën te bouwen terwijl het systeem begrijpelijk en onderhoudbaar blijft voor quants van alle niveaus.

---

**Referenties:**
-   [`MIGRATION_MAP.md`](MIGRATION_MAP.md) - Volledige V2 → V3 migratie gids
-   [`WORKER_TAXONOMIE_V3.md`](../development/251014%20Bijwerken%20documentatie/WORKER_TAXONOMIE_V3.md) - Uitgebreide worker taxonomie
-   [`Uitwerking Kernafwijking #4A2`](../development/251014%20Bijwerken%20documentatie/Uitwerking%20Kernafwijking%20%234A2%20-%20Plugin%20Event%20Architectuur.md) - Plugin event architectuur details
-   [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md) - Hoofd architectuur document