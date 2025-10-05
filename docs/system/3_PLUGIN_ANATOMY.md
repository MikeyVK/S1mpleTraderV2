# 3. De Anatomie van een V2 Plugin

Dit document beschrijft de gedetailleerde structuur en de technische keuzes achter de plugins in de S1mpleTrader V2 architectuur. Plugins zijn de specialistische, onafhankelijke en testbare bouwstenen van elke strategie.

---
## 3.1. Fundamentele Mappenstructuur

Elke plugin is een opzichzelfstaande Python package. Deze structuur garandeert dat logica, contracten en metadata altijd bij elkaar blijven, wat essentieel is voor het "Plugin First" principe.

Een typische plugin heeft de volgende structuur:

plugins/[plugin_naam]/
├── manifest.yaml         # De ID-kaart (wie ben ik?)
├── worker.py             # De Logica (wat doe ik?)
├── schema.py             # Het Contract (wat heb ik nodig?)
├── context_schema.py     # Het visuele context contract (wat kan ik laten zien?)
└── test/test_worker      # Unit test voor de plugin


* `manifest.yaml`: De "ID-kaart" van de plugin. Dit bestand maakt de plugin vindbaar en begrijpelijk voor de `PluginRegistry`.
* `worker.py`: Bevat de Python-klasse met de daadwerkelijke businesslogica van de plugin.
* `schema.py`: Bevat het Pydantic-model dat de structuur en validatieregels voor de configuratieparameters van de plugin definieert.
* `context_schema.py: Bevat het concrete context model voor de visualisatie van gegevens die de plugin produceert. Het maakt gebruik van de (visualisatie) modellen die het platform beschikbaar stelt in visualization_schema.py.
* `test/test_worker.py`: Dit bestand bevat de unit tests voor het valideren van de werking van de plugin. Het is een verplicht onderdeel dat de ontwikkelaar zal moeten schrijven en wordt gebruikt bij de enrollment van de plugin. Een 100% score als uitkomst van pytest is noodzakelijk als onderdeel van de succesvolle enrollment van een nieuwe plugin.

---
## 3.2. Formaat Keuzes: `YAML` vs. `JSON`

De keuze voor een dataformaat hangt af van de primaire gebruiker: **een mens of een machine**. We hanteren daarom een hybride model om zowel leesbaarheid als betrouwbaarheid te maximaliseren.

* **`YAML` voor Menselijke Configuratie**
    * **Toepassing:** `plugin_manifest.yaml` en alle door de gebruiker geschreven `run_config.yaml`-bestanden.
    * **Waarom:** De superieure leesbaarheid, de mogelijkheid om commentaar toe te voegen, en de flexibelere syntax zijn essentieel voor ontwikkelaars en strategen die deze bestanden handmatig schrijven en onderhouden.

* **`JSON` voor Machine-Data**
    * **Toepassing:** Alle machine-gegenereerde data, zoals API-responses, `state.json`-bestanden, en gestructureerde logs (`run.log.json`).
    * **Waarom:** De strikte syntax en universele portabiliteit maken `JSON` de betrouwbare standaard voor communicatie tussen systemen (bv. tussen de Python backend en een TypeScript frontend) en voor het opslaan van gestructureerde data waar absolute betrouwbaarheid vereist is.

---
## **3.3. Het manifest: de zelfbeschrijvende ID-kaart van de plugin**

Het plugin_manifest.yaml is de kern van het "plugin discovery" mechanisme. Het stelt het **Assembly Team** (specifiek de PluginRegistry) in staat om een plugin volledig te begrijpen, valideren en correct te categoriseren **zonder de Python-code te hoeven inspecteren**. Dit manifest is een strikt contract, afgedwongen door het PluginManifest Pydantic-model, dat alle cruciale metadata van een plugin vastlegt.

### **Core Identity**

De **core_identity**-sectie definieert de technische identiteit en versie van het manifest-schema zelf. Deze velden zorgen ervoor dat het systeem het bestand correct kan interpreteren en toekomstige wijzigingen in de manifest-structuur kan beheren.

* **apiVersion**: Identificeert de schemaversie van het manifest. Dit heeft een vaste waarde zoals s1mpletrader.io/v1 om aan te geven welke versie van de specificatie wordt gevolgd.  
* **kind**: Specificeert dat dit bestand een PluginManifest is, wat het type van het document definieert.

### **Identification**

De **identification**-sectie bevat alle beschrijvende metadata die de plugin identificeert voor zowel het systeem als de gebruiker.

* **name**: De unieke, machine-leesbare naam van de plugin (bv. market_structure_detector).  
* **display_name**: De naam zoals deze in de gebruikersinterface wordt getoond (bv. Market Structure Detector).  
* **type**: De belangrijkste categorie die bepaalt in welke van de negen workflow-fasen de plugin thuishoort (bv. structural_context).  
* **version**: De semantische versie van de plugin (bv. 1.0.1), wat essentieel is voor dependency management.  
* **description**: Een korte, duidelijke beschrijving van de functionaliteit van de plugin.  
* **author**: De naam van de ontwikkelaar of het team achter de plugin.

### **Dependencies**

De **dependencies**-sectie definieert het dat-contract van de plugin, met name voor dataverrijkingsplugins (ContextWorker).

* **requires**: Een lijst van datakolommen die de plugin als **input** verwacht (bv. ['high', 'low', 'close']). De DependencyValidator controleert of aan deze vereisten wordt voldaan door voorgaande plugins.  
* **provides**: Een lijst van nieuwe datakolommen die de plugin als **output** toevoegt aan de data (bv. ['is_swing_high']).

### **Permissions**

De **permissions**-sectie fungeert als een beveiligingscontract dat expliciet aangeeft welke potentieel risicovolle operaties de plugin nodig heeft. Standaard heeft een plugin geen toegang tot externe bronnen.

* **network_access**: Een 'allowlist' van netwerkbestemmingen die de plugin mag benaderen (bv. ['https://api.kraken.com']).  
* **filesystem_access**: Een 'allowlist' van bestanden of mappen waartoe de plugin toegang heeft.

---
## 3.4. De Worker & het BaseWorker Raamwerk

De `worker.py` bevat de daadwerkelijke logica. Om de ontwikkeling te versnellen en de consistentie te borgen, biedt de architectuur een set aan basisklassen in `backend/core/base_worker.py`.

* **Doel:** Het automatiseren van de complexe, geneste DTO-creatie en het doorgeven van de `correlation_id`.
* **Voorbeeld (`BaseEntryPlanner`):**
    ```python
    class MyEntryPlanner(BaseEntryPlanner):
        def _process(self, input_dto: Signal, correlation_id: UUID, context: TradingContext) -> Optional[Dict[str, Any]]:
            # Developer focust alleen op de logica
            entry_price = ... # bereken de entry prijs
            return {"entry_price": entry_price}
    ```
De `BaseEntryPlanner` handelt automatisch de creatie van de `EntrySignal` DTO af, nest de oorspronkelijke `Signal` erin, en zorgt dat de `correlation_id` correct wordt doorgegeven. Dit maakt de plugin-code extreem schoon en gefocust.