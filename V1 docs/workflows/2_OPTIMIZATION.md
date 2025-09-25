# 2. Optimalisatie Workflow

Dit document beschrijft de workflow van de `OptimizerApp`. De architectuur volgt een "onderzoekslab" model, waarbij een reeks experimenten wordt uitgevoerd om de meest performante parameters voor een strategie te vinden.

## 2.1. De Analogie: Het Onderzoekslab

1.  **De Onderzoeksvraag (`optimization` blueprint):** De gebruiker levert een `optimization` blueprint aan. Dit document bevat de 'onderzoeksvraag': "Wat is de beste combinatie van `atr_multiplier` en `rr_ratio` voor de `atr_exit` planner?"
2.  **De Labmanager (`OptimizationService`):** Deze service leest de onderzoeksvraag en genereert een lijst van alle mogelijke "experimenten". Elk experiment is een complete, unieke configuratie met één specifieke combinatie van de te testen parameters.
3.  **Het Robotleger (`ParallelRunService`):** De lijst met experimenten wordt overgedragen aan deze service. Het robotleger voert voor elk experiment een volledige, onafhankelijke backtest uit, parallel aan elkaar om tijd te besparen.
4.  **De Resultatenanalyse (`OptimizationPresenter`):** Zodra alle experimenten zijn afgerond, verzamelt de presenter de resultaten en toont deze in een overzichtelijke tabel, gerangschikt van de beste naar de slechtste prestatie.

## 2.2. De Dataflow

**Input:** Gebruikersselectie van een `run` en een `optimization` blueprint.

1.  **Actor:** `OptimizerApp` (de Controller)
    * **Actie:** Vraagt de `OptimizationService` om de optimalisatie uit te voeren met de geselecteerde blueprints.

2.  **Actor:** `OptimizationService` (de Labmanager)
    * **Actie 1:** Laadt de `run` en `optimization` blueprints en combineert ze.
    * **Actie 2:** Genereert een lijst van tijdelijke, volledig uitgewerkte `run` configuraties, één voor elke parametercombinatie.
    * **Actie 3:** Roept de `ParallelRunService` aan met de lijst van configuraties.

3.  **Actor:** `ParallelRunService` (het Robotleger)
    * **Actie:** Start voor elke configuratie in de lijst een apart proces om `BacktestService.run_backtest()` uit te voeren.
    * **Output:** Een lijst van `BacktestResult` objecten.

4.  **Actor:** `OptimizerApp`
    * **Actie:** Ontvangt de lijst van resultaten en geeft deze door aan de `OptimizationPresenter`.

5.  **Actor:** `OptimizationPresenter` (de Analist)
    * **Actie:** Formatteert de resultaten in een duidelijke tabel en toont deze aan de gebruiker.