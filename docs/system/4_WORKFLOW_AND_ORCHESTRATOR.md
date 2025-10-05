# **4. De Quant Workflow & De Analytische Pijplijn**

Versie: 3.0 (Bijgewerkt)  
Status: Definitief

## **4.1. Introductie: Een Gescheiden Pijplijn**

Dit document beschrijft de volledige workflow van data-analyse tot handelsvoorstel. Deze workflow is bewust opgesplitst in twee conceptueel verschillende, opeenvolgende processen:

1. **De Context Pijplijn (Fase 1-2):** De eerste twee fasen (Regime Context en Structurele Context) zijn de verantwoordelijkheid van de stateful **ContextOrchestrator**. Deze fasen verrijken de ruwe marktdata en bereiden de complete, state-bewuste TradingContext voor. Dit proces wordt voor elke tick uitgevoerd en eindigt met het publiceren van een ContextReady-event.  
2. **De Analytische Pijplijn (Fase 3-9):** De daaropvolgende zeven fasen vormen de kern van de **StrategyEngine**. In reactie op de ContextReady-event, voert de StrategyEngine zijn interne, stateless en procedurele **7-fasen trechter** uit. Het doel is niet om definitieve beslissingen te nemen, maar om een *analytisch voorstel* (EngineCycleResult) te produceren. Dit voorstel wordt vervolgens gepubliceerd als een StrategyProposalReady-event.

Deze scheiding zorgt ervoor dat de StrategyEngine zich puur kan richten op zijn analytische kerntaak, opererend op een perfect voorbereide dataset, zonder zich bezig te hoeven houden met het complexe beheer van de staat.

## **4.2. De 9-Fasen Trechter/pijplijn: Een Praktijkvoorbeeld**

   ┌───────────────────────────────────────────┐  
   │        RUWE DATAFRAME (OHLCV)             │  
   └────────────────────┬──────────────────────┘  
                        │  
                        v

┌──────────────────────────────────────────────────────────────────┐  
│ Fase 1: REGIME CONTEXT (De "Weerman")                            │
│ Plugin: regime_context                                           │  
│ Taak: Voegt macro-context toe (bv. regime='trending').           │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
v  
┌───────────────────────────────────────────┐  
│ VERRIJKTE DATAFRAME (enriched_df)         │  
└────────────────────┬──────────────────────┘  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 2: STRUCTURELE CONTEXT (De "Cartograaf")                    │  
│ Plugin: structural_context                                       │  
│ Taak: Voegt micro-context toe (bv. is_mss, support_level).       │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
v  
┌───────────────────────────────────────────┐  
│ FINALE ENRICHED DATAFRAME                 │
└────────────────────┬──────────────────────┘  
│ (Start StrategyEngine Loop)  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 3: SIGNAAL GENERATIE (De "Verkenner")                       │  
│ Plugin: signal_generator                                         │  
│ Taak: Detecteert een specifieke, actiegerichte gebeurtenis.      │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
│ DTO: Signal  
│ -------------------------------  
│ { correlation_id, timestamp, asset,  
│ direction, signal_type }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 4: SIGNAAL VERFIJNING (De "Kwaliteitscontroleur")           │  
│ Plugin: signal_refiner                                           │  
│ Taak: Keurt Signal goed of af op basis van secundaire criteria.  │  
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
│ Taak: Bepaalt de precieze entry-prijs.                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
│ DTO: EntrySignal  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ signal: Signal (genest),  
│ + entry_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 6: EXIT PLANNING (De "Strateeg")                            │  
│ Plugin: exit_planner                                             │  
│ Taak: Berekent de initiële stop-loss en take-profit.             │  
└────────────────────┬─────────────────────────────────────────────┘  
│  
│ DTO: RiskDefinedSignal  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ entry_signal: EntrySignal (genest),  
│ + sl_price, tp_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐
│ Fase 7: SIZE PLANNING (De "Logistiek Manager")                   │
│ Plugin: size_planner                                             │
│ Taak: Berekent de definitieve positiegrootte.                    │
└────────────────────┬─────────────────────────────────────────────┘
│  
│ DTO: TradePlan  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ risk_defined_signal: RiskDefinedSignal (genest),  
│ + position_value_quote, position_size_asset }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐
│ Fase 8: ORDER ROUTING (De "Verkeersleider")                      │
│ Plugin: order_router                                             │
│ Taak: Vertaalt het plan naar technische executie-instructies.    │
└────────────────────┬─────────────────────────────────────────────┘
│  
│ DTO: RoutedTradePlan  
│ -------------------------------  
│ { correlation_id (gepromoot),  
│ trade_plan: TradePlan (genest),  
│ + order_type, time_in_force, ... }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐
│ Fase 9: CRITICAL EVENT DETECTION (De "Waakhond")                 │
│ Plugin: critical_event_detector                                  │
│ Taak: Detecteert systeem-brede risico's (bv. max drawdown).      │
└────────────────────┬─────────────────────────────────────────────┘
│  
│ DTO: CriticalEvent  
│ -------------------------------  
│ { correlation_id, event_type, timestamp }  
│  
v  
┌─────────────────────────────────────────────┐
│ FINAAL EngineCycleResult DTO                │
│ { routed_trade_plans?, critical_events? }   │
└────────────────────┬────────────────────────┘
│  
v  
[ Publiceert StrategyProposalReady Event ]  
Elk handelsidee wordt systematisch gevalideerd door een vaste, logische trechter. We volgen een concreet voorbeeld: een **"Market Structure Shift + FVG Entry"** strategie.

