# 2. S1mpleTrader Code Standaarden

Dit document beschrijft de standaarden en best practices voor het schrijven van code in het S1mpleTrader-project. Het naleven van deze standaarden is verplicht om de codebase consistent, leesbaar en onderhoudbaar te houden.

## 2.1. Code Kwaliteit en Stijl

### **PEP 8 & Linting**
Alle Python-code moet voldoen aan de [PEP 8](https://peps.python.org/pep-0008/) stijlgids. We gebruiken `pylint` om dit te bewaken. De volgende regels verdienen speciale aandacht:
* **Regellengte:** De absolute maximale lengte van een regel is **100 tekens**.
* **Trailing Whitespace:** Regels mogen nooit eindigen met witruimte.
* **Newline aan Einde Bestand:** Elk `.py` bestand moet eindigen met exact één lege, nieuwe regel.

### **Type Hinting**
Alle functies, methodes en variabelen moeten voorzien zijn van type hints. We streven naar een 100% getypeerde codebase.

### **Commentaar en Leesbaarheid**
* **Zelfdocumenterende Code:** Streef er altijd naar om code te schrijven die zo duidelijk is dat het geen commentaar nodig heeft. Gebruik heldere namen voor variabelen en functies.
* **Commentaar in het Engels:** Als een stuk logica complex of niet-evident is, voeg dan commentaar toe om het te verduidelijken. Al het commentaar in de code (`# dit is commentaar`) moet **in het Engels** geschreven worden.

## 2.2. Gestructureerde Docstrings

Elk Python-bestand, elke klasse en elke publieke methode moet voorzien zijn van gestructureerde documentatie. De documentatie volgt een hiërarchie van bestand -> klasse -> methode.

### **Bestand Header Documentatie**
Aan het begin van **elk `.py` bestand** staat een header die de locatie en de rol van het bestand in de applicatie beschrijft. Deze header bestaat uit twee delen:

1.  **Een commentaarregel** met het volledige pad vanaf de project-root.
2.  **Een multi-line docstring** die het doel van het bestand en alle relevante metadata-tags bevat.

**Standaard Header Tags:**
* **Beschrijving:** Een korte, duidelijke omschrijving van het doel van het bestand.
* **`@layer`**: De architectuurlaag of functionele groepering (bv. `Backend`, `Service`, `Configuration`).
* **`@dependencies`**: De belangrijkste externe libraries of interne modules waarvan dit bestand afhankelijk is.
* **`@responsibilities`**: Een lijst van de hoofdtaken van de component(en) in dit bestand.
* **`@inputs`**: De primaire data die het bestand of de hoofdcomponent als input verwacht.
* **`@outputs`**: De primaire data die het bestand of de hoofdcomponent produceert.

**Voorbeeld (Bestand Header):**
```python
# backend/config/loader.py
"""
Contains the ConfigLoader, responsible for loading, merging, and validating
configuration files based on a 3-layer system (run, mode, override).

@layer: Configuration
@dependencies:
    - pydantic: Used to validate the final merged data.
    - yaml: Used to parse the YAML configuration files.
    - backend.config.schemas: Imports the Pydantic models.
@responsibilities:
    - Acts as a pure assembler of configuration layers.
    - Performs a 'deep merge' of dictionaries.
    - Validates the final, assembled configuration against Pydantic schemas.
@inputs:
    - Names for the run, mode, and override configurations.
@outputs:
    - A single, validated `AppConfig` object, or `None` on failure.
"""
```

### **Klasse en Methode Docstrings**
Omdat de belangrijkste metadata al in de file header staat, kunnen de docstrings voor klassen en methodes beknopter zijn en zich richten op hun specifieke taak.

**Voorbeeld (Klasse):**
```python
class ConfigLoader:
    """A pure assembler of configuration layers that validates the result."""
```

**Voorbeeld (Methode):**
```python
    def load_and_validate(self, run_name: str) -> AppConfig | None:
        """
        Loads, merges, and validates a set of configuration files.

        @inputs:
            run_name (str): The name of the base run configuration.
        @outputs:
            (AppConfig | None): A validated config object or None on failure.
        """
        # ... method implementation ...
```

## 2.3. Logging

Logging is de primaire manier om de werking van de applicatie te volgen.
* **LogEnricher:** Gebruik altijd de `LogEnricher` wrapper in plaats van de standaard `logging.getLogger()`.
* **Geen Print Statements:** `print()`-statements zijn verboden in de `Backend` en `Service` lagen.
* **Vertaalsleutels:** Logberichten die voor de gebruiker bedoeld zijn, moeten vertaalsleutels gebruiken.

## 2.4. Internationalisatie (i18n)

Alle tekst die aan de gebruiker wordt getoond, moet vertaalbaar zijn.
* **Key-Based Systeem:** Hardcodeer nooit tekst. Gebruik altijd vertaalsleutels (bv. `main_menu.welcome_message`).
* **Centrale Translator:** De `Translator`-klasse is de enige component die sleutels naar tekst omzet.