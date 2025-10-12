# **4\. De Anatomie van een Plugin**

Versie: 2.2 (Details Hersteld & Aangevuld)  
Status: Definitief  
Dit document beschrijft de gedetailleerde structuur en de technische keuzes achter de plugins in de S1mpleTrader V2 architectuur. Plugins zijn de specialistische, onafhankelijke en testbare bouwstenen van elke Operation.

## **4.1. Fundamentele Mappenstructuur**

Elke plugin is een opzichzelfstaande Python package. Deze structuur garandeert dat logica, contracten en metadata altijd bij elkaar blijven, wat essentieel is voor het "Plugin First" principe.

plugins/\[plugin\_naam\]/  
├── manifest.yaml         \# De ID-kaart (wie ben ik?)  
├── worker.py             \# De Logica (wat doe ik?)  
├── schema.py             \# Het Contract (wat heb ik nodig?)  
├── context\_schema.py     \# Het visuele contract (wat kan ik laten zien?)  
└── test/test\_worker.py   \# De Kwaliteitscontrole (werk ik correct?)

* **manifest.yaml**: De "ID-kaart" van de plugin. Dit bestand maakt de plugin vindbaar en begrijpelijk voor het Assembly Team.  
* **worker.py**: Bevat de Python-klasse met de daadwerkelijke businesslogica van de plugin.  
* **schema.py**: Bevat het Pydantic-model dat de structuur en validatieregels voor de configuratieparameters (params) van de plugin definieert.  
* **context\_schema.py**: Bevat het concrete context model voor de visualisatie van gegevens die de plugin produceert. Dit is cruciaal voor de "Trade Explorer" in de frontend.  
* **test/test\_worker.py**: Dit bestand bevat de verplichte unit tests voor het valideren van de werking van de plugin. Een 100% score als uitkomst van pytest is noodzakelijk voor de succesvolle "enrollment" van een nieuwe plugin.

## **4.2. Formaat Keuzes: YAML vs. JSON**

De keuze voor een dataformaat hangt af van de primaire gebruiker: **een mens of een machine**. We hanteren daarom een hybride model om zowel leesbaarheid als betrouwbaarheid te maximaliseren.

* **YAML voor Menselijke Configuratie**  
  * **Toepassing:** manifest.yaml en alle door de gebruiker geschreven strategy\_blueprint.yaml en operation.yaml-bestanden.  
  * **Waarom:** De superieure leesbaarheid, de mogelijkheid om commentaar toe te voegen, en de flexibelere syntax zijn essentieel voor ontwikkelaars en strategen die deze bestanden handmatig schrijven en onderhouden.  
* **JSON voor Machine-Data**  
  * **Toepassing:** Alle machine-gegenereerde data, zoals API-responses, state-bestanden, en gestructureerde logs.  
  * **Waarom:** De strikte syntax en universele portabiliteit maken JSON de betrouwbare standaard voor communicatie tussen systemen en voor het opslaan van gestructureerde data waar absolute betrouwbaarheid vereist is.

## **4.3. Het Manifest: De Zelfbeschrijvende ID-kaart**

Het manifest.yaml is de kern van het "plugin discovery" mechanisme. Het stelt het Assembly Team in staat om een plugin volledig te begrijpen **zonder de Python-code te hoeven inspecteren**. Dit manifest is een strikt contract dat alle cruciale metadata van een plugin vastlegt.

### **4.3.1. Identification**

De identification-sectie bevat alle beschrijvende metadata.

* **name**: De unieke, machine-leesbare naam (bv. market\_structure\_detector).  
* **display\_name**: De naam zoals deze in de UI wordt getoond.  
* **type**: De **cruciale** categorie die bepaalt tot welke van de vier functionele pijlers de plugin behoort. Toegestane waarden zijn:  
  * context\_worker  
  * analysis\_worker  
  * monitor\_worker  
  * execution\_worker  
