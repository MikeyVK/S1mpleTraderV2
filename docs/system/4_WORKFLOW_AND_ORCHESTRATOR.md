# 4. De Quant Workflow & Orkestratie

Dit document beschrijft de volledige "data-assemblagelijn" van de S1mpleTrader V2 architectuur. De kern is een gelaagde workflow die een handelsidee systematisch transformeert, valideert en omzet in een uitvoerbaar handelsplan.

---
## 4.1. De 6-Fasen Trechter: Een Praktijkvoorbeeld

Elk handelsidee wordt systematisch gevalideerd door een vaste, logische trechter. We volgen een concreet voorbeeld: een **"Market Structure Shift + FVG Entry"** strategie.

#### **Fase 1: Regime Analyse**
* **Doel:** Is de markt überhaupt geschikt? Voor onze strategie willen we alleen handelen in een trending markt.
* **Input:** De ruwe `DataFrame` met OHLCV-data.
* **Proces (voorbeeld):** Een `ADXTrendFilter`-plugin berekent de ADX-indicator. De plugin is geconfigureerd om de strategie alleen te activeren als `ADX > 25`.
* **Output:** Een signaal dat de markt "in trend" is. De volgende fasen worden alleen voor deze periodes uitgevoerd.

#### **Fase 2: Structurele Context**
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?
* **Input:** De gefilterde `DataFrame`.
* **Proces (voorbeeld):** Een `MarketStructureDetector`-plugin analyseert de prijs en voegt twee nieuwe kolommen toe aan de data: `trend_direction` (met waarden als `bullish` of `bearish`) en `is_mss` (een `True`/`False` vlag op de candle waar een Market Structure Shift plaatsvindt).
* **Output:** Een **verrijkte `DataFrame` (`enriched_df`)**. We hebben nu "slimme" data.

#### **Fase 3: Signaal Generatie**
* **Doel:** Waar is de precieze, actiegerichte trigger? We zoeken naar een Fair Value Gap (FVG) ná een Market Structure Shift.
* **Input:** De `enriched_df`.
* **Proces (voorbeeld):** Een `FVGEntryDetector`-plugin scant de data. Wanneer het een rij tegenkomt waar `is_mss` `True` is, begint het te zoeken naar een FVG in de volgende candles. Als het er een vindt, genereert het een signaal.
* **Output:** Een **`Signal` DTO**. Dit object bevat: `{asset: 'BTC/EUR', timestamp: '2023-10-27 10:30:00', direction: 'long'}`.

#### **Fase 4: Signaal Verfijning**
* **Doel:** Is er bevestiging voor het signaal? We willen volume zien bij de FVG-entry.
* **Input:** Het `Signal` DTO en de `enriched_df`.
* **Proces (voorbeeld):** Een `VolumeSpikeRefiner`-plugin controleert het volume op de timestamp van het `Signal`. Als het volume lager is dan het 20-perioden gemiddelde, wordt het signaal afgekeurd en vernietigd.
* **Output:** Een **gevalideerd `Signal` DTO**.

#### **Fase 5: Trade Constructie**
* **Doel:** Wat is het concrete handelsplan?
* **Input:** Het gevalideerde `Signal` DTO.
* **Proces (voorbeeld):** Een `LiquidityTargetExit`-plugin wordt aangeroepen. Het plaatst de entry op de FVG-fill, de stop-loss onder de laatste swing low, en de take-profit op de volgende major liquidity high.
* **Output:** Een **`Trade` DTO**, met alle velden (entry, exit, size) ingevuld.

#### **Fase 6: Portfolio Overlay**
* **Doel:** Finale risico-check. Stel, we willen nooit meer dan 2% van ons kapitaal riskeren op één trade.
* **Input:** Het `Trade` DTO en de actuele `Portfolio`-staat.
* **Proces (voorbeeld):** Een `MaxRiskOverlay`-plugin berekent de potentiële verlies op de trade (`positiegrootte * |entry - stop_loss|`). Als dit bedrag meer is dan 2% van de totale equity van het portfolio, wordt de trade definitief afgekeurd.
* **Output:** Een **goedgekeurde `Trade` DTO**, klaar voor executie.

