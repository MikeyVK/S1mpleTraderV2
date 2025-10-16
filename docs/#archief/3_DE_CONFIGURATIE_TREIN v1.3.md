# **3\. De Configuratie Trein: Een Gids voor S1mpleTrader V2 YAML-bestanden**

Versie: 1.3 (Detailniveau Hersteld)  
Status: Definitief

## **3.1. Voorwoord: De Bron van Waarheid**

In de S1mpleTrader V2 architectuur is de configuratie koning. De YAML-bestanden zijn niet slechts instellingen; ze zijn het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft. Het platform zelf is een agnostische uitvoerder die tot leven komt op basis van deze bestanden.

Dit document beschrijft de "configuratie trein": de logische hiërarchie en samenhang van de verschillende YAML-bestanden die samen een volledige, gevalideerde en uitvoerbare operatie definiëren. We volgen de stroom van de meest stabiele, platform-brede bestanden tot de meest specifieke, gedetailleerde plugin-parameters.

## **3.2. Het Landschap van de Configuratie**

De configuratie is opgedeeld in een reeks van gespecialiseerde bestanden. Elk bestand heeft een duidelijke Single Responsibility (SRP).

**De Hiërarchie (van Stabiel naar Dynamisch):**

1. **platform.yaml**: De fundering van het hele platform.  
2. **connectors.yaml**: De technische "stekkerdoos" voor **live** verbindingen.  
3. **data\_sources.yaml**: De catalogus van **lokale** historische datasets.  
4. **environments.yaml**: De definitie van de abstracte "werelden".  
5. **event\_map.yaml**: De grondwet van de interne communicatie.  
6. **wiring\_map.yaml**: De bouwtekening van de dataflow.  
7. **schedule.yaml**: De agnostische "metronoom" van het systeem.  
8. **operation.yaml**: Het centrale "draaiboek" van de quant.  
9. **strategy\_blueprint.yaml**: De gedetailleerde "receptenkaart".  
10. **plugin\_manifest.yaml**: De "ID-kaart" van elke individuele plugin.

## **3.3. De Platform- & Systeemarchitectuur**

Deze bestanden vormen de stabiele basis. Ze worden doorgaans één keer opgezet en veranderen zelden.

### **3.3.1. platform.yaml \- De Fundering**

* **Doel**: Definieert globale, niet-strategische instellingen voor het hele platform. Dit is het domein van de platformbeheerder, niet van de quant.  
* **Inhoud**:  
  * **Logging-profielen**: Definieert welke log-niveaus worden getoond (developer, analysis).  
  * **Taalinstellingen**: Bepaalt de standaardtaal voor de UI en logs.  
  * **Archiveringsformaat**: Bepaalt of resultaten worden opgeslagen als csv, parquet, etc.  
  * **Bestandspaden**: Definieert de root-locatie van de plugins-map.  
* **Voorbeeld (Conceptueel)**:  
  \# config/platform.yaml  
  language: "nl"  
  logging:  
    profile: "analysis"  
    profiles:  
      developer: \[INFO, WARNING, ERROR\]  
      analysis: \[DEBUG, INFO, SETUP, MATCH, FILTER, RESULT, TRADE, ERROR\]  
  archiving:  
    format: "parquet"  
  plugins\_root\_path: "plugins"

### **3.3.2. connectors.yaml \- De Stekkerdoos**

* **Doel**: Centraliseert de technische configuratie van **alle** mogelijke verbindingen met externe, **live** partijen (exchanges).  
* **Inhoud**: Een lijst van benoemde connector-instanties. Elke instantie heeft een unieke naam (de *identifier*), een type (die de ConnectorFactory vertelt welke Python-klasse hij moet gebruiken), en de benodigde credentials en API-eindpunten.  
* **Voorbeeld (Conceptueel)**:  
  \# config/connectors.yaml  
  kraken\_live\_eur\_account:  
    type: "kraken\_private"  
    api\_key: "${KRAKEN\_API\_KEY}"  
    api\_secret: "${KRAKEN\_API\_SECRET}"

  binance\_paper\_trading:  
    type: "binance\_public"  
    base\_url: "\[https://testnet.binance.vision/api\](https://testnet.binance.vision/api)"

### **3.3.3. data\_sources.yaml \- De Archievenkast**

