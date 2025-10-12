# **Overdrachtsdocument: Architectonische Inzichten & Beslissingen**

Versie: 1.0 (Post-Brainstorm)  
Status: Definitief  
Dit document consolideert de belangrijkste architectonische inzichten en beslissingen die zijn voortgekomen uit onze diepgaande discussies. Het dient als een overkoepelende gids en "Staat van de Unie" voor de verdere ontwikkeling van S1mpleTrader V2.

## **1\. De Kerngedachte: Scheiding van Verantwoordelijkheden**

De meest fundamentele uitkomst van onze gesprekken is de formalisering van een strikte scheiding tussen de **rol van S1mpleTrader** en de **rol van de exchanges**.

* **De Exchanges zijn de "Arena"**: Zij zijn de ultieme bron van waarheid voor de totale accountwaarde, live marktdata en de visuele trading-ervaring. We bouwen hun dashboards niet na.  
* **S1mpleTrader is het "Commandocentrum"**: Ons platform is een gespecialiseerde tool voor het ontwikkelen, testen en **geautomatiseerd uitvoeren van strategieën**. De PnL en status binnen S1mpleTrader reflecteren **uitsluitend** de performance van de door het platform beheerde strategieën.

Dit betekent dat het "Overall Portfolio" in de UI een aggregatie is van onze strategie-specifieke kasboeken (StrategyLedgers), en **geen** 1-op-1 spiegel van een exchange-account.

## **2\. Het Gelaagde Configuratiemodel**

We hebben een krachtig, hiërarchisch model voor configuratie gedefinieerd dat zowel flexibel als schaalbaar is.

**2.1. De Technische Basislaag: ExecutionEnvironment**

* **Concept**: De definitie van een technische "wereld" waarin een strategie kan draaien.  
* **Configuratie**: Gedefinieerd in een nieuw environments.yaml-bestand.  
* **Rollen**:  
  * Een backtest environment definieert welke data\_archives beschikbaar zijn.  
  * Een live of paper environment is gekoppeld aan exact één connector\_id.

**2.2. De Strategische Toplaag: Portfolio**

* **Concept**: De logische, strategische container waar de gebruiker mee werkt. Het is **niet** direct gekoppeld aan één exchange.  
* **Configuratie**: Gedefinieerd in een portfolio.yaml-bestand.  
* **Rollen**:  
  * Definieert overkoepelende risico-regels (max\_drawdown\_pct, etc.).  
  * Beheert een lijst van strategies, waarbij elke strategie expliciet wordt gekoppeld aan een execution\_environment\_id.  
  * De PortfolioSupervisor is de levende instantie die deze configuratie beheert en de geaggregeerde PnL van de onderliggende StrategyLedgers bijhoudt.

**2.3. Het Kasboek: StrategyLedger**

* **Concept**: De hernoemde versie van het oude Portfolio-component. Het is het "domme grootboek" dat de financiële staat (kapitaal, posities, PnL) bijhoudt voor **één enkele, geïsoleerde strategie-run**.  
* **Relatie**: Er is een 1-op-1 relatie tussen een actieve strategie en zijn StrategyLedger.

## **3\. De Gebruikersworkflow ("Top-Down")**

De gebruikerservaring in de UI volgt nu een logische, "top-down" hiërarchie:

1. **Portfolio Eerst**: Alles start in de **Portfolio Management** werkruimte. De gebruiker creëert of selecteert eerst een Portfolio en definieert daarmee de "wereld" (de beschikbare ExecutionEnvironments).  
2. **Context-Bewuste Strategy Builder**: De Strategy Builder wordt **vanuit een portfolio** gestart. De UI is nu "slim":  
   * Het toont alleen de handelsparen die beschikbaar zijn in het portfolio.  
   * Plugins worden dynamisch gefilterd. Een plugin wordt **uitgeschakeld** als zijn *vereiste* data (requires\_context) niet beschikbaar is.  
   * Een plugin krijgt een **waarschuwing** als *optionele* data (uses) niet beschikbaar is.  
   * De wizard helpt met het **resamplen van timeframes**.

## **4\. De Data-Architectuur: Hybride en Taak-Specifiek**

Onze discussies over data-opslag hebben geleid tot een geavanceerde, hybride architectuur.

**4.1. Fysieke Opslag: Catalogus & Archieven**

* **Data Archieven**: De bulk-data (trades, OHLCV) wordt opgeslagen in efficiënte **Parquet-bestanden**.  
* **De Catalogus**: Een **SQLite-database (catalog.db)** fungeert als centrale index. Het bevat niet de data zelf, maar alleen *metadata* over de Parquet-bestanden (welke data, welke bron, welke periode, etc.). Dit maakt het opvragen van data razendsnel.

**4.2. Ingestion Beleid: Taak-Specifieke Profielen**

* **Het Probleem**: De optimale strategie voor het schrijven van data verschilt per taak.  
* **De Oplossing**: We definiëren **taak-specifieke ingestion profiles** in platform.yaml:  
  * **historical\_task**: Voor bulk-downloads. Gebruikt een grote in-memory buffer (max\_records: 500000\) om grote, efficiënte Parquet-bestanden te creëren.  
  * **live\_task**: Voor real-time streams. Gebruikt een kleine buffer en een korte tijd-trigger (max\_seconds: 300\) voor maximale data-integriteit en minimale kans op verlies bij een crash.  
* **De Implementatie**: De DataCommandService gebruikt het historical\_task-profiel. De LiveDataSource (of een vergelijkbare component) gebruikt het live\_task-profiel.

**4.3. Live Data Handling: Producer-Consumer**

* **Het Probleem**: Trage schijf-I/O mag de ontvangst van snelle, live WebSocket-data niet blokkeren.  
* **De Oplossing**: Een **asynchroon Producer-Consumer patroon**:  
  * Een **Producer** ("Ontvanger") luistert naar de WebSocket en dumpt data direct in een in-memory **Queue** ("Wachtrij"). Deze taak is bliksemsnel.  
  * Een aparte **Consumer** ("Verwerker") haalt in zijn eigen tempo data uit de Queue en voert de tragere operaties uit (schrijven naar schijf, updaten van de buffer).  
  * Er is een **aparte Queue en buffer per unieke datastroom** (connector\_id, pair, data\_type) om data-integriteit te garanderen.

## **5\. Live State Reconciliation: De Dubbele Strategie**

Om de StrategyLedgers perfect synchroon te houden met de exchange, gebruiken we een tweeledige strategie:

1. **Push (WebSocket)**: Voor real-time updates. De LiveEnvironment luistert naar TradeExecuted-berichten die door de exchange worden *gepusht* en werkt de StrategyLedger direct bij.  
2. **Pull (REST API)**: Als veiligheidsnet. De PortfolioSupervisor instrueert de LiveEnvironment periodiek (en altijd bij herstart) om via de REST API de "absolute waarheid" op te halen en de interne StrategyLedgers te controleren en corrigeren.

De correlatie tussen externe order\_id's en onze interne correlation\_id wordt beheerd via het userref-veld bij het plaatsen van een order.

Dit document vat de kern van onze gezamenlijke architectonische visie samen.