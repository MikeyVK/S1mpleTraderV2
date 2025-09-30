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
│ Plugin: regime_context                                           │
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
│ Plugin: structural_context                                       │
│ Taak:   Voegt micro-context toe (bv. is_mss, support_level).     │
└────────────────────┬─────────────────────────────────────────────┘
│
v
┌───────────────────────────────────────────┐
│   FINALE ENRICHED DATAFRAME               │
└────────────────────┬──────────────────────┘
│ (Start StrategyEngine Loop)
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 3: SIGNAAL GENERATIE (De "Verkenner")                       │
│ Plugin: signal_generator                                         │
│ Taak:   Detecteert een specifieke, actiegerichte gebeurtenis.    │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: Signal
│ -------------------------------
│ { correlation_id, timestamp, asset,
│   direction, signal_type }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 4: SIGNAAL VERFIJNING (De "Kwaliteitscontroleur")           │
│ Plugin: signal_refiner                                           │
│ Taak:   Keurt Signal goed of af op basis van secundaire criteria.│
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: Signal (of None)
│ -------------------------------
│ { ... (inhoud blijft gelijk) }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 5: ENTRY PLANNING (De "Timing Expert")                      │
│ Plugin: entry_planner                                            │
│ Taak:   Bepaalt de precieze entry-prijs.                         │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: EntrySignal
│ -------------------------------
│ { correlation_id (gepromoot),
│   signal: Signal (genest),
│   + entry_price }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 6: EXIT PLANNING (De "Strateeg")                            │
│ Plugin: exit_planner                                             │
│ Taak:   Berekent de initiële stop-loss en take-profit.           │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: RiskDefinedSignal
│ -------------------------------
│ { correlation_id (gepromoot),
│   entry_signal: EntrySignal (genest),
│   + sl_price, tp_price }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 7: SIZE PLANNING (De "Logistiek Manager")                   │
│ Plugin: size_planner                                             │
│ Taak:   Berekent de definitieve positiegrootte.                  │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: TradePlan
│ -------------------------------
│ { correlation_id (gepromoot),
│   risk_defined_signal: RiskDefinedSignal (genest),
│   + position_value_quote, position_size_asset }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 8: ORDER ROUTING (De "Verkeersleider")                      │
│ Plugin: order_router                                             │
│ Taak:   Vertaalt het plan naar technische executie-instructies.  │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: RoutedTradePlan
│ -------------------------------
│ { correlation_id (gepromoot),
│   trade_plan: TradePlan (genest),
│   + order_type, time_in_force, ... }
│
v
┌──────────────────────────────────────────────────────────────────┐
│ Fase 9: CRITICAL EVENT DETECTION (De "Waakhond")                 │
│ Plugin: critical_event_detector                                  │
│ Taak:   Detecteert systeem-brede risico's (bv. max drawdown).    │
└────────────────────┬─────────────────────────────────────────────┘
│
│ DTO: CriticalEvent
│ -------------------------------
│ { correlation_id, event_type, timestamp }
│
v
┌───────────────────────────────────────────┐
│        FINAAL TRADEPROPOSAL DTO           │
│ { routed_trade_plan?, critical_event? }   │
└────────────────────┬──────────────────────┘
│
v
[ Naar de Workflow Service & ExecutionHandler ]

Elk handelsidee wordt systematisch gevalideerd door een vaste, logische trechter. We volgen een concreet voorbeeld: een **"Market Structure Shift + FVG Entry"** strategie.

#### **Fase 1: Regime Context (De "Weerman")**
* **Doel:** Wat is de algemene "weersverwachting" van de markt? Deze fase classificeert de marktomstandigheid zonder data weg te gooien.
* **Input:** De ruwe `DataFrame` met OHLCV-data.
* **Proces (voorbeeld):** Een `ADXContext`-plugin (`type: regime_context`) berekent de ADX-indicator en voegt een nieuwe kolom `regime` toe. Deze kolom krijgt de waarde 'trending' als `ADX > 25` en 'ranging' als `ADX < 25`.
* **Output:** Een verrijkte `DataFrame`. Er wordt geen data verwijderd; er wordt alleen een contextuele "tag" toegevoegd aan elke rij.

#### **Fase 2: Structurele Context (De "Cartograaf")**
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?
* **Input:** De verrijkte `DataFrame` uit Fase 1.
* **Proces (voorbeeld):** Een `MarketStructureDetector`-plugin (`type: structural_context`) analyseert de prijs en voegt twee nieuwe kolommen toe: `trend_direction` (met waarden als `bullish` of `bearish`) en `is_mss` (een `True`/`False` vlag op de candle waar een Market Structure Shift plaatsvindt).
* **Output:** De finale `enriched_df`. We hebben nu "slimme" data met meerdere lagen context, klaar voor de `StrategyEngine`.

