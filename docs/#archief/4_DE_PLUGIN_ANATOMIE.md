# **4\. De Anatomie van een Plugin**

Status: Definitief
Dit document beschrijft de gedetailleerde structuur en de technische keuzes achter de plugins in de S1mpleTrader-architectuur.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Fundamentele Mappenstructuur](#41-fundamentele-mappenstructuur)
3. [Formaat Keuzes: YAML vs. JSON](#42-formaat-keuzes-yaml-vs-json)
4. [Het Manifest: De Zelfbeschrijvende ID-kaart](#43-het-manifest-de-zelfbeschrijvende-id-kaart)
5. [De Worker & het BaseWorker Raamwerk](#44-de-worker--het-baseworker-raamwerk)
6. [Gelaagde Plugin Capaciteiten](#45-gelaagde-plugin-capaciteiten)

---

## **Executive Summary**

Dit document beschrijft de plugin anatomie van S1mpleTrader, een modulair systeem gebouwd op vier kernprincipes:

### **🎯 Kernkenmerken**

**1. 5-Categorie Worker Model**
- ContextWorker - De Cartograaf (marktdata verrijking)
- OpportunityWorker - De Verkenner (handelskansen herkennen)
- ThreatWorker - De Waakhond (risico's detecteren)
- PlanningWorker - De Strateeg (kansen → plannen)
- ExecutionWorker - De Uitvoerder (plannen uitvoeren)

**2. 27 Sub-Categorieën voor Fijnmazige Classificatie**
- Een gedetailleerde taxonomie voor het classificeren van elke plugin, wat filtering en begrip verbetert.

**3. Het "Manifest-Gedreven Capability Model"**
- De architectuur scheidt de **ROL** van een worker (bepaald door de basisklasse `StandardWorker` of `EventDrivenWorker`) strikt van zijn **CAPABILITIES** (aangevraagd in het `manifest.yaml`).

**4. Opt-in Capabilities**
- De `capabilities`-sectie in het manifest stelt een plugin in staat om expliciet extra functionaliteit aan te vragen, zoals `state`, `events`, en `journaling`.

### **🔑 Design Principes**

✅ **Plugin First** - Alles begint bij de plugin.
✅ **Zelfbeschrijvend** - Het manifest is de enige bron van waarheid.
✅ **ROL vs. CAPABILITIES** - Zuivere scheiding van verantwoordelijkheden.
✅ **Opt-in Complexiteit** - Vraag alleen de capabilities aan die je nodig hebt.

---

**Architectuur Kenmerken:**
-   5 Worker Categorieën: Context, Opportunity, Threat, Planning, Execution
-   27 Sub-Categorieën voor fijnmazige classificatie
-   Gelaagde Plugin Capaciteiten (opt-in complexiteit)
-   Event Configuration support voor expert workflows

## **4.1. Fundamentele Mappenstructuur**

Elke plugin is een opzichzelfstaande Python package. Deze structuur garandeert dat logica, contracten en metadata altijd bij elkaar blijven, wat essentieel is voor het "Plugin First" principe.

### **Basis Structuur (90% van plugins)**

```
plugins/[plugin_naam]/
├── manifest.yaml           # De ID-kaart (wie ben ik?)
├── worker.py               # De Logica (wat doe ik?)
├── schema.py               # Het Contract (wat heb ik nodig?)
├── context_schema.py       # Het visuele contract (wat kan ik laten zien?)
└── test/test_worker.py     # De Kwaliteitscontrole (werk ik correct?)
```

### **Uitgebreide Structuur (event-aware plugins)**

Voor plugins die gebruik maken van event communication ([`BaseEventAwareWorker`](backend/core/base_worker.py:BaseEventAwareWorker)):

```
plugins/[plugin_naam]/
├── manifest.yaml           # De ID-kaart (wie ben ik?)
├── worker.py               # De Logica (wat doe ik?)
├── schema.py               # Het Contract (wat heb ik nodig?)
├── context_schema.py       # Het visuele contract (wat kan ik laten zien?)
├── dtos/                   # Event DTO's (ALLEEN voor event-aware plugins)
│   ├── __init__.py
│   ├── opportunity_signal.py    # Voorbeeld: custom Signal DTO
│   └── threat_alert.py          # Voorbeeld: custom CriticalEvent DTO
└── test/test_worker.py     # De Kwaliteitscontrole (werk ik correct?)
```

### **Bestandsbeschrijvingen**

*   **[`manifest.yaml`](plugins/)**: De "ID-kaart" van de plugin. Dit bestand maakt de plugin vindbaar en begrijpelijk voor het Assembly Team. Bevat ook de optionele `event_config` sectie voor event-aware plugins.

*   **[`worker.py`](plugins/)**: Bevat de Python-klasse met de daadwerkelijke businesslogica van de plugin. Erft van [`BaseWorker`](backend/core/base_worker.py) of een van de gespecialiseerde basisklassen.

*   **[`schema.py`](plugins/)**: Bevat het Pydantic-model dat de structuur en validatieregels voor de configuratieparameters (`params`) van de plugin definieert.

*   **[`context_schema.py`](plugins/)**: Bevat het concrete context model voor de visualisatie van gegevens die de plugin produceert. Dit is cruciaal voor de "Trade Explorer" in de frontend.

*   **`dtos/`** (optioneel): Bevat custom Data Transfer Objects voor event payloads. **Alleen nodig voor event-aware plugins** die custom event payloads publiceren (niet de standaard [`Signal`](backend/dtos/pipeline/signal.py) of [`CriticalEvent`](backend/dtos/pipeline/) types).
    *   *Voorbeeld*: Een [`OpportunityWorker`](backend/core/base_worker.py) die een custom opportunity score publiceert
    *   *Voorbeeld*: Een [`ThreatWorker`](backend/core/base_worker.py) die een custom threat alert stuurt

*   **[`test/test_worker.py`](plugins/)**: Bevat de verplichte unit tests voor het valideren van de werking van de plugin. Een 100% score als uitkomst van pytest is noodzakelijk voor de succesvolle "enrollment" van een nieuwe plugin.

### **Wanneer dtos/ Map Nodig Is**

De `dtos/` map is **ALLEEN** nodig wanneer:
1.  De plugin event-aware is ([`BaseEventAwareWorker`](backend/core/base_worker.py:BaseEventAwareWorker))
2.  **EN** de plugin custom event payloads publiceert die niet de standaard types zijn

**95% van plugins heeft GEEN dtos/ map nodig** omdat:
-   Ze zijn stateless (geen events)
-   Of ze gebruiken standaard DTO's zoals [`Signal`](backend/dtos/pipeline/signal.py) en [`TradePlan`](backend/dtos/pipeline/trade_plan.py)

## **4.2. Formaat Keuzes: YAML vs. JSON**

De keuze voor een dataformaat hangt af van de primaire gebruiker: **een mens of een machine**. We hanteren daarom een hybride model om zowel leesbaarheid als betrouwbaarheid te maximaliseren.

*   **YAML voor Menselijke Configuratie**
    *   **Toepassing:** manifest.yaml en alle door de gebruiker geschreven strategy\_blueprint.yaml en operation.yaml-bestanden.
    *   **Waarom:** De superieure leesbaarheid, de mogelijkheid om commentaar toe te voegen, en de flexibelere syntax zijn essentieel voor ontwikkelaars en strategen die deze bestanden handmatig schrijven en onderhouden.
*   **JSON voor Machine-Data**
    *   **Toepassing:** Alle machine-gegenereerde data, zoals API-responses, state-bestanden, en gestructureerde logs.
    *   **Waarom:** De strikte syntax en universele portabiliteit maken JSON de betrouwbare standaard voor communicatie tussen systemen en voor het opslaan van gestructureerde data waar absolute betrouwbaarheid vereist is.

## **4.3. Het Manifest: De Zelfbeschrijvende ID-kaart**

Het manifest.yaml is de kern van het "plugin discovery" mechanisme. Het stelt het Assembly Team in staat om een plugin volledig te begrijpen **zonder de Python-code te hoeven inspecteren**. Dit manifest is een strikt contract dat alle cruciale metadata van een plugin vastlegt.

### **4.3.1. Identification**

De identification-sectie bevat alle beschrijvende metadata.

*   **name**: De unieke, machine-leesbare naam (bv. [`market_structure_detector`](plugins/structural_context/market_structure_detector/)).
*   **display_name**: De naam zoals deze in de UI wordt getoond.
*   **type**: De **cruciale** categorie die bepaalt tot welke van de vijf functionele pijlers de plugin behoort. Toegestane waarden zijn:
    *   [`context_worker`](backend/core/enums.py:WorkerType) - "De Cartograaf" - Verrijkt marktdata met context
    *   [`opportunity_worker`](backend/core/enums.py:WorkerType) - "De Verkenner" - Herkent handelskansen
    *   [`threat_worker`](backend/core/enums.py:WorkerType) - "De Waakhond" - Detecteert risico's
    *   [`planning_worker`](backend/core/enums.py:WorkerType) - "De Strateeg" - Transformeert kansen naar plannen
    *   [`execution_worker`](backend/core/enums.py:WorkerType) - "De Uitvoerder" - Voert plannen uit en beheert posities
    
*   **subtype**: De **sub-categorie** binnen het worker type. Zie sectie 4.3.1b voor alle 27 sub-categorieën.
*   **version**: De semantische versie van de plugin (bv. 1.0.1).
*   **description**: Een korte, duidelijke beschrijving van de functionaliteit.
*   **author**: De naam van de ontwikkelaar.

**Rationale voor de Indeling:**
De [`OpportunityWorker`](backend/core/base_worker.py) categorie richt zich op patroonherkenning en signaal generatie, terwijl [`PlanningWorker`](backend/core/base_worker.py) zich focust op trade constructie (entry/exit planning, sizing, routing).

Deze scheiding zorgt voor conceptuele zuiverheid en sluit beter aan bij hoe een quant denkt over strategievorming.

### **4.3.1b. De 27 Sub-Categorieën**

De architectuur biedt een verfijnde taxonomie met **27 sub-categorieën** verdeeld over de 5 worker types. Deze sub-categorieën bieden fijnmazige classificatie voor betere organisatie, filtering en begrip van plugin functionaliteit.

#### **ContextType (7 sub-categorieën)**

Voor [`ContextWorker`](backend/core/base_worker.py) plugins die marktdata verrijken:

*   [`REGIME_CLASSIFICATION`](backend/core/enums.py:ContextType) - Markt regime & conditie classificatie
    *   *Voorbeelden:* ADX trend filter, volatility regime classifier
*   [`STRUCTURAL_ANALYSIS`](backend/core/enums.py:ContextType) - Technische structuur analyse
    *   *Voorbeelden:* Market structure detector, swing point identifier, liquidity zones
*   [`INDICATOR_CALCULATION`](backend/core/enums.py:ContextType) - Indicatoren & berekeningen
    *   *Voorbeelden:* EMA, RSI, MACD, Bollinger Bands, ATR
*   [`MICROSTRUCTURE_ANALYSIS`](backend/core/enums.py:ContextType) - Orderbook & microstructuur
    *   *Voorbeelden:* Orderbook imbalance, bid-ask spread analyzer
*   [`TEMPORAL_CONTEXT`](backend/core/enums.py:ContextType) - Temporele context
    *   *Voorbeelden:* Session analyzer, time-of-day patterns, killzones
*   [`SENTIMENT_ENRICHMENT`](backend/core/enums.py:ContextType) - Sentiment & alternatieve data
    *   *Voorbeelden:* News sentiment, social media analysis, fear & greed index
*   [`FUNDAMENTAL_ENRICHMENT`](backend/core/enums.py:ContextType) - On-chain & fundamentele data
    *   *Voorbeelden:* On-chain metrics, earnings data, economic indicators

**Organisatieprincipe:** Type data-verrijking en abstractieniveau

#### **OpportunityType (7 sub-categorieën)**

Voor [`OpportunityWorker`](backend/core/base_worker.py) plugins die handelskansen herkennen:

*   [`TECHNICAL_PATTERN`](backend/core/enums.py:OpportunityType) - Technische patroon herkenning
    *   *Voorbeelden:* FVG detector, breakout scanner, divergence finder
*   [`MOMENTUM_SIGNAL`](backend/core/enums.py:OpportunityType) - Momentum & trend following
    *   *Voorbeelden:* Trend continuation, momentum breakout
*   [`MEAN_REVERSION`](backend/core/enums.py:OpportunityType) - Mean reversion strategieën
    *   *Voorbeelden:* Oversold/overbought, range bounce
*   [`STATISTICAL_ARBITRAGE`](backend/core/enums.py:OpportunityType) - Arbitrage & statistical
    *   *Voorbeelden:* Pair trading, correlation breaks
*   [`EVENT_DRIVEN`](backend/core/enums.py:OpportunityType) - Event-driven signalen
    *   *Voorbeelden:* News-based signals, "buy the rumour"
*   [`SENTIMENT_SIGNAL`](backend/core/enums.py:OpportunityType) - Sentiment-driven signalen
    *   *Voorbeelden:* Extreme fear/greed, social sentiment spikes
*   [`ML_PREDICTION`](backend/core/enums.py:OpportunityType) - Machine learning predictions
    *   *Voorbeelden:* Trained model predictions, pattern recognition AI

**Organisatieprincipe:** Strategische benadering en theoretische basis

#### **ThreatType (5 sub-categorieën)**

Voor [`ThreatWorker`](backend/core/base_worker.py) plugins die risico's detecteren:

*   [`PORTFOLIO_RISK`](backend/core/enums.py:ThreatType) - Portfolio & financieel risico
    *   *Voorbeelden:* Max drawdown monitor, exposure monitor, correlation risk
*   [`MARKET_RISK`](backend/core/enums.py:ThreatType) - Markt risico & volatiliteit
    *   *Voorbeelden:* Volatility spike detector, liquidity drought detector
*   [`SYSTEM_HEALTH`](backend/core/enums.py:ThreatType) - Systeem & technische gezondheid
    *   *Voorbeelden:* Connection monitor, data gap detector, latency monitor
*   [`STRATEGY_PERFORMANCE`](backend/core/enums.py:ThreatType) - Strategie performance
    *   *Voorbeelden:* Win rate degradation, parameter drift detector
*   [`EXTERNAL_EVENT`](backend/core/enums.py:ThreatType) - Externe events
    *   *Voorbeelden:* Breaking news monitor, regulatory change detector

**Organisatieprincipe:** Domein van risico

#### **PlanningPhase (4 sub-categorieën)**

Voor [`PlanningWorker`](backend/core/base_worker.py) plugins die plannen construeren:

*   [`ENTRY_PLANNING`](backend/core/enums.py:PlanningPhase) - Entry planning
    *   *Voorbeelden:* Limit entry planner, market entry planner, TWAP entry
*   [`EXIT_PLANNING`](backend/core/enums.py:PlanningPhase) - Exit planning (stops & targets)
    *   *Voorbeelden:* Liquidity target exit, ATR-based stops, fixed R:R
*   [`SIZE_PLANNING`](backend/core/enums.py:PlanningPhase) - Position sizing
    *   *Voorbeelden:* Fixed risk sizer, Kelly criterion, volatility-based sizing
*   [`ORDER_ROUTING`](backend/core/enums.py:PlanningPhase) - Order routing & execution tactics
    *   *Voorbeelden:* Default router, limit order router, iceberg router

**Organisatieprincipe:** Natuurlijke volgorde van trade planning

#### **ExecutionType (4 sub-categorieën)**

Voor [`ExecutionWorker`](backend/core/base_worker.py) plugins die uitvoeren en beheren:

*   [`TRADE_INITIATION`](backend/core/enums.py:ExecutionType) - Trade initiatie
    *   *Voorbeelden:* Plan executor, manual trade executor
*   [`POSITION_MANAGEMENT`](backend/core/enums.py:ExecutionType) - Actieve position management
    *   *Voorbeelden:* Trailing stop manager, partial profit taker, scale-in/out
*   [`RISK_SAFETY`](backend/core/enums.py:ExecutionType) - Risk & safety management
    *   *Voorbeelden:* Emergency exit agent, circuit breaker, forced liquidation
*   [`OPERATIONAL`](backend/core/enums.py:ExecutionType) - Operationele & geplande taken
    *   *Voorbeelden:* DCA rebalancer, scheduled rebalancing, portfolio cleanup

**Organisatieprincipe:** Aard van de actie en lifecycle fase

#### **Overzichtstabel**

| Worker Type | Sub-Categorie Enum | Aantal | Organisatie Principe |
|-------------|-------------------|--------|---------------------|
| [`ContextWorker`](backend/core/base_worker.py) | [`ContextType`](backend/core/enums.py:ContextType) | 7 | Type data-verrijking |
| [`OpportunityWorker`](backend/core/base_worker.py) | [`OpportunityType`](backend/core/enums.py:OpportunityType) | 7 | Strategische benadering |
| [`ThreatWorker`](backend/core/base_worker.py) | [`ThreatType`](backend/core/enums.py:ThreatType) | 5 | Domein van risico |
| [`PlanningWorker`](backend/core/base_worker.py) | [`PlanningPhase`](backend/core/enums.py:PlanningPhase) | 4 | Planningsfase |
| [`ExecutionWorker`](backend/core/base_worker.py) | [`ExecutionType`](backend/core/enums.py:ExecutionType) | 4 | Type actie |

**Totaal:** 5 hoofdcategorieën, 27 sub-categorieën

### **4.3.2. Dependencies (Het Data Contract)**

De dependencies-sectie is het formele contract dat definieert welke data een plugin nodig heeft om te functioneren en wat het produceert. Dit is de kern van de "context-bewuste" UI en validatie.

*   **requires (Verplichte DataFrame Kolommen)**: Een lijst van datakolommen die een ContextWorker als **harde eis** verwacht in de DataFrame (bv. \['high', 'low', 'close'\]). Het Assembly Team controleert of aan deze vereisten wordt voldaan.
*   **provides (Geproduceerde DataFrame Kolommen)**: Een lijst van nieuwe datakolommen die een ContextWorker als **output** toevoegt aan de DataFrame (bv. \['is\_swing\_high'\]).
*   **requires\_context (Verplichte Rijke Data)**: Een lijst van **niet-DataFrame** data-objecten die de plugin als **harde eis** verwacht in de TradingContext. Als deze data niet beschikbaar is, zal de plugin in de UI **uitgeschakeld** zijn en zal de ComponentBuilder een fout genereren bij de bootstrap.
    *   *Voorbeeld*: \['orderbook\_snapshot'\].
*   **uses (Optionele Rijke Data)**: Een lijst van **niet-DataFrame** data-objecten die de plugin kan gebruiken voor een **verbeterde analyse**, maar die **niet verplicht** zijn. Als deze data niet beschikbaar is, zal de plugin in een "fallback-modus" werken.
    *   *Voorbeeld*: \['tick\_by\_tick\_volume'\].
*   **produces\_events (Gepubliceerde Events)**: **Specifiek voor ThreatWorker-plugins** (was MonitorWorker). Dit is een lijst van de unieke event-namen die deze monitor kan publiceren op de EventBus.

### **4.3.3. Capabilities (Optioneel)**

Dit is de meest cruciale sectie van het manifest in de nieuwe architectuur. Het vervangt de oude `event_config` en legt alle extra vaardigheden vast die een worker nodig heeft. Standaard heeft een worker geen extra capabilities.

> **⚠️ BELANGRIJK PRINCIPE: Single Source of Truth**
>
> Het `manifest.yaml` is de **enige bron van waarheid** voor de behoeften van een plugin. De `WorkerBuilder` leest deze sectie en injecteert de benodigde functionaliteit via gespecialiseerde factories. Dit garandeert dat een plugin volledig zelfstandig en portable is.

```yaml
# manifest.yaml
capabilities:
  # Capability voor statefulness
  state:
    enabled: true
    state_dto: "dtos.state_dto.MyWorkerState"

  # Capability voor event-interactie
  events:
    enabled: true
    publishes:
      # Definieert welke events deze worker MAG publiceren
      - as_event: "MyCustomEventFired"
        payload_dto: "MyCustomSignal"
    wirings:
      # Definieert op welke events deze worker reageert en welke methode wordt aangeroepen
      - listens_to: "SomeTriggerEvent"
        invokes:
          method: "on_some_trigger"

  # Capability voor journaling
  journaling:
    enabled: true
```

### **4.3.4. Permissions (Optioneel)**

De `permissions`-sectie fungeert als een beveiligingscontract. Standaard heeft een plugin geen toegang tot externe bronnen.

-   **`network_access`**: Een 'allowlist' van netwerkbestemmingen.
-   **`filesystem_access`**: Een 'allowlist' van bestanden of mappen.

## **4.4. De Worker & het Architecturale Contract**

De `worker.py` bevat de daadwerkelijke logica. Om de ontwikkeling te standaardiseren, dwingt de architectuur een expliciete keuze af voor de **ROL** van de worker. De ontwikkelaar moet erven van een van de twee abstracte basisklassen.

### **De ROL-definitie: Het Architecturale Contract**

Een ontwikkelaar moet een van de volgende twee basisklassen kiezen. Dit definieert de architecturale rol van de worker.

```python
# backend/core/base_worker.py
from abc import ABC, abstractmethod

# De absolute basis, bevat alleen de __init__
class BaseWorker(ABC):
    def __init__(self, params: Any):
        self.params = params

# 1. De ROL en het contract voor een Standaard Worker
class StandardWorker(BaseWorker, ABC):
    """
    Definieert de ROL van een worker die deelneemt aan de georkestreerde
    pijplijn. Deze klasse dwingt de implementatie van een 'process'-methode af.
    """
    @abstractmethod
    def process(self, context: Any, **kwargs) -> Any:
        raise NotImplementedError

# 2. De ROL en het contract voor een Event-Driven Worker
class EventDrivenWorker(BaseWorker, ABC):
    """
    Definieert de ROL van een worker die uitsluitend reageert op events
    van de EventBus. Deze klasse heeft bewust GEEN 'process'-methode.
    Zijn methodes worden aangeroepen door de EventAdapter n.a.v. de
    'wirings' configuratie in het manifest.
    """
    pass
```

### **Voorbeeld van een StandardWorker**

Dit type worker is voor 90% van de gevallen de juiste keuze. Het is een pure, voorspelbare component in een georkestreerde pijplijn.

```python
# plugins/opportunity_workers/fvg_detector/worker.py
from backend.core.base_worker import StandardWorker
from backend.dtos.pipeline.signal import Signal

class FVGDetector(StandardWorker):
    """Detecteert Fair Value Gaps - pure, voorspelbare logica."""

    def process(self, context: TradingContext) -> List[Signal]:
        signals = []
        # Pure business logica...
        return signals
```

### **Voorbeeld van een EventDrivenWorker**

Dit type worker is voor autonome componenten die reageren op de EventBus.

```python
# plugins/threat_workers/dca_risk_assessor/worker.py
from backend.core.base_worker import EventDrivenWorker

class DCARiskAssessor(EventDrivenWorker):
    """Beoordeelt risico's n.a.v. een wekelijkse tick."""

    def assess_risk(self, payload: Any):
        # Deze methode wordt aangeroepen door de EventAdapter
        # zoals geconfigureerd in manifest.yaml
        risk_event = self._calculate_risk()
        if risk_event:
            # De 'emit' functie is dynamisch geïnjecteerd
            # door de EventAdapterFactory omdat de 'events'
            # capability is aangevraagd in het manifest.
            self.emit("dca_risk_assessed", risk_event)
```

### **Dynamisch Geïnjecteerde Capabilities**

Functionaliteit zoals `self.state`, `self.emit` en `self.log_entry` wordt niet langer verkregen via overerving van verschillende basisklassen. In plaats daarvan worden deze methodes en properties dynamisch geïnjecteerd door de `WorkerBuilder` en de bijbehorende factories wanneer een plugin de betreffende capability aanvraagt in zijn `manifest.yaml`.

Dit zorgt voor een zuivere scheiding:

-   De **klasse** (`worker.py`) definieert de **ROL** en de businesslogica.
-   De **configuratie** (`manifest.yaml`) definieert de **CAPABILITIES** die de worker nodig heeft om die logica uit te voeren.

**Zie ook:**
-   [`Uitwerking Kernafwijking #4`](docs/development/251014%20Bijwerken%20documentatie/Uitwerking%20Kernafwijking%20%234%20-%20Gelaagde%20Plugin%20Capaciteiten.md) - Volledige uitwerking gelaagde capaciteiten
-   [`Uitwerking Kernafwijking #4A2`](docs/development/251014%20Bijwerken%20documentatie/Uitwerking%20Kernafwijking%20%234A2%20-%20Plugin%20Event%20Architectuur.md) - Deep dive event architectuur