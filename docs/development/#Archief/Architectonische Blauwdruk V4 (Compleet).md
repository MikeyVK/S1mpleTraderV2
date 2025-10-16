# **Architectonische Blauwdruk V4 (Compleet)**

**Versie:** 4.0 (Definitief Ontwerp)

**Status:** Vastgesteld

**Auteurs:** Michel Verkaik & Programmeerpartner

**Datum:** 12 oktober 2025

## **Voorwoord: De Reis naar Architectonische Zuiverheid**

Dit document is het logboek van een intellectuele reis. Het markeert de evolutie van een gestructureerd, hiërarchisch systeem naar een volledig gedecentraliseerd, agnostisch en event-gedreven ecosysteem. Elke beslissing die hierin is vastgelegd, is het resultaat van een kritische dialoog, waarbij we complexe problemen hebben ontrafeld en opgelost met elegante, zuivere oplossingen die trouw blijven aan onze kernprincipes.

Het doel van dit document is om de **filosofie**, de **structuur**, de **configuratie**, de **componenten** en de **interacties** van de definitieve V4-architectuur op een ondubbelzinnige manier vast te leggen. Het dient als de "Grondwet" voor alle toekomstige ontwikkeling, een ankerpunt dat ons scherp houdt op de principes die we samen hebben gedefinieerd: **Single Responsibility (SRP)**, **Configuratie-gedreven**, **Contract-gedreven**, en bovenal, **Plugin-First**.

## **Hoofdstuk 1: De Kernfilosofie \- Het Platform als Puur Framework**

De meest fundamentele doorbraak in ons denken is de herdefiniëring van de rol van het platform zelf.

**Oude Visie (impliciet):** Het platform is een applicatie die strategieën uitvoert.

**Nieuwe Visie (expliciet):** Het platform is een agnostisch **besturingssysteem** voor quants.

Dit betekent dat de taak van het platform niet is om een specifieke manier van handelen af te dwingen. Zijn enige doel is het bieden van een extreem robuust, flexibel en schaalbaar **framework** waarbinnen een quant **alle** mogelijke kwantitatieve en operationele functionaliteit kan implementeren via zelfstandige, specialistische plugins. Het platform is de facilitator; de plugins, geconfigureerd door de quant, doen het werk. Deze filosofie is de drijvende kracht achter elke architectonische keuze in dit document.

## **Hoofdstuk 2: De Configuratie Trein \- De Bron van Waarheid**

In de V4 architectuur is de configuratie koning. De YAML-bestanden zijn niet slechts instellingen; ze zijn het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft. Dit hoofdstuk beschrijft de "configuratie trein": de logische hiërarchie en samenhang van de verschillende YAML-bestanden die samen een volledige, gevalideerde en uitvoerbare operatie definiëren.

### **2.1. De Hiërarchie (van Stabiel naar Dynamisch)**

1. **platform.yaml**: De fundering van het hele platform.  
2. **connectors.yaml**: De technische "stekkerdoos" voor **live** verbindingen.  
3. **data\_sources.yaml**: De catalogus van **lokale** historische datasets.  
4. **environments.yaml**: De definitie van de "werelden" waarin strategieën kunnen draaien.  
5. **event\_map.yaml**: De grondwet van de interne communicatie.  
6. **wiring\_map.yaml**: De bouwtekening van de dataflow.  
7. **schedule.yaml**: De agnostische "metronoom" van het systeem.  
8. **operation.yaml**: Het centrale "draaiboek" van de quant, dat alles samenbrengt.  
9. **strategy\_blueprint.yaml**: De gedetailleerde "receptenkaart" voor elke plugin.  
10. **plugin\_manifest.yaml**: De "ID-kaart" van elke individuele plugin.

### **2.2. Gedetailleerd Overzicht van de Configuratiebestanden**

#### **Platformbeheer**

* **platform.yaml**: Globale, niet-strategische instellingen.  
  \# config/platform.yaml  
  language: "nl"  
  logging:  
    profile: "analysis"  
  plugins\_root\_path: "plugins"

* **connectors.yaml**: Technische configuratie van verbindingen met externe, live partijen.  
  \# config/connectors.yaml  
  kraken\_live\_eur\_account:  
    type: "kraken\_private"  
    api\_key: "${KRAKEN\_API\_KEY}"  
    api\_secret: "${KRAKEN\_API\_SECRET}"