#### **Fase 3: Signaal Generatie (De "Verkenner")**
* **Doel:** Waar is de precieze, actiegerichte trigger? We zoeken naar een Fair Value Gap (FVG) ná een Market Structure Shift.
* **Input:** De `enriched_df` (via het `TradingContext` object).
* **Proces (voorbeeld):** Een `FVGEntryDetector`-plugin (`type: signal_generator`) scant de data. Wanneer het een rij tegenkomt waar `is_mss` `True` is, begint het te zoeken naar een FVG. Als het er een vindt, genereert het een signaal.
* **Output:** Een **`Signal` DTO**. Dit object krijgt een unieke `correlation_id` (UUID) en bevat de essentie: `{asset: 'BTC/EUR', timestamp: '...', direction: 'long', signal_type: 'fvg_entry'}`.

#### **Fase 4: Signaal Verfijning (De "Kwaliteitscontroleur")**
* **Doel:** Is er bevestiging voor het signaal? We willen volume zien bij de FVG-entry.
* **Input:** Het `Signal` DTO en het `TradingContext`.
* **Proces (voorbeeld):** Een `VolumeSpikeRefiner`-plugin (`type: signal_refiner`) controleert het volume op de timestamp van het `Signal`. Als het volume te laag is, wordt het signaal afgekeurd.
* **Output:** Het **gevalideerde `Signal` DTO** of `None`. De `correlation_id` blijft behouden.

#### **Fase 5: Entry Planning (De "Timing Expert")**
* **Doel:** Wat is de precieze entry-prijs voor ons goedgekeurde signaal?
* **Input:** Het gevalideerde `Signal` DTO.
* **Proces (voorbeeld):** Een `LimitEntryPlanner`-plugin (`type: entry_planner`) bepaalt dat de entry een limietorder moet zijn op de 50% retracement van de FVG.
* **Output:** Een **`EntrySignal` DTO**. Dit DTO *nest* het originele `Signal` en verrijkt het met `{ entry_price: 34500.50 }`. De `correlation_id` wordt gepromoot naar het top-level voor gemakkelijke toegang.

#### **Fase 6: Exit Planning (De "Strateeg")**
* **Doel:** Wat is het initiële plan voor risico- en winstmanagement?
* **Input:** Het `EntrySignal` DTO.
* **Proces (voorbeeld):** Een `LiquidityTargetExit`-plugin (`type: exit_planner`) plaatst de stop-loss onder de laatste swing low en de take-profit op de volgende major liquidity high.
* **Output:** Een **`RiskDefinedSignal` DTO**. Nest het `EntrySignal` en voegt `{ sl_price: 34200.0, tp_price: 35100.0 }` toe.

#### **Fase 7: Size Planning (De "Logistiek Manager")**
* **Doel:** Wat is de definitieve positiegrootte, gegeven ons risicoplan en kapitaal?
* **Input:** Het `RiskDefinedSignal` DTO en het `Portfolio` (via `TradingContext`).
* **Proces (voorbeeld):** Een `FixedRiskSizer`-plugin (`type: size_planner`) berekent de positiegrootte zodat het risico (`entry_price - sl_price`) exact 1% van de totale equity van het portfolio is.
* **Output:** Een **`TradePlan` DTO**. Dit DTO nest het `RiskDefinedSignal` en bevat de finale, berekende `{ position_value_quote: 1000.0, position_size_asset: 0.0289 }`. Dit is het complete *strategische* plan.

#### **Fase 8: Order Routing (De "Verkeersleider")**
* **Doel:** Hoe moet dit strategische plan *technisch* worden uitgevoerd?
* **Input:** Het `TradePlan` DTO.
* **Proces (voorbeeld):** Een `DefaultRouter`-plugin (`type: order_router`) vertaalt het plan naar concrete order-instructies.
* **Output:** Een **`RoutedTradePlan` DTO**. Dit nest het `TradePlan` en voegt de *tactische* executie-instructies toe, zoals `{ order_type: 'limit', time_in_force: 'GTC' }`. Dit is de definitieve opdracht voor de `ExecutionHandler`.

#### **Fase 9: Critical Event Detection (De "Waakhond")**
* **Doel:** Zijn er systeem-brede risico's die onmiddellijke actie vereisen, los van nieuwe trades?
* **Input:** De volledige `TradingContext` en de lijst van `RoutedTradePlan`'s.
* **Proces (voorbeeld):** Een `MaxDrawdownDetector`-plugin (`type: critical_event_detector`) controleert de equity curve van het `Portfolio`. Als de drawdown een drempel overschrijdt, genereert het een event.
* **Output:** Een **`CriticalEvent` DTO** (bv. `{ event_type: 'MAX_DRAWDOWN_BREACHED' }`) of `None`.

