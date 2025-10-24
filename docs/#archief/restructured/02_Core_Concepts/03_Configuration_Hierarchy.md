# Configuration Hierarchy: YAML Structuur

**Versie:** 3.0
**Status:** Definitief

Dit document beschrijft de "configuratie trein": de logische hiërarchie en samenhang van de YAML-bestanden die een volledige, gevalideerde en uitvoerbare operatie definiëren, gebaseerd op de drie gescheiden configuratielagen.

---

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Voorwoord: Configuratie is Koning](#voorwoord-configuratie-is-koning)
3. [Configuratie Lagen](#configuratie-lagen)
4. [Het Landschap van de Configuratie](#het-landschap-van-de-configuratie)
5. [De Platform- & Systeemarchitectuur](#de-platform--systeemarchitectuur)
6. [De Operationele Configuratie](#de-operationele-configuratie)
7. [Event & Capability Configuratie](#event--capability-configuratie)
8. [De Onderlinge Samenhang](#de-onderlinge-samenhang)
9. [Configuratie Validatie](#configuratie-validatie)
10. [Best Practices](#best-practices)

---

## **Executive Summary**

In de S1mpleTrader-architectuur is de configuratie de applicatie. De YAML-bestanden vormen het complete "draaiboek" dat de operatie van het trading-ecosysteem beschrijft, gebaseerd op het principe: **"Configuratie is Koning"**. Dit document beschrijft de "configuratie trein", de logische hiërarchie van YAML-bestanden die samen een volledige operatie definiëren.

### **Kernkenmerken**

**1. Drie Gescheiden Configuratielagen**
- PlatformConfig: Globale, statische platform instellingen
- OperationConfig: Specifieke werkruimte met strategieën en omgevingen
- StrategyConfig: Gebruikersintentie voor één strategie

**2. ConfigTranslator en BuildSpecs**
- ConfigTranslator vertaalt configuratielagen naar machine-instructies
- BuildSpecs bevatten complete instructies voor runtime componenten
- Volledige scheiding tussen configuratie en runtime

**3. Platgeslagen Bedrading**
- Geen Operator-laag meer; directe worker-naar-worker communicatie
- UI-gegenereerde strategy_wiring_map voor expliciete flow
- Base wiring templates voor standaard patterns

**4. Manifest-Gedreven Capabilities**
- Workers declareren hun behoeften in manifest.yaml
- Capabilities worden geïnjecteerd door WorkerBuilder
- Opt-in complexiteit via configuratie

### **Design Principes**

✅ **Configuratie is Koning** - Alle operationele logica is gedefinieerd in YAML
✅ **Scheiding van Verantwoordelijkheden** - Elke configuratielaag heeft één duidelijke functie
✅ **Fail Fast Validatie** - Het systeem valideert de volledige configuratie-keten bij opstart
✅ **Expliciete Contracten** - Configuratiebestanden zijn zelf-documenterend

---

## **Voorwoord: Configuratie is Koning**

> **"Configuratie is Koning"**

In de S1mpleTrader-architectuur is de configuratie niet slechts een set instellingen - het **IS** de applicatie. De YAML-bestanden zijn het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft. Het platform zelf is een agnostische uitvoerder die tot leven komt op basis van deze bestanden.

**Van Hard-Coded naar Configuratie-Gedreven**

De architectuur markeert een fundamentele paradigma-shift:
- **Vorige aanpak**: Logica was hard-coded in Python classes
- **Huidige aanpak**: Configuratie dicteert gedrag, code is mechanica

Dit document beschrijft de "configuratie trein": de logische hiërarchie en samenhang van de verschillende YAML-bestanden die samen een volledige, gevalideerde en uitvoerbare operatie definiëren.

---

## **Configuratie Lagen**

Het systeem gebruikt drie strikt gescheiden configuratielagen, elk met een eigen doel en levenscyclus.

### **PlatformConfig (De Fundering)**

Bevat alle globale, statische en run-onafhankelijke configuratie van het platform.

```yaml
# platform.yaml
language: "nl"
logging:
  profile: "analysis"
  levels: ["DEBUG", "INFO", "SETUP", "MATCH", "FILTER", "RESULT", "TRADE", "ERROR"]
archiving:
  format: "parquet"
plugins_root_path: "plugins"
data_root_path: "data"
```

### **OperationConfig (De Werkruimte)**

Definieert een specifieke "werkruimte" of "campagne" met alle technische middelen en strategieën.

```yaml
# operation.yaml
display_name: "Mijn BTC Operatie"
description: "Live trading en backtesting voor BTC strategieën"
strategy_links:
  - strategy_blueprint_id: "ict_smc_strategy"
    execution_environment_id: "live_kraken_main"
    is_active: true
  - strategy_blueprint_id: "smart_dca_btc"
    execution_environment_id: "backtest_2020_2024"
    is_active: true
```

### **StrategyConfig (De Blauwdruk)**

Vertegenwoordigt de volledige gebruikersintentie voor één specifieke strategie.

```yaml
# strategy_blueprint.yaml
display_name: "ICT/SMC Strategy"
version: "1.0.0"
description: "ICT methodology with FVG entries and liquidity targets"

workforce:
  context_workers:
    - plugin: "market_structure_detector"
      subtype: "structural_analysis"
      params:
        detect_bos: true
        detect_choch: true

  opportunity_workers:
    - plugin: "fvg_detector"
      subtype: "technical_pattern"
      params:
        min_gap_size: 5
        require_structure_break: true
```

### **ConfigTranslator**

De centrale component die alle configuratielagen vertaalt naar machine-instructies (BuildSpecs).

```python
class ConfigTranslator:
    def collect_build_specs(self, strategy_config, platform_config, operation_config):
        # Genereert complete BuildSpecs voor runtime componenten
        return BuildSpecCollection(
            workforce_spec=self._build_workforce_spec(strategy_config),
            wiring_spec=self._build_wiring_spec(strategy_config),
            environment_spec=self._build_environment_spec(operation_config)
        )
```

---

## **Het Landschap van de Configuratie**

De configuratie is opgedeeld in een reeks van gespecialiseerde bestanden. Elk bestand heeft een duidelijke Single Responsibility (SRP).

**De Hiërarchie (van Stabiel naar Dynamisch):**

1. [`platform.yaml`](config/platform.yaml) - De fundering van het hele platform
2. [`connectors.yaml`](config/connectors.yaml) - De technische "stekkerdoos" voor live verbindingen
3. [`data_sources.yaml`](config/data_sources.yaml) - De catalogus van lokale historische datasets
4. [`environments.yaml`](config/environments.yaml) - De definitie van de abstracte "werelden"
5. [`event_map.yaml`](config/event_map.yaml) - De grondwet van de interne communicatie
6. [`base_wiring.yaml`](config/base_wiring.yaml) - De standaard bouwplaat voor flow templates
7. [`schedule.yaml`](config/schedule.yaml) - De agnostische "metronoom" van het systeem
8. [`operation.yaml`](config/operation.yaml) - Het centrale "draaiboek" van de quant
9. [`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml) - De gedetailleerde "receptenkaart"
10. [`strategy_wiring_map.yaml`](config/runs/strategy_wiring_map.yaml) - De UI-gegenereerde "bedrading"
11. [`plugin_manifest.yaml`](plugins/*/plugin_manifest.yaml) - De "ID-kaart" van elke individuele plugin

---

## **De Platform- & Systeemarchitectuur**

Deze bestanden vormen de stabiele basis. Ze worden doorgaans één keer opgezet en veranderen zelden.

### **platform.yaml - De Fundering**

* **Doel**: Definieert globale, niet-strategische instellingen voor het hele platform. Dit is het domein van de platformbeheerder, niet van de quant.
* **Inhoud**:
  * **Logging-profielen**: Definieert welke log-niveaus worden getoond
  * **Taalinstellingen**: Bepaalt de standaardtaal voor de UI en logs
  * **Archiveringsformaat**: Bepaalt of resultaten worden opgeslagen als csv, parquet, etc.
  * **Bestandspaden**: Definieert de root-locatie van de plugins-map

* **Voorbeeld**:
```yaml
# config/platform.yaml
language: "nl"
logging:
  profile: "analysis"
  levels: ["DEBUG", "INFO", "SETUP", "MATCH", "FILTER", "RESULT", "TRADE", "ERROR"]
archiving:
  format: "parquet"
plugins_root_path: "plugins"
data_root_path: "data"
```

### **connectors.yaml - De Stekkerdoos**

* **Doel**: Centraliseert de technische configuratie van **alle** mogelijke verbindingen met externe, **live** partijen (exchanges).
* **Inhoud**: Een lijst van benoemde connector-instanties. Elke instantie heeft een unieke naam, een type, en de benodigde credentials en API-eindpunten.

* **Voorbeeld**:
```yaml
# config/connectors.yaml
kraken_live_eur_account:
  type: "kraken_private"
  api_key: "${KRAKEN_API_KEY}"
  api_secret: "${KRAKEN_API_SECRET}"

binance_paper_trading:
  type: "binance_public"
  base_url: "https://testnet.binance.vision/api"
```

### **data_sources.yaml - De Archievenkast**

* **Doel**: Centraliseert de definitie van alle beschikbare, op schijf opgeslagen, **historische datasets** (archieven). Dit creëert een register van alle "backtest-werelden".
* **Inhoud**: Een lijst van benoemde data sources. Elke data source heeft een unieke naam en specificaties over de fysieke locatie en het type data.

* **Voorbeeld**:
```yaml
# config/data_sources.yaml
btc_eur_15m_archive:
  type: "parquet_archive"
  path: "source_data/BTC_EUR_15m/"
  asset_pair: "BTC/EUR"
  timeframe: "15m"
```

### **environments.yaml - De Werelden**

* **Doel**: Definieert de operationele "werelden" (live, paper, backtest) en koppelt ze aan een technische bron.
* **Inhoud**: Een lijst van benoemde omgevingen met een unieke naam, een type, en een verwijzing naar ofwel een connector_id ofwel een data_source_id.

* **Voorbeeld**:
```yaml
# config/environments.yaml
live_kraken_main:
  type: "live"
  connector_id: "kraken_live_eur_account"

backtest_2020_2024_btc:
  type: "backtest"
  data_source_id: "btc_eur_15m_archive"
```

### **event_map.yaml - De Grondwet van de Communicatie**

* **Doel**: Functioneert als de strikte "Grondwet" voor alle communicatie op de EventBus. Het definieert welke events mogen bestaan en wat hun exacte data-contract is.
* **Inhoud**: Een lijst van alle toegestane event-namen met hun verplichte payload_dto-contract.

* **Voorbeeld**:
```yaml
# config/event_map.yaml
events:
  - event_name: "OperationStarted"
    payload_dto: "OperationParameters"
  - event_name: "ContextReady"
    payload_dto: "TradingContext"
  - event_name: "SignalsGenerated"
    payload_dto: "List[Signal]"
  - event_name: "ThreatsDetected"
    payload_dto: "List[CriticalEvent]"
```

### **base_wiring.yaml - De Standaard Bouwplaat**

* **Doel**: Een configureerbaar template dat de standaard logische flow beschrijft tussen worker-categorieën.
* **Inhoud**: Een lijst wiring_rules, waarbij component_id verwijst naar categorie-namen.

* **Voorbeeld**:
```yaml
# config/base_wiring.yaml
base_wiring_id: "standard_trading_flow_v1"
wiring_rules:
  - wiring_id: "ctx_to_opp"
    source:
      component_id: "ContextWorker"
      event_name: "ContextOutput"
    target:
      component_id: "OpportunityWorker"
      handler_method: "process"
  - wiring_id: "opp_to_plan"
    source:
      component_id: "OpportunityWorker"
      event_name: "OpportunityOutput"
    target:
      component_id: "PlanningWorker"
      handler_method: "process"
```

### **schedule.yaml - De Metronoom**

* **Doel**: Configureert de Scheduler service voor alle tijd-gebaseerde events.
* **Inhoud**: Een lijst van event-definities, elk met een event_name en een type (interval of cron).

* **Voorbeeld**:
```yaml
# config/schedule.yaml
schedules:
  - name: "weekly_dca"
    event: "WEEKLY_DCA_TICK"
    type: "cron"
    value: "0 10 * * 1"  # Every Monday 10:00
    timezone: "Europe/Amsterdam"
```

---

## **De Operationele Configuratie**

Deze bestanden beschrijven de **strategische en operationele intentie** van de quant.

### **operation.yaml - Het Centrale Draaiboek**

* **Doel**: Het **hoofdbestand** dat een volledige operatie definieert door strategy_links te creëren die blueprints aan environments koppelen.
* **Inhoud**: Een display_name, description, en een lijst van strategy_links, elk met een strategy_blueprint_id en een execution_environment_id.

* **Voorbeeld**:
```yaml
# config/operations/my_btc_operation.yaml
display_name: "Mijn BTC Operatie (Live & Backtest)"
description: "Draait een ICT/SMC strategie live en backtest een DCA strategie."
strategy_links:
  - strategy_blueprint_id: "ict_smc_strategy"
    execution_environment_id: "live_kraken_main"
    is_active: true

  - strategy_blueprint_id: "smart_dca_btc"
    execution_environment_id: "backtest_2020_2024_btc"
    is_active: true
```

### **strategy_blueprint.yaml - Het Gedetailleerde Recept**

* **Doel**: Bevat de **volledige configuratie van alle plugins** (workforce) voor één strategy_link.
* **Huidige structuur**: 5 worker categorieën met gestructureerde sub-categorieën

#### **De 5-Worker Structuur**:

```yaml
# strategy_blueprint.yaml
display_name: "ICT/SMC Strategy"
version: "1.0.0"
description: "ICT/SMC methodologie met FVG entries en liquidity targets"

workforce:
  # === 1. CONTEXT WORKERS ===
  # Bouw de "kaart" van de markt
  context_workers:
    - plugin: "market_structure_detector"
      subtype: "structural_analysis"
      params:
        detect_bos: true          # Break of Structure
        detect_choch: true        # Change of Character

    - plugin: "regime_classifier"
      subtype: "regime_classification"
      params:
        lookback_period: 100

  # === 2. OPPORTUNITY WORKERS ===
  # Detecteer handelskansen
  opportunity_workers:
    - plugin: "fvg_detector"
      subtype: "technical_pattern"
      params:
        min_gap_size: 5
        require_structure_break: true

    - plugin: "liquidity_sweep_detector"
      subtype: "momentum_signal"
      params:
        detect_stop_hunts: true

  # === 3. THREAT WORKERS ===
  # Monitor risico's (parallel aan opportunity detection)
  threat_workers:
    - plugin: "max_drawdown_monitor"
      subtype: "portfolio_risk"
      params:
        max_daily_drawdown: 2.0

    - plugin: "news_event_monitor"
      subtype: "market_risk"
      params:
        high_impact_events: true
        pause_trading_minutes_before: 30

  # === 4. PLANNING WORKERS ===
  # Transformeer kansen naar concrete plannen
  # Gestructureerd in 4 sub-fasen
  planning_workers:
    entry_planning:
      - plugin: "limit_entry_at_fvg"
        params:
          entry_at_fvg_midpoint: true

    exit_planning:
      - plugin: "liquidity_target_exit"
        params:
          target_opposite_liquidity: true
          stop_below_order_block: true

    size_planning:
      - plugin: "fixed_risk_sizer"
        params:
          risk_per_trade_percent: 1.0

    order_routing:
      - plugin: "limit_order_router"

  # === 5. EXECUTION WORKERS ===
  # Voer uit en beheer actieve posities
  # Gestructureerd in 4 sub-categorieën
  execution_workers:
    trade_initiation:
      - plugin: "default_plan_executor"

    position_management:
      - plugin: "partial_profit_taker"
        params:
          take_50_percent_at_first_target: true
          move_stop_to_breakeven: true

    risk_safety:
      - plugin: "emergency_exit_agent"
        params:
          exit_on_severity: ["CRITICAL", "HIGH"]
```

#### **Sub-Categorie Specificatie**:

Elke worker categorie heeft zijn eigen sub-types:

| Categorie | Sub-Type Enum | Aantal | Voorbeelden |
|-----------|---------------|--------|-------------|
| ContextWorker | ContextType | 7 | regime_classification, structural_analysis, indicator_calculation |
| OpportunityWorker | OpportunityType | 7 | technical_pattern, momentum_signal, mean_reversion |
| ThreatWorker | ThreatType | 5 | portfolio_risk, market_risk, system_health |
| PlanningWorker | PlanningPhase | 4 | entry_planning, exit_planning, size_planning, order_routing |
| ExecutionWorker | ExecutionType | 4 | trade_initiation, position_management, risk_safety, operational |

---

## **Event & Capability Configuratie**

S1mpleTrader hanteert het "Manifest-Gedreven Capability Model". De configuratie van een worker is strikt gescheiden in zijn **ROL** (de basisklasse die de ontwikkelaar kiest) en zijn **CAPABILITIES** (de extra functies die in het manifest worden aangevraagd).

### **Niveau 1: Standaard Pijplijn (Geen Capability Nodig)**

**Voor wie**: De meeste quants die een lineaire strategie bouwen.
**Hoe het werkt**: De ontwikkelaar kiest de `StandardWorker` als basisklasse. Er is geen `capabilities`-sectie nodig in het manifest, tenzij state of journaling wordt gebruikt. Het systeem creëert automatisch de dataflow tussen de workers.

**Voorbeeld**:
Een `fvg_detector` erft van `StandardWorker`. Zijn manifest is minimaal:

```yaml
# plugins/opportunity_workers/fvg_detector/manifest.yaml
identification:
  name: "fvg_detector"
  type: "opportunity_worker"
  subtype: "technical_pattern"
  # ... etc.
# Geen 'capabilities' sectie nodig voor basisfunctionaliteit
```

De `strategy_blueprint.yaml` wijst de worker simpelweg toe aan de juiste categorie:

```yaml
# strategy_blueprint.yaml
workforce:
  opportunity_workers:
    - plugin: "fvg_detector"
```

### **Niveau 2: Event-Gedreven Workers (Capability Configuratie)**

**Voor wie**: Quants die autonome workers willen bouwen die reageren op de EventBus.
**Hoe het werkt**:

1. De ontwikkelaar kiest de `EventDrivenWorker` als basisklasse. Deze klasse heeft geen `process`-methode.
2. In het `manifest.yaml` wordt de `events`-capability geactiveerd. Hier worden de `publishes` (wat de worker mag uitzenden) en `wirings` (waar de worker op reageert) gedefinieerd.

**Voorbeeld: Smart DCA met Event Coördinatie**:
De `dca_opportunity_scorer` erft van `EventDrivenWorker`. Zijn manifest definieert zijn volledige event-contract:

```yaml
# plugins/opportunity_workers/dca_opportunity_scorer/manifest.yaml
identification:
  name: "dca_opportunity_scorer"
  type: "opportunity_worker"
  subtype: "technical_pattern"
  # ... etc.

capabilities:
  events:
    enabled: true
    publishes:
      - event: "dca_opportunity_scored"
        payload_type: "Signal"
    wirings:
      - listens_to: "WEEKLY_DCA_TICK"
        invokes:
          method: "on_weekly_tick"
```

De `strategy_blueprint.yaml` hoeft alleen de worker toe te wijzen. De volledige event-logica staat nu in het manifest.

```yaml
# strategy_blueprint.yaml
workforce:
  opportunity_workers:
    - plugin: "dca_opportunity_scorer"
```

Deze aanpak zorgt voor een **Single Source of Truth**: het manifest van een plugin beschrijft zijn volledige set van benodigde vaardigheden, wat het systeem transparant en robuust maakt.

---

## **De Onderlinge Samenhang**

De magie van het systeem zit in hoe alle componenten samenwerken tijdens de bootstrap-fase.

**Voorbeeld Flow**:

1. **Startpunt**: De gebruiker start de applicatie met de opdracht: `run ict_smc_operation`

2. **ConfigTranslator leest alle configuratie**:
   - [`platform.yaml`](config/platform.yaml)
   - [`operation.yaml`](config/operation.yaml)
   - [`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml)
   - [`base_wiring.yaml`](config/base_wiring.yaml)
   - [`strategy_wiring_map.yaml`](config/runs/strategy_wiring_map.yaml)

3. **ConfigTranslator genereert BuildSpecs**:
   - platform_wiring_spec
   - strategy_wiring_spec
   - workforce_spec

4. **EventWiringFactory creëert EventAdapters**:
   - Leest wiring_specs uit BuildSpecs
   - Creëert geconfigureerde adapters voor alle componenten

5. **WorkerBuilder bouwt workers**:
   - Leest manifests van alle plugins
   - Injecteert capabilities op basis van manifest
   - Creëert worker instanties

6. **Systeem is klaar**: EventBus is geconfigureerd, alle subscriptions zijn actief

Het resultaat is een volledig geassembleerd, gevalideerd en onderling verbonden ecosysteem van plugins en adapters, klaar om van start te gaan, **puur en alleen op basis van de declaratieve YAML-bestanden**.

---

## **Configuratie Validatie**

Het systeem valideert automatisch de volledige configuratie tijdens bootstrap:

**Validatie Checks**:

1. **Schema Validatie**: Alle YAML bestanden tegen Pydantic schemas
2. **Referentie Validatie**: Alle ID verwijzingen bestaan
3. **Event Chain Validatie**: Alle triggers hebben een publisher
4. **Dependency Validatie**: Alle plugin dependencies zijn vervuld
5. **Capability Validatie**: Manifest declarations zijn consistent

**Error Handling**:
```python
try:
    config_validator.validate_all()
except ConfigurationError as e:
    if isinstance(e, MissingReferenceError):
        print(f"❌ Configuration error: {e.field} '{e.value}' not found in {e.source_file}")
    elif isinstance(e, EventChainError):
        print(f"❌ Event chain error: Worker '{e.worker}' triggers '{e.event}' but no publisher found")
```

---

## **Best Practices**

### **DO's**:

✅ **Start simpel** - Gebruik standaard flows tenzij je specifieke behoeften hebt
✅ **Gebruik sub-types** - Ze helpen met organisatie en plugin discovery
✅ **Test je configuratie** - Gebruik de validatie tools voordat je live gaat
✅ **Documenteer custom events** - Maak duidelijk wat elk event betekent
✅ **Volg naming conventions** - Consistent gebruik van snake_case voor IDs

### **DON'Ts**:

❌ **Complexiteit zonder reden** - Gebruik geen custom events als standaard flows voldoen
❌ **Circular dependencies** - Voorkom event loops in je configuratie
❌ **Hard-coded waarden** - Gebruik environment variables voor credentials
❌ **Te veel workers** - Begin klein, schaal op waar nodig
❌ **Onduidelijke IDs** - Gebruik beschrijvende namen voor alle identifiers

---

**Einde Document**

Voor meer details over specifieke concepten, zie:
- **[Worker Ecosystem](01_Worker_Ecosystem.md)** - 5-worker model en sub-types
- **[Event Architecture](02_Event_Architecture.md)** - Event system en 3-niveaus
- **[Plugin Anatomy](03_Development/01_Plugin_Anatomy.md)** - Plugin development guide

---

**Einde Document**