* **data\_sources.yaml**: Register van alle beschikbare historische datasets op schijf.  
  \# config/data\_sources.yaml  
  btc\_eur\_15m\_archive:  
    type: "parquet\_archive"  
    path: "source\_data/BTC\_EUR\_15m/"  
    asset\_pair: "BTC/EUR"

#### **Systeemarchitectuur**

* **environments.yaml**: Definieert de "werelden" (backtest, paper, live) en koppelt ze aan een connector\_id of data\_source\_id.  
  \# config/environments.yaml  
  live\_kraken\_main:  
    type: "live"  
    connector\_id: "kraken\_live\_eur\_account"  
  backtest\_2020\_2024\_btc:  
    type: "backtest"  
    data\_source\_id: "btc\_eur\_15m\_archive"

* **event\_map.yaml**: De "woordenlijst" die events koppelt aan DTO-contracten en toegestane publishers/subscribers.  
* **wiring\_map.yaml**: De "bouwtekening" die de dataflow beschrijft: welk event triggert welke methode.  
* **schedule.yaml**: Configureert de Scheduler om tijd-gebaseerde events te publiceren.  
  \# config/schedule.yaml  
  schedule:  
    \- event\_name: "five\_minute\_reconciliation\_tick"  
      type: "interval"  
      value: "5m"  
    \- event\_name: "daily\_dca\_buy\_signal"  
      type: "cron"  
      value: "0 9 \* \* \*" \# Elke dag om 9:00

#### **Operationeel Beheer (Quant Domein)**

* **operation.yaml**: Het hoofdbestand dat blueprints koppelt aan environments om een operatie te vormen.  
  \# config/operations/my\_btc\_operation.yaml  
  display\_name: "Mijn BTC Operatie (Live & Backtest)"  
  strategy\_links:  
    \- strategy\_blueprint\_id: "live\_fvg\_strategy"  
      execution\_environment\_id: "live\_kraken\_main"  
      is\_active: true  
    \- strategy\_blueprint\_id: "experimental\_mean\_reversion"  
      execution\_environment\_id: "backtest\_2020\_2024\_btc"  
      is\_active: true

* **strategy\_blueprint.yaml**: De volledige configuratie van alle plugins voor één strategie.  
  \# config/strategy\_blueprints/live\_fvg\_strategy.yaml  
  display\_name: "Live FVG Entry Strategy"  
  workforce:  
    context\_workers:  
      ema\_detector\_fast:  
        plugin\_name: "ema\_detector"  
        params: { period: 50 }  
    analysis\_workers:  
      fvg\_entry:  
        plugin\_name: "fvg\_entry\_detector"  
        params: { fvg\_min\_size\_pct: 0.1 }

#### **Plugin Definitie**

* **plugin\_manifest.yaml**: De "ID-kaart" van een plugin, maakt hem ontdekbaar en valideerbaar.  
  \# plugins/monitors/max\_drawdown\_monitor/manifest.yaml  
  identification:  
    name: "max\_drawdown\_monitor"  
    type: "monitor\_worker"  
  produces\_events:  
    \- "MAX\_DRAWDOWN\_BREACHED"

## **Hoofdstuk 3: De Werelden: Backtest, Paper & Live Environments**

Het environments.yaml-bestand is de cruciale schakel tussen de abstracte strategie en de concrete uitvoering. Het definieert de **ExecutionEnvironments** waarin strategieën leven.

### **3.1. De Kracht van de "Discriminated Union"**

De flexibiliteit van environments.yaml is gebaseerd op het concept van een "discriminated union". Het veld **type** fungeert als de "discriminator":

* type: "backtest" \-\> Vereist een data\_source\_id.  
* type: "paper" \-\> Vereist een connector\_id.  
* type: "live" \-\> Vereist een connector\_id.

Dit dwingt een robuuste en zelf-documenterende configuratie af: een backtest heeft altijd een databron nodig, en een live- of paper-omgeving altijd een live connector.

### **3.2. De backtest Omgeving: De Tijdreiziger**

* **Doel**: Het uitvoeren van een strategie tegen een eindige, historische dataset.  
* **Dataflow**: Een interne SimulatedClock itereert rij voor rij door de dataset en publiceert MarketDataReceived-events.  
* **Trade Verwerking**: ExecutionApproved-events worden verwerkt door een **in-memory StrategyLedger-object**.

### **3.3. De live Omgeving: De Connectie met de Realiteit**