* **Doel**: Centraliseert de definitie van alle beschikbare, op schijf opgeslagen, **historische datasets** (archieven). Dit creëert een register van alle "backtest-werelden".  
* **Inhoud**: Een lijst van benoemde data sources. Elke data source heeft een unieke naam (de *identifier*) en specificaties over de fysieke locatie en het type data.  
* **Voorbeeld (Conceptueel)**:  
  \# config/data\_sources.yaml  
  btc\_eur\_15m\_archive:  
    type: "parquet\_archive"  
    path: "source\_data/BTC\_EUR\_15m/"  
    asset\_pair: "BTC/EUR"  
    timeframe: "15m"

### **3.3.4. environments.yaml \- De Werelden**

* **Doel**: Definieert de operationele "werelden" (live, paper, backtest) en koppelt ze aan een technische bron.  
* **Inhoud**: Een lijst van benoemde omgevingen met een unieke naam, een type, en een verwijzing naar ofwel een connector\_id ofwel een data\_source\_id.  
* **Voorbeeld (Conceptueel)**:  
  \# config/environments.yaml  
  live\_kraken\_main:  
    type: "live"  
    connector\_id: "kraken\_live\_eur\_account" \# VERWIJST NAAR connectors.yaml

  backtest\_2020\_2024\_btc:  
    type: "backtest"  
    data\_source\_id: "btc\_eur\_15m\_archive" \# VERWIJST NAAR data\_sources.yaml

### **3.3.5. event\_map.yaml \- De Grondwet van de Communicatie**

* **Doel**: Functioneert als de strikte "Grondwet" voor alle communicatie op de EventBus. Het definieert welke events mogen bestaan en wat hun exacte data-contract is.  
* **Inhoud**: Een lijst van alle toegestane event-namen met hun verplichte payload\_dto-contract.  
* **Voorbeeld (Conceptueel)**:  
  \# config/event\_map.yaml  
  \- event\_name: "OperationStarted"  
    payload\_dto: "OperationParameters"  
  \- event\_name: "ContextReady"  
    payload\_dto: "TradingContext"

### **3.3.6. wiring\_map.yaml \- De Bouwtekening van de Dataflow**

* **Doel**: De "bouwtekening" die beschrijft hoe Operators via EventAdapters op de EventBus worden aangesloten. Het definieert de dataflow: welk event triggert welke actie?  
* **Inhoud**: Een lijst van "wiring"-regels die een component en method koppelen aan een listens\_to event, en specificeren hoe het resultaat gepubliceerd wordt (publishes\_result\_as).  
* **Voorbeeld (Conceptueel)**:  
  \# config/wiring\_map.yaml  
  \- adapter\_id: "ContextPipelineAdapter"  
    listens\_to: "MarketDataReceived"  
    invokes:  
      component: "ContextOperator"  
      method: "run\_pipeline"  
    publishes\_result\_as: "ContextReady"

### **3.3.7. schedule.yaml \- De Metronoom**

* **Doel**: Configureert de Scheduler service voor alle tijd-gebaseerde events.  
* **Inhoud**: Een lijst van event-definities, elk met een event\_name en een type (interval of cron).  
* **Voorbeeld (Conceptueel)**:  
  \# config/schedule.yaml  
  schedule:  
    \- event\_name: "five\_minute\_reconciliation\_tick"  
      type: "interval"  
      value: "5m"  
    \- event\_name: "daily\_dca\_buy\_signal"  
      type: "cron"  
      value: "0 9 \* \* \*"  
      timezone: "Europe/Amsterdam"

## **3.4. De Operationele Configuratie**

Deze bestanden beschrijven de **strategische en operationele intentie** van de quant.

### **3.4.1. operation.yaml \- Het Centrale Draaiboek**

* **Doel**: Het **hoofdbestand** dat een volledige operatie definieert door strategy\_links te creëren die blueprints aan environments koppelen.  
* **Inhoud**: Een display\_name, description, en een lijst van strategy\_links, elk met een strategy\_blueprint\_id en een execution\_environment\_id.  
* **Voorbeeld (Conceptueel)**:  
  \# config/operations/my\_btc\_operation.yaml  
  display\_name: "Mijn BTC Operatie (Live & Backtest)"  
  description: "Draait een FVG-strategie live en backtest een nieuwe mean-reversion strategie."  
  strategy\_links:  
    \- strategy\_blueprint\_id: "live\_fvg\_strategy"  
      execution\_environment\_id: "live\_kraken\_main"  
      is\_active: true

    \- strategy\_blueprint\_id: "experimental\_mean\_reversion"  
      execution\_environment\_id: "backtest\_2020\_2024\_btc"  
      is\_active: true

