# 3. De Anatomie van een V2 Plugin

Dit document beschrijft de gedetailleerde structuur en de technische keuzes achter de plugins in de S1mpleTrader V2 architectuur. Plugins zijn de specialistische, onafhankelijke en testbare bouwstenen van elke strategie.

---
## 3.1. Fundamentele Mappenstructuur

Elke plugin is een opzichzelfstaande Python package. Deze structuur garandeert dat logica, contracten en metadata altijd bij elkaar blijven, wat essentieel is voor het "Plugin First" principe.

Een typische plugin heeft de volgende structuur:

plugins/[plugin_naam]/
├── plugin_manifest.yaml  # De ID-kaart (wie ben ik?)
├── worker.py             # De Logica (wat doe ik?)
├── schema.py             # Het Contract (wat heb ik nodig?)
└── state.json            # (Optioneel) Het Geheugen (wat was mijn vorige staat?)


* `plugin_manifest.yaml`: De "ID-kaart" van de plugin. Dit bestand maakt de plugin vindbaar en begrijpelijk voor de `AbstractPluginFactory`.
* `worker.py`: Bevat de Python-klasse met de daadwerkelijke businesslogica van de plugin.
* `schema.py`: Bevat het Pydantic-model dat de structuur en validatieregels voor de configuratieparameters van de plugin definieert.
* `state.json`: Dit bestand is **optioneel** en wordt alleen gebruikt door 'stateful' plugins (zoals een Grid Trading manager die zijn openstaande orders moet onthouden). De `StrategyOrchestrator` is verantwoordelijk voor het aanroepen van `load_state()` en `save_state()` op de worker, maar de worker zelf beheert de inhoud van dit bestand.

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
## 3.3. Het Manifest: De Zelfbeschrijvende ID-kaart

Het `plugin_manifest.yaml` is de kern van het "plugin discovery" mechanisme. Het stelt de `AbstractPluginFactory` in staat om een plugin volledig te begrijpen, te valideren en correct te categoriseren **zonder de Python-code te hoeven inspecteren**.

Dit manifest is een contract dat de volgende cruciale informatie vastlegt:

* **`name`**: De unieke, machine-leesbare naam van de plugin (bv. `market_structure_detector`).
* **`version`**: Semantische versie (bv. "1.0.1") om dependency management mogelijk te maken.
* **`type`**: De belangrijkste categorie-aanduiding. Dit veld bepaalt in welke van de 6 fasen van de `StrategyOrchestrator` de plugin thuishoort. Mogelijke waarden zijn:
    * `regime_filter`
    * `structural_context`
    * `signal_generator`
    * `signal_refiner`
    * `trade_constructor`
    * `portfolio_overlay`
* **`entry_class`**: De exacte naam van de hoofdklasse in het `worker.py` bestand (bv. `MarketStructureDetector`).
* **`schema_path`**: Het pad naar het Python-bestand dat het Pydantic-schema bevat (meestal `schema.py`).
* **`params_class`**: De exacte naam van de Pydantic-klasse in het `schema.py` bestand (bv. `MarketStructureParams`).
* **`stateful`**: Een boolean (`true` / `false`) die aangeeft of de plugin een `state.json`-bestand gebruikt.
* **`dependencies`**: Een lijst van datavelden die de plugin verwacht als input. Voor een `ContextWorker` is dit een lijst van kolomnamen (bv. `['high', 'low', 'close']`) die aanwezig moeten zijn in de DataFrame. De `AbstractPluginFactory` valideert hierop voordat de plugin wordt uitgevoerd.
