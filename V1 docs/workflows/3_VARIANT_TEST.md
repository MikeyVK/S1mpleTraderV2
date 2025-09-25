# 3. Variant Test Workflow

Dit document beschrijft de workflow van de `VariantTesterApp`. De architectuur volgt een "A/B test" of "head-to-head race" model, waarbij een klein aantal discrete strategie-varianten direct met elkaar worden vergeleken.

## 3.1. De Analogie: De Head-to-Head Race

1.  **De Deelnemers (`variant` blueprint):** De gebruiker levert een `variant` blueprint aan. Dit definieert de deelnemers aan de race, bijvoorbeeld: "Variant A gebruikt een `fixed_percentage_exit` en Variant B gebruikt een `atr_exit_planner`."
2.  **De Race-organisator (`VariantTestService`):** Deze service leest de lijst met deelnemers. Voor elke deelnemer stelt het een complete, unieke `run` configuratie samen.
3.  **Het Startschot (`ParallelRunService`):** De lijst met race-configuraties wordt overgedragen aan deze service, die voor elke variant tegelijk een volledige backtest start.
4.  **De Finishfoto (`VariantTestPresenter`):** Wanneer alle backtests voltooid zijn, verzamelt de presenter de eindresultaten en toont deze naast elkaar, zodat de gebruiker direct kan zien welke variant het beste heeft gepresteerd.

## 3.2. De Dataflow

**Input:** Gebruikersselectie van een `run` en een `variant` blueprint.

1.  **Actor:** `VariantTesterApp` (de Controller)
    * **Actie:** Vraagt de `VariantTestService` om de test uit te voeren.

2.  **Actor:** `VariantTestService` (de Race-organisator)
    * **Actie 1:** Laadt de `run` en `variant` blueprints.
    * **Actie 2:** Genereert een lijst van volledig uitgewerkte `run` configuraties, één voor elke gedefinieerde variant.
    * **Actie 3:** Roept de `ParallelRunService` aan met de lijst van configuraties.

3.  **Actor:** `ParallelRunService`
    * **Actie:** Start voor elke configuratie in de lijst een apart proces om `BacktestService.run_backtest()` uit te voeren.
    * **Output:** Een lijst van `BacktestResult` objecten.

4.  **Actor:** `VariantTesterApp`
    * **Actie:** Ontvangt de resultaten en geeft deze door aan de `VariantTestPresenter`.

5.  **Actor:** `VariantTestPresenter` (de Jury)
    * **Actie:** Formatteert de resultaten in een vergelijkende tabel en toont deze aan de gebruiker.