#### **Fase 1: Regime Context (De "Weerman")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** Wat is de algemene "weersverwachting" van de markt? Deze fase classificeert de marktomstandigheid zonder data weg te gooien.  
* **Input:** De ruwe DataFrame met OHLCV-data uit de TradingContext.  
* **Proces (voorbeeld):** Een ADXContext-plugin (type: regime_context) berekent de ADX-indicator en voegt een nieuwe kolom regime toe aan de DataFrame. Deze kolom krijgt de waarde 'trending' als ADX > 25 en 'ranging' als ADX < 25.  
* **Output:** Een verrijkte DataFrame. Er wordt geen data verwijderd; er wordt alleen een contextuele "tag" toegevoegd aan elke rij.

#### **Fase 2: Structurele Context (De "Cartograaf")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?  
* **Input:** De verrijkte DataFrame uit Fase 1.  
* **Proces (voorbeeld):** Een MarketStructureDetector-plugin (type: structural_context) analyseert de prijs en voegt twee nieuwe kolommen toe: trend_direction (met waarden als bullish of bearish) en is_mss (een True/False vlag op de candle waar een Market Structure Shift plaatsvindt).  
* **Output:** De finale enriched_df. We hebben nu "slimme" data met meerdere lagen context, klaar voor de StrategyEngine.

## ***De controle wordt overgedragen aan de StrategyEngine na ontvangst van de ContextReady-event.***

#### **Fase 3: Signaal Generatie (De "Verkenner")**

* **Categorie:** StrategyWorker-plugin (signal_generator)  
* **Doel:** Waar is de precieze, actiegerichte trigger? We zoeken naar een Fair Value Gap (FVG) ná een Market Structure Shift.  
* **Input:** De enriched_df (via het TradingContext object).  
* **Proces (voorbeeld):** Een FVGEntryDetector-plugin scant de data. Wanneer het een rij tegenkomt waar is_mss True is, begint het te zoeken naar een FVG. Als het er een vindt, genereert het een signaal.  
* **Output:** Een **Signal DTO**. Dit object krijgt een unieke correlation_id (UUID) en bevat de essentie: {asset: 'BTC/EUR', timestamp: '...', direction: 'long', signal_type: 'fvg_entry'}.

#### **Fase 4: Signaal Verfijning (De "Kwaliteitscontroleur")**

* **Categorie:** StrategyWorker-plugin (signal_refiner)  
* **Doel:** Is er bevestiging voor het signaal? We willen volume zien bij de FVG-entry.  
* **Input:** Het Signal DTO en het TradingContext.  
* **Proces (voorbeeld):** Een VolumeSpikeRefiner-plugin (type: signal_refiner) controleert het volume op de timestamp van het Signal. Als het volume te laag is, wordt het signaal afgekeurd.  
* **Output:** Het **gevalideerde Signal DTO** of None. De correlation_id blijft behouden.

#### **Fase 5: Entry Planning (De "Timing Expert")**

* **Categorie:** StrategyWorker-plugin (entry_planner)  
* **Doel:** Wat is de precieze entry-prijs voor ons goedgekeurde signaal?  
* **Input:** Het gevalideerde Signal DTO.  
* **Proces (voorbeeld):** Een LimitEntryPlanner-plugin (type: entry_planner) bepaalt dat de entry een limietorder moet zijn op de 50% retracement van de FVG.  
* **Output:** Een **EntrySignal DTO**. Dit DTO *nest* het originele Signal en verrijkt het met { entry_price: 34500.50 }. De correlation_id wordt gepromoot naar het top-level voor gemakkelijke toegang.

#### **Fase 6: Exit Planning (De "Strateeg")**

