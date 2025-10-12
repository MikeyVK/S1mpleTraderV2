# **5\. De Analytische Pijplijn**

Versie: 2.2 (Gecorrigeerd & Aangevuld)  
Status: Definitief

## **5.1. Introductie: Een Gescheiden Pijplijn**

Dit document beschrijft de volledige workflow van data-analyse tot handelsvoorstel. Deze workflow is bewust opgesplitst in twee conceptueel verschillende, opeenvolgende processen die worden beheerd door gespecialiseerde Operators:

1. **De Context Pijplijn (Fase 1-2):** De eerste twee fasen zijn de verantwoordelijkheid van de **ContextOperator**. Deze fasen verrijken de ruwe marktdata en bereiden de complete, state-bewuste TradingContext voor. Dit proces eindigt met het publiceren van een ContextReady-event.  
2. **De Analytische Pijplijn (Fase 3-8):** De daaropvolgende fasen vormen de kern van de **AnalysisOperator**. In reactie op de ContextReady-event, voert de AnalysisOperator zijn interne, stateless en procedurele trechter uit om een *analytisch voorstel* (EngineCycleResult) te produceren. Dit voorstel wordt gepubliceerd als een StrategyProposalReady-event.

## **5.2. De Pijplijn: Een Praktijkvoorbeeld**

We volgen een concreet voorbeeld: een **"Market Structure Shift \+ FVG Entry"** strategie.

   ┌───────────────────────────────────────────┐  
   │        RUWE DATAFRAME (OHLCV)             │  
   └────────────────────┬──────────────────────┘  
                        │ (Beheerd door ContextOperator)  
                        v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 1: REGIME CONTEXT (De "Weerman")                            │  
│ Plugin: ContextWorker                                            │  
└────────────────────┬─────────────────────────────────────────────┘  
                        v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 2: STRUCTURELE CONTEXT (De "Cartograaf")                    │  
│ Plugin: ContextWorker                                            │  
└────────────────────┬─────────────────────────────────────────────┘  
                        │  
                        v (Publiceert ContextReady event)  
   ┌───────────────────────────────────────────┐  
   │ FINALE TRADING CONTEXT (met enriched\_df)  │  
   └────────────────────┬──────────────────────┘  
                        │ (Start AnalysisOperator Pijplijn)  
                        v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 3: SIGNAAL GENERATIE (De "Verkenner")                       │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: Signal  