---
## 4.2. Rolverdeling: De Regisseur en de Projectmanager

### **De `StrategyOrchestrator` (De Regisseur)**
De `Orchestrator` is de **"regisseur"** van een enkele run. Hij is de eigenaar van de businesslogica en volgt het script van de 6-fasen trechter.

* **Plek:** `Service`-laag.
* **Verantwoordelijkheid:** Het end-to-end managen van één strategie-executie (backtest, paper, of live) door het `Assembly Team`, het `Portfolio`, en de `ExecutionEnvironment` in de juiste volgorde aan te sturen.

#### **Procesflow van de Orchestrator:**
1.  **Initialisatie:** Wordt geïnitialiseerd met een `AppConfig` en een `ExecutionEnvironment`. Hij creëert een `Portfolio`-object en een `AbstractPluginFactory`-instantie (het Assembly Team).
2.  **Fase 1 & 2 (Delegatie):** Roept de `Factory` aan om de `context_pipeline` uit te voeren en de `enriched_df` te genereren. De `Orchestrator` wacht tot dit proces is afgerond.
3.  **Fase 3-6 (Eigen Regie):** Met de `enriched_df` in de hand, begint de `Orchestrator` aan zijn event-loop, gestuurd door de `Clock` van de `Environment`. Voor elke tijdstap doorloopt hij Fase 3 t/m 6: hij vraagt de `Factory` de juiste plugins te bouwen en roept hun `process`-methodes in de juiste volgorde aan om van een `Signal` naar een goedgekeurde `Trade` te komen.
4.  **Executie:** Geeft de goedgekeurde `Trade` DTO door aan de `ExecutionHandler` in de `Environment`.
5.  **Afronding:** Verzamelt de finale data van het `Portfolio` en verpakt dit in een `BacktestResult`.


### **Het `Assembly Team` (De Technische Projectmanager)**
Het `Assembly Team` (geïmplementeerd als de `AbstractPluginFactory` en gerelateerde klassen) is het **"technische projectbureau"** en de machinekamer. Het weet niets over de 6 fasen of backtesten, maar is een expert in het beheren van plugins en het efficiënt uitvoeren van data-transformaties.

* **Plek:** `Backend`-laag.
* **Verantwoordelijkheid:** Het ontdekken, valideren, bouwen en technisch orkestreren van alle plugins.
* **Taken in Detail:**
    * **Plugin Discovery:** Scant de `plugins/`-map en bouwt een intern **Plugin Register**.
    * **Orkestratie van Context:** Voert de `context_pipeline` (Fase 1 & 2) uit, inclusief seriële en parallelle executie van workers.
    * **Dataflow Management:** Geeft de `DataFrame` door van de ene contextgroep naar de volgende en valideert of alle `dependencies` (uit het manifest) aanwezig zijn.
    * **Worker Constructie:** Bouwt op aanvraag van de `Orchestrator` een geïnstantieerde, gevalideerde plugin.

---
## 4.3. De Feedback Loops: Technisch vs. Strategisch

De architectuur faciliteert twee cruciale cycli:

1.  **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** **een run**. De staat van het `Portfolio` (het "domme" grootboek) wordt gebruikt als input voor de `Portfolio Overlay`-plugins in Fase 6. De resultaten uit het verleden beïnvloeden dus direct de beslissingen in het heden.
2.  **De Strategische "Supercharged" Ontwikkelcyclus (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** **de runs**, volgens het **"Bouwen -> Meten -> Leren"** principe. Je analyseert de resultaten van een backtest in de Web UI (**Meten**), ontdekt een zwakte (**Leren**), past de `YAML`-configuratie aan in de Strategy Builder (**Bouwen**) en start direct een nieuwe run.