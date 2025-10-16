# **9. Meta Workflows: Van Analyse tot Inzicht**

**Versie:** 3.0 (V3 Architectuur - 5-Worker Model)
**Status:** Definitief
Dit document beschrijft de architectuur en de rol van de "Meta Workflows", de hoog-niveau services voor geavanceerde analyses en optimalisaties.

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Concept: De Operations-Service als Motor](#91-concept-de-operations-service-als-motor)
3. [De OptimizationService (Het Onderzoekslab)](#92-de-optimizationservice-het-onderzoekslab)
4. [De VariantTestService (De Vergelijkings-Arena)](#93-de-varianttestservice-de-vergelijkings-arena)
5. [De Rol van ParallelRunService](#94-de-rol-van-parallelrunservice)
6. [Best Practices voor Meta Workflows](#95-best-practices-voor-meta-workflows)
7. [Integratie met Trade Explorer UI](#96-integratie-met-trade-explorer-ui)

---

## **Executive Summary**

Dit document beschrijft de "Meta Workflows" van S1mpleTrader V3, een laag van hoog-niveau services die bovenop de kern-executielogica draaien om geavanceerde, kwantitatieve analyses mogelijk te maken. Deze services gebruiken de `Operations-service` als een "black box"-motor die herhaaldelijk en systematisch wordt aangeroepen om complexe vragen te beantwoorden.

### **🎯 Kerncomponenten**

**1. De `OptimizationService` (Het Onderzoekslab)**
-   **Doel**: Het systematisch doorzoeken van een grote, multidimensionale parameterruimte om de meest performante configuraties te vinden.
-   **V3-uitbreidingen**: Optimaliseert niet alleen worker-parameters, maar ook architecturale keuzes zoals worker sub-types, operator-strategieën (`execution_strategy`), en event-chain configuraties.

**2. De `VariantTestService` (De Vergelijkings-Arena)**
-   **Doel**: Het direct vergelijken van een klein aantal discrete strategie-varianten onder exact dezelfde marktomstandigheden om de robuustheid en impact van specifieke keuzes te valideren.
-   **Gebruik**: Ideaal voor "head-to-head" A/B-testen van bijvoorbeeld verschillende exit-strategieën of risicomanagement-configuraties.

**3. De `ParallelRunService` (De Werkpaard)**
-   **Doel**: Een herbruikbare backend-component die de efficiënte, parallelle uitvoering van duizenden backtests beheert. Zowel de `OptimizationService` als de `VariantTestService` zijn "klanten" van deze service.

### **🔑 Design Principes**

✅ **Configuratie-gedreven Analyse** - Zowel optimalisaties als variant-testen worden volledig gedefinieerd in YAML-bestanden (`optimization.yaml`, `variant.yaml`).
✅ **Multidimensionale Optimalisatie** - De V3-architectuur maakt het mogelijk om niet alleen parameters te tunen, maar ook fundamentele strategische en architecturale keuzes te testen.
✅ **Causale Analyse in Resultaten** - De resultaten van meta-workflows bevatten causale data (bv. `opportunities_rejected`), waardoor diepgaandere inzichten mogelijk zijn dan alleen PnL.
✅ **Single Responsibility Principle (SRP)** - Elke service heeft één duidelijke verantwoordelijkheid: de `OptimizationService` definieert de "wat", de `ParallelRunService` regelt de "hoe".

---

## **9.1. Concept: De Operations-Service als Motor**

De Operations-service, aangestuurd via het [`run_operation.py`](../../run_operation.py) entrypoint, is de motor die in staat is om **één enkele, volledig gedefinieerde Operation** uit te voeren. Meta Workflows zijn services in de Service-laag die deze motor herhaaldelijk en systematisch aanroepen, met steeds een andere configuratie, om complexe, kwantitatieve vragen te beantwoorden.

Ze fungeren als "onderzoekleiders" die de Operations-service als een "black box"-motor gebruiken. Ze leunen zwaar op een [`ParallelRunService`](../../services/parallel_run_service.py) om duizenden backtests efficiënt en parallel uit te voeren. Waar optimalisatie in V1 een ad-hoc script was, wordt het in V3 een **"eerste klas burger"** van de architectuur.

### **9.1.1. De Evolutie: 4-Worker → 5-Worker Model**

**V2 (Oud):** 4 worker categorieën
-   [`ContextWorker`](../../backend/core/base_worker.py)
-   [`AnalysisWorker`](../../backend/core/base_worker.py) (detectie + planning gecombineerd)
-   [`MonitorWorker`](../../backend/core/base_worker.py)
-   [`ExecutionWorker`](../../backend/core/base_worker.py)

**V3 (Nieuw):** 5 gespecialiseerde categorieën
-   [`ContextWorker`](../../backend/core/base_worker.py) - "De Cartograaf"
-   [`OpportunityWorker`](../../backend/core/base_worker.py) - "De Verkenner" ✨
-   [`ThreatWorker`](../../backend/core/base_worker.py) - "De Waakhond" (hernoemd)
-   [`PlanningWorker`](../../backend/core/base_worker.py) - "De Strateeg" ✨
-   [`ExecutionWorker`](../../backend/core/base_worker.py) - "De Uitvoerder"

**→ Voor volledige taxonomie, zie: [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md#24-het-worker-ecosysteem-5-gespecialiseerde-rollen)**

---

## **9.2. De OptimizationService (Het Onderzoekslab)**

### **9.2.1. Doel & Analogie**

*   **Doel:** Het systematisch doorzoeken van een grote parameterruimte om de meest performante combinaties voor een strategie te vinden.
*   **Analogie:** Een farmaceutisch lab dat duizenden moleculaire variaties test om het meest effectieve medicijn te vinden.

### **9.2.2. Gedetailleerde Workflow**

#### **Input (Het Onderzoeksplan)**

De service vereist:
1.  **Basis [`operation.yaml`](../../config/operation.yaml)** - Definieert de te testen strategy_link
2.  **[`optimization.yaml`](../../config/optimizations/)** - Definieert de onderzoeksvraag:
    -   Welke parameters moeten worden gevarieerd
    -   Welke worker categorieën en sub-types
    -   Parameter ranges (start, end, step)

#### **Proces (De Experimenten)**

1.  **Parameter Space Generation**
    -   De OptimizationService genereert een volledige lijst van alle mogelijke parameter-combinaties
    -   Ondersteunt optimalisatie op verschillende niveaus:
        *   Worker parameters (traditioneel)
        *   Worker sub-type selectie (nieuw in V3)
        *   Operator configuratie (execution/aggregation strategies)
        *   Event chain configuratie

2.  **Blueprint Generation**
    -   Voor elke combinatie creëert het:
        *   Een unieke, **tijdelijke [`strategy_blueprint.yaml`](../../config/runs/)** waarin de parameters zijn aangepast
        *   Een unieke, **tijdelijke en uitgeklede [`operation.yaml`](../../config/operation.yaml)** die slechts één strategy_link bevat

3.  **Parallel Execution**
    -   Het delegeert de volledige lijst van paden naar deze tijdelijke operation.yaml-bestanden aan de [`ParallelRunService`](../../services/parallel_run_service.py)

#### **Executie (Het Robotleger)**

*   De [`ParallelRunService`](../../services/parallel_run_service.py) start een pool van workers (één per CPU-kern)
*   Elke worker ontvangt een pad naar een unieke operation.yaml, roept de Operations-service aan via [`run_operation.py`](../../run_operation.py) en voert een volledige backtest uit

#### **Output (De Analyse)**

*   De OptimizationService verzamelt alle [`BacktestResult`](../../backend/dtos/execution/) objecten
*   Het creëert een pandas DataFrame met:
    -   Geteste parameters
    -   Worker configuraties (types, sub-types)
    -   Resulterende performance-metrieken
    -   Causale IDs voor traceerbaarheid
*   Deze data wordt naar de Web UI gestuurd voor presentatie in een interactieve, sorteerbare tabel

### **9.2.3. V3 Optimalisatie Dimensies**

De OptimizationService ondersteunt nu optimalisatie op meerdere dimensies:

#### **1. Worker Parameter Optimization (Traditioneel)**

```yaml
# config/optimizations/optimize_fvg_params.yaml
optimization_config:
  name: "FVG Parameter Sweep"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  parameter_space:
    - worker_category: "opportunity_workers"
      worker_plugin: "fvg_entry_detector"
      parameters:
        min_gap_size:
          start: 3
          end: 10
          step: 1
        require_structure_break:
          values: [true, false]
```

#### **2. Worker Sub-Type Selection (Nieuw in V3)**

```yaml
# config/optimizations/optimize_opportunity_types.yaml
optimization_config:
  name: "Opportunity Type Comparison"
  base_operation: "config/operations/multi_strategy_backtest.yaml"
  
  worker_selection:
    - worker_category: "opportunity_workers"
      subtype_variants:
        - subtype: "technical_pattern"
          plugins: ["fvg_detector", "breakout_scanner"]
        - subtype: "momentum_signal"
          plugins: ["trend_follower", "momentum_scanner"]
        - subtype: "mean_reversion"
          plugins: ["oversold_detector", "rsi_reversal"]
```

#### **3. Planning Phase Configuration (Nieuw in V3)**

```yaml
# config/optimizations/optimize_planning_phases.yaml
optimization_config:
  name: "Planning Strategy Comparison"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  planning_variants:
    - phase: "entry_planning"
      variants:
        - plugin: "limit_entry_at_fvg"
          params:
            entry_at_midpoint: true
        - plugin: "market_entry_immediate"
        - plugin: "twap_entry"
          params:
            duration_minutes: 15
    
    - phase: "exit_planning"
      variants:
        - plugin: "liquidity_target_exit"
        - plugin: "atr_based_stops"
          params:
            atr_multiplier:
              start: 1.0
              end: 3.0
              step: 0.5
```

#### **4. Operator Configuration Optimization (Nieuw in V3)**

Deze dimensie test de impact van verschillende orkestratiestrategieën door de configuratie in `operators.yaml` te variëren.

```yaml
# config/optimizations/optimize_operator_strategies.yaml
optimization_config:
  name: "Operator Strategy Testing"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  operator_variants:
    # Test de impact van parallelle vs. sequentiële planning
    - operator_id: "PlanningOperator"
      execution_strategy:
        values: ["SEQUENTIAL", "PARALLEL"]
      # Aggregation strategy wordt automatisch aangepast
      # (CHAIN_THROUGH voor SEQUENTIAL, COLLECT_ALL voor PARALLEL)

    # Test de impact van verschillende Opportunity detectie strategieën
    - operator_id: "OpportunityOperator"
      execution_strategy:
        values: ["PARALLEL"] # Standaard is parallel
```

#### **5. Event & Capability Optimization (Nieuw in V3)**

Deze dimensie test de impact van het toevoegen van event-driven gedrag. Dit wordt gedaan door te variëren tussen een `StandardWorker` (impliciete pijplijn) en een `EventDrivenWorker` (expliciete events).

```yaml
# config/optimizations/optimize_event_workflows.yaml
optimization_config:
  name: "Event Workflow Variants"
  base_operation: "config/operations/smart_dca.yaml"
  
  # We definiëren varianten door de ROL en CAPABILITIES van workers aan te passen
  worker_variants:
    - name: "implicit_chain_variant"
      description: "Traditionele pijplijn zonder expliciete events"
      overrides:
        planning_workers:
          entry_planning:
            # Gebruik een StandardWorker die wacht op een standaard input
            - plugin: "simple_dca_planner" # Dit is een StandardWorker
              # Geen 'events' capability in het manifest van deze plugin

    - name: "custom_event_chain_variant"
      description: "Volledig event-driven met coördinatie"
      overrides:
        planning_workers:
          entry_planning:
            # Gebruik een EventDrivenWorker die luistert naar custom events
            - plugin: "adaptive_dca_planner" # Dit is een EventDrivenWorker
              # Het manifest van deze plugin bevat de 'events' capability
              # met de benodigde 'wirings'.
```

### **9.2.4. Code Voorbeeld: Comprehensive Optimization**

```yaml
# config/optimizations/comprehensive_ict_optimization.yaml
optimization_config:
  name: "ICT Strategy Comprehensive Optimization"
  description: "Multi-dimensional optimization voor ICT/SMC strategie"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  # === WORKER PARAMETERS ===
  parameter_space:
    # Opportunity Detection
    - worker_category: "opportunity_workers"
      worker_plugin: "fvg_entry_detector"
      subtype: "technical_pattern"
      parameters:
        min_gap_size:
          start: 3
          end: 10
          step: 1
        require_structure_break:
          values: [true, false]
    
    # Exit Planning
    - worker_category: "planning_workers"
      worker_phase: "exit_planning"
      worker_plugin: "liquidity_target_exit"
      parameters:
        target_opposite_liquidity:
          values: [true, false]
        stop_below_order_block:
          values: [true, false]
    
    # Size Planning
    - worker_category: "planning_workers"
      worker_phase: "size_planning"
      worker_plugin: "fixed_risk_sizer"
      parameters:
        risk_per_trade_percent:
          start: 0.5
          end: 2.0
          step: 0.25
  
  # === OPERATOR CONFIGURATION ===
  operator_variants:
    - operator_id: "OpportunityOperator"
      execution_strategy:
        values: ["PARALLEL"]  # Fixed
      aggregation_strategy:
        values: ["COLLECT_ALL"]  # Fixed
  
  # === PERFORMANCE METRICS ===
  optimization_targets:
    primary_metric: "sharpe_ratio"
    secondary_metrics:
      - "total_return"
      - "max_drawdown"
      - "win_rate"
    
  constraints:
    min_trades: 10
    max_drawdown: 15.0
  
  # === EXECUTION CONFIG ===
  parallel_config:
    max_workers: 8
    timeout_per_run: 300  # seconds
```

### **9.2.5. Results Output**

De OptimizationService genereert gestructureerde resultaten:

```python
# Conceptueel: OptimizationResult DTO
{
    "optimization_id": "uuid-abc-123",
    "optimization_name": "ICT Strategy Comprehensive Optimization",
    "timestamp": "2025-10-14T10:00:00Z",
    "total_combinations": 480,
    "successful_runs": 478,
    "failed_runs": 2,
    
    "results": [
        {
            "run_id": "uuid-def-456",
            "configuration": {
                "fvg_entry_detector": {
                    "min_gap_size": 5,
                    "require_structure_break": true
                },
                "liquidity_target_exit": {
                    "target_opposite_liquidity": true,
                    "stop_below_order_block": true
                },
                "fixed_risk_sizer": {
                    "risk_per_trade_percent": 1.0
                }
            },
            "metrics": {
                "sharpe_ratio": 2.45,
                "total_return": 34.5,
                "max_drawdown": 8.2,
                "win_rate": 58.3,
                "total_trades": 127
            },
            "causality": {
                "opportunities_detected": 245,
                "opportunities_filtered": 118,
                "threats_detected": 34
            }
        },
        # ... more results
    ],
    
    "best_configuration": {
        # Top performer based on primary_metric
    }
}
```

**→ Voor operator configuratie details, zie: [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md#27-de-data-gedreven-operator)**
**→ Voor worker taxonomie, zie: [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md#24-het-worker-ecosysteem-5-gespecialiseerde-rollen)**

---

## **9.3. De VariantTestService (De Vergelijkings-Arena)**

### **9.3.1. Doel & Analogie**

*   **Doel:** Het direct vergelijken van een klein aantal discrete strategie-varianten onder exact dezelfde marktomstandigheden om de robuustheid en de impact van specifieke keuzes te valideren.
*   **Analogie:** Een "head-to-head" race tussen een paar topatleten om te zien wie de beste allrounder is.

### **9.3.2. Gedetailleerde Workflow**

#### **Input (De Deelnemers)**

De service vereist:
1.  **Basis [`operation.yaml`](../../config/operation.yaml)**
2.  **[`variant.yaml`](../../config/variants/)** die de "deelnemers" definieert door middel van "overrides"

**Voorbeeld:**
*   **Variant A ("Baseline"):** De basisconfiguratie
*   **Variant B ("Aggressive Opportunity"):** Overschrijft opportunity_workers configuratie
*   **Variant C ("Conservative Exit"):** Vervangt exit planning plugins
*   **Variant D ("Parallel Planning"):** Overschrijft operator execution strategy

#### **Proces (De Race-Opzet)**

1.  De VariantTestService past voor elke gedefinieerde variant de "overrides" toe op de basis-blueprint om unieke, **tijdelijke [`strategy_blueprint.yaml`](../../config/runs/)**-bestanden te creëren
2.  Vervolgens creëert het voor elke variant een **tijdelijke, uitgeklede [`operation.yaml`](../../config/operation.yaml)** die naar de juiste tijdelijke blueprint linkt
3.  Het delegeert de lijst van paden naar deze operation.yaml-bestanden aan de [`ParallelRunService`](../../services/parallel_run_service.py)

#### **Executie (Het Startschot)**

*   De [`ParallelRunService`](../../services/parallel_run_service.py) voert voor elke variant een volledige backtest uit door de Operations-service aan te roepen met het juiste operation.yaml-bestand

#### **Output (De Finishfoto)**

*   De VariantTestService verzamelt de [`BacktestResult`](../../backend/dtos/execution/) objecten
*   Deze data wordt naar de Web UI gestuurd voor een directe, visuele vergelijking, bijvoorbeeld door de equity curves van alle varianten in één grafiek te plotten

### **9.3.3. V3 Variant Dimensies**

#### **1. Worker Configuration Variants (Traditioneel)**

```yaml
# config/variants/fvg_strategy_variants.yaml
variant_config:
  name: "FVG Strategy Robustness Test"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  variants:
    - name: "baseline"
      description: "Standard FVG configuratie"
      overrides: {}  # Geen wijzigingen
    
    - name: "strict_fvg"
      description: "Striktere FVG criteria"
      overrides:
        opportunity_workers:
          - plugin: "fvg_entry_detector"
            params:
              min_gap_size: 8
              require_structure_break: true
    
    - name: "relaxed_fvg"
      description: "Soepelere FVG criteria"
      overrides:
        opportunity_workers:
          - plugin: "fvg_entry_detector"
            params:
              min_gap_size: 3
              require_structure_break: false
```

#### **2. Worker Sub-Type Variants (Nieuw in V3)**

```yaml
# config/variants/opportunity_type_variants.yaml
variant_config:
  name: "Opportunity Type Head-to-Head"
  base_operation: "config/operations/multi_strategy_backtest.yaml"
  
  variants:
    - name: "technical_pattern"
      description: "Pure technical pattern detection"
      overrides:
        opportunity_workers:
          - plugin: "fvg_detector"
            subtype: "technical_pattern"
          - plugin: "breakout_scanner"
            subtype: "technical_pattern"
    
    - name: "momentum_signal"
      description: "Pure momentum signals"
      overrides:
        opportunity_workers:
          - plugin: "trend_follower"
            subtype: "momentum_signal"
          - plugin: "momentum_scanner"
            subtype: "momentum_signal"
    
    - name: "hybrid"
      description: "Mix van technical + momentum"
      overrides:
        opportunity_workers:
          - plugin: "fvg_detector"
            subtype: "technical_pattern"
          - plugin: "trend_follower"
            subtype: "momentum_signal"
```

#### **3. Planning Phase Variants (Nieuw in V3)**

```yaml
# config/variants/exit_strategy_variants.yaml
variant_config:
  name: "Exit Strategy Comparison"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  variants:
    - name: "liquidity_targets"
      description: "ICT liquidity-based exits"
      overrides:
        planning_workers:
          exit_planning:
            - plugin: "liquidity_target_exit"
              params:
                target_opposite_liquidity: true
    
    - name: "atr_based"
      description: "ATR-based stops"
      overrides:
        planning_workers:
          exit_planning:
            - plugin: "atr_based_stops"
              params:
                atr_multiplier: 2.0
    
    - name: "fixed_rr"
      description: "Fixed Risk:Reward"
      overrides:
        planning_workers:
          exit_planning:
            - plugin: "fixed_rr_exit"
              params:
                risk_reward_ratio: 3.0
```

#### **4. Operator Configuration Variants (Nieuw in V3)**

```yaml
# config/variants/operator_strategy_variants.yaml
variant_config:
  name: "Operator Execution Strategy Test"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  variants:
    - name: "sequential_planning"
      description: "Planning workers draaien sequentieel (default)"
      overrides:
        operator_overrides:
          PlanningOperator:
            execution_strategy: "SEQUENTIAL"
            aggregation_strategy: "CHAIN_THROUGH"
    
    - name: "parallel_planning"
      description: "Planning workers draaien parallel (experimental)"
      overrides:
        operator_overrides:
          PlanningOperator:
            execution_strategy: "PARALLEL"
            aggregation_strategy: "COLLECT_ALL"
    
    - name: "event_driven_opportunity"
      description: "Opportunity detection via events"
      overrides:
        operator_overrides:
          OpportunityOperator:
            execution_strategy: "EVENT_DRIVEN"
            aggregation_strategy: "NONE"
```

#### **5. Event Chain Variants (Nieuw in V3)**

Deze varianten testen de impact van verschillende workflow-architecturen door te wisselen tussen `StandardWorker`-gebaseerde (impliciete) en `EventDrivenWorker`-gebaseerde (expliciete) implementaties.

```yaml
# config/variants/event_chain_variants.yaml
variant_config:
  name: "Event Configuration Comparison"
  base_operation: "config/operations/smart_dca.yaml"
  
  variants:
    - name: "implicit_chain"
      description: "Automatische, lineaire pijplijn"
      overrides:
        planning_workers:
          entry_planning:
            # Vervang de event-driven planner door een simpele StandardWorker
            - plugin: "simple_dca_planner"

    - name: "custom_event_chain"
      description: "Volledig custom event-driven workflow"
      overrides:
        planning_workers:
          entry_planning:
            # Gebruik de originele EventDrivenWorker die coördinatie vereist
            - plugin: "adaptive_dca_planner"
```

Dit stelt ons in staat om de prestaties en robuustheid van een simpele, lineaire workflow direct te vergelijken met een complexere, asynchrone, event-gedreven workflow onder exact dezelfde marktomstandigheden.

### **9.3.4. Code Voorbeeld: Comprehensive Variant Test**

```yaml
# config/variants/comprehensive_robustness_test.yaml
variant_config:
  name: "ICT Strategy Robustness Test"
  description: "Test multiple dimensions van de strategie"
  base_operation: "config/operations/ict_smc_backtest.yaml"
  
  variants:
    # === BASELINE ===
    - name: "baseline"
      description: "Standard configuratie"
      overrides: {}
    
    # === OPPORTUNITY VARIANTS ===
    - name: "strict_entry"
      description: "Striktere entry criteria"
      overrides:
        opportunity_workers:
          - plugin: "fvg_entry_detector"
            subtype: "technical_pattern"
            params:
              min_gap_size: 8
              require_structure_break: true
              require_volume_confirmation: true
    
    - name: "relaxed_entry"
      description: "Soepelere entry criteria"
      overrides:
        opportunity_workers:
          - plugin: "fvg_entry_detector"
            subtype: "technical_pattern"
            params:
              min_gap_size: 3
              require_structure_break: false
    
    # === THREAT INTEGRATION ===
    - name: "threat_aware"
      description: "Actieve threat monitoring"
      overrides:
        threat_workers:
          - plugin: "max_drawdown_monitor"
            subtype: "portfolio_risk"
            triggers:
              - "on_ledger_update"
            params:
              max_daily_drawdown: 2.0
          
          - plugin: "volatility_spike_detector"
            subtype: "market_risk"
            triggers:
              - "on_context_ready"
            params:
              volatility_threshold_percentile: 95
        
        planning_workers:
          size_planning:
            - plugin: "adaptive_risk_sizer"
              params:
                base_risk_percent: 1.0
                reduce_on_high_threat: true  # Reageert op threats
    
    # === EXIT VARIANTS ===
    - name: "liquidity_exits"
      description: "ICT liquidity-based exits"
      overrides:
        planning_workers:
          exit_planning:
            - plugin: "liquidity_target_exit"
              params:
                target_opposite_liquidity: true
                stop_below_order_block: true
    
    - name: "atr_exits"
      description: "ATR-based exits"
      overrides:
        planning_workers:
          exit_planning:
            - plugin: "atr_based_stops"
              params:
                atr_multiplier: 2.0
    
    # === OPERATOR VARIANTS ===
    - name: "parallel_opportunity"
      description: "Test parallel opportunity detection"
      overrides:
        operator_overrides:
          OpportunityOperator:
            execution_strategy: "PARALLEL"
            aggregation_strategy: "COLLECT_ALL"
    
    # === EXECUTION VARIANTS ===
    - name: "aggressive_management"
      description: "Aggressive positie management"
      overrides:
        execution_workers:
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
            - plugin: "emergency_exit_agent"
              triggers:
                - "on_threat_detected"
              params:
                exit_on_severity: ["CRITICAL", "HIGH"]

  # === COMPARISON CONFIGURATION ===
  comparison_config:
    metrics:
      - "sharpe_ratio"
      - "total_return"
      - "max_drawdown"
      - "win_rate"
      - "total_trades"
      - "avg_trade_duration"
    
    visualizations:
      - "equity_curves"
      - "drawdown_curves"
      - "monthly_returns"
      - "trade_distribution"
    
    causality_analysis:
      - "opportunities_per_variant"
      - "threats_per_variant"
      - "rejection_reasons"
```

### **9.3.5. Results Output**

De VariantTestService genereert gestructureerde vergelijkingsdata:

```python
# Conceptueel: VariantComparisonResult DTO
{
    "test_id": "uuid-abc-789",
    "test_name": "ICT Strategy Robustness Test",
    "timestamp": "2025-10-14T11:00:00Z",
    "total_variants": 10,
    "market_period": {
        "start": "2020-01-01",
        "end": "2024-12-31"
    },
    
    "results": [
        {
            "variant_name": "baseline",
            "metrics": {
                "sharpe_ratio": 2.45,
                "total_return": 34.5,
                "max_drawdown": 8.2,
                "win_rate": 58.3,
                "total_trades": 127
            },
            "causality": {
                "opportunity_id_count": 245,
                "threat_id_count": 34,
                "opportunities_rejected": 118,
                "top_rejection_reasons": [
                    {"threat_type": "MAX_DRAWDOWN_BREACHED", "count": 45},
                    {"threat_type": "VOLATILITY_SPIKE", "count": 28}
                ]
            }
        },
        {
            "variant_name": "threat_aware",
            "metrics": {
                "sharpe_ratio": 2.78,  # Improvement!
                "total_return": 31.2,
                "max_drawdown": 5.4,   # Lower drawdown
                "win_rate": 61.5,
                "total_trades": 98
            },
            "causality": {
                "opportunity_id_count": 245,
                "threat_id_count": 56,  # More threats detected
                "opportunities_rejected": 147,  # More rejected (defensive)
                "top_rejection_reasons": [
                    {"threat_type": "MAX_DRAWDOWN_BREACHED", "count": 67},
                    {"threat_type": "VOLATILITY_SPIKE", "count": 43},
                    {"threat_type": "MARKET_RISK_HIGH", "count": 37}
                ]
            }
        },
        # ... more variants
    ],
    
    "comparative_analysis": {
        "best_sharpe": "threat_aware",
        "best_return": "baseline",
        "lowest_drawdown": "threat_aware",
        "most_trades": "relaxed_entry",
        "most_defensive": "threat_aware"
    }
}
```

**→ Voor event configuratie details, zie: [`3_DE_CONFIGURATIE_TREIN.md`](3_DE_CONFIGURATIE_TREIN.md#35-event-configuratie-op-3-niveaus)**
**→ Voor causaal ID framework, zie: [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md#25-het-traceability-framework)**

---

## **9.4. De Rol van ParallelRunService**

Deze service is een cruciale, herbruikbare Backend-component. Zowel de [`OptimizationService`](../../services/optimization_service.py) als de [`VariantTestService`](../../services/variant_test_service.py) zijn "klanten" van deze service.

### **9.4.1. Single Responsibility**

Zijn enige verantwoordelijkheid is het efficiënt managen van de multiprocessing-pool, het tonen van de voortgang en het netjes aggregeren van resultaten. Dit is een perfect voorbeeld van het **Single Responsibility Principle**.

### **9.4.2. V3 Capabilities**

**Nieuwe functionaliteit in V3:**

1.  **Causale ID Tracking** - Behoudt OpportunityIDs en ThreatIDs in aggregatie
2.  **Event Chain Validatie** - Valideert event configuraties voor elke run
3.  **Worker Type Awareness** - Begrijpt 5-worker model
4.  **Crash Recovery** - Atomic writes en recovery mechanismen
5.  **Progress Reporting** - Real-time voortgang met worker breakdown

```python
# Conceptueel: ParallelRunService interface
class ParallelRunService:
    def run_parallel(
        self,
        operation_paths: List[Path],
        max_workers: int = None,
        progress_callback: Callable = None
    ) -> List[BacktestResult]:
        """
        Voert operations parallel uit.
        
        Returns:
            List van BacktestResult met causale IDs intact
        """
        pass
```

**→ Voor parallel execution details, zie: [`7_RESILIENCE_AND_OPERATIONS.md`](7_RESILIENCE_AND_OPERATIONS.md)**

---

## **9.5. Best Practices voor Meta Workflows**

### **9.5.1. OptimizationService Best Practices**

✅ **DO:**
-   Start met kleine parameter ranges, schaal op indien nodig
-   Optimaliseer één dimensie tegelijk (worker params, dan operator config, dan events)
-   Gebruik constraints om onrealistische combinaties te filteren
-   Valideer resultaten met out-of-sample testing
-   Gebruik causale IDs om te begrijpen waarom configuraties wel/niet werken

❌ **DON'T:**
-   Optimaliseer niet te veel parameters tegelijkertijd (curse of dimensionality)
-   Negeer niet de runtime implications van grote parameter spaces
-   Gebruik niet alleen primaire metric - kijk ook naar drawdown en trade count
-   Vertrouw niet blind op beste resultaten - overfitting is reëel

### **9.5.2. VariantTestService Best Practices**

✅ **DO:**
-   Test meaningful verschillen tussen variants
-   Gebruik dezelfde marktperiode voor alle variants
-   Analyseer causale data (rejection reasons, threat patterns)
-   Visualiseer equity curves voor side-by-side vergelijking
-   Test operator configuratie variants voor robuustheid

❌ **DON'T:**
-   Maak niet te veel minor variants - focus op conceptuele verschillen
-   Vergelijk niet variants met fundamenteel verschillende strategieën
-   Negeer niet de causale analyse - dat is waar de inzichten zitten
-   Test niet zonder adequate data (minimaal 1000 bars)

### **9.5.3. Worker Category Considerations**

**Context Workers:**
-   Optimaliseer indicator parameters (EMA periods, ATR settings)
-   Test verschillende regime classification methods
-   Validate structural analysis algorithms

**Opportunity Workers:**
-   Test verschillende sub-types (technical_pattern vs momentum_signal)
-   Optimaliseer detection thresholds
-   Compare single vs multiple opportunity workers

**Threat Workers:**
-   Test verschillende risk thresholds
-   Validate threat detection timing (on_ledger_update vs on_context_ready)
-   Measure impact op rejection rates

**Planning Workers:**
-   Test entry/exit phase configurations
-   Optimize risk sizing algorithms
-   Compare order routing strategies

**Execution Workers:**
-   Test position management variants
-   Validate emergency exit triggers
-   Measure operational task efficiency

---

## **9.6. Integratie met Trade Explorer UI**

De resultaten van Meta Workflows worden gevisualiseerd in de Trade Explorer UI.

### **9.6.1. Optimization Results Viewer**

**Features:**
-   Sorteerbare tabel met alle parameter combinaties
-   Scatter plots (Risk vs Return, Sharpe vs Drawdown)
-   Heatmaps voor 2D parameter spaces
-   Causale analyse dashboard:
    *   Opportunities detected per configuratie
    *   Threats triggered per configuratie
    *   Rejection patterns

### **9.6.2. Variant Comparison Dashboard**

**Features:**
-   Side-by-side equity curves
-   Comparative metrics table
-   Drawdown overlays
-   Trade distribution histograms
-   Causale breakdown:
    *   OpportunityID counts per variant
    *   ThreatID patterns per variant
    *   Rejection reason analysis

**→ Voor UI integratie details, zie: [`6_FRONTEND_INTEGRATION.md`](6_FRONTEND_INTEGRATION.md)**

---

## **9.7. Gerelateerde Documenten**

Voor diepere uitwerkingen van gerelateerde concepten:

-   **Architectuur:** [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md) - Core architectuur met 5-worker model
-   **Configuratie:** [`3_DE_CONFIGURATIE_TREIN.md`](3_DE_CONFIGURATIE_TREIN.md) - operators.yaml en event configuratie
-   **Worker Workflows:** [`5_DE_WORKFLOW_ORKESTRATIE.md`](5_DE_WORKFLOW_ORKESTRATIE.md) - Event workflows en causale IDs
-   **Operator Details:** [`2_ARCHITECTURE.md#27`](2_ARCHITECTURE.md#27-de-data-gedreven-operator) - BaseOperator en execution strategies
-   **Traceability:** [`2_ARCHITECTURE.md#25`](2_ARCHITECTURE.md#25-het-traceability-framework) - Causaal ID framework
-   **UI Integration:** [`6_FRONTEND_INTEGRATION.md`](6_FRONTEND_INTEGRATION.md) - Frontend visualisaties

---

## **9.8. Samenvatting: De Kracht van Meta Workflows**

### **9.8.1. Wat Maakt V3 Uniek?**

| Aspect | V2 | V3 |
|--------|----|----|
| **Worker Model** | 4 categorieën | 5 gespecialiseerde categorieën |
| **Optimalisatie** | Alleen worker parameters | Multi-dimensionaal (workers, operators, events) |
| **Causale Tracking** | Geen | OpportunityID, ThreatID in results |
| **Event Configuratie** | Niet mogelijk | Impliciete → Predefined → Custom |
| **Operator Testing** | Niet mogelijk | Execution & aggregation strategies |
| **Threat Analysis** | Niet mogelijk | Rejection patterns en threat impact |

### **9.8.2. Belangrijkste Voordelen**

1.  **Multidimensionale Optimalisatie** - Test niet alleen parameters, maar ook architecturale keuzes
2.  **Causale Transparantie** - Begrijp waarom configuraties wel/niet werken via OpportunityIDs en ThreatIDs
3.  **Flexibele Vergelijking** - Test worker types, operator strategies en event chains
4.  **Robuustheid Validatie** - Variant testing toont strategie gedrag onder verschillende condities
5.  **Intelligente Compositie** - Complexiteit komt van configuratie, niet van code

### **9.8.3. Use Cases**

**OptimizationService:**
-   Parameter tuning voor bestaande strategieën
-   Sub-type selection (welke OpportunityType werkt het beste?)
-   Operator strategy testing (SEQUENTIAL vs PARALLEL planning)
-   Event chain optimization (implicit vs custom)

**VariantTestService:**
-   A/B testing van strategische keuzes
-   Robuustheid validatie over verschillende marktregimes
-   Threat integration impact analyse
-   Exit strategy vergelijkingen

---

**Einde Document v3.0**

*"Van simpele parameter sweeps naar intelligente multi-dimensionale exploratie - waar data, configuratie en causaliteit samenkomen om strategische inzichten te ontsluiten."*