**Finale Output: Het `TradeProposal` DTO**
De `StrategyEngine` verpakt de outputs van Fase 8 en 9 in één enkel `TradeProposal`-object. Dit object wordt teruggestuurd naar de `Workflow Service`, die het interpreteert en de juiste acties onderneemt (bv. de `RoutedTradePlan` naar de `ExecutionHandler` sturen of de run stoppen bij een `CriticalEvent`).

---
## 4.2. Rolverdeling: De Manager en de Motor

### **De Workflow Service (bv. `BacktestService`) (De Manager)**
Een service zoals de `BacktestService` is de **"manager"** van een enkele run. Hij is de eigenaar van de setup-logica en bereidt de fabriek voor.

* **Plek:** `Service`-laag.
* **Verantwoordelijkheid:** Het end-to-end voorbereiden en starten van een strategie-executie.

#### **Procesflow van de Service:**
1.  **Initialisatie:** Ontvangt de `AppConfig` van de frontend of CLI.
2.  **Bouwfase:** Instantieert alle benodigde, langlevende backend-componenten:
    * De `ExecutionEnvironment` (bv. `BacktestEnvironment`).
    * Het `Portfolio` (geïnitialiseerd met simpele waarden, niet de config).
    * Het `Assembly Team` (`PluginRegistry`, `WorkerBuilder`, `ContextBuilder`).
3.  **Assemblage:** Gebruikt het `Assembly Team` om de `StrategyEngine` te bouwen, en injecteert een "toolbox" met alle benodigde, geïnstantieerde plugin-workers.
4.  **Context Preparatie (Fase 1 & 2):** Roept de `ContextBuilder` aan om de `enriched_df` te genereren.
5.  **Startschot:** Creëert het finale `TradingContext` DTO (met de `enriched_df`, `Portfolio`, etc.) en roept de `run()`-methode van de `StrategyEngine` aan, waarmee de controle wordt overgedragen.

### **De `StrategyEngine` (De Motor)**
De `StrategyEngine` is de **"motor"** van de executie-loop (Fase 3-9). Hij weet niets van de setup, maar is een expert in het efficiënt doorlopen van de signaal-pijplijn.

* **Plek:** `Backend`-laag.
* **Verantwoordelijkheid:** Het uitvoeren van de event-loop, gestuurd door de `Clock`, en het doorlopen van de DTO-trechter van `Signal` tot `TradeProposal`.
* **Procesflow van de Engine:**
    1.  **Start:** De `run()`-methode wordt aangeroepen door de `Service`.
    2.  **Event Loop:** Voor elke `tick` van de `Clock`:
        * Vraagt alle `signal_generator` plugins om een lijst van `Signal` DTO's.
        * Voor elk `Signal`, leidt het door de volledige trechter (Fase 4-8), waarbij elke stap de DTO verder nest en verrijkt via de `BaseWorker`-automatisering.
        * Roept de `critical_event_detector` plugins aan (Fase 9).
        * `yield` elk `TradeProposal` terug naar de `Service`.

### **Het `Assembly Team` (De Technische Projectmanager)**
Het `Assembly Team` (`PluginRegistry`, `WorkerBuilder`, `ContextBuilder`) is het **"technische projectbureau"**. Het weet niets over de fasen, maar is expert in het beheren en bouwen van plugins.

* **Plek:** `Backend`-laag.
* **Verantwoordelijkheid:** Het ontdekken, bouwen en technisch orkestreren van de context-pijplijn.
* **Taken in Detail:**
    * **Plugin Discovery:** Scant de `plugins/`-map en bouwt het `PluginRegistry`.
    * **Worker Constructie:** Bouwt op aanvraag van de `Workflow Service` alle benodigde, gevalideerde plugin-instanties.
    * **Orkestratie van Context:** Voert de `context_pipeline` (Fase 1 & 2) uit.

---
## 4.3. De Feedback Loops: Technisch vs. Strategisch

De architectuur faciliteert twee cruciale cycli:

1.  **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** **een run**. De staat van het `Portfolio` (het "domme" grootboek) wordt via het `TradingContext` object gebruikt als input voor plugins in latere fasen (bv. de `SizePlanner` in Fase 7).
2.  **De Strategische "Supercharged" Ontwikkelcyclus (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** **de runs**, volgens het **"Bouwen -> Meten -> Leren"** principe. Je analyseert de resultaten van een backtest in de Web UI (**Meten**), ontdekt een zwakte (**Leren**), past de `YAML`-configuratie aan in de Strategy Builder (**Bouwen**) en start direct een nieuwe run.