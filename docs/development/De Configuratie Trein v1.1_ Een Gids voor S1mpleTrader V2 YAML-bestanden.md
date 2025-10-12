# **De Configuratie Trein: Een Gids voor S1mpleTrader V2 YAML-bestanden**

Versie: 1.1  
Status: Definitief

## **Voorwoord: De Bron van Waarheid**

In de S1mpleTrader V2 architectuur is de configuratie koning. De YAML-bestanden zijn niet slechts instellingen; ze zijn het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft. Het platform zelf is een agnostische uitvoerder die tot leven komt op basis van deze bestanden.

Dit document beschrijft de "configuratie trein": de logische hiërarchie en samenhang van de verschillende YAML-bestanden die samen een volledige, gevalideerde en uitvoerbare operatie definiëren. We volgen de stroom van de meest stabiele, platform-brede bestanden tot de meest specifieke, gedetailleerde plugin-parameters.

## **Hoofdstuk 1: Het Landschap van de Configuratie**

De configuratie is opgedeeld in een reeks van gespecialiseerde bestanden. Elk bestand heeft een duidelijke Single Responsibility (SRP) en bevindt zich op een specifiek niveau van de hiërarchie.

**De Hiërarchie (van Stabiel naar Dynamisch):**

1. **platform.yaml**: De fundering van het hele platform.  
2. **connectors.yaml**: De technische "stekkerdoos" voor **live** verbindingen.  
3. **data\_sources.yaml**: De catalogus van **lokale** historische datasets.  
4. **environments.yaml**: De definitie van de abstracte "werelden" waarin strategieën kunnen draaien.  
5. **schedule.yaml**: De agnostische "metronoom" van het systeem.  
6. **operation.yaml**: Het centrale "draaiboek" van de quant, dat alles samenbrengt.  
7. **strategy\_blueprint.yaml**: De gedetailleerde "receptenkaart" voor elke plugin.  
8. **plugin\_manifest.yaml**: De "ID-kaart" van elke individuele plugin.

Laten we elk van deze bestanden in detail bekijken.

## **Hoofdstuk 2: De Platform- & Omgevingsconfiguratie**

Deze bestanden vormen de stabiele basis. Ze worden doorgaans één keer opgezet en veranderen zelden.

### **2.1. platform.yaml \- De Fundering**

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

### **2.2. connectors.yaml \- De Stekkerdoos**

* **Doel**: Centraliseert de technische configuratie van **alle** mogelijke verbindingen met externe, **live** partijen (exchanges).  
* **Inhoud**: Een lijst van benoemde connector-instanties. Elke instantie heeft een unieke naam (de *identifier*), een type (die de ConnectorFactory vertelt welke Python-klasse hij moet gebruiken), en de benodigde credentials en API-eindpunten.  
* **Voorbeeld (Conceptueel)**:  
  \# config/connectors.yaml  
  \# Een unieke naam die we zelf kiezen  
  kraken\_live\_eur\_account:  
    type: "kraken\_private" \# Verwijst naar de KrakenAPIConnector  
    api\_key: "${KRAKEN\_API\_KEY}" \# Gebruikt environment variables  
    api\_secret: "${KRAKEN\_API\_SECRET}"

  binance\_paper\_trading:  
    type: "binance\_public" \# Een andere connector  
    base\_url: "\[https://testnet.binance.vision/api\](https://testnet.binance.vision/api)"

### **2.3. data\_sources.yaml \- De Archievenkast (NIEUW)**

* **Doel**: Centraliseert de definitie van alle beschikbare, op schijf opgeslagen, **historische datasets** (archieven). Dit creëert een register van alle "backtest-werelden". Het is de lokale tegenhanger van connectors.yaml.  
* **Inhoud**: Een lijst van benoemde data sources. Elke data source heeft een unieke naam (de *identifier*) en specificaties over de fysieke locatie en het type data (bv. Parquet, CSV). Deze informatie komt overeen met de metadata in de catalog.db.  
* **Voorbeeld (Conceptueel)**:  
  \# config/data\_sources.yaml  
  btc\_eur\_15m\_archive:  
    type: "parquet\_archive"  
    path: "source\_data/BTC\_EUR\_15m/" \# Verwijst naar de map van de dataset  
    asset\_pair: "BTC/EUR"  
    timeframe: "15m"

  eth\_usd\_1h\_csv:  
    type: "csv\_archive"  
    path: "source\_data/ETH\_USD\_1h.csv"  
    asset\_pair: "ETH/USD"  
    timeframe: "1h"

### **2.4. environments.yaml \- De Werelden (AANGEPAST)**

* **Doel**: Definieert de operationele "werelden" (ExecutionEnvironments) waarin strategieën kunnen draaien. Dit bestand is de cruciale brug tussen de abstracte wereld en de technische realiteit.  
* **Inhoud**: Een lijst van benoemde omgevingen. Elke omgeving heeft een unieke naam (de *identifier*), een type (live, paper, backtest), en een verwijzing naar **ofwel** een connector\_id (uit connectors.yaml) **ofwel** een data\_source\_id (uit data\_sources.yaml).  
* **Voorbeeld (Conceptueel)**:  
  \# config/environments.yaml  
  \# Een live-omgeving die onze Kraken-account gebruikt  
  live\_kraken\_main:  
    type: "live"  
    connector\_id: "kraken\_live\_eur\_account" \# VERWIJST NAAR connectors.yaml

  \# Een backtest-omgeving met een specifieke dataset  
  backtest\_2020\_2024\_btc:  
    type: "backtest"  
    data\_source\_id: "btc\_eur\_15m\_archive" \# VERWIJST NAAR data\_sources.yaml

