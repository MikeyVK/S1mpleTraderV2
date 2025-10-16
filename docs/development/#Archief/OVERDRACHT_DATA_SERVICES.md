# **Overdracht: Architectuur & Implementatie Data Services**

**Versie:** 1.0 · **Status:** Ontwerp Gevestigd, Eerste Implementatie Voltooid

Dit document dient als een samenvatting van de gevestigde architectuur voor de data services en beschrijft de status van de implementatie. Het is het ankerpunt voor de verdere ontwikkeling.

## **1\. Wat Hebben We Bereikt?**

We hebben een robuust, schaalbaar en architectonisch zuiver fundament gelegd voor alle data-operaties binnen S1mpleTrader V2.

### **Architectuur Verankerd in "De Wet"**

Het **CQRS (Command Query Responsibility Segregation)** principe is nu de leidraad en is verankerd in onze design principles. Dit heeft geleid tot een glasheldere scheiding met bijbehorende naamgevingsconventies:

* **DataCommandService**: De specialist voor alle **schrijf-acties (Commands)**. Methodes zijn actieve werkwoorden (bv. fetch\_period()) en de bijbehorende DTO's hebben de \*Command suffix.  
* **DataQueryService**: De specialist voor alle **lees-acties (Queries)**. Methodes zijn "vragen" die beginnen met get\_\* (bv. get\_coverage()) en de bijbehorende DTO's hebben de \*Query suffix.

### **Configuratie is Contract-gedreven en Schaalbaar**

De volledige configuratiestructuur is vastgelegd in Pydantic-schema's, wat zorgt voor een voorspelbaar en type-veilig systeem.

* **Logische Structuur**: platform.yaml heeft een hiërarchische indeling (core, services, data, portfolio) die onze architectuur weerspiegelt.  
* **Scheiding van Verantwoordelijkheden**: Connector-definities zijn afgesplitst naar een eigen connectors.yaml.  
* **Veiligheid & Schaalbaarheid**: We hebben een toekomstbestendig ontwerp voor het veilig beheren van private API-sleutels (via environment variabelen) en een schaalbaar model voor een eventueel multi-user platform (gebruikersconfiguratie in een database).

### **Eerste "Interactor" Geïmplementeerd via TDD**

De fetch\_period command handler in de DataCommandService is volledig geïmplementeerd en gevalideerd met unit tests. De implementatie is robuust:

* Het werkt in beheersbare, dagelijkse chunks.  
* Het respecteert de centraal geconfigureerde veiligheidslimieten (max\_history\_days).

## **2\. Wat is de Volgende Stap?**

De volgende stap is om de resterende "placeholders" in onze service-raamwerken systematisch te implementeren, waarbij we voor elke methode de TDD-cyclus volgen.

### **Implementatie DataCommandService**

1. **synchronize()**: Schrijf een test die valideert dat alleen data *na* de laatste bekende timestamp wordt opgehaald. Implementeer vervolgens de logica.  
2. **extend\_history()**: Schrijf een test die valideert dat de methode de *oudste* bekende datum vindt en vanaf daar terugwerkt. Implementeer de logica.  
3. **fill\_gaps()**: Schrijf een test die, met behulp van get\_coverage, een "datakaart" met een gat simuleert en valideert dat de service alleen het ontbrekende blok ophaalt. Implementeer de logica.

### **Implementatie DataQueryService**

1. **get\_coverage()**: Schrijf een test die valideert dat de service de persistor.get\_data\_coverage() correct aanroept. Implementeer de "pass-through" logica.  
2. **get\_pairs()**: Schrijf een test die valideert dat de service de connector.get\_available\_pairs() aanroept. Implementeer de logica.  
3. **get\_range()**: Breid de IDataPersistor interface uit, schrijf de test, en implementeer de logica.

### **Implementatie ConnectorFactory**

* Bouw de ConnectorFactory die we hebben ontworpen, inclusief de "lazy loading" functionaliteit, om de services van de juiste connector-instanties te voorzien.

## **3\. De Definitieve Blauwdruk**

Deze tabel blijft onze gids voor de verdere ontwikkeling:

| Service | Verantwoordelijkheid | Publieke Methoden | Request DTO | Use Case |
| :---- | :---- | :---- | :---- | :---- |
| **DataCommandService** | **Interactoren (Commands)** | fetch\_period() | FetchPeriodCommand | I.A & I.B (Nieuw archief bouwen) |
|  |  | fill\_gaps() | FillGapsCommand | II.A (Gaten vullen) |
|  |  | extend\_history() | ExtendHistoryCommand | II.B (Archief uitbreiden) |
|  |  | synchronize() | SynchronizationCommand | III (Archief actueel houden) |
| **DataQueryService** | **Inquiries (Queries)** | get\_pairs() | PairsQuery | Voorbereiding (Paren selecteren) |
|  |  | get\_coverage() | CoverageQuery | Voorbereiding (Data-staat tonen) |
|  |  | get\_range() | RangeQuery | Trade Explorer (Detailanalyse) |