* **version**: De semantische versie van de plugin (bv. 1.0.1).  
* **description**: Een korte, duidelijke beschrijving van de functionaliteit.  
* **author**: De naam van de ontwikkelaar.

### **4.3.2. Dependencies (Het Data Contract)**

De dependencies-sectie is het formele contract dat definieert welke data een plugin nodig heeft om te functioneren en wat het produceert. Dit is de kern van de "context-bewuste" UI en validatie.

* **requires (Verplichte DataFrame Kolommen)**: Een lijst van datakolommen die een ContextWorker als **harde eis** verwacht in de DataFrame (bv. \['high', 'low', 'close'\]). Het Assembly Team controleert of aan deze vereisten wordt voldaan.  
* **provides (Geproduceerde DataFrame Kolommen)**: Een lijst van nieuwe datakolommen die een ContextWorker als **output** toevoegt aan de DataFrame (bv. \['is\_swing\_high'\]).  
* **requires\_context (Verplichte Rijke Data)**: Een lijst van **niet-DataFrame** data-objecten die de plugin als **harde eis** verwacht in de TradingContext. Als deze data niet beschikbaar is, zal de plugin in de UI **uitgeschakeld** zijn en zal de ComponentBuilder een fout genereren bij de bootstrap.  
  * *Voorbeeld*: \['orderbook\_snapshot'\].  
* **uses (Optionele Rijke Data)**: Een lijst van **niet-DataFrame** data-objecten die de plugin kan gebruiken voor een **verbeterde analyse**, maar die **niet verplicht** zijn. Als deze data niet beschikbaar is, zal de plugin in een "fallback-modus" werken.  
  * *Voorbeeld*: \['tick\_by\_tick\_volume'\].  
* **produces\_events (Gepubliceerde Events)**: **Specifiek voor MonitorWorker-plugins**. Dit is een lijst van de unieke event-namen die deze monitor kan publiceren op de EventBus. De EventWiringFactory valideert dit tegen de event\_map.yaml.

### **4.3.3. Permissions (Optioneel)**

De permissions-sectie fungeert als een beveiligingscontract. Standaard heeft een plugin geen toegang tot externe bronnen.

* **network\_access**: Een 'allowlist' van netwerkbestemmingen.  
* **filesystem\_access**: Een 'allowlist' van bestanden of mappen.

## **4.4. De Worker & het BaseWorker Raamwerk**

De worker.py bevat de daadwerkelijke logica. Om de ontwikkeling te versnellen en te standaardiseren, biedt de architectuur een set aan basisklassen (BaseWorker) in de backend.

* **Doel:** Het automatiseren van de complexe, geneste DTO-creatie die veel voorkomt in de AnalysisWorker-pijplijn en het consistent doorgeven van de correlation\_id.  
* **Voorbeeld (BaseEntryPlanner binnen de AnalysisWorker-pijplijn):**

Een ontwikkelaar die een EntryPlanner-plugin schrijft, hoeft niet zelf de volledige EntrySignal DTO te construeren. Hij kan erven van een BaseEntryPlanner.

\# Voorbeeld van een simpele Entry Planner plugin  
class MySimpleEntryPlanner(BaseEntryPlanner):  
    def \_process(self, input\_dto: Signal, correlation\_id: UUID, context: TradingContext) \-\> Optional\[Dict\[str, Any\]\]:  
        \# De ontwikkelaar focust zich puur op de kernlogica:  
        \# het berekenen van de entry-prijs.  
        entry\_price \= context.get\_last\_price('close') \* 0.99  
          
        \# Hij retourneert alleen de \*nieuwe\* data.  
        return {"entry\_price": entry\_price}

De BaseEntryPlanner-klasse handelt op de achtergrond automatisch de creatie van de EntrySignal DTO af, nest de oorspronkelijke Signal erin, en zorgt dat de correlation\_id correct wordt doorgegeven. Dit maakt de plugin-code extreem schoon, gefocust en minder foutgevoelig.