# S1mpleTrader Configuration Structure

This document describes the structure of the `backtest_pipeline` section within a configuration file. This structure is designed to be fully self-descriptive and drives the `PipelineFactory`.

## Top-Level Key: `backtest_pipeline`

This key contains the entire configuration for a single backtest run and is composed of two main parts: the `TASKBOARD` and the `WORKFORCE`.

### `TASKBOARD` (The "What")

The `TASKBOARD` defines **what** should be built for a specific run. It contains a key for each **task** in the pipeline (e.g., `pattern_detection`, `exit_planning`).

-   You only need to specify the workers that **deviate** from the default setup. If a key is empty or not present on the `TASKBOARD`, the factory will use the `default` specified in the `WORKFORCE`.

### `WORKFORCE` (The "Who" and "How")

The `WORKFORCE` is the complete library of all available workers and the rules to build them.

#### 1. `import_base_path`
-   A single string that defines the root Python import path for all strategy components (e.g., `"backend.strategies"`).

#### 2. `tasks` (The "Job Profiles")
-   This section defines the profiles for each type of task. The factory uses this to understand how to build a worker for a given task. Each profile contains:
    -   `folder` (str): The name of the sub-directory in `import_base_path`.
    -   `suffix` (str): The class name suffix.
    -   `default`: The default worker(s) to load. The **data type** of this value is crucial:
        -   A **list** (e.g., `[]` or `[default_a]`) implies the task uses **0..N workers**.
        -   A **string** (e.g., `my_default_planner`) implies the task uses **one** worker.

#### 3. `definitions` (The "CVs")
-   A dictionary containing the definitions for all available workers, grouped by their task.
-   The key for each group must correspond to a key in the `tasks` section.

### Complete Example
```yaml
backtest_pipeline:
  TASKBOARD:
    pattern_detection: [mss_bull, mss_bear]
    match_filtering: [adx, volume]
    # exit_planning and others will be loaded via their default.

  WORKFORCE:
    import_base_path: "backend.strategies"

    tasks:
      pattern_detection:
        folder: "pattern_detectors"
        suffix: "Pattern"
        default: []
      exit_planning:
        folder: "exit_planners"
        suffix: "Plan"
        default: fixed_percentage_exit

    definitions:
      pattern_detection:
        - name: mss_bull
          params: { ... }
      exit_planning:
        - name: fixed_percentage_exit
          params: { ... }