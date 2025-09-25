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
    * **Principe:** Alle user-facing strings (labels in de UI, rapportages, log-berichten voor de gebruiker) moeten via een internationalisatie-laag lopen, niet hardcoded in de code staan.
    * **Implementatie:** Een centrale `Translator`-klasse laadt `YAML`-bestanden uit de `/locales` map. Code gebruikt vertaalsleutels (bv. `log.backtest.complete`).
    * **Interactie met Logger:** De `Translator` wordt één keer geïnitialiseerd en geïnjecteerd in de `LogFormatter`. De formatter is de enige component binnen het logsysteem die sleutels vertaalt naar leesbare berichten. Componenten die direct output genereren (zoals `Presenters`) krijgen de `Translator` ook apart geïnjecteerd.

* **Configuratie Formaat:** `YAML` is de standaard voor alle door mensen geschreven configuratie. `JSON` wordt gebruikt voor machine-naar-machine data-uitwisseling.