* **Categorie:** StrategyWorker-plugin (exit_planner)  
* **Doel:** Wat is het initiële plan voor risico- en winstmanagement?  
* **Input:** Het EntrySignal DTO.  
* **Proces (voorbeeld):** Een LiquidityTargetExit-plugin (type: exit_planner) plaatst de stop-loss onder de laatste swing low en de take-profit op de volgende major liquidity high.  
* **Output:** Een **RiskDefinedSignal DTO**. Nest het EntrySignal en voegt { sl_price: 34200.0, tp_price: 35100.0 } toe.

#### **Fase 7: Size Planning (De "Logistiek Manager")**

* **Categorie:** StrategyWorker-plugin (size_planner)  
* **Doel:** Wat is de definitieve positiegrootte, gegeven ons risicoplan en kapitaal?  
* **Input:** Het RiskDefinedSignal DTO en het Portfolio (via context.portfolio_state).  
* **Proces (voorbeeld):** Een FixedRiskSizer-plugin (type: size_planner) berekent de positiegrootte zodat het risico (entry_price - sl_price) exact 1% van de totale equity van het portfolio is.  
* **Output:** Een **TradePlan DTO**. Dit DTO nest het RiskDefinedSignal en bevat de finale, berekende { position_value_quote: 1000.0, position_size_asset: 0.0289 }. Dit is het complete *strategische* plan.

#### **Fase 8: Order Routing (De "Verkeersleider")**

* **Categorie:** StrategyWorker-plugin (order_router)  
* **Doel:** Hoe moet dit strategische plan *technisch* worden uitgevoerd?  
* **Input:** Het TradePlan DTO.  
* **Proces (voorbeeld):** Een DefaultRouter-plugin (type: order_router) vertaalt het plan naar concrete order-instructies.  
* **Output:** Een **RoutedTradePlan DTO**. Dit nest het TradePlan en voegt de *tactische* executie-instructies toe, zoals { order_type: 'limit', time_in_force: 'GTC' }. Dit is de definitieve opdracht voor de ExecutionHandler.

#### **Fase 9: Critical Event Detection (De "Waakhond")**

* **Categorie:** StrategyWorker-plugin (critical_event_detector)  
* **Doel:** Zijn er systeem-brede risico's die onmiddellijke actie vereisen, los van nieuwe trades?  
* **Input:** De volledige TradingContext en de lijst van RoutedTradePlan's.  
* **Proces (voorbeeld):** Een MaxDrawdownDetector-plugin (type: critical_event_detector) controleert de equity curve van het Portfolio. Als de drawdown een drempel overschrijdt, genereert het een event.  
* **Output:** Een lijst van **CriticalEvent DTO's** (bv. { event_type: 'MAX_DRAWDOWN_BREACHED' }).

## **4.3. Rolverdeling in de Event-Gedreven Architectuur**

Waar voorheen sprake was van een strikte hiërarchie, werken de componenten nu als samenwerkende specialisten.

* **ContextOrchestrator (De State Manager)**: Dit is de stateful "voorbereider". Het ontvangt MarketDataReceived-events, roept de Fase 1 & 2 ContextWorker-plugins aan om de TradingContext op te bouwen en te verrijken, en publiceert vervolgens de ContextReady-event.  
* **StrategyEngine (De Analist)**: Dit component is de stateless "motor" van de analytische pijplijn (Fase 3-9). Het abonneert zich op ContextReady. Na ontvangst doorloopt het de procedurele DTO-trechter (van Signal tot RoutedTradePlan) en publiceert het eindresultaat als een StrategyProposalReady-event. Het is een pure, analytische machine.  
* **PortfolioSupervisor (De Operationeel Manager)**: Dit is de beslissende "poortwachter". Het abonneert zich op StrategyProposalReady-events. Het ontvangt de voorstellen van de StrategyEngine, toetst deze aan overkoepelende, portfolio-brede risicoregels, en beslist of de trades daadwerkelijk uitgevoerd mogen worden.

## **4.4. De Feedback Loops: Technisch vs. Strategisch**

De architectuur faciliteert nog steeds twee cruciale cycli:

1. **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** **een run**, via de EventBus. Een PortfolioStateChanged-event, gepubliceerd door de ExecutionHandler, wordt opgevangen door de ContextOrchestrator. Deze gebruikt de nieuwe PortfolioState om de *volgende* TradingContext te bouwen, die vervolgens weer wordt gebruikt als input voor de StrategyEngine. Dit creëert een continue, real-time feedback-cyclus.  
2. **De Strategische "Supercharged" Ontwikkelcyclus (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** **de runs**, volgens het **"Bouwen -> Meten -> Leren"** principe. Je analyseert de resultaten van een backtest in de Web UI (**Meten**), ontdekt een zwakte (**Leren**), past de YAML-configuratie aan in de Strategy Builder (**Bouwen**) en start direct een nieuwe run.