### **2.5. schedule.yaml \- De Metronoom**

* **Doel**: Configureert de Scheduler service en definieert alle tijd-gebaseerde events die op de EventBus gepubliceerd moeten worden.  
* **Inhoud**: Een lijst van event-definities, elk met een unieke event\_name en een type (interval of cron).  
* **Voorbeeld (Conceptueel)**:  
  \# config/schedule.yaml  
  schedule:  
    \- event\_name: "five\_minute\_reconciliation\_tick"  
      type: "interval"  
      value: "5m"

    \- event\_name: "daily\_dca\_buy\_signal"  
      type: "cron"  
      value: "0 9 \* \* \*" \# Elke dag om 9:00  
      timezone: "Europe/Amsterdam"

## **Hoofdstuk 3: De Operationele Configuratie**

Deze bestanden worden door de quant gecreëerd en beheerd en beschrijven de **strategische en operationele intentie**.

### **3.1. operation.yaml \- Het Centrale Draaiboek**

* **Doel**: Dit is het **hoofdbestand** dat een volledige, draaiende operatie definieert. Het is het startpunt voor de Operations-service. Het brengt alle andere componenten samen en wijst ze toe aan de omgevingen waarin ze moeten draaien.  
* **Inhoud**: Een display\_name, description, en een lijst van **strategy\_links**. Elke link is een drieluik dat een strategy\_blueprint\_id koppelt aan een execution\_environment\_id.  
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

### **3.2. strategy\_blueprint.yaml \- Het Gedetailleerde Recept**

* **Doel**: Bevat de **volledige configuratie van alle plugins** die nodig zijn voor één strategy\_link. Het definieert de "wat" en "hoe" voor elke specialist.  
* **Inhoud**: Een workforce-sectie die, gegroepeerd per plugin-categorie, de parameters voor elke individuele plugin definieert.  
* **Voorbeeld (Conceptueel)**:  
  \# config/strategy\_blueprints/live\_fvg\_strategy.yaml  
  display\_name: "Live FVG Entry Strategy"

  workforce:  
    context\_workers:  
      ema\_detector\_fast: { plugin\_name: "ema\_detector", params: { period: 50 } }  
    strategy\_workers:  
      fvg\_entry: { plugin\_name: "fvg\_entry\_detector", params: { fvg\_min\_size\_pct: 0.1 } }  
    strategy\_monitors:  
      daily\_drawdown: { plugin\_name: "max\_drawdown\_monitor", params: { max\_drawdown\_pct: 5.0 } }  
    operational\_agents:  
      emergency\_exit: { plugin\_name: "emergency\_exit\_agent", params: { listens\_to\_event: "MAX\_DRAWDOWN\_BREACHED" } }

## **Hoofdstuk 4: De Plugin-Configuratie**

Deze bestanden zijn onderdeel van de plugin zelf en maken hem vindbaar en configureerbaar.

### **4.1. plugin\_manifest.yaml \- De ID-kaart**

* **Doel**: Maakt een plugin **ontdekbaar en begrijpelijk** voor het Assembly Team.  
* **Inhoud**: identification (incl. type), dependencies, en produces\_events voor StrategyMonitors.  
* **Voorbeeld (Conceptueel)**:  
  \# plugins/strategy\_monitors/max\_drawdown\_monitor/manifest.yaml  
  identification:  
    name: "max\_drawdown\_monitor"  
    type: "strategy\_monitor"  
    \# ...  
  dependencies:  
    produces\_events:  
      \- "MAX\_DRAWDOWN\_BREACHED"

## **Hoofdstuk 5: De Onderlinge Samenhang \- De "Configuratie Trein" in Actie (AANGEPAST)**

De magie van het systeem zit in hoe Operations deze bestanden aan elkaar koppelt tijdens de bootstrap-fase.

1. **Startpunt**: De gebruiker start de applicatie met de opdracht: run my\_btc\_operation.  
2. **Operations leest operation.yaml**: Hij vindt de strategy\_link voor experimental\_mean\_reversion.  
3. **Analyse van de Link**:  
   * Operations kijkt naar de execution\_environment\_id: backtest\_2020\_2024\_btc.  
   * Hij zoekt in **environments.yaml** en vindt backtest\_2020\_2024\_btc. Hij ziet dat dit een backtest\-omgeving is die data\_source\_id: btc\_eur\_15m\_archive vereist.  
   * Hij zoekt nu in **data\_sources.yaml** en vindt btc\_eur\_15m\_archive. Hij heeft nu alle technische details (pad, type) om de BacktestEnvironment en zijn DataSource te bouwen.  
   * Vervolgens kijkt Operations naar de strategy\_blueprint\_id: experimental\_mean\_reversion.  
   * Hij laadt **strategy\_blueprints/experimental\_mean\_reversion.yaml** en ziet de volledige workforce.  
   * Voor elke plugin in de workforce, gebruikt het Assembly Team de **manifest.yaml** van die plugin om de code te vinden en de params uit de blueprint te valideren tegen de schema.py.  
4. **Herhaling**: Operations herhaalt dit proces voor de live\_fvg\_strategy\-link, maar volgt nu het pad via environments.yaml naar **connectors.yaml** om de LiveEnvironment te bouwen.  
5. **Afronding**: Operations laadt tot slot schedule.yaml om de Scheduler te configureren en voltooit de "wiring" van de EventBus.

Het resultaat is een volledig geassembleerd, gevalideerd en onderling verbonden ecosysteem van plugins, klaar om van start te gaan, puur en alleen op basis van de declaratieve YAML-bestanden.