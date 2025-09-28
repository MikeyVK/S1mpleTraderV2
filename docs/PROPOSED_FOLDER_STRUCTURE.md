S1mpleTrader_V2/
├── config/
│   ├── runs/
│   │   └── mss_fvg_strategy.yaml
│   ├── optimizations/
│   │   └── optimize_atr_params.yaml
│   ├── variants/
│   │   └── robustness_test.yaml
│   ├── overrides/
│   │   └── use_eth_pair.yaml
│   ├── index.yaml
│   └── platform.yaml
│
├── plugins/
│   ├── regime_filters/
│   │   └── adx_trend_filter/
│   │       ├── init.py
│   │       ├── plugin_manifest.yaml
│   │       ├── worker.py
│   │       ├── schema.py
│   │       └── tests/
│   │           └── test_worker.py
│   │
│   ├── structural_context/
│   │   └── market_structure_detector/
│   │       ├── init.py
│   │       ├── plugin_manifest.yaml
│   │       ├── worker.py
│   │       ├── schema.py
│   │       └── tests/
│   │           └── test_worker.py
│   │
│   ├── signal_generators/
│   │   └── fvg_entry_detector/
│   │       ├── init.py
│   │       ├── plugin_manifest.yaml
│   │       ├── worker.py
│   │       ├── schema.py
│   │       └── tests/
│   │           └── test_worker.py
│   │
│   ├── signal_refiners/
│   │   └── volume_spike_refiner/
│   │       ├── init.py
│   │       ├── plugin_manifest.yaml
│   │       ├── worker.py
│   │       ├── schema.py
│   │       └── tests/
│   │           └── test_worker.py
│   │
│   ├── trade_constructors/
│   │   └── liquidity_target_exit/
│   │       ├── init.py
│   │       ├── plugin_manifest.yaml
│   │       ├── worker.py
│   │       ├── schema.py
│   │       └── tests/
│   │           └── test_worker.py
│   │
│   └── portfolio_overlays/
│       └── max_drawdown_overlay/
│           ├── init.py
│           ├── plugin_manifest.yaml
│           ├── worker.py
│           ├── schema.py
│           └── tests/
│               └── test_worker.py
│
├── backend/
│   ├── config/
│   │   └── schemas/
│   │       ├── init.py
│   │       ├── app_schema.py
│   │       └── run_schema.py
│   │
│   ├── assembly/
│   │   ├── init.py
│   │   ├── plugin_registry.py
│   │   ├── worker_builder.py
│   │   └── context_pipeline_runner.py
│   │
│   ├── core/
│   │   ├── init.py
│   │   ├── portfolio.py
│   │   ├── execution.py
│   │   ├── performance_analyzer.py
│   │   ├── interfaces.py
│   │   └── constants.py
│   │
│   ├── environments/
│   │   ├── init.py
│   │   ├── base_environment.py
│   │   ├── backtest_environment.py
│   │   ├── paper_environment.py
│   │   └── live_environment.py
│   │
│   ├── dtos/
│   │   ├── init.py
│   │   ├── signal.py
│   │   ├── trade.py
│   │   ├── closed_trade.py
│   │   └── backtest_result.py
│   │
│   └── utils/
│       ├── init.py
│       ├── app_logger.py
│       ├── translator.py
│       └── data_utils.py
│
├── services/
│   ├── init.py
│   ├── strategy_orchestrator.py
│   ├── optimization_service.py
│   ├── variant_test_service.py
│   ├── parallel_run_service.py
│   └── api_services/
│       ├── init.py
│       ├── plugin_query_service.py
│       └── visualization_service.py
│
├── frontends/
│   ├── web/
│   │   ├── api/
│   │   │   ├── init.py
│   │   │   ├── main.py
│   │   │   └── routers/
│   │   │       ├── init.py
│   │   │       ├── plugins_router.py
│   │   │       └── backtest_router.py
│   │   └── ui/
│   │       ├── src/
│   │       │   ├── components/
│   │       │   ├── services/
│   │       │   └── App.tsx
│   │       └── package.json
│   │
│   └── cli/
│       ├── presenters/
│       │   └── optimization_presenter.py
│       └── reporters/
│           └── cli_reporter.py
│
├── docs/
│   └── system/
│       ├── V2_ARCHITECTURE.md
│       ├── 3_PLUGIN_ANATOMY.md
│       ├── 4_WORKFLOW_AND_ORCHESTRATION.md
│       ├── 5_FRONTEND_INTEGRATION.md
│       ├── 6_RESILIENCE_AND_OPERATIONS.md
│       └── 7_DEVELOPMENT_STRATEGY.md
│
├── locales/
│   ├── en.yaml
│   └── nl.yaml
│
├── tools/
│   ├── generate_structure.py
│   └── plugin_creator.py
│
├── source_data/
│   └── BTC_EUR_15m.csv
│
├── results/
│   └── 20250924_213000_mss_fvg_strategy/
│       ├── run_config.yaml
│       ├── result_trades.csv
│       ├── result_metrics.yaml
│       └── run.log.json
│
├── run_web.py
├── run_supervisor.py
├── run_backtest_cli.py
└── pyproject.toml