* **Doel**: Het uitvoeren van een strategie met echt kapitaal op een live exchange.  
* **Dataflow**: Een LiveEnvironment zet een **WebSocket-verbinding** op met de exchange en publiceert binnenkomende marktberichten als MarketDataReceived-events.  
* **Trade Verwerking**: ExecutionApproved-events leiden tot een aanroep van place\_order() op de **echte APIConnector**.

### **3.4. De paper Omgeving: De Hybride Simulator**

* **Doel**: Het simuleren van trades op een **live markt-feed** zonder echt kapitaal te riskeren.  
* **Dataflow**: Identiek aan de live-omgeving.  
* **Trade Verwerking**: Identiek aan de backtest-omgeving (in-memory StrategyLedger).

## **Hoofdstuk 4: De Functionele Pijlers: Een Consistente Terminologie**

Alle logica in het systeem is ondergebracht in vier duidelijk gescheiden, functionele categorieën. Elke categorie bestaat uit een **Worker** (de plugin) en een **Operator** (de manager).

| Quant's Doel | Hoofdverantwoordelijkheid | Plugin Categorie (De "Worker") | De Manager (De "Operator") |
| :---- | :---- | :---- | :---- |
| "Ik wil mijn data voorbereiden" | **Contextualiseren** | ContextWorker | ContextOperator |
| "Ik wil een handelsidee ontwikkelen" | **Analyseren** | AnalysisWorker | AnalysisOperator |
| "Ik wil de situatie in de gaten houden" | **Monitoren** | MonitorWorker | MonitorOperator |
| "Ik wil een regel direct laten uitvoeren" | **Executeren** | ExecutionWorker | ExecutionOperator |

### **4.1 ContextWorker \- De Voorbereider**

* **Rol:** Verrijkt ruwe marktdata met analytische context (indicatoren, etc.).  
* **Aansturing:** Beheerd door de ContextOperator, die luistert naar MarketDataReceived en ContextReady publiceert.

### **4.2 AnalysisWorker \- De Analist**

* **Rol:** Genereert niet-deterministische handelsvoorstellen.  
* **Aansturing:** Beheerd door de AnalysisOperator, die luistert naar ContextReady en StrategyProposalReady publiceert.

### **4.3 MonitorWorker \- De Waakhond**

* **Rol:** Observeert de operatie en publiceert informatieve, strategische events. Handelt **nooit** zelf.  
* **Subtypes:**  
  * **Context Monitors:** Bewaken externe marktomstandigheden (luisteren naar ContextReady). Voorbeeld: VolumeSpikeMonitor.  
  * **State Monitors:** Bewaken de interne, financiële staat (luisteren naar LedgerStateChanged). Voorbeeld: MaxDrawdownMonitor.

### **4.4 ExecutionWorker \- De Uitvoerder**

* **Rol:** Voert deterministische, op regels gebaseerde acties uit.  
* **Aansturing:** Worden getriggerd door specifieke events (bv. een TimerEvent of een event van een MonitorWorker).  
* **Output:** Een ExecutionApproved event (een directe opdracht, geen voorstel).  
* **Voorbeelden:** DCAWorker, EmergencyExitWorker.

## **Hoofdstuk 5: De Communicatie-Architectuur \- De EventAdapter**

De kerncomponenten (Operators) zijn **volledig bus-agnostisch**. De oplossing is het **EventAdapter-patroon**, geïmplementeerd door een centrale EventWiringFactory.

### **5.1. Het Principe van de EventAdapter**

De EventAdapter is een generieke tussenpersoon tussen de EventBus en een pure business-component. Zijn gedrag wordt volledig gedicteerd door de wiring\_map.yaml.

* **Een wiring\_map.yaml regel:**  
  \- adapter\_id: "AnalysisPipelineAdapter"  
    listens\_to: "ContextReady"  
    invokes:  
      component: "AnalysisOperator"  
      method: "run\_pipeline"  
    publishes\_result\_as: "StrategyProposalReady"

* **De Kerncomponent (AnalysisOperator):** Is een pure Python-klasse. Weet niets van de bus.  
  \# services/operators/analysis\_operator.py  
  class AnalysisOperator:  
      def run\_pipeline(self, context: TradingContext) \-\> Optional\[EngineCycleResult\]:  
          \# 100% PURE BUSINESS LOGICA  
          \# Ontvangt een DTO, retourneert een DTO.  
          print("ANALYSIS OPERATOR: Start analyse...")  
          result \= EngineCycleResult(...)  
          return result