│ \-------------------------------  
│ { correlation\_id, timestamp, asset,  
│   direction, signal\_type }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 4: SIGNAAL VERFIJNING (De "Kwaliteitscontroleur")           │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: Signal (of None)  
│ \-------------------------------  
│ { ... (inhoud blijft gelijk) }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 5: ENTRY PLANNING (De "Timing Expert")                      │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: EntrySignal  
│ \-------------------------------  
│ { correlation\_id (gepromoot),  
│   signal: Signal (genest),  
│   \+ entry\_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 6: EXIT PLANNING (De "Strateeg")                            │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: RiskDefinedSignal  
│ \-------------------------------  
│ { correlation\_id (gepromoot),  
│   entry\_signal: EntrySignal (genest),  
│   \+ sl\_price, tp\_price }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 7: SIZE PLANNING (De "Logistiek Manager")                   │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: TradePlan  
│ \-------------------------------  
│ { correlation\_id (gepromoot),  
│   risk\_defined\_signal: RiskDefinedSignal (genest),  
│   \+ position\_value\_quote, position\_size\_asset }  
│  
v  
┌──────────────────────────────────────────────────────────────────┐  
│ Fase 8: ORDER ROUTING (De "Verkeersleider")                      │  
│ Plugin: AnalysisWorker                                           │  
└────────────────────┬─────────────────────────────────────────────┘  
│ DTO: RoutedTradePlan  
│ \-------------------------------  
│ { correlation\_id (gepromoot),  
│   trade\_plan: TradePlan (genest),  
│   \+ order\_type, time\_in\_force, ... }  
│  
v  
   ┌─────────────────────────────────────────────┐  
   │ FINAAL EngineCycleResult DTO                │  
   │ { routed\_trade\_plans?, ... }                │  
   └────────────────────┬────────────────────────┘  
                        │  
                        v (Publiceert StrategyProposalReady Event)

*Opmerking: Fase 9 (CriticalEventDetection) is in de V4-architectuur verplaatst naar een aparte MonitorWorker en maakt geen deel meer uit van deze lineaire, analytische pijplijn.*

### **5.2.1. Gedetailleerde Fasen**

#### **Fase 1: Regime Context (De "Weerman")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** Wat is de algemene "weersverwachting" van de markt? Deze fase classificeert de marktomstandigheid zonder data weg te gooien.  
* **Input:** De ruwe DataFrame met OHLCV-data uit de TradingContext.  
* **Proces (voorbeeld):** Een ADXContext-plugin berekent de ADX-indicator en voegt een nieuwe kolom regime toe aan de DataFrame. Deze kolom krijgt de waarde 'trending' als ADX \> 25 en 'ranging' als ADX \< 25\.  
* **Output:** Een verrijkte DataFrame. Er wordt geen data verwijderd; er wordt alleen een contextuele "tag" toegevoegd aan elke rij.

#### **Fase 2: Structurele Context (De "Cartograaf")**

* **Categorie:** ContextWorker-plugin  
* **Doel:** De markt "leesbaar" maken. Waar is de trend en wat zijn de belangrijke zones?  
* **Input:** De verrijkte DataFrame uit Fase 1\.  
* **Proces (voorbeeld):** Een MarketStructureDetector-plugin analyseert de prijs en voegt twee nieuwe kolommen toe: trend\_direction (met waarden als bullish of bearish) en is\_mss (een True/False vlag op de candle waar een Market Structure Shift plaatsvindt).  
* **Output:** De finale enriched\_df. We hebben nu "slimme" data met meerdere lagen context, klaar voor de AnalysisOperator.

***Controle wordt via een ContextReady-event overgedragen.***

#### **Fase 3: Signaal Generatie (De "Verkenner")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Waar is de precieze, actiegerichte trigger? We zoeken naar een Fair Value Gap (FVG) ná een Market Structure Shift.  
* **Input:** De enriched\_df (via het TradingContext object).  
* **Proces (voorbeeld):** Een FVGEntryDetector-plugin scant de data. Wanneer het een rij tegenkomt waar is\_mss True is, begint het te zoeken naar een FVG. Als het er een vindt, genereert het een signaal.  
* **Output:** Een **Signal DTO**. Dit object krijgt een unieke correlation\_id (UUID) en bevat de essentie: {asset: 'BTC/EUR', timestamp: '...', direction: 'long', signal\_type: 'fvg\_entry'}.

#### **Fase 4: Signaal Verfijning (De "Kwaliteitscontroleur")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Is er bevestiging voor het signaal? We willen volume zien bij de FVG-entry.  
* **Input:** Het Signal DTO en het TradingContext.  
* **Proces (voorbeeld):** Een VolumeSpikeRefiner-plugin controleert het volume op de timestamp van het Signal. Als het volume te laag is, wordt het signaal afgekeurd.  
* **Output:** Het **gevalideerde Signal DTO** of None. De correlation\_id blijft behouden.

#### **Fase 5: Entry Planning (De "Timing Expert")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Wat is de precieze entry-prijs voor ons goedgekeurde signaal?  
* **Input:** Het gevalideerde Signal DTO.  
* **Proces (voorbeeld):** Een LimitEntryPlanner-plugin bepaalt dat de entry een limietorder moet zijn op de 50% retracement van de FVG.  
* **Output:** Een **EntrySignal DTO**. Dit DTO *nest* het originele Signal en verrijkt het met { entry\_price: 34500.50 }. De correlation\_id wordt gepromoot naar het top-level.

#### **Fase 6: Exit Planning (De "Strateeg")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Wat is het initiële plan voor risico- en winstmanagement?  
* **Input:** Het EntrySignal DTO.  
* **Proces (voorbeeld):** Een LiquidityTargetExit-plugin plaatst de stop-loss onder de laatste swing low en de take-profit op de volgende major liquidity high.  
* **Output:** Een **RiskDefinedSignal DTO**. Nest het EntrySignal en voegt { sl\_price: 34200.0, tp\_price: 35100.0 } toe.

#### **Fase 7: Size Planning (De "Logistiek Manager")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Wat is de definitieve positiegrootte, gegeven ons risicoplan en kapitaal?  
* **Input:** Het RiskDefinedSignal DTO en de StrategyLedger (via de TradingContext).  
* **Proces (voorbeeld):** Een FixedRiskSizer-plugin berekent de positiegrote zodat het risico (entry\_price \- sl\_price) exact 1% van de totale equity van de StrategyLedger is.  
* **Output:** Een **TradePlan DTO**. Nest het RiskDefinedSignal en bevat de finale, berekende { position\_value\_quote: 1000.0, position\_size\_asset: 0.0289 }.

#### **Fase 8: Order Routing (De "Verkeersleider")**

* **Categorie:** AnalysisWorker-plugin  
* **Doel:** Hoe moet dit strategische plan *technisch* worden uitgevoerd?  
* **Input:** Het TradePlan DTO.  
* **Proces (voorbeeld):** Een DefaultRouter-plugin vertaalt het plan naar concrete order-instructies.  
* **Output:** Een **RoutedTradePlan DTO**. Nest het TradePlan en voegt de *tactische* executie-instructies toe, zoals { order\_type: 'limit', time\_in\_force: 'GTC' }.

## **5.3. Rolverdeling in de Architectuur**

* **ContextOperator (De Voorbereider)**: Verantwoordelijk voor Fase 1 & 2\. Abonneert (via zijn adapter) op MarketDataReceived, roept de ContextWorker-plugins aan, en publiceert de ContextReady-event.  
* **AnalysisOperator (De Analist)**: Verantwoordelijk voor Fase 3 t/m 8\. Abonneert (via zijn adapter) op ContextReady. Na ontvangst doorloopt het de procedurele DTO-trechter en publiceert het eindresultaat als een StrategyProposalReady-event.  
* **MonitorOperator (De Waakhond)**: Draait **parallel** aan de AnalysisOperator. Abonneert (via zijn adapter) op events zoals ContextReady en LedgerStateChanged om de algehele staat van de operatie te bewaken. Het publiceert informatieve of waarschuwende events (bv. MAX\_DRAWDOWN\_BREACHED) maar handelt nooit zelf.  
* **ExecutionOperator (De Poortwachter)**: Abonneert (via zijn adapter) op StrategyProposalReady-events (van de AnalysisOperator) en eventuele events van MonitorWorkers. Het ontvangt de voorstellen, toetst deze aan overkoepelende regels, en beslist of de trades daadwerkelijk uitgevoerd mogen worden door een ExecutionApproved-event te publiceren.

## **5.4. De Feedback Loops**

1. **De Technische Feedback Loop (Real-time):** Dit gebeurt ***binnen*** een Operation, via de EventBus. Een LedgerStateChanged-event, gepubliceerd door de ExecutionEnvironment, wordt opgenomen in de volgende TradingContext. Hierdoor heeft de AnalysisOperator bij de volgende tick altijd de meest actuele financiële staat beschikbaar voor zijn berekeningen.  
2. **De Strategische Feedback Loop (Human-in-the-loop):** Dit is de cyclus die *jij* als strateeg doorloopt ***tussen*** de Operations, volgens het **"Bouwen \-\> Meten \-\> Leren"** principe. Je analyseert de resultaten, past de strategy\_blueprint.yaml aan en start een nieuwe Operation.