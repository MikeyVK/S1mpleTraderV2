# 9. Coding Standaarden

**Versie:** 2.0 · **Status:** Definitief

Dit document beschrijft de verplichte standaarden en best practices voor het schrijven van alle code binnen het S1mpleTrader V2 project. Het doel is een consistente, leesbare, onderhoudbare en robuuste codebase. Het naleven van deze standaarden is niet optioneel.

---
## 9.1. Code Kwaliteit & Stijl

### **9.1.1. Fundamenten**
* **PEP 8 Compliant:** Alle Python-code moet strikt voldoen aan de [PEP 8](https://peps.python.org/pep-0008/) stijlgids. Een linter wordt gebruikt om dit te handhaven.
    * **Regellengte:** Maximaal 100 tekens.
    * **Naamgeving:** `snake_case` voor variabelen, functies en modules; `PascalCase` voor klassen.
* **Volledige Type Hinting:** Alle functies, methodes, en variabelen moeten volledig en correct getypeerd zijn. We streven naar een 100% getypeerde codebase om runtime-fouten te minimaliseren.
* **Commentaar in het Engels:** Al het commentaar in de code (`# ...`) en docstrings moeten in het Engels zijn voor universele leesbaarheid en onderhoudbaarheid.

### **9.1.2. Gestructureerde Docstrings**
Elk bestand, elke klasse en elke functie moet een duidelijke docstring hebben.

* **Bestands-Header Docstring:** Elk `.py`-bestand begint met een gestandaardiseerde header die de inhoud en de plaats in de architectuur beschrijft.
    ```python
    # backend/assembly/plugin_registry.py
    """
    Contains the PluginRegistry, responsible for discovering and validating all
    available plugins within the ecosystem.

    @layer: Backend (Assembly)
    @dependencies: [PyYAML, Pydantic]
    @responsibilities:
        - Scans plugin directories for manifests.
        - Validates manifest schemas.
        - Builds and maintains the central plugin registry.
    """
    ```
* **Functie & Methode Docstrings (Google Style):** Voor alle functies en methodes hanteren we de **Google Style Python Docstrings**. Dit is een leesbare en gestructureerde manier om parameters, return-waarden en voorbeelden te documenteren.
    ```python
    def process_data(df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
        """Calculates an indicator and adds it as a new column.

        Args:
            df (pd.DataFrame): The input DataFrame with OHLCV data.
            length (int, optional): The lookback period for the indicator.
                Defaults to 14.

        Returns:
            pd.DataFrame: The DataFrame with the new indicator column added.
        """
        # ... function logic ...
        return df
    ```

### **9.1.3. Naamgevingsconventies**
Naast de algemene [PEP 8]-richtlijnen hanteren we een aantal strikte, aanvullende conventies om de leesbaarheid en de architectonische zuiverheid van de code te vergroten.

* **Interfaces (Contracten):**

  * **Principe:** Elke abstracte klasse (`ABC`) of Protocol die een contract definieert, moet worden voorafgegaan door een hoofdletter `I`.

  * **Doel:** Dit maakt een onmiddellijk en ondubbelzinnig onderscheid tussen een abstract contract en een concrete implementatie. Het dwingt het "Dependency Inversion Principle" af door voor ontwikkelaars visueel te maken wanneer ze tegen een abstractie programmeren.

  * **Voorbeeld:**

        ```Python
        # Het contract (de abstractie)
        class IAPIConnector(Protocol):
            ...

        # De concrete implementatie
        class KrakenAPIConnector(IAPIConnector):
            ...
        ```

* **Klassen, Functies en Variabelen:**

  * **We volgen strikt de [PEP 8]-standaard:**

   `PascalCase` voor alle klassen (bv. `StrategyOperator`, `DataPersistor`).

   `snake_case` voor alle functies, methodes, variabelen en modules (bv. `get_historical_trades`, `_prepare_components`).

* **Interne Attributen en Methodes:**

  * **Principe:** Attributen of methodes die niet bedoeld zijn voor gebruik buiten de klasse (beschouwd als "private" of "protected"), moeten worden voorafgegaan door een enkele underscore (_).

  * **Doel:** Dit communiceert duidelijk de publieke API van een klasse en helpt onbedoelde afhankelijkheden van interne implementatiedetails te voorkomen.

  * **Voorbeeld:**

        ```Python
        class StrategyOperator:
            def __init__(self):
                self._app_config = ... # Intern, wordt niet van buitenaf benaderd

            def run(self): # Publieke methode
                self._prepare_components() # Interne hulpmethode

            def _prepare_components(self):
                ...
        ```
---
## 9.2. Contract-Gedreven Ontwikkeling

### **9.2.1. Pydantic voor alle Data-Structuren**
* **Principe:** Alle data die tussen componenten wordt doorgegeven, moet worden ingekapseld in een **Pydantic `BaseModel`**. Dit geldt voor DTO's, configuraties en plugin-parameters.
* **Voordeel:** Dit garandeert dat data van het juiste type en de juiste structuur is *voordat* het wordt verwerkt.

### **9.2.2. Abstracte Basisklassen (Interfaces)**
* **Principe:** Componenten die uitwisselbaar moeten zijn (zoals plugins), moeten erven van een gemeenschappelijke abstracte basisklasse (ABC) die een consistent contract afdwingt.

---
## 9.3. Gelaagde Logging & Traceability

### **9.3.1. Drie Lagen van Logging**
1.  **Laag 1: `stdio` (Console via `print()`):** Uitsluitend voor snelle, lokale, vluchtige debugging. Mag nooit gecommit worden.
2.  **Laag 2: Gestructureerde `JSON`-logs:** De standaard output voor alle runs, bedoeld voor analyse.
3.  **Laag 3: De Web UI (Log Explorer):** De primaire interface voor het analyseren en debuggen van runs.

### **9.3.2. Traceability via `Correlation ID`**
* **Principe:** Elk `Signal` DTO krijgt een unieke `UUID`. Elke volgende plugin die dit signaal verwerkt, neemt deze `correlation_id` over in zijn log-berichten. Dit maakt de volledige levenscyclus van een trade traceerbaar.

---
## 9.4. Testen als Voorwaarde

* **Principe:** Code zonder tests wordt beschouwd als onvolledig.
* **Implementatie:** Elke plugin is **verplicht** om een `tests/test_worker.py`-bestand te bevatten. Continue Integratie (CI) voert alle tests automatisch uit na elke `push`.

---
## 9.5. Overige Standaarden

* **Internationalisatie (i18n):**
    * **Principe:** *Alle* tekst die direct of indirect aan een gebruiker kan worden getoond, moet via de internationalisatie-laag lopen. Hardgecodeerde, gebruikersgerichte strings in de Python-code zijn niet toegestaan.
    * **Implementatie:** Een centrale `Translator`-klasse laadt `YAML`-bestanden uit de `/locales` map. Code gebruikt vertaalsleutels in "dot-notation" (bv. `log.backtest.complete`).
    * **Scope van de Regel:** Deze regel is van toepassing op, maar niet beperkt tot, de volgende onderdelen:
      1. * **Log Berichten:** Alle log-berichten die bedoeld zijn om de gebruiker te informeren over de voortgang of status van de applicatie (voornamelijk [INFO]-niveau en hoger). Foutmeldingen voor ontwikkelaars ([DEBUG]-niveau) mogen wel hardcoded zijn.
        **Correct:** `logger.info('run.starting', pair=pair_name)`
        **Incorrect:** `logger.info(f'Starting run for {pair_name}...')`
      2. * **ConfigPydantic Veldbeschrijvingen:** Alle `description` velden binnen Pydantic-modellen (DTO's, configuratie-schema's). Deze beschrijvingen kunnen direct in de UI of in documentatie worden getoond.
        **Correct:** `equity: float = Field(..., description="portfolio_state.equity.desc")`
        **Incorrect:** `equity: float = Field(..., description="The total current value...")`
      3. * **Plugin Manifesten:** Alle beschrijvende velden in een plugin_manifest.yaml, zoals description en display_name. De PluginQueryService moet deze velden door de Translator halen voordat ze naar de frontend worden gestuurd.
    * **Interactie met Logger:** De `Translator` wordt één keer geïnitialiseerd en geïnjecteerd in de `LogFormatter`. De formatter is de enige component binnen het logsysteem die sleutels vertaalt naar leesbare berichten. Componenten die direct output genereren (zoals UI `Presenters`) krijgen de `Translator` ook apart geïnjecteerd.

### **9.5.1. Structuur van i18n Dotted Labels**
Om de `locales/*.yaml` bestanden georganiseerd en onderhoudbaar te houden, hanteren we een strikte, hiërarchische structuur voor alle vertaalsleutels. De structuur volgt over het algemeen het pad van de component of het datamodel waar de tekst wordt gebruikt.

  * **Principe:** component_of_laag.specifieke_context.naam_van_de_tekst

  **Voorbeelden van de Structuur:**
    1. **Log Berichten:**
    De sleutel begint met de naam van de module of de belangrijkste klasse waarin de log wordt aangeroepen.

    **Structuur:** component_name.actie_of_gebeurtenis

    **Voorbeelden:**

    ```YAML
    # Voor backend/assembly/plugin_registry.py
    plugin_registry:
    scan_start: "Scanning for plugins in '{path}'..."
    scan_complete: "Scan complete. Found {count} valid plugins."

    # Voor services/strategy_operator.py
    strategy_operator:
    run_start: "StrategyOperator run starting..."
    critical_event: "Critical event detected: {event_type}"
    Pydantic Veldbeschrijvingen (description):

    De sleutel weerspiegelt het pad naar het veld binnen het DTO of schema. De sleutel eindigt altijd op .desc om aan te geven dat het een beschrijving is.
    ```  

    **Structuur:** schema_naam.veld_naam.desc

    **Voorbeelden:**

    ```YAML
    # Voor backend/dtos/portfolio_state.py
    portfolio_state:
    equity:
        desc: "The total current value of the portfolio."
    available_cash:
        desc: "The amount of cash available for new positions."

    # Voor een plugin's schema.py
    ema_detector_params:
    period:
        desc: "The lookback period for the EMA calculation."
    Plugin Manifesten (plugin_manifest.yaml):

    Voor de beschrijvende velden van een plugin gebruiken we een structuur die de plugin uniek identificeert.
    ```

    **Structuur:** plugins.plugin_naam.veld_naam

    **Voorbeelden:**

    ```YAML
    plugins:
    ema_detector:
        display_name: "EMA Detector"
        description: "Calculates and adds an Exponential Moving Average."
    fvg_entry_detector:
        display_name: "FVG Entry Detector"
        description: "Detects a Fair Value Gap after a Market Structure Shift."

    * **Configuratie Formaat:** `YAML` is de standaard voor alle door mensen geschreven configuratie. `JSON` wordt gebruikt voor machine-naar-machine data-uitwisseling.
    ```

---
## 9.6. Design Principles & Kernconcepten

De architectuur is gebouwd op de **SOLID**-principes en een aantal kern-ontwerppatronen die de vier kernprincipes (Plugin First, Scheiding van Zorgen, Configuratie-gedreven, Contract-gedreven) tot leven brengen.

### **De Synergie: Configuratie- & Contract-gedreven Executie**

Het meest krachtige concept van V2 is de combinatie van configuratie- en contract-gedreven werken. De code is de motor; **de configuratie is de bestuurder, en de contracten zijn de verkeersregels die zorgen dat de bestuurder binnen de lijntjes blijft.**

* **Configuratie-gedreven:** De *volledige samenstelling* van een strategie (welke plugins, in welke volgorde, met welke parameters) wordt gedefinieerd in een `YAML`-bestand. Dit maakt het mogelijk om strategieën drastisch te wijzigen zonder één regel code aan te passen.

* **Contract-gedreven:** Elk stukje configuratie en data wordt gevalideerd door een strikt **Pydantic-schema**. Dit werkt op twee niveaus:
  1.  **Algemene Schema's:** De hoofdstructuur van een `run_blueprint.yaml` wordt gevalideerd door een algemeen `app_schema.py`. Dit contract dwingt af dat er bijvoorbeeld altijd een `environment` en een `strategy_pipeline` sectie aanwezig is.
  2.  **Plugin-Specifieke Schema's:** De parameters voor een specifieke plugin (bv. de `length` van een `EMA`-indicator) worden gevalideerd door de Pydantic-klasse in de `schema.py` van *die ene plugin*.

Bij het starten van een run, leest de applicatie het `YAML`-bestand en bouwt een gevalideerd `AppConfig`-object. Als een parameter ontbreekt, een verkeerd type heeft, of een plugin wordt aangeroepen die niet bestaat, faalt de applicatie *onmiddellijk* met een duidelijke foutmelding. Dit voorkomt onvoorspelbare runtime-fouten en maakt het systeem extreem robuust en voorspelbaar.

### **SOLID in de Praktijk**
* **SRP (Single Responsibility Principle):** Elke klasse heeft één duidelijke taak.
  * ***V2 voorbeeld:*** Een `FVGEntryDetector`-plugin detecteert alleen Fair Value Gaps. Het bepalen van de positiegrootte of het analyseren van de marktstructuur gebeurt in aparte `position_sizer`- of context-plugins.

* **OCP (Open/Closed Principle):** Uitbreidbaar zonder bestaande code te wijzigen.
    * ***V2 voorbeeld:*** Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe `exit_planner`-plugin; de `StrategyEngine` hoeft hiervoor niet aangepast te worden.

* **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.
    * ***V2 voorbeeld:*** De `BacktestService` (Service-laag) hangt af van de `BaseEnvironment`-interface, niet van de specifieke `BacktestEnvironment`. Hierdoor zijn de services volledig herbruikbaar in elke context.

### **Kernpatronen**
* **Factory Pattern:** Het `Assembly Team` (met `WorkerBuilder`) centraliseert het ontdekken, valideren en creëren van alle plugins.
* **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.
* **DTO’s (Data Transfer Objects):** Pydantic-modellen (`Signal`, `TradePlan`, `ClosedTrade`) zorgen voor een voorspelbare en type-veilige dataflow tussen alle componenten.