* **De EventAdapter:** Een generieke vertaler.  
  \# services/event\_wiring/adapter.py  
  class EventAdapter(ISubscriber):  
      def handle\_event(self, event\_name: str, payload: BaseModel) \-\> None:  
          \# Roep de geconfigureerde methode aan  
          result \= self.\_target.run\_pipeline(payload)  
          \# Publiceer het resultaat onder de geconfigureerde naam  
          if result:  
              event\_to\_publish \= self.\_rule\["publishes\_result\_as"\]  
              self.\_event\_bus.publish(event\_to\_publish, result)

### **5.2. De EventWiringFactory: De Meester-Assembler**

Dit is de "hoofdaannemer" die tijdens de bootstrap-fase de wiring\_map.yaml leest en voor elke regel een geconfigureerde EventAdapter creëert en abonneert op de EventBus.

## **Hoofdstuk 6: Het Contract-Gedreven Fundament**

Het systeem wordt bijeengehouden door strikte, expliciete contracten.

* **Configuratie-Contracten (Pydantic Schema's)**: Elk \*.yaml-bestand heeft een Pydantic-model dat de structuur valideert bij het opstarten.  
* **Data-Contracten (DTOs)**: De enige toegestane vorm van payload op de EventBus. De event\_map.yaml koppelt een event-naam aan zijn DTO-contract.  
* **Interface-Contracten (IPublisher & ISubscriber)**: typing.Protocol-interfaces die een voorspelbaar gedrag afdwingen. De EventWiringFactory valideert de claims van een component (via get\_published\_events()) tegen de regels in de event\_map.yaml. Een mismatch leidt tot een fout bij het opstarten.

## **Hoofdstuk 7: Het Grote Geheel \- De Bootstrap & Runtime Flow**

### **7.1. De Bootstrap-Fase (De "Configuratie Trein" in Actie)**

1. **Startpunt**: De gebruiker start een operatie (run my\_btc\_operation).  
2. **Operations leest operation.yaml**: Vindt alle actieve strategy\_links.  
3. **Per Link**:  
   * Leest execution\_environment\_id en zoekt in environments.yaml.  
   * Bepaalt het pad naar connectors.yaml (voor live/paper) of data\_sources.yaml (voor backtest) om de correcte ExecutionEnvironment te bouwen.  
   * Leest strategy\_blueprint\_id en laadt het strategy\_blueprint.yaml om de workforce te bepalen.  
   * Gebruikt plugin\_manifest.yaml voor elke plugin om deze te vinden en valideren.  
4. **Componenten Bouwen**: Alle benodigde, pure business-componenten worden gebouwd.  
5. **EventBus Initialisatie**: Gebeurt met de event\_map.yaml.  
6. **Bedrading**: De EventWiringFactory leest de wiring\_map.yaml en creëert alle EventAdapters.  
7. **Startschot**: Het OperationStarted-event wordt gepubliceerd. Het systeem is nu live.

### **7.2. Een Runtime Voorbeeld (Eén Tick)**

1. Een ExecutionEnvironment publiceert een MarketDataReceived-event.  
2. De EventAdapter voor de ContextOperator vangt dit op en roept run\_pipeline() aan.  
3. De adapter publiceert het resultaat als een ContextReady-event.  
4. **Tegelijkertijd** worden nu meerdere adapters wakker die luisteren naar ContextReady: die voor de AnalysisOperator, MonitorWorkers, ExecutionWorkers, etc.  
5. Elke adapter roept zijn eigen, pure business-component aan.  
6. De resultaten worden via de adapters weer als nieuwe, specifieke events op de bus gepubliceerd. De cyclus herhaalt zich.

## **Conclusie**

De reis heeft ons geleid tot een architectuur die de ultieme manifestatie is van onze kernvisie. Het is een systeem dat niet alleen technisch robuust, schaalbaar en testbaar is, maar dat ook een perfecte scheiding aanbrengt tussen de wereld van de programmeur en de wereld van de quant.

* **SRP is Absoluut**: De businesslogica is volledig gescheiden van de communicatielogica.  
* **Configuratie is Koning**: De YAML-bestanden zijn de absolute "single source of truth".  
* **DRY is Gerespecteerd**: De EventAdapter is een enkele, generieke component die alle bus-interactie afhandelt.

Dit is de blauwdruk. Een puur, decentraal, en contract-gedreven "Quant Operating System". Het platform faciliteert; de configuratie dicteert; de plugins doen het werk.