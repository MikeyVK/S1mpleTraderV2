# 4. De Quant Workflow & Orkestratie

Dit document beschrijft de volledige "data-assemblagelijn" van de S1mpleTrader V2 architectuur. De kern is een gelaagde workflow die een handelsidee systematisch transformeert, valideert en omzet in een uitvoerbaar handelsplan.

---
## 4.1. De Workflow Trechter: Een Praktijkvoorbeeld

       ┌───────────────────────────────────────────┐
       │        RUWE DATAFRAME (OHLCV)             │
       └────────────────────┬──────────────────────┘
                            │
                            v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 1: REGIME CONTEXT (De "Weerman")                            │
│ Plugin: regime_context                                         │
│ Taak:   Voegt macro-context toe (bv. regime='trending').         │
└────────────────────┬─────────────────────────────────────────────┘
│
v
┌───────────────────────────────────────────┐
│   VERRIJKTE DATAFRAME (enriched_df)       │
└────────────────────┬──────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 2: STRUCTURELE CONTEXT (De "Cartograaf")                    │
│ Plugin: structural_context                                     │
│ Taak:   Voegt micro-context toe (bv. is_mss, support_level).   │
└────────────────────┬─────────────────────────────────────────────┘
│
v
┌───────────────────────────────────────────┐
│   FINALE ENRICHED DATAFRAME               │
└────────────────────┬──────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 3: SIGNAAL GENERATIE (De "Verkenner")                       │
│ Plugin: signal_generator                                       │
│ Taak:   Detecteert een specifieke, actiegerichte gebeurtenis.      │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: Signal
│ -------------------------------
│ { correlation_id, timestamp,
│   asset, direction, signal_type }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 4: SIGNAAL VERFIJNING (De "Kwaliteitscontroleur")           │
│ Plugin: signal_refiner                                         │
│ Taak:   Keurt een Signal goed of af op basis van secundaire criteria.│
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: Signal (of None)
│ -------------------------------
│ { ... (inhoud blijft gelijk) }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 5a: ENTRY PLANNING (De "Timing Expert")                     │
│ Plugin: execution_planner                                      │
│ Taak:   Bepaalt de precieze entry-prijs.                         │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: ExecutionSignal
│ -------------------------------
│ { ... (alles van Signal) +
│   entry_price, entry_method }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 5b: EXIT PLANNING (De "Strateeg")                           │
│ Plugin: exit_planner                                           │
│ Taak:   Berekent de initiële stop-loss en take-profit.           │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: PricedSignal
│ -------------------------------
│ { ... (alles van ExecutionSignal) +
│   sl_price, tp_price }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 5c: SIZE PLANNING (De "Logistiek Manager")                  │
│ Plugin: size_planner                                           │
│ Taak:   Berekent de definitieve positiegrootte.                  │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: Trade
│ -------------------------------
│ { ... (alles van PricedSignal) +
│   position_value_eur,
│   position_size_asset }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 6: PORTFOLIO OVERLAY (De "Risicomanager")                   │
│ Plugin: portfolio_overlay                                      │
│ Taak:   Voert een finale check uit op portfolio-niveau.          │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: Trade (of None)
│ -------------------------------
│ { ... (inhoud blijft gelijk) }
│
v
┌───────────────────────────────────────────┐
│        GOEDGEKEURD TRADE DTO              │
└────────────────────┬──────────────────────┘
│
v
[ Naar de ExecutionHandler ]


Elk handelsidee wordt systematisch gevalideerd door een vaste, logische trechter. We volgen een concreet voorbeeld: een **"Market Structure Shift + FVG Entry"** strategie.

#### **Fase 1: Regime Context (De "Weerman")**
* **Doel:** Wat is de algemene "weersverwachting" van de markt? Deze fase classificeert de marktomstandigheid.
* **Input:** De ruwe `DataFrame` (OHLCV).
* **Proces (voorbeeld):** Een `ADXContext`-plugin (`type: regime_context`) voegt een kolom `regime` toe met waarden als `'trending'` of `'ranging'`.
* **Output:** Een verrijkte `DataFrame`. Er wordt alleen context toegevoegd.

#### **Fase 2: Structurele Context (De "Cartograaf")**
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?
* **Input:** De verrijkte `DataFrame` uit Fase 1.
* **Proces (voorbeeld):** Een `MarketStructureDetector`-plugin (`type: structural_context`) voegt `trend_direction` en `is_mss` kolommen toe.
* **Output:** De finale `enriched_df` met meerdere lagen context.

#### **Fase 3: Signaal Generatie (De "Verkenner")**
* **Doel:** Waar is de precieze, actiegerichte trigger?
* **Input:** De `enriched_df`.
* **Proces (voorbeeld):** Een `FVGEntryDetector`-plugin (`type: signal_generator`) detecteert een FVG ná een `is_mss` vlag.
* **Output:** Een **`Signal` DTO**. Dit is een gestandaardiseerd data-object dat een potentieel handelskans vertegenwoordigt. `{ correlation_id, timestamp, asset, direction, signal_type }`.

#### **Fase 4: Signaal Verfijning (De "Kwaliteitscontroleur")**
* **Doel:** Is er bevestiging voor het signaal? Weurt het goedgekeurd op basis van secundaire criteria?
* **Input:** Het `Signal` DTO en de `enriched_df`.
* **Proces (voorbeeld):** Een `VolumeSpikeRefiner`-plugin (`type: signal_refiner`) controleert of het volume op de signaalkaars bovengemiddeld is.
* **Output:** Het oorspronkelijke **`Signal` DTO** als het wordt goedgekeurd, anders `None`.

