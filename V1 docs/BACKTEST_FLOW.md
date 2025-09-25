# S1mpleTrader: Backtest Data Flow Architecture

This document describes the data flow and component responsibilities for a single backtest run. The architecture follows an "assembly line" or "specialist team" model, where a trading idea is progressively enriched as it passes through a chain of modular components.

## The Specialist Team

The backtest workflow is orchestrated by a sequence of specialists, each with a single responsibility:

1.  **`PatternDetector`**: The "Scout". Scans market data for raw, potential opportunities.
2.  **`MatchFilter`**: The "Gatekeeper". Applies simple, objective filters to the raw opportunities.
3.  **`ExecutionPlanner`**: The "Timing Expert". Determines the precise entry tactic (e.g., price, order type) for a qualified opportunity.
4.  **`ExitPlanner`**: The "Strategist". Defines the initial risk parameters by calculating absolute stop-loss and take-profit prices.
5.  **`SizePlanner`**: The "Quartermaster". Calculates the final position size based on risk and account balance.
6.  **`TradeRefiner`**: The "Specialist". An optional component that can modify or veto a complete trade plan based on advanced rules (e.g., trailing stops, portfolio-level risk).
7.  **`OrderRouter`**: The "Execution Specialist". Translates the final trade plan into a specific order execution strategy (primarily for live trading).
8.  **`Portfolio`**: The "Bookkeeper". A "dumb" component that purely executes final orders and maintains the account state.

---

## The Data Flow Assembly Line

The process is a one-way flow of data, where each specialist passes a specific Data Transfer Object (DTO) to the next station. A single `TradingContext` object (the "toolbox") is passed to all relevant specialists.

**Input:** `[price_data]` (DataFrame) & `TradingContext` (Toolbox)

1.  **Actor:** `PatternDetector` & `MatchFilter`
    * **Output:** `PatternMatch` (DTO)
        * *Content:* `timestamp`, `asset`, `direction`

2.  **Actor:** `ExecutionPlanner`
    * **Input:** `PatternMatch`
    * **Output:** `ExecutionSignal` (DTO)
        * *Content:* All data from `PatternMatch` + `entry_price`, `entry_method`, `rules` (Set)

3.  **Actor:** `ExitPlanner`
    * **Input:** `ExecutionSignal`
    * **Output:** `PricedSignal` (DTO)
        * *Content:* All data from `ExecutionSignal` + `sl_price`, `tp_price`. The `rules` set can be added to (e.g., with `'LOCK_SL'`).

4.  **Actor:** `SizePlanner`
    * **Input:** `PricedSignal`
    * **Output:** `Trade` (DTO)
        * *Content:* All data from `PricedSignal` + `position_value_eur`, `position_size_asset`. The `rules`.

5.  **Actor:** `TradeRefiner`(s)
    * **Input:** `Trade`
    * **Output:** A (possibly modified) `Trade` object.

6.  **Actor:** `OrderRouter`
    * **Input:** The final `Trade`
    * **Output:** `ExecutionOrder` (DTO)
        * *Content:* `asset`, `direction`, `quantity`, `order_type`, `params`.

7.  **Actor:** `Portfolio`
    * **Input:** `ExecutionOrder`
    * **Action:** Executes the order and updates its internal state.

---

## DTO Glossary

| DTO Name          | Created By                        | Role / Content                                               |
| :---------------- | :------------------------------   | :----------------------------------------------------------- |
| `PatternMatch`    | `PatternDetector` / `MatchFilter` | The raw, filtered opportunity (what, where, when).           |
| `ExecutionSignal` | `ExecutionPlanner`                | A `PatternMatch` with a concrete entry tactic.               |
| `PricedSignal`    | `ExitPlanner`                     | An `ExecutionSignal` with absolute SL/TP prices.             |
| `Trade`           | `SizePlanner` / `TradeRefiner`    | The final, complete, and executable trade plan.              |
| `ExecutionOrder`  | `OrderRouter`                     | The specific instructions for the `Portfolio` or exchange.   |
| `TradingContext`  | `BacktestService`                 | The "toolbox" with all contex data (`price_data`, `balance`, etc.). |