### **3.4.2. strategy\_blueprint.yaml \- Het Gedetailleerde Recept**

* **Doel**: Bevat de **volledige configuratie van alle plugins** (workforce) voor één strategy\_link.  
* **Inhoud**: Een workforce-sectie die, gegroepeerd per plugin-categorie, de parameters voor elke individuele plugin definieert.  
* **Voorbeeld (Conceptueel)**:  
  \# config/strategy\_blueprints/live\_fvg\_strategy.yaml  
  display\_name: "Live FVG Entry Strategy"  
  workforce:  
    context\_workers:  
      ema\_detector\_fast: { plugin\_name: "ema\_detector", params: { period: 50 } }  
    analysis\_workers:  
      fvg\_entry: { plugin\_name: "fvg\_entry\_detector", params: { fvg\_min\_size\_pct: 0.1 } }  
    monitor\_workers:  
      daily\_drawdown: { plugin\_name: "max\_drawdown\_monitor", params: { max\_drawdown\_pct: 5.0 } }  
    execution\_workers:  
      emergency\_exit: { plugin\_name: "emergency\_exit\_agent", params: { listens\_to\_event: "MAX\_DRAWDOWN\_BREACHED" } }

## **3.5. De Plugin-Configuratie**

Deze bestanden zijn onderdeel van de plugin zelf en maken hem vindbaar en configureerbaar.
### **3.5.1. plugin\_manifest.yaml \- De ID-kaart**

* **Doel**: Maakt een plugin **ontdekbaar en begrijpelijk** voor het Assembly Team.  
* **Inhoud**: identification (incl. type), dependencies, en produces\_events voor MonitorWorkers.  
* **Voorbeeld (Conceptueel)**:  
  \# plugins/monitor\_workers/max\_drawdown\_monitor/manifest.yaml  
  identification:  
    name: "max\_drawdown\_monitor"  
    type: "monitor\_worker"  
  dependencies:  
    produces\_events:  
      \- "MAX\_DRAWDOWN\_BREACHED"

## **3.6. De Onderlinge Samenhang \- De "Configuratie Trein" in Actie**

De magie van het systeem zit in hoe Operations deze bestanden aan elkaar koppelt tijdens de bootstrap-fase.

1. **Startpunt**: De gebruiker start de applicatie met de opdracht: run my\_btc\_operation.  
2. **Operations leest operation.yaml**: Hij vindt de strategy\_link voor experimental\_mean\_reversion.  
3. **Analyse van de Link**:  
   * Operations kijkt naar de execution\_environment\_id: backtest\_2020\_2024\_btc.  
   * Hij zoekt in **environments.yaml** en vindt backtest\_2020\_2024\_btc. Hij ziet dat dit een backtest-omgeving is die data\_source\_id: btc\_eur\_15m\_archive vereist.  
   * Hij zoekt nu in **data\_sources.yaml** en vindt btc\_eur\_15m\_archive. Hij heeft nu alle technische details (pad, type) om de BacktestEnvironment en zijn DataSource te bouwen.  
   * Vervolgens kijkt Operations naar de strategy\_blueprint\_id: experimental\_mean\_reversion.  
   * Hij laadt **strategy\_blueprints/experimental\_mean\_reversion.yaml** en ziet de volledige workforce.  
   * Voor elke plugin in de workforce, gebruikt het Assembly Team de **manifest.yaml** van die plugin om de code te vinden en de params uit de blueprint te valideren tegen de schema.py.  
4. **Herhaling**: Operations herhaalt dit proces voor de live\_fvg\_strategy-link, maar volgt nu het pad via environments.yaml naar **connectors.yaml** om de LiveEnvironment te bouwen.  
5. **Afronding**: Operations laadt tot slot schedule.yaml, event\_map.yaml en wiring\_map.yaml om de Scheduler en de volledige "bedrading" van de EventBus te configureren.

Het resultaat is een volledig geassembleerd, gevalideerd en onderling verbonden ecosysteem van plugins, klaar om van start te gaan, puur en alleen op basis van de declaratieve YAML-bestanden.