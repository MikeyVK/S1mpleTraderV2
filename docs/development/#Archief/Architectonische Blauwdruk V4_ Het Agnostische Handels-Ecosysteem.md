# **Architectonische Blauwdruk V4: Het Agnostische Handels-Ecosysteem**

Versie: 4.0 (Definitief Ontwerp)  
Status: Vastgesteld  
Auteurs: Michel Verkaik & Programmeerpartner  
Datum: 12 oktober 2025

## **Voorwoord: De Reis naar Architectonische Zuiverheid**

Dit document is het logboek van een intellectuele reis. Het markeert de evolutie van S1mpleTrader V2 van een gestructureerd, hiërarchisch systeem naar een volledig gedecentraliseerd, agnostisch en event-gedreven ecosysteem. Elke beslissing die hierin is vastgelegd, is het resultaat van een kritische dialoog, waarbij we complexe problemen hebben ontrafeld en opgelost met elegante, zuivere oplossingen die trouw blijven aan onze kernprincipes.

Het doel van dit document is om de **filosofie**, de **structuur**, de **componenten** en de **interacties** van de definitieve V4-architectuur op een ondubbelzinnige manier vast te leggen. Het dient als de "Grondwet" voor alle toekomstige ontwikkeling, een ankerpunt dat ons scherp houdt op de principes die we samen hebben gedefinieerd: **Single Responsibility (SRP)**, **Configuratie-gedreven**, **Contract-gedreven**, en bovenal, **Plugin-First**.

## **Hoofdstuk 1: De Kernfilosofie \- Het Platform als Puur Framework**

De meest fundamentele doorbraak in ons denken is de herdefiniëring van de rol van S1mpleTrader zelf.

**Oude Visie (impliciet):** S1mpleTrader is een applicatie die strategieën uitvoert.

**Nieuwe Visie (expliciet):** S1mpleTrader is een agnostisch **besturingssysteem** voor quants.

Dit betekent dat de taak van het platform niet is om een specifieke manier van handelen af te dwingen. Zijn enige doel is het bieden van een extreem robuust, flexibel en schaalbaar **framework** waarbinnen een quant **alle** mogelijke kwantitatieve en operationele functionaliteit kan implementeren via zelfstandige, specialistische plugins. Het platform is de facilitator; de plugins, geconfigureerd door de quant, doen het werk. Deze filosofie is de drijvende kracht achter elke architectonische keuze in dit document.

## **Hoofdstuk 2: Het Paradigma \- Een Decentraal, Contract-Gedreven Ecosysteem**

Om de "agnostische framework"-filosofie technisch mogelijk te maken, stappen we volledig af van een centraal aangestuurde flow. We omarmen een decentraal, event-gedreven model, waarvan de regels en verbindingen niet in code, maar in centrale configuratiebestanden zijn vastgelegd.

### **2.1. De Drie Pilaren van de Configuratie**

De volledige werking van het systeem wordt gedefinieerd door drie door de **programmeur** beheerde "master" configuratiebestanden. Zij vormen samen de ruggengraat van het systeem.

1. **event\_map.yaml (De Grondwet van Communicatie):** Definieert **wat** er gecommuniceerd kan worden. Het is de "woordenlijst" van het systeem, die voor elk officieel systeem-event het DTO-contract, de toegestane publishers en de verplichte subscribers vastlegt.  
2. **wiring\_map.yaml (De Bouwtekening van de Dataflow):** Definieert **hoe** de componenten met elkaar praten. Het is de bouwtekening die beschrijft welke trigger (een event) leidt tot welke businesslogica (een methode op een component), en wat er met het resultaat moet gebeuren.  
3. **operation.yaml (Het Draaiboek van de Quant):** Definieert **wie** er meedoet. In dit bestand, dat door de quant wordt beheerd, wordt de "cast" van plugins voor een specifieke operatie samengesteld.

### **2.2. De Vier Functionele Pijlers: Een Consistente Terminologie**

Alle logica in het systeem is ondergebracht in vier duidelijk gescheiden, functionele categorieën. De naamgeving is rigoureus doorgevoerd om maximale helderheid en consistentie te garanderen, verankerd in het perspectief van de quant.

| Quant's Doel | Hoofdverantwoordelijkheid | Plugin Categorie (De "Worker") | De Manager (De "Operator") |
| :---- | :---- | :---- | :---- |
| "Ik wil mijn data voorbereiden" | **Contextualiseren** | ContextWorker | ContextOperator |
| "Ik wil een handelsidee ontwikkelen" | **Analyseren** | AnalysisWorker | AnalysisOperator |
| "Ik wil de situatie in de gaten houden" | **Monitoren** | MonitorWorker | MonitorOperator |
| "Ik wil een regel direct laten uitvoeren" | **Executeren** | ExecutionWorker | ExecutionOperator |

