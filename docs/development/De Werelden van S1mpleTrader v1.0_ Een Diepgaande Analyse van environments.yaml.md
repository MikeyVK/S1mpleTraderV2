# **De Werelden van S1mpleTrader: Een Diepgaande Analyse van environments.yaml**

Versie: 1.0  
Status: Definitief

## **Hoofdstuk 1: De Rol van environments.yaml in het Ecosysteem**

Binnen de S1mpleTrader V2-architectuur is het environments.yaml-bestand de cruciale schakel tussen de abstracte, strategische intentie van de quant en de concrete, technische realiteit van de uitvoering. Waar operation.yaml definieert *welke* strategieën er moeten draaien, definieert environments.yaml de **"werelden"** (ExecutionEnvironments) *waarin* deze strategieën zullen leven.

Het is de architectonische brug die antwoord geeft op de vraag: "Waar komt de data vandaan en waar worden trades naartoe gestuurd?" Dit bestand stelt ons in staat om een strategie met één enkele aanpassing in de operation.yaml te "promoveren" van een backtest-omgeving naar een live-handelsomgeving, zonder ook maar één regel code te wijzigen.

## **Hoofdstuk 2: De Kracht van de "Discriminated Union"**

De flexibiliteit van environments.yaml wordt technisch mogelijk gemaakt door een krachtig Pydantic-concept genaamd een **discriminated union**.

### **2.1. Wat is een Discriminated Union?**

Stel je voor dat je een formulier hebt voor "Vervoersmiddel". Afhankelijk van welk vervoersmiddel je kiest, veranderen de overige velden:

* Als je "Fiets" kiest (type: "fiets"), moet je het aantal\_versnellingen invullen.  
* Als je "Auto" kiest (type: "auto"), moet je het kenteken en brandstof\_type invullen.

Dit is precies wat een discriminated union doet. Het is een Pydantic-model dat, op basis van de waarde van één specifiek veld (de "discriminator"), bepaalt welke andere velden verplicht en geldig zijn.

### **2.2. De Implementatie in environments.yaml**

In ons systeem is het veld **type** de discriminator. Door de waarde van type in te stellen op backtest, paper of live, dwingt het validatie-schema af welke *andere* sleutels in die omgevingsconfiguratie aanwezig moeten zijn.

* type: "backtest" \-\> Vereist een data\_source\_id.  
* type: "paper" \-\> Vereist een connector\_id.  
* type: "live" \-\> Vereist een connector\_id.

Dit zorgt voor een extreem robuuste en zelf-documenterende configuratie. Het is onmogelijk om een backtest-omgeving te definiëren zonder een databron op te geven, of een live-omgeving zonder een connector te specificeren.

## **Hoofdstuk 3: Diepgaande Analyse van de Omgevingstypes**

Laten we elke omgeving in detail ontleden en de implicaties voor de dataflow en trade-executie analyseren.

### **3.1. De backtest Omgeving: De Tijdreiziger**

* **Doel**: Het uitvoeren van een strategie tegen een eindige, historische dataset. Dit is de primaire omgeving voor strategieontwikkeling en \-validatie.  
* **Specifieke Parameters**:  
  * type: "backtest" (verplicht)  
  * data\_source\_id: str (verplicht): De unieke naam van een dataset zoals gedefinieerd in data\_sources.yaml.  
* **Constructie door Operations**:  
  1. Operations leest een strategy\_link in operation.yaml en vindt execution\_environment\_id: "backtest\_btc\_2023".  
  2. Het zoekt backtest\_btc\_2023 op in environments.yaml en ziet type: "backtest" en data\_source\_id: "btc\_eur\_1h\_archive".  
  3. Het zoekt btc\_eur\_1h\_archive op in data\_sources.yaml en vindt de fysieke locatie van de Parquet- of CSV-bestanden.  
  4. Het Assembly Team krijgt de opdracht een BacktestEnvironment-object te bouwen. Deze klasse zal intern een ParquetDataSource (of vergelijkbaar) en een SimulatedClock instantiëren, geladen met de data van het opgegeven pad.  
* **Generatie van MarketSnapshot / MarketDataReceived**:  
  * De SimulatedClock is de motor. Het is een simpele for-lus die rij voor rij door de geladen DataFrame itereert.  
  * Bij elke iteratie (elke "tick" van de klok) publiceert de BacktestEnvironment een MarketDataReceived-event. De payload van dit event bevat de data van die ene rij uit de DataFrame (timestamp, open, high, low, close, volume, etc.).  
* **Verwerking van Trades (ExecutionApproved)**:  
  * Wanneer de ExecutionHandler een ExecutionApproved-event ontvangt, bevindt hij zich in een volledig gesimuleerde wereld.  
  * Hij roept **niet** een externe APIConnector aan.  
  * In plaats daarvan roept hij de open\_trade() of close\_trade() methodes aan op het **in-memory StrategyLedger-object**.  
  * De StrategyLedger werkt zijn interne staat bij (saldo, open positie) en berekent PnL. Dit is een pure, bliksemsnelle, wiskundige operatie zonder externe afhankelijkheden.

### **3.2. De live Omgeving: De Connectie met de Realiteit**

