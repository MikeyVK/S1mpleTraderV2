# 8. Meta Workflows: Van Analyse tot Inzicht

Dit document beschrijft de architectuur en de rol van de "Meta Workflows". Dit zijn hoog-niveau services die bovenop de kern-strategie-executie draaien om geavanceerde analyses, optimalisaties en automatisering mogelijk te maken.

---
## 8.1. Concept: De Orchestrator als Werknemer

De `StrategyOrchestrator` is de motor die in staat is om **één enkele** strategie-configuratie uit te voeren. Meta Workflows zijn services in de `Service`-laag die deze motor herhaaldelijk en systematisch aanroepen om complexe, kwantitatieve vragen te beantwoorden.

Ze fungeren als "onderzoekleiders" die de `StrategyOrchestrator` als een werknemer behandelen, en leunen zwaar op de `ParallelRunService` om duizenden backtests efficiënt en parallel uit te voeren. Waar optimalisatie in V1 een ad-hoc script was, wordt het in V2 een **"eerste klas burger"** van de architectuur.

---
## 8.2. De `OptimizationService` (Het Onderzoekslab)

* **Doel:** Het systematisch doorzoeken van een grote parameterruimte om de meest performante combinaties voor een strategie te vinden.
* **Analogie:** Een farmaceutisch lab dat duizenden moleculaire variaties test om het meest effectieve medicijn te vinden.

#### **Gedetailleerde Workflow:**

1.  **Input (Het Onderzoeksplan):** De service vereist een basis `run.yaml` (de strategie) en een `optimization.yaml` die de onderzoeksvraag definieert: welke parameters (`start`, `end`, `step`) moeten worden gevarieerd en op welke metriek (`sharpe_ratio`, `profit_factor`) moet worden geoptimaliseerd.

2.  **Proces (De Experimenten):**
    * De `OptimizationService` genereert een volledige lijst van alle mogelijke parameter-combinaties.
    * Voor elke combinatie creëert het een unieke `AppConfig` in het geheugen.
    * Het delegeert de volledige lijst van configuraties aan de `ParallelRunService`.

3.  **Executie (Het Robotleger):**
    * De `ParallelRunService` start een pool van workers (één per CPU-kern).
    * Elke worker ontvangt één configuratie, start een `StrategyOrchestrator` en voert een volledige backtest uit.

4.  **Output (De Analyse):**
    * De `OptimizationService` verzamelt alle `BacktestResult`-objecten.
    * Het creëert een `pandas DataFrame` met de geteste parameters en de resulterende performance-metrieken.
    * Deze data wordt naar de Web UI gestuurd voor presentatie in een interactieve, sorteerbare tabel.

---
## 8.3. De `VariantTestService` (De Vergelijkings-Arena)

* **Doel:** Het direct vergelijken van een klein aantal discrete strategie-varianten onder exact dezelfde marktomstandigheden om de robuustheid en de impact van specifieke keuzes te valideren.
* **Analogie:** Een "head-to-head" race tussen een paar topatleten om te zien wie de beste allrounder is.

#### **Gedetailleerde Workflow:**

1.  **Input (De Deelnemers):** De service vereist een basis `run.yaml` en een `variant.yaml` die de "deelnemers" definieert.
    * **Voorbeeld:**
        * **Variant A ("Baseline"):** De basisconfiguratie.
        * **Variant B ("Hoge RR"):** Overschrijft alleen de `risk_reward_ratio` parameter.
        * **Variant C ("Andere Exit"):** Vervangt de `ATR` exit-plugin door een `FixedPercentage` exit-plugin.

2.  **Proces (De Race-Opzet):**
    * De `VariantTestService` past voor elke gedefinieerde variant de "overrides" toe op de basisconfiguratie om unieke `AppConfig`-objecten te creëren.
    * Het delegeert de lijst van deze variant-configuraties aan de `ParallelRunService`.

3.  **Executie (Het Startschot):**
    * De `ParallelRunService` voert voor elke variant een volledige backtest uit.

4.  **Output (De Finishfoto):**
    * De `VariantTestService` verzamelt de `BacktestResult`-objecten.
    * Deze data wordt naar de Web UI gestuurd voor een directe, visuele vergelijking, bijvoorbeeld door de equity curves van alle varianten in één grafiek te plotten en een heatmap van de belangrijkste metrieken te tonen.

---
## 8.4. De Rol van `ParallelRunService`

Deze service is een cruciale, herbruikbare `Backend`-component. Zowel de `OptimizationService` als de `VariantTestService` zijn "klanten" van deze service. Zijn enige verantwoordelijkheid is het efficiënt managen van de `multiprocessing`-pool, het tonen van de voortgang en het netjes aggregeren van resultaten. Dit is een perfect voorbeeld van het **Single Responsibility Principle**.