## **Hoofdstuk 3: De Communicatie-Architectuur \- De EventAdapter**

Onze meest diepgaande discussie leidde tot het inzicht dat kerncomponenten (zoals de Operators) **volledig bus-agnostisch** moeten zijn. De SRP- en DRY-principes dicteerden dat de bus-interactie en de businesslogica strikt gescheiden moesten zijn.

De oplossing is het **EventAdapter-patroon**, geïmplementeerd door een centrale EventWiringFactory.

### **3.1. Het Principe van de EventAdapter**

De EventAdapter is een generieke, herbruikbare "communicatie-officier" die als tussenpersoon fungeert tussen de EventBus en een pure business-component.

* **De Kerncomponent** (AnalysisOperator, MonitorOperator, etc.) is een pure "worker". Hij weet niets van de EventBus. Zijn enige interface met de buitenwereld is het accepteren van een DTO als input voor zijn methodes en het retourneren van een DTO als output.  
* **De EventAdapter** is een "domme" maar effectieve vertaler. Zijn enige taak, geconfigureerd door de EventWiringFactory, is:  
  1. Luisteren naar een specifiek, geconfigureerd event op de bus (listens\_to).  
  2. De payload van dat event doorgeven aan een specifieke methode van zijn doel-component (invokes).  
  3. De return-waarde van die methode publiceren op de bus onder een specifieke, geconfigureerde event-naam (publishes\_result\_as).

### **3.2. De EventWiringFactory: De Meester-Assembler**

Dit is de "hoofdaannemer" van het systeem, die tijdens de bootstrap-fase het volledige communicatienetwerk opbouwt.

1. **Lezen**: De factory leest de wiring\_map.yaml.  
2. Itereren: Voor elke wiring\_rule in het bestand:  
   a. Hij zoekt de juiste doel-component op (bv. de instantie van de AnalysisOperator).  
   b. Hij creëert een nieuwe, generieke EventAdapter-instantie.  
   c. Hij configureert deze adapter met de specifieke regel uit de YAML.  
   d. Hij abonneert de zojuist gecreëerde adapter op het listens\_to-event.

Dit proces garandeert dat alle intelligentie over de dataflow centraal in de wiring\_map.yaml leeft en dat de kerncomponenten puur en ontkoppeld blijven.

### **3.3. Een Concreet Voorbeeld: De AnalysisOperator en zijn Adapter**

Laten we de volledige keten volgen voor de AnalysisOperator.

1. **De wiring\_map.yaml definieert de regel:**  
   \- adapter\_id: "AnalysisPipelineAdapter"  
     listens\_to: "ContextReady"  
     invokes:  
       component: "AnalysisOperator"  
       method: "run\_pipeline"  
     publishes\_result\_as: "StrategyProposalReady"

2. **De AnalysisOperator is een pure business-component:**  
   \# services/operators/analysis\_operator.py  
   class AnalysisOperator:  
       def \_\_init\_\_(self, workers: List\[AnalysisWorker\]):  
           self.\_workers \= workers

       def run\_pipeline(self, context: TradingContext) \-\> Optional\[EngineCycleResult\]:  
           \# 100% PURE BUSINESS LOGICA: voert de 9-fasen trechter uit.  
           \# Weet niets van 'ContextReady' of 'StrategyProposalReady'.  
           \# Ontvangt een DTO, retourneert een DTO.  
           print("ANALYSIS OPERATOR: Start analyse op basis van ontvangen context...")  
           result \= EngineCycleResult(...) \# Resultaat van de 9-fasen trechter  
           print("ANALYSIS OPERATOR: Analyse compleet. Retourneer resultaat.")  
           return result

3. **De EventAdapter is de generieke vertaler:**  
   \# services/event\_wiring/adapter.py  
   class EventAdapter(ISubscriber):  
       def \_\_init\_\_(self, wiring\_rule: dict, target\_component: Any, event\_bus: EventBus):  
           \# ... slaat configuratie op ...

       def handle\_event(self, event\_name: str, payload: BaseModel) \-\> None:  
           \# Roep de geconfigureerde methode aan (AnalysisOperator.run\_pipeline)  
           result \= self.\_target.run\_pipeline(payload)

           \# Publiceer het resultaat onder de geconfigureerde naam  
           if result:  
               event\_to\_publish \= self.\_rule\["publishes\_result\_as"\]  
               self.\_event\_bus.publish(event\_to\_publish, result)

4. De EventWiringFactory legt de verbinding:  
   Tijdens de bootstrap creëert de factory een EventAdapter-instantie specifiek voor deze regel en roept dan aan:  
   event\_bus.subscribe("ContextReady", adapter.handle\_event)

Deze structuur is de ultieme manifestatie van onze kernprincipes. De scheiding van verantwoordelijkheden is absoluut, de configuratie is de "single source of truth", en de componenten zijn perfect ontkoppeld.