#### **Fase 5a: Entry Planning (De "Timing Expert")**
* **Doel:** Wat is de precieze entry-prijs voor ons goedgekeurde signaal?
* **Input:** Het gevalideerde `Signal` DTO.
* **Proces (voorbeeld):** Een `LimitEntryPlanner`-plugin (`type: execution_planner`) bepaalt dat de entry een limietorder moet zijn op de 50% retracement van de FVG.
* **Output:** Een **`ExecutionSignal` DTO**, die alle data van `Signal` bevat, plus `{ entry_price, entry_method }`.

#### **Fase 5b: Exit Planning (De "Strateeg")**
* **Doel:** Wat is het initiële plan voor risico- en winstmanagement?
* **Input:** Het `ExecutionSignal` DTO.
* **Proces (voorbeeld):** Een `LiquidityTargetExit`-plugin (`type: exit_planner`) plaatst de stop-loss onder de laatste swing low en de take-profit op de volgende major liquidity high.
* **Output:** Een **`PricedSignal` DTO**, die alle data van `ExecutionSignal` bevat, plus `{ sl_price, tp_price }`.

#### **Fase 5c: Size Planning (De "Logistiek Manager")**
* **Doel:** Wat is de definitieve positiegrootte, gegeven ons risicoplan?
* **Input:** Het `PricedSignal` DTO en de `Portfolio`-staat.
* **Proces (voorbeeld):** Een `FixedRiskSizer`-plugin (`type: size_planner`) berekent de positiegrootte zodat het verschil tussen `entry_price` en `sl_price` exact 1% van de totale equity van het portfolio is.
* **Output:** Een finaal **`Trade` DTO**. Dit is een compleet, uitvoerbaar plan met alle benodigde informatie, inclusief `{ position_value_eur, position_size_asset }`.

#### **Fase 6: Portfolio Overlay (De "Risicomanager")**
* **Doel:** Finale check op portfolio-niveau. Past deze trade binnen onze overkoepelende risicostrategie?
* **Input:** Het volledige `Trade` DTO en de actuele `Portfolio`-staat.
* **Proces (voorbeeld):** Een `MaxExposureOverlay`-plugin (`type: portfolio_overlay`) controleert of de `position_value_eur` van deze nieuwe trade, opgeteld bij alle openstaande posities, niet de maximale exposure-limiet van het portfolio overschrijdt.
* **Output:** Het **goedgekeurde `Trade` DTO** als het de check passeert, anders `None`. Dit wordt vervolgens naar de `ExecutionHandler` gestuurd.

---
## 4.2. Rolverdeling: De Regisseur en de Projectmanager

### **De `StrategyOrchestrator` (De Regisseur)**
De `Orchestrator` is de **"regisseur"** van een enkele run. Hij is de eigenaar van de businesslogica en volgt het script van de workflow trechter.

#### **Procesflow van de Orchestrator:**
1.  **Initialisatie:** Wordt geïnitialiseerd met een `AppConfig` en een `ExecutionEnvironment`.
2.  **Fase 1 & 2 (Delegatie):** Roept de `Factory` aan om de `context_pipeline` uit te voeren en de `enriched_df` te genereren.
3.  **Fase 3-6 (Eigen Regie):** Met de `enriched_df` in de hand, begint de `Orchestrator` aan zijn event-loop. Voor elke tijdstap doorloopt hij de volledige trechter:
    * Hij roept de `signal_generator` aan.
    * Als er een `Signal` DTO uitkomt, stuurt hij deze door de `signal_refiner`.
    * Als het signaal overleeft, wordt het DTO stapsgewijs verrijkt door de `execution_planner`, `exit_planner`, en `size_planner` tot een compleet `Trade` DTO.
    * Tot slot wordt dit `Trade` DTO gevalideerd door de `portfolio_overlay`.
4.  **Executie:** Geeft het finale, goedgekeurde `Trade` DTO door aan de `ExecutionHandler`.
5.  **Afronding:** Verzamelt de data van het `Portfolio` en verpakt dit in een `BacktestResult`.

### **Het `Assembly Team` (De Technische Projectmanager)**
Het `Assembly Team` (`AbstractPluginFactory`) is het **"technische projectbureau"**. Het weet niets over de fasen, maar is expert in het beheren en uitvoeren van plugins.

* **Plek:** `Backend`-laag.
* **Verantwoordelijkheid:** Het ontdekken, bouwen en technisch orkestreren van alle plugins.
* **Taken in Detail:**
    * **Plugin Discovery:** Scant de `plugins/`-map en bouwt een intern **Plugin Register**.
    * **Orkestratie van Context:** Voert de `context_pipeline` (Fase 1 & 2) uit, inclusief seriële en parallelle executie van workers.
    * **Worker Constructie:** Bouwt op aanvraag van de `Orchestrator` een geïnstantieerde, gevalideerde plugin.

---
## 4.3. De Feedback Loops: Technisch vs. Strategisch

De architectuur faciliteert twee cruciale cycli:

1.  **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** **een run**. De staat van het `Portfolio` (het "domme" grootboek) wordt gebruikt als input voor de `Portfolio Overlay`-plugins in Fase 6. De resultaten uit het verleden beïnvloeden dus direct de beslissingen in het heden.
2.  **De Strategische "Supercharged" Ontwikkelcyclus (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** **de runs**, volgens het **"Bouwen -> Meten -> Leren"** principe. Je analyseert de resultaten van een backtest in de Web UI (**Meten**), ontdekt een zwakte (**Leren**), past de `YAML`-configuratie aan in de Strategy Builder (**Bouwen**) en start direct een nieuwe run.