* **Doel**: Het uitvoeren van een strategie met echt kapitaal op een live exchange.  
* **Specifieke Parameters**:  
  * type: "live" (verplicht)  
  * connector\_id: str (verplicht): De unieke naam van een connector zoals gedefinieerd in connectors.yaml.  
* **Constructie door Operations**:  
  1. Operations leest execution\_environment\_id: "live\_kraken\_main".  
  2. Het zoekt dit op in environments.yaml en ziet type: "live" en connector\_id: "kraken\_live\_eur\_account".  
  3. Het zoekt kraken\_live\_eur\_account op in connectors.yaml en vindt de type: "kraken\_private" en de API-credentials.  
  4. Het Assembly Team krijgt de opdracht een LiveEnvironment-object te bouwen. Deze klasse zal intern de ConnectorFactory gebruiken om een KrakenAPIConnector-instantie te creëren met de juiste credentials.  
* **Generatie van MarketSnapshot / MarketDataReceived**:  
  * De LiveEnvironment gebruikt de geïnstantieerde APIConnector om een **WebSocket-verbinding** met de exchange op te zetten.  
  * De APIConnector luistert naar de live stroom van marktdata (trades, orderboek-updates).  
  * Elke keer dat er een relevant bericht via de WebSocket binnenkomt, vertaalt de APIConnector dit naar een gestandaardiseerd formaat en geeft het door aan de LiveEnvironment.  
  * De LiveEnvironment publiceert deze data vervolgens als een MarketDataReceived-event. De "hartslag" van het systeem wordt hier bepaald door de markt, niet door een interne klok.  
* **Verwerking van Trades (ExecutionApproved)**:  
  * Wanneer de ExecutionHandler een ExecutionApproved-event ontvangt, is de impact direct en reëel.  
  * Hij roept de place\_order()-methode aan op de **echte APIConnector**.  
  * De APIConnector stuurt een gesigneerd API-verzoek naar de exchange om de order te plaatsen.  
  * De bevestiging van de order-fill komt asynchroon terug via de **private user data WebSocket stream**. De APIConnector vangt dit op, en de ExecutionHandler publiceert op zijn beurt een LedgerStateChanged-event om de interne StrategyLedger bij te werken.

### **3.3. De paper Omgeving: De Hybride Simulator**

* **Doel**: Het simuleren van trades op een **live markt-feed** zonder echt kapitaal te riskeren. Dit is de laatste testfase voor live-gang.  
* **Specifieke Parameters**:  
  * type: "paper" (verplicht)  
  * connector\_id: str (verplicht): Net als de live-omgeving heeft het een verbinding met de echte wereld nodig voor de datafeed.  
* **Constructie door Operations**:  
  * Het proces is **identiek aan de live-omgeving**. Operations bouwt een PaperEnvironment (een specifieke klasse) die, net als de LiveEnvironment, een APIConnector instantieert op basis van de connector\_id.  
* **Generatie van MarketSnapshot / MarketDataReceived**:  
  * Dit proces is **identiek aan de live-omgeving**. De PaperEnvironment gebruikt de APIConnector om zich te abonneren op de live WebSocket-feed en publiceert MarketDataReceived-events zodra er nieuwe marktdata binnenkomt.  
* **Verwerking van Trades (ExecutionApproved)**:  
  * **Dit is het cruciale verschil.** Wanneer de ExecutionHandler binnen een PaperEnvironment een ExecutionApproved-event ontvangt:  
  * Hij roept **NIET** de place\_order()-methode van de APIConnector aan.  
  * In plaats daarvan roept hij, net als in de backtest-omgeving, de methodes aan op een **in-memory, gesimuleerd StrategyLedger-object**.  
  * De PaperEnvironment simuleert vervolgens de "fills" van de orders op basis van de binnenkomende live ticks. Als er een limit buy order op €50.000 staat en er komt een live trade binnen op €49.999, dan zal de PaperEnvironment de order als gevuld markeren en de StrategyLedger updaten.

### **Hoofdstuk 4: Voorbeeld environments.yaml in Context**

Hieronder een voorbeeld dat de samenhang met connectors.yaml en data\_sources.yaml illustreert.

\# In config/connectors.yaml  
kraken\_live:  
  type: "kraken\_private"  
  api\_key: "..."  
  api\_secret: "..."

binance\_public\_feed:  
  type: "binance\_public"

\# In config/data\_sources.yaml  
btc\_eur\_1h\_archive:  
  type: "parquet\_archive"  
  path: "source\_data/BTC\_EUR\_1h/"

\# In config/environments.yaml  
\# De sleutels (bv. 'live\_kraken\_main') zijn de unieke identifiers die  
\# in operation.yaml worden gebruikt.

\# Een LIVE omgeving, gekoppeld aan een private Kraken connector  
live\_kraken\_main:  
  type: "live"  
  connector\_id: "kraken\_live"

\# Een PAPER omgeving, die de publieke datafeed van Binance gebruikt  
paper\_binance\_test:  
  type: "paper"  
  connector\_id: "binance\_public\_feed"

\# Een BACKTEST omgeving, gekoppeld aan een lokale dataset  
backtest\_btc\_historisch:  
  type: "backtest"  
  data\_source\_id: "btc\_eur\_1h\_archive"  