## **Hoofdstuk 4: Het Contract-Gedreven Fundament**

Het hele systeem wordt bijeengehouden door een web van strikte, expliciete contracten.

### **4.1. Configuratie-Contracten (Pydantic Schema's)**

Elk \*.yaml-bestand heeft een corresponderend Pydantic-model dat de structuur, datatypes en regels valideert bij het opstarten. Dit geldt voor event\_map.yaml, wiring\_map.yaml, en operation.yaml. Dit voorkomt runtime-fouten door configuratiefouten.

### **4.2. Data-Contracten (DTOs)**

Data Transfer Objects, gedefinieerd met Pydantic, zijn de **enige toegestane vorm van payload** op de EventBus. Dit garandeert dat elke component precies weet welke data hij ontvangt. De event\_map.yaml legt de koppeling tussen een event-naam en zijn DTO-contract vast.

### **4.3. Interface-Contracten (IPublisher & ISubscriber)**

Deze typing.Protocol-interfaces dwingen een voorspelbaar gedrag af voor alle communicerende partijen en maken een waterdichte, tweezijdige validatie mogelijk.

* **ISubscriber**: Garandeert dat een component een handle\_event(event\_name, payload) methode heeft. Dit wordt gebruikt door de EventAdapter.  
* **IPublisher**: Garandeert dat een component een get\_published\_events() methode heeft. Deze methode retourneert de events die de component *claimt* te kunnen publiceren.

De EventWiringFactory gebruikt deze IPublisher-claim om de event\_map.yaml te valideren: "De event\_map zegt dat AnalysisOperator het StrategyProposalReady-event publiceert. Claimt de AnalysisOperator-klasse dit zelf ook in zijn code?". Een mismatch leidt tot een fout bij het opstarten.

## **Hoofdstuk 5: Het Grote Geheel \- De Bootstrap & Runtime Flow**

### **5.1. De Bootstrap-Fase (De Opbouw)**

1. **Operations Start**: De Operations-component wordt gestart.  
2. **Configuratie Laden**: Operations laadt alle master-configuraties (event\_map.yaml, wiring\_map.yaml) en de operation.yaml van de quant.  
3. **Componenten Bouwen**: Het Assembly Team wordt aangeroepen om alle benodigde, pure business-componenten te bouwen op basis van de operation.yaml (alle Workers en Operators).  
4. **EventBus Initialisatie**: De EventBus wordt geïnitialiseerd met de event\_map.yaml, waardoor hij alle event-namen en hun DTO-contracten kent.  
5. **Bedrading**: De EventWiringFactory wordt geïnitialiseerd met de wiring\_map.yaml, de lijst van gebouwde componenten en de EventBus. Hij voert zijn wire\_all()-methode uit, creëert alle EventAdapters en legt alle abonnementen.  
6. **Startschot**: Operations publiceert het OperationStarted-event. Het systeem is nu live en autonoom.

### **5.2. Een Runtime Voorbeeld (Eén Tick)**

1. Een ExecutionEnvironment publiceert een MarketDataReceived-event.  
2. De EventAdapter voor de ContextOperator vangt dit op.  
3. De adapter roept context\_operator.run\_pipeline() aan met de MarketSnapshotDTO.  
4. De ContextOperator retourneert een TradingContext-DTO.  
5. De EventAdapter publiceert dit resultaat als een ContextReady-event.  
6. **Tegelijkertijd** worden nu meerdere adapters wakker die luisteren naar ContextReady:  
   * De adapter voor de AnalysisOperator.  
   * De adapters voor eventuele MonitorWorkers die context-data nodig hebben.  
   * De adapters voor eventuele ExecutionWorkers die op elke tick moeten reageren.  
7. Elke adapter roept zijn eigen, pure business-component aan.  
8. De resultaten worden via de adapters weer als nieuwe, specifieke events op de bus gepubliceerd.  
9. De cyclus herhaalt zich.

## **Conclusie**

De reis heeft ons geleid tot een architectuur die de ultieme manifestatie is van onze kernvisie. Het is een systeem dat niet alleen technisch robuust, schaalbaar en testbaar is, maar dat ook een perfecte scheiding aanbrengt tussen de wereld van de programmeur en de wereld van de quant.

* **SRP is Absoluut**: De businesslogica is volledig gescheiden van de communicatielogica.  
* **Configuratie is Koning**: De event\_map.yaml en wiring\_map.yaml zijn de absolute "single source of truth" voor de werking van het systeem.  
* **DRY is Gerespecteerd**: De EventAdapter is een enkele, generieke component die alle bus-interactie afhandelt.

Dit is de blauwdruk. Een puur, decentraal, en contract-gedreven "Quant Operating System". Het platform faciliteert; de configuratie dicteert; de plugins doen het werk.