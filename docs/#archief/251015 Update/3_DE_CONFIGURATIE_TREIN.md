# **3. De Configuratie Trein: Een Gids voor S1mpleTrader V2 YAML-bestanden**

Versie: 2.0 (Configuratie-Gedreven Architectuur)  
Status: Definitief

## **3.1. Voorwoord: Configuratie is Koning**

> **"Operators zijn dom, configuratie is slim"**

In de S1mpleTrader V2 architectuur is de configuratie niet slechts een set instellingen - het **IS** de applicatie. De YAML-bestanden zijn het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft. Het platform zelf is een agnostische uitvoerder die tot leven komt op basis van deze bestanden.

**SHIFT 2: Van Hard-Coded naar Data-Driven**

De evolutie van V1 naar V2 markeert een fundamentele paradigma-shift:
- **V1**: Operator-logica was hard-coded in Python classes
- **V2**: Operators zijn generieke executors, configuratie dicteert gedrag

Dit document beschrijft de "configuratie trein": de logische hiërarchie en samenhang van de verschillende YAML-bestanden die samen een volledige, gevalideerde en uitvoerbare operatie definiëren. We volgen de stroom van de meest stabiele, platform-brede bestanden tot de meest specifieke, gedetailleerde plugin-parameters.

## **3.2. Het Landschap van de Configuratie**

De configuratie is opgedeeld in een reeks van gespecialiseerde bestanden. Elk bestand heeft een duidelijke Single Responsibility (SRP).

**De Hiërarchie (van Stabiel naar Dynamisch):**

1. [`platform.yaml`](config/platform.yaml) - De fundering van het hele platform
2. [`operators.yaml`](config/operators.yaml) - **NIEUW**: Het gedrag van alle operators ⭐
3. [`connectors.yaml`](config/connectors.yaml) - De technische "stekkerdoos" voor **live** verbindingen
4. [`data_sources.yaml`](config/data_sources.yaml) - De catalogus van **lokale** historische datasets
5. [`environments.yaml`](config/environments.yaml) - De definitie van de abstracte "werelden"
6. [`event_map.yaml`](config/event_map.yaml) - De grondwet van de interne communicatie
7. [`wiring_map.yaml`](config/wiring_map.yaml) - De bouwtekening van de dataflow
8. [`schedule.yaml`](config/schedule.yaml) - De agnostische "metronoom" van het systeem
9. [`operation.yaml`](config/operation.yaml) - Het centrale "draaiboek" van de quant
10. [`strategy_blueprint.yaml`](config/runs/strategy_blueprint.yaml) - De gedetailleerde "receptenkaart"
11. [`plugin_manifest.yaml`](plugins/*/plugin_manifest.yaml) - De "ID-kaart" van elke individuele plugin

## **3.3. De Platform- & Systeemarchitectuur**

Deze bestanden vormen de stabiele basis. Ze worden doorgaans één keer opgezet en veranderen zelden.

### **3.3.1. platform.yaml - De Fundering**

* **Doel**: Definieert globale, niet-strategische instellingen voor het hele platform. Dit is het domein van de platformbeheerder, niet van de quant.
* **Inhoud**:
  * **Logging-profielen**: Definieert welke log-niveaus worden getoond (developer, analysis)
  * **Taalinstellingen**: Bepaalt de standaardtaal voor de UI en logs
  * **Archiveringsformaat**: Bepaalt of resultaten worden opgeslagen als csv, parquet, etc.
  * **Bestandspaden**: Definieert de root-locatie van de plugins-map

* **Voorbeeld (Conceptueel)**:
```yaml
# config/platform.yaml
language: "nl"
logging:
  profile: "analysis"
  profiles:
    developer: [INFO, WARNING, ERROR]
    analysis: [DEBUG, INFO, SETUP, MATCH, FILTER, RESULT, TRADE, ERROR]
archiving:
  format: "parquet"
plugins_root_path: "plugins"
```

### **3.3.2. operators.yaml - Het Configuratie-Hart** ⭐

> **"Operators zijn dom, configuratie is slim"**

* **Doel**: Het **meest cruciale configuratiebestand** dat het gedrag van alle 5 operators definieert. Dit bestand maakt het mogelijk om orkestratie-strategieën te wijzigen zonder een regel code aan te passen.

* **Waarom Dit Cruciaal Is**:
  - **Voor V2**: Elk operator type had eigen hard-coded logica
  - **In V2**: Eén [`BaseOperator`](backend/core/operators/base_operator.py) class, vijf configuraties
  - **Resultaat**: Maximum flexibiliteit, geen code-wijzigingen nodig

* **Structuur**:
```yaml
# config/operators.yaml
operators:
  - operator_id: "ContextOperator"
    manages_worker_type: "ContextWorker"
    execution_strategy: "SEQUENTIAL"      # Hoe worden workers uitgevoerd?
    aggregation_strategy: "CHAIN_THROUGH" # Hoe worden outputs gecombineerd?
```

Execution Strategies:

| Strategy | Beschrijving | Gebruikt door OperatorFactory voor... |
|---|---|---|
| `SEQUENTIAL` | Workers draaien één voor één, output → input chaining | `ContextOperator`, `PlanningOperator` |
| `PARALLEL` | Workers draaien tegelijkertijd, verzamel alle outputs | `OpportunityOperator`, `ThreatOperator` |
| `EVENT_DRIVEN` | Setup-signaal: Geeft aan dat de workers `EventDrivenWorkers` zijn die autonoom opereren. De `BaseOperator` zelf heeft GEEN runtime-logica voor deze strategie. | `ExecutionOperator` |

#### **Volledige Configuratie voor Alle 5 Operators**:

```yaml
# config/operators.yaml
operators:
  # === CONTEXT OPERATOR ===
  # Verrijkt context sequentieel, elke worker bouwt voort op de vorige
  - operator_id: "ContextOperator"
    manages_worker_type: "ContextWorker"
    execution_strategy: "SEQUENTIAL"
    aggregation_strategy: "CHAIN_THROUGH"
    rationale: >
      Context workers (altijd StandardWorker) moeten sequentieel draaien omdat
      latere workers vaak afhankelijk zijn van de output van eerdere.

  # === OPPORTUNITY OPERATOR ===
  # Zoekt parallel naar kansen, verzamel alle gevonden signalen
  - operator_id: "OpportunityOperator"
    manages_worker_type: "OpportunityWorker"
    execution_strategy: "PARALLEL"
    aggregation_strategy: "COLLECT_ALL"
    rationale: >
      Opportunity workers (altijd StandardWorker) kunnen onafhankelijk en
      tegelijkertijd verschillende patronen herkennen.

  # === THREAT OPERATOR ===
  # Monitort parallel voor risico's, verzamel alle detecties
  - operator_id: "ThreatOperator"
    manages_worker_type: "ThreatWorker"
    execution_strategy: "PARALLEL"
    aggregation_strategy: "COLLECT_ALL"
    rationale: >
      Threat workers (kunnen StandardWorker of EventDrivenWorker zijn)
      detecteren parallel risico's. De operator beheert alleen de StandardWorkers.

  # === PLANNING OPERATOR ===
  # Plant sequentieel: entry → exit → size → routing
  - operator_id: "PlanningOperator"
    manages_worker_type: "PlanningWorker"
    execution_strategy: "SEQUENTIAL"
    aggregation_strategy: "CHAIN_THROUGH"
    rationale: >
      Planning workers (altijd StandardWorker) zijn sequentieel; elke fase
      verfijnt het plan op basis van de vorige fase.

  # === EXECUTION OPERATOR ===
  # De workers zijn autonoom en reageren op events.
  - operator_id: "ExecutionOperator"
    manages_worker_type: "ExecutionWorker"
    execution_strategy: "EVENT_DRIVEN"
    aggregation_strategy: "NONE"
    rationale: >
      De 'EVENT_DRIVEN' strategie signaleert aan de assembly-laag dat deze
      workers van het type EventDrivenWorker zijn. De operator zelf
      orkestreert ze niet; ze worden direct aan de EventBus gekoppeld.
```

#### **Configuratie Override per Strategy**:

Je kunt operator gedrag ook per strategy overriden:

```yaml
# strategy_blueprint.yaml
name: "Experimental_Parallel_Planning"

# Override default operator behavior
operator_overrides:
  PlanningOperator:
    execution_strategy: "PARALLEL"  # Test parallel planning
    aggregation_strategy: "COLLECT_ALL"

workforce:
  # ... rest van configuratie
```

### **3.3.3. connectors.yaml - De Stekkerdoos**

* **Doel**: Centraliseert de technische configuratie van **alle** mogelijke verbindingen met externe, **live** partijen (exchanges).
* **Inhoud**: Een lijst van benoemde connector-instanties. Elke instantie heeft een unieke naam (de *identifier*), een type (die de ConnectorFactory vertelt welke Python-klasse hij moet gebruiken), en de benodigde credentials en API-eindpunten.

* **Voorbeeld (Conceptueel)**:
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

### **3.3.4. data_sources.yaml - De Archievenkast**

* **Doel**: Centraliseert de definitie van alle beschikbare, op schijf opgeslagen, **historische datasets** (archieven). Dit creëert een register van alle "backtest-werelden".
* **Inhoud**: Een lijst van benoemde data sources. Elke data source heeft een unieke naam (de *identifier*) en specificaties over de fysieke locatie en het type data.

* **Voorbeeld (Conceptueel)**:
```yaml
# config/data_sources.yaml
btc_eur_15m_archive:
  type: "parquet_archive"
  path: "source_data/BTC_EUR_15m/"
  asset_pair: "BTC/EUR"
  timeframe: "15m"
```

### **3.3.5. environments.yaml - De Werelden**

* **Doel**: Definieert de operationele "werelden" (live, paper, backtest) en koppelt ze aan een technische bron.
* **Inhoud**: Een lijst van benoemde omgevingen met een unieke naam, een type, en een verwijzing naar ofwel een connector_id ofwel een data_source_id.

* **Voorbeeld (Conceptueel)**:
```yaml
# config/environments.yaml
live_kraken_main:
  type: "live"
  connector_id: "kraken_live_eur_account" # VERWIJST NAAR connectors.yaml

backtest_2020_2024_btc:
  type: "backtest"
  data_source_id: "btc_eur_15m_archive" # VERWIJST NAAR data_sources.yaml
```

### **3.3.6. event_map.yaml - De Grondwet van de Communicatie**

* **Doel**: Functioneert als de strikte "Grondwet" voor alle communicatie op de EventBus. Het definieert welke events mogen bestaan en wat hun exacte data-contract is.
* **Inhoud**: Een lijst van alle toegestane event-namen met hun verplichte payload_dto-contract.

* **Voorbeeld (Conceptueel)**:
```yaml
# config/event_map.yaml
- event_name: "OperationStarted"
  payload_dto: "OperationParameters"
- event_name: "ContextReady"
  payload_dto: "TradingContext"
- event_name: "OpportunityDetected"
  payload_dto: "OpportunitySignal"
- event_name: "ThreatDetected"
  payload_dto: "ThreatEvent"
```

### **3.3.7. wiring_map.yaml - De Bouwtekening van de Dataflow**

* **Doel**: De "bouwtekening" die beschrijft hoe Operators via EventAdapters op de EventBus worden aangesloten. Het definieert de dataflow: welk event triggert welke actie?
* **Inhoud**: Een lijst van "wiring"-regels die een component en method koppelen aan een listens_to event, en specificeren hoe het resultaat gepubliceerd wordt (publishes_result_as).

* **Voorbeeld (Conceptueel)**:
```yaml
# config/wiring_map.yaml
- adapter_id: "ContextPipelineAdapter"
  listens_to: "MarketDataReceived"
  invokes:
    component: "ContextOperator"
    method: "run_pipeline"
  publishes_result_as: "ContextReady"

- adapter_id: "OpportunityPipelineAdapter"
  listens_to: "ContextReady"
  invokes:
    component: "OpportunityOperator"
    method: "run_pipeline"
  publishes_result_as: "OpportunityDetected"
```

### **3.3.8. schedule.yaml - De Metronoom**

* **Doel**: Configureert de Scheduler service voor alle tijd-gebaseerde events.
* **Inhoud**: Een lijst van event-definities, elk met een event_name en een type (interval of cron).

* **Voorbeeld (Conceptueel)**:
```yaml
# config/schedule.yaml
schedules:
  - name: "five_minute_reconciliation"
    event: "RECONCILIATION_TICK"
    type: "interval"
    value: "5m"
  
  - name: "daily_dca_buy_signal"
    event: "WEEKLY_DCA_TICK"
    type: "cron"
    value: "0 10 * * 1"  # Elke maandag 10:00
    timezone: "Europe/Amsterdam"
```

## **3.4. De Operationele Configuratie**

Deze bestanden beschrijven de **strategische en operationele intentie** van de quant.

### **3.4.1. operation.yaml - Het Centrale Draaiboek**

* **Doel**: Het **hoofdbestand** dat een volledige operatie definieert door strategy_links te creëren die blueprints aan environments koppelen.
* **Inhoud**: Een display_name, description, en een lijst van strategy_links, elk met een strategy_blueprint_id en een execution_environment_id.

* **Voorbeeld (Conceptueel)**:
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

### **3.4.2. strategy_blueprint.yaml - Het Gedetailleerde Recept** ⭐

* **Doel**: Bevat de **volledige configuratie van alle plugins** (workforce) voor één strategy_link.
* **SHIFT V2**: Van 4 naar 5 worker categorieën met gestructureerde sub-categorieën

#### **De 5-Worker Structuur**:

```yaml
# strategy_blueprint.yaml
display_name: "ICT/SMC Strategy"
version: "1.0.0"

workforce:
  # === 1. CONTEXT WORKERS ===
  # Bouw de "kaart" van de markt
  context_workers:
    - plugin: "market_structure_detector"
      subtype: "structural_analysis"
      params:
        detect_bos: true
        detect_choch: true
    
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
      
      - plugin: "trailing_stop_manager"
        params:
          trail_after_first_target: true
          trail_by_structure: true
    
    risk_safety:
      - plugin: "emergency_exit_on_news"
        params:
          exit_all_on_high_impact_news: true
    
    operational: []  # Geen operational workers in deze strategie
```

#### **Sub-Categorie Specificatie**:

Elke worker categorie heeft zijn eigen sub-types (zie [`MIGRATION_MAP.md`](docs/system/MIGRATION_MAP.md) sectie 4):

| Categorie | Sub-Type Enum | Aantal | Voorbeelden |
|-----------|---------------|--------|-------------|
| [`ContextWorker`](backend/core/base_worker.py) | [`ContextType`](backend/core/enums.py:ContextType) | 7 | regime_classification, structural_analysis, indicator_calculation |
| [`OpportunityWorker`](backend/core/base_worker.py) | [`OpportunityType`](backend/core/enums.py:OpportunityType) | 7 | technical_pattern, momentum_signal, mean_reversion |
| [`ThreatWorker`](backend/core/base_worker.py) | [`ThreatType`](backend/core/enums.py:ThreatType) | 5 | portfolio_risk, market_risk, system_health |
| [`PlanningWorker`](backend/core/base_worker.py) | [`PlanningPhase`](backend/core/enums.py:PlanningPhase) | 4 | entry_planning, exit_planning, size_planning, order_routing |
| [`ExecutionWorker`](backend/core/base_worker.py) | [`ExecutionType`](backend/core/enums.py:ExecutionType) | 4 | trade_initiation, position_management, risk_safety, operational |

## **3.5. Event & Capability Configuratie** ⭐

S1mpleTrader V3 hanteert het "Manifest-Gedreven Capability Model". De configuratie van een worker is strikt gescheiden in zijn **ROL** (de basisklasse die de ontwikkelaar kiest) en zijn **CAPABILITIES** (de extra functies die in het manifest worden aangevraagd). De oude `triggers`- en `publishes`-sleutels op het hoogste niveau van de worker-configuratie zijn vervangen door een centrale `capabilities`-sectie in het `manifest.yaml`.

### **Niveau 1: Standaard Pijplijn (Geen Capability Nodig)**

**Voor wie**: De meeste quants die een lineaire strategie bouwen.
**Hoe het werkt**: De ontwikkelaar kiest de `StandardWorker` als basisklasse. Er is geen `capabilities`-sectie nodig in het manifest, tenzij state of journaling wordt gebruikt. Het systeem creëert automatisch de dataflow tussen de operators.

**Voorbeeld**:
Een `fvg_detector` erft van `StandardWorker`. Zijn manifest is minimaal:

```yaml
# plugins/opportunity_workers/fvg_detector/manifest.yaml
identification:
  name: "fvg_detector"
  type: "opportunity_worker"
  # ... etc.
# Geen 'capabilities' sectie nodig voor basisfunctionaliteit
```

De `strategy_blueprint.yaml` wijst de worker simpelweg toe aan de juiste operator:

```yaml
# strategy_blueprint.yaml
workforce:
  opportunity_workers:
    - plugin: "fvg_detector"
```

### **Niveau 2: Event-Gedreven Workers (Capability Configuratie)**

**Voor wie**: Quants die autonome workers willen bouwen die reageren op de EventBus.
**Hoe het werkt**:

1.  De ontwikkelaar kiest de `EventDrivenWorker` als basisklasse. Deze klasse heeft geen `process`-methode.
2.  In het `manifest.yaml` wordt de `events`-capability geactiveerd. Hier worden de `publishes` (wat de worker mag uitzenden) en `wirings` (waar de worker op reageert) gedefinieerd.

**Voorbeeld: Smart DCA met Event Coördinatie**:
De `dca_opportunity_scorer` erft van `EventDrivenWorker`. Zijn manifest definieert zijn volledige event-contract:

```yaml
# plugins/opportunity_workers/dca_opportunity_scorer/manifest.yaml
identification:
  name: "dca_opportunity_scorer"
  type: "opportunity_worker"
  # ... etc.

capabilities:
  events:
    enabled: true
    publishes:
      - as_event: "dca_opportunity_scored"
        payload_dto: "Signal"
    wirings:
      # Deze worker wordt actief wanneer de scheduler de 'WEEKLY_DCA_TICK' publiceert,
      # en roept dan zijn eigen 'on_weekly_tick' methode aan.
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

## **3.6. Code Voorbeelden**

### **3.6.1. Volledige ICT/SMC Strategy Blueprint**

```yaml
# config/strategy_blueprints/ict_smc_liquidity_sweep.yaml
name: "ICT_FVG_Liquidity_Sweep"
version: "1.0.0"
description: "ICT/SMC methodologie met FVG entries en liquidity targets"

workforce:
  # === CONTEXT: Bouw de ICT "kaart" ===
  context_workers:
    # Structurele analyse
    - plugin: "market_structure_detector"
      subtype: "structural_analysis"
      params:
        detect_bos: true          # Break of Structure
        detect_choch: true        # Change of Character
    
    - plugin: "liquidity_zone_mapper"
      subtype: "structural_analysis"
      params:
        map_buy_side_liquidity: true
        map_sell_side_liquidity: true
    
    - plugin: "order_block_identifier"
      subtype: "structural_analysis"
    
    # Indicatoren
    - plugin: "premium_discount_calculator"
      subtype: "indicator_calculation"
      params:
        fibonacci_levels: [0.5, 0.618, 0.786]
    
    - plugin: "session_analyzer"
      subtype: "temporal_context"
      params:
        london_session: true
        new_york_session: true
        killzones: true
    
    # Regime
    - plugin: "higher_timeframe_bias"
      subtype: "regime_classification"
      params:
        timeframes: ["4H", "Daily", "Weekly"]
  
  # === OPPORTUNITY: Detecteer ICT setups ===
  opportunity_workers:
    - plugin: "fvg_detector"
      subtype: "technical_pattern"
      params:
        min_gap_size: 5
        require_structure_break: true
    
    - plugin: "optimal_trade_entry_finder"
      subtype: "technical_pattern"
      params:
        look_for_ote: true         # Optimal Trade Entry
        require_order_block: true
    
    - plugin: "liquidity_sweep_detector"
      subtype: "momentum_signal"
      params:
        detect_stop_hunts: true
  
  # === THREAT: Monitor risico's ===
  threat_workers:
    - plugin: "max_drawdown_monitor"
      subtype: "portfolio_risk"
      triggers:
        - "on_ledger_update"
      params:
        max_daily_drawdown: 2.0
    
    - plugin: "news_event_monitor"
      subtype: "market_risk"
      triggers:
        - "on_context_ready"
      params:
        high_impact_events: true
        pause_trading_minutes_before: 30
    
    - plugin: "economic_calendar_monitor"
      subtype: "external_event"
      params:
        track_fomc: true
        track_nfp: true
  
  # === PLANNING: Construeer het trade plan ===
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
      
      - plugin: "atr_based_stops"
        params:
          atr_multiplier: 1.5
    
    size_planning:
      - plugin: "fixed_risk_sizer"
        params:
          risk_per_trade_percent: 1.0
    
    order_routing:
      - plugin: "limit_order_router"
  
  # === EXECUTION: Voer uit en beheer ===
  execution_workers:
    trade_initiation:
      - plugin: "default_plan_executor"
    
    position_management:
      - plugin: "partial_profit_taker"
        params:
          take_50_percent_at_first_target: true
          move_stop_to_breakeven: true
      
      - plugin: "trailing_stop_manager"
        params:
          trail_after_first_target: true
          trail_by_structure: true
    
    risk_safety:
      - plugin: "emergency_exit_on_news"
        params:
          exit_all_on_high_impact_news: true
```

### **3.6.2. Smart DCA Strategy (Event-Driven)**

```yaml
# config/strategy_blueprints/smart_dca_btc.yaml
name: "Smart_DCA_BTC"
version: "1.0.0"
description: "Intelligent DCA die reageert op marktcondities en risico's"

workforce:
  # === CONTEXT ===
  context_workers:
    - plugin: "regime_classifier"
      subtype: "regime_classification"
      params:
        lookback_period: 100
    
    - plugin: "premium_discount_detector"
      subtype: "indicator_calculation"
      params:
        fibonacci_levels: [0.5, 0.618]
    
    - plugin: "volatility_percentile_calculator"
      subtype: "indicator_calculation"
      params:
        lookback_period: 90
  
  # === OPPORTUNITY (Event-Aware) ===
  opportunity_workers:
    - plugin: "dca_opportunity_scorer"
      subtype: "technical_pattern"
      triggers:
        - "on_schedule:weekly_dca"
      publishes:
        - event: "dca_opportunity_scored"
          payload_type: "Signal"
          description: "Published when DCA opportunity is scored"
      params:
        score_regime: true
        score_price_zone: true
        score_volatility: true
        weights:
          regime: 0.4
          price_zone: 0.4
          volatility: 0.2
  
  # === THREAT (Event-Aware) ===
  threat_workers:
    - plugin: "dca_risk_assessor"
      subtype: "portfolio_risk"
      triggers:
        - "on_schedule:weekly_dca"
      publishes:
        - event: "dca_risk_assessed"
          payload_type: "CriticalEvent"
          description: "Published when DCA risk is assessed"
      params:
        max_drawdown_for_dca: 15.0
        max_volatility_percentile: 95
        min_liquidity_threshold: 1000000
  
  # === PLANNING (Event-Aware met Synchronisatie) ===
  planning_workers:
    entry_planning:
      - plugin: "adaptive_dca_planner"
        triggers:
          - "dca_opportunity_scored"
          - "dca_risk_assessed"
        requires_all: true
        publishes:
          - event: "dca_plan_ready"
            payload_type: "TradePlan"
        params:
          base_amount: 1000
          min_amount: 500
          max_amount: 2000
          # Beslissingsmatrix:
          decision_matrix:
            high_opportunity_low_risk: 2000
            high_opportunity_medium_risk: 1000
            medium_opportunity_low_risk: 1000
            medium_opportunity_medium_risk: 500
            low_opportunity: 500
            high_risk: 0  # Skip
  
  # === EXECUTION ===
  execution_workers:
    operational:
      - plugin: "dca_plan_executor"
        triggers:
          - "dca_plan_ready"
        params:
          execution_method: "market_order"
          log_to_journal: true
```

**Scheduler Configuratie**:
```yaml
# config/schedule.yaml
schedules:
  - name: "weekly_dca"
    event: "WEEKLY_DCA_TICK"
    type: "cron"
    value: "0 10 * * 1"  # Elke maandag 10:00
    timezone: "Europe/Amsterdam"
```

### **3.6.3. Event Configuratie Voorbeelden**

#### **Voorbeeld 1: Threat Worker met Predefined Trigger**

```yaml
threat_workers:
  - plugin: "max_drawdown_monitor"
    subtype: "portfolio_risk"
    triggers:
      - "on_ledger_update"  # Predefined trigger
    params:
      max_drawdown_percent: 10.0
      check_frequency: "on_update"  # Real-time monitoring
```

#### **Voorbeeld 2: Multi-Event Worker**

```yaml
execution_workers:
  risk_safety:
    - plugin: "emergency_exit_agent"
      triggers:
        - "MAX_DRAWDOWN_BREACHED"     # Custom event from threat worker
        - "HIGH_VOLATILITY_DETECTED"  # Custom event from threat worker
        - "CONNECTION_LOST"           # System event
      requires_all: false  # Trigger op ELK event (niet alle)
      params:
        exit_method: "market_order"
        close_all_positions: true
```

#### **Voorbeeld 3: Fan-Out Pattern**

```yaml
opportunity_workers:
  - plugin: "multi_timeframe_analyzer"
    subtype: "technical_pattern"
    publishes:
      - event: "htf_bullish"         # Higher timeframe bullish
        payload_type: "Signal"
      - event: "htf_bearish"         # Higher timeframe bearish
        payload_type: "Signal"
      - event: "htf_neutral"         # Higher timeframe neutral
        payload_type: "Signal"

planning_workers:
  entry_planning:
    - plugin: "aggressive_entry_planner"
      triggers:
        - "htf_bullish"  # Alleen bij bullish HTF
    
    - plugin: "conservative_entry_planner"
      triggers:
        - "htf_neutral"  # Alleen bij neutral HTF
```

## **3.7. De Plugin-Configuratie**

Deze bestanden zijn onderdeel van de plugin zelf en maken hem vindbaar, valideerbaar en configureerbaar.

### **3.7.1. manifest.yaml - De ID-kaart en het Capability Paspoort**

**Doel**: Maakt een plugin ontdekbaar, begrijpelijk en valideerbaar voor de Assembly Laag. Het is de enige bron van waarheid over de identiteit en de behoeften (capabilities) van de plugin.

**Inhoud**:

-   **`identification`**: Metadata zoals `name`, `type`, `subtype`.
-   **`dependencies`**: Vereiste data-kolommen.
-   **`capabilities`**: Een cruciale sectie die alle extra, opt-in functionaliteiten definieert die de worker nodig heeft.

**Voorbeeld (Nieuwe V3 Formaat)**:
Een `EventDrivenWorker` die ook `state` nodig heeft.

```yaml
# plugins/threat_workers/dca_risk_assessor/manifest.yaml
identification:
  name: "dca_risk_assessor"
  display_name: "DCA Risk Assessor"
  type: "threat_worker"
  subtype: "portfolio_risk"
  version: "1.0.0"
  description: "Beoordeelt risico's voor een DCA-aankoop."
  author: "S1mpleTrader Team"

dependencies:
  requires: ['close', 'high', 'low']

# De centrale hub voor alle speciale vaardigheden.
capabilities:
  # 1. Deze worker heeft state nodig.
  state:
    enabled: true
    state_dto: "dtos.state.RiskState"

  # 2. Deze worker is event-gedreven.
  events:
    enabled: true
    publishes:
      - as_event: "dca_risk_assessed"
        payload_dto: "CriticalEvent"
    wirings:
      - listens_to: "WEEKLY_DCA_TICK"
        invokes:
          method: "assess_risk"
```

De oude `event_config`-sectie is hiermee volledig vervangen door de `capabilities.events`-structuur, wat zorgt voor een consistent en uniform model voor alle plugin-vaardigheden.

## **3.8. De Onderlinge Samenhang - De "Configuratie Trein" in Actie**

De magie van het systeem zit in hoe Operations deze bestanden aan elkaar koppelt tijdens de bootstrap-fase.

**Voorbeeld Flow**:

1. **Startpunt**: De gebruiker start de applicatie met de opdracht: `run ict_smc_operation`

2. **Operations leest [`operation.yaml`](config/operation.yaml)**:
   - Hij vindt de strategy_link voor `ict_smc_strategy`

3. **Analyse van de Link**:
   - Operations kijkt naar de `execution_environment_id`: `live_kraken_main`
   - Hij zoekt in [`environments.yaml`](config/environments.yaml) en vindt `live_kraken_main`
   - Hij ziet dat dit een live-omgeving is die `connector_id: kraken_live_eur_account` vereist
   - Hij zoekt nu in [`connectors.yaml`](config/connectors.yaml) en vindt de connector details
   
   - Vervolgens kijkt Operations naar de `strategy_blueprint_id`: `ict_smc_strategy`
   - Hij laadt [`strategy_blueprints/ict_smc_strategy.yaml`](config/runs/strategy_blueprint.yaml)
   - Voor elke plugin in de workforce, gebruikt het Assembly Team de [`manifest.yaml`](plugins/*/plugin_manifest.yaml) van die plugin om de code te vinden en de params te valideren

4. **Operator Configuratie**:
   - Operations laadt [`operators.yaml`](config/operators.yaml)
   - Hij bouwt 5 operator instances op basis van de configuratie
   - Elke operator krijgt zijn execution_strategy en aggregation_strategy

5. **Event Chain Setup**:
   - Operations analyseert de event configuratie in de blueprints
   - Hij genereert automatisch impliciete chains waar nodig
   - Hij valideert dat alle custom events correct zijn gekoppeld
   - Hij laadt [`wiring_map.yaml`](config/wiring_map.yaml) om de EventBus te configureren

6. **Scheduler Setup**:
   - Als er scheduled events zijn, laadt Operations [`schedule.yaml`](config/schedule.yaml)
   - Hij configureert de Scheduler om de juiste events te publiceren

Het resultaat is een volledig geassembleerd, gevalideerd en onderling verbonden ecosysteem van plugins en operators, klaar om van start te gaan, **puur en alleen op basis van de declaratieve YAML-bestanden**.

## **3.9. Configuratie Validatie**

Het systeem valideert automatisch de volledige configuratie tijdens bootstrap:

**Validatie Checks**:

1. **Schema Validatie**: Alle YAML bestanden tegen Pydantic schemas
2. **Referentie Validatie**: Alle ID verwijzingen (connector_id, plugin_id, etc.) bestaan
3. **Event Chain Validatie**: Alle triggers hebben een publisher
4. **Dependency Validatie**: Alle plugin dependencies zijn vervuld
5. **Operator Configuratie**: Alle operators hebben een valid configuratie

**Error Handling**:
```python
# Conceptueel
try:
    operations.bootstrap()
except ConfigurationError as e:
    if isinstance(e, MissingReferenceError):
        print(f"❌ Configuration error: {e.field} '{e.value}' not found in {e.source_file}")
    elif isinstance(e, EventChainError):
        print(f"❌ Event chain error: Worker '{e.worker}' triggers '{e.event}' but no publisher found")
    elif isinstance(e, SchemaValidationError):
        print(f"❌ Schema error in {e.file}: {e.errors}")
```

## **3.10. Best Practices**

### **DO's**:

✅ **Start simpel** - Gebruik Niveau 1 (impliciete chains) tenzij je specifieke behoeften hebt
✅ **Gebruik sub-types** - Ze helpen met organisatie en plugin discovery
✅ **Test je configuratie** - Gebruik de validatie tools voordat je live gaat
✅ **Documenteer custom events** - Maak duidelijk wat elk event betekent
✅ **Volg naming conventions** - Consistent gebruik van snake_case voor IDs

### **DON'Ts**:

❌ **Complexiteit zonder reden** - Gebruik geen custom events als predefined triggers voldoen
❌ **Circular dependencies** - Voorkom event loops in je configuratie
❌ **Hard-coded waarden** - Gebruik environment variables voor credentials
❌ **Te veel workers** - Begin klein, schaal op waar nodig
❌ **Onduidelijke IDs** - Gebruik beschrijvende namen voor alle identifiers

---

**Einde Document**

Voor meer details over specifieke concepten, zie:
- [`MIGRATION_MAP.md`](docs/system/MIGRATION_MAP.md) - V2 → V3 mappings en migratie
- [`WORKER_TAXONOMIE_V3.md`](docs/development/251014%20Bijwerken%20documentatie/WORKER_TAXONOMIE_V3.md) - Volledige worker taxonomie uitwerking
- [`2_ARCHITECTURE.md`](docs/system/2_ARCHITECTURE.md) - Core architectuur principes
- [`4_DE_PLUGIN_ANATOMIE.md`](docs/system/4_DE_PLUGIN_ANATOMIE.md) - Plugin development guide