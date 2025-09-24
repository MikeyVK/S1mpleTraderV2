# 4. De Workflow & Orkestratie (Gedetailleerde Uwerking)

Dit document beschrijft de volledige data-assemblagelijn van de S1mpleTrader V2 architectuur, van ruwe marktdata tot een uitgevoerd handelsplan.

## 4.1. De 6-Fasen Trechter: Een Gedetailleerde Data-Assemblagelijn

Elke fase is een werkstation. Een "product" (een trade-idee) wordt alleen doorgegeven aan het volgende station als het de kwaliteitscontrole van het huidige station doorstaat.

#### **Fase 1: Regime Analyse**
* **Doel:** Bepalen of de huidige marktomstandigheden überhaupt geschikt zijn voor de beoogde strategie.
* **Input:** De ruwe, volledige `DataFrame` met OHLCV-data.
* **Proces:** `Regime Filter`-plugins (uitgevoerd door de `Factory`) analyseren de data. Een `TrendRegime`-plugin kan bijvoorbeeld de ADX berekenen en besluiten dat alleen periodes met ADX > 25 "interessant" zijn.
* **Output (Artefact):** Een **gefilterde `DataFrame`**. Rijen die niet voldoen aan de regime-eisen worden *conceptueel* genegeerd voor de volgende fasen.

#### **Fase 2: Structurele Context**
* **Doel:** De gefilterde marktdata "leesbaar" maken door er structurele betekenis aan te geven.
* **Input:** De gefilterde `DataFrame` uit Fase 1.
* **Proces:** `Structural Context`-plugins (uitgevoerd door de `Factory` in seriële/parallelle groepen) voegen kolommen toe. De `MarketStructureDetector` voegt `trend_state` en `current_range_high` toe.
* **Output (Artefact):** Een **verrijkte `DataFrame` (`enriched_df`)**. Dit is de "slimme" data waarop alle volgende beslissingen worden gebaseerd.

#### **Fase 3: Signaal Generatie**
* **Doel:** Op basis van de verrijkte context zoeken naar specifieke, actiegerichte entry-triggers.
* **Input:** De `enriched_df`.
* **Proces:** `Signal Generator`-plugins scannen de `enriched_df` op zoek naar condities die een potentieel signaal vormen.
* **Output (Artefact):** Een `Signal` DTO. Dit object zegt: "Op *deze* timestamp, voor *dit* asset, is er een potentieel `long` signaal."

#### **Fase 4: Signaal Verfijning**
* **Doel:** De waarschijnlijkheid van het signaal verhogen door te zoeken naar bevestiging (confluentie).
* **Input:** Een `Signal` DTO en de `enriched_df`.
* **Proces:** `Signal Refiner`-plugins passen veto-logica toe. Een `VolumeSpikeRefiner` controleert het volume op de timestamp van het `Signal`. Is het te laag? Dan wordt het signaal vernietigd.
* **Output (Artefact):** Een **gevalideerd `Signal` DTO**.

#### **Fase 5: Trade Constructie**
* **Doel:** Het gevalideerde signaal omzetten in een concreet, uitvoerbaar handelsplan.
* **Input:** Een gevalideerd `Signal` DTO en de `enriched_df`.
* **Proces:** Een interne mini-pijplijn: `EntryPricePlanner` -> `ExitPricePlanner` -> `PositionSizePlanner`.
* **Output (Artefact):** Een `Trade` DTO, met alle informatie: asset, richting, entry, exit, en grootte.

#### **Fase 6: Portfolio Overlay**
* **Doel:** De finale "sanity check" op portfolio-niveau.
* **Input:** Een `Trade` DTO en de `Portfolio`-staat (equity, open posities, etc.).
* **Proces:** `Portfolio Overlay`-plugins passen de laatste veto-logica toe. Een `MaxDrawdownOverlay` kan de trade afkeuren als de portfolio in een te diepe drawdown zit.
* **Output (Artefact):** Een **goedgekeurde `Trade` DTO**, klaar voor executie.

---
## 4.2. De Rol van de `StrategyOrchestrator` (De Regisseur)

De `Orchestrator` is de "regisseur" van een enkele run. Hij is de eigenaar van de businesslogica en volgt het script van de 6-fasen trechter.

* **Plek:** `Service`-laag.
* **Verantwoordelijkheid:** Het end-to-end managen van één strategie-executie (backtest, paper, of live) door de `Factory`, het `Portfolio`, en de `ExecutionEnvironment` in de juiste volgorde aan te sturen.

#### **Procesflow van de Orchestrator:**
1.  **Initialisatie:** Wordt geïnitialiseerd met een `AppConfig` en een `ExecutionEnvironment`. Hij creëert een `Portfolio`-object en een `AbstractPluginFactory`-instantie.
2.  **Fase 1 & 2 (Delegatie):** Roept de `Factory` aan om de `context_pipeline` uit te voeren en de `enriched_df` te genereren. De `Orchestrator` wacht tot dit proces is afgerond.
3.  **Fase 3-6 (Eigen Regie):** Met de `enriched_df` in de hand, begint de `Orchestrator` aan zijn event-loop, gestuurd door de `Clock` van de `Environment`. Voor elke tijdstap doorloopt hij Fase 3 t/m 6: hij vraagt de `Factory` de juiste plugins te bouwen en roept hun `process`-methodes in de juiste volgorde aan om van `Signal` naar een goedgekeurde `Trade` te komen.
4.  **Executie:** Geeft de goedgekeurde `Trade` DTO door aan de `ExecutionHandler` in de `Environment`.
5.  **Afronding:** Verzamelt de finale data van het `Portfolio` en verpakt dit in een `BacktestResult`.

---
## 4.3. De Rol van de `AbstractPluginFactory` (De Technische Projectmanager)

De `Factory` is de "technische projectmanager" en machinekamer. Hij weet niets over backtesten, maar is een expert in het beheren van plugins en het efficiënt uitvoeren van data-transformaties.

* **Plek:** `Backend`-laag.
* **Verantwoordelijkheid:** Het ontdekken, valideren, bouwen en technisch orkestreren van alle plugins.

#### **Taken van de Factory in Detail:**
* **Plugin Discovery:** Scant bij initialisatie de `plugins/`-map, valideert alle `plugin_manifest.yaml`-bestanden en bouwt een intern **Plugin Register**.
* **Orkestratie van Context:** Voert de `context_pipeline` (Fase 1 & 2) uit. Dit is zijn meest complexe taak, waarbij hij seriële groepen en de parallelle executie van workers binnen die groepen beheert.
* **Dataflow Management:** Geeft de `DataFrame` (de "snijplank") door van de ene contextgroep naar de volgende. Cruciaal hierbij is dat hij voor elke worker controleert of de vereiste `dependencies` (uit het manifest) aanwezig zijn als kolommen in de `DataFrame`.
* **Worker Constructie:** Bouwt op aanvraag van de `Orchestrator` een geïnstantieerde, gevalideerde plugin uit het register.

---
## 4.4. De Feedback Loop: Technisch vs. Strategisch

De term "feedback loop" verwijst naar twee verschillende cycli:

1.  **De Technische Feedback Loop (Real-time):** Dit gebeurt *binnen* een run. De staat van het `Portfolio` (bv. huidige drawdown) wordt gebruikt als input voor de `Portfolio Overlay`-plugins in Fase 6. De resultaten van het verleden beïnvloeden dus direct de beslissingen in het heden.
2.  **De Strategische Feedback Loop (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt *tussen* de runs. Je analyseert de resultaten van een backtest (Meten), ontdekt een zwakte (Leren), past de `YAML`-configuratie aan (Bouwen) en start een nieuwe run. De architectuur is ontworpen om deze cyclus zo snel en frictieloos mogelijk te maken.