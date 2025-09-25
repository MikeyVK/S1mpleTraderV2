# 3. S1mpleTrader Systeemconfiguratie

Dit document beschrijft de structuur en filosofie achter de configuratiebestanden en validatie-schema's van S1mpleTrader. Het systeem is bewust opgedeeld in drie functioneel gescheiden locaties, die elk een eigen, unieke verantwoordelijkheid hebben.

## 3.1. Overzicht van de Drie Locaties

De configuratie en validatie zijn verdeeld over de volgende drie mappen. Deze structuur zorgt voor een duidelijke scheiding tussen de "recepten" (blueprints), de "backend-grondwet" (backend-schemas) en de "API-contracten" (frontend-schemas).

```
S1mpleTrader/
├── config/
│   ├── runs/
│   ├── optimizations/
│   ├── variants/
│   ├── overrides/
│   ├── index.yaml
│   └── platform.yaml
│
├── backend/
│   └── config/
│       └── schemas/
│           ├── app_schema.py
│           ├── blueprint_schema.py
│           └── ...
│
└── frontends/
    └── web/
        └── api/
            └── schemas/  <-- Toekomstige locatie voor API-modellen
```

## 3.2. De Functie per Locatie

### **Locatie 1: `config/` (De Recepten)**
* **Functie:** Bevat alle `YAML`-bestanden die de parameters voor een specifieke applicatie-run definiëren. Dit is de input die de gebruiker aanlevert.
* **Inhoud:**
    * `runs/`: Complete basisstrategieën.
    * `optimizations/`: Definities voor parameter-optimalisaties.
    * `variants/`: Definities voor A/B- of variantentests.
    * `overrides/`: Kleine fragmenten om specifieke parameters van een basis-run aan te passen.
    * `platform.yaml`: Stabiele, globale instellingen die zelden veranderen.
    * `index.yaml`: Een register dat korte, gebruiksvriendelijke namen koppelt aan de volledige bestandspaden.

### **Locatie 2: `backend/config/schemas/` (De Backend Grondwet)**
* **Functie:** Bevat alle `Pydantic`-modellen die de structuur van de `YAML`-bestanden in `config/` valideren.
* **Inhoud:** Python-bestanden (`*_schema.py`) die de regels afdwingen voor de backend-engine. Ze garanderen dat de "recepten" van de gebruiker correct zijn voordat de engine ze uitvoert.

### **Locatie 3: `frontends/web/api/schemas/` (De API Contracten)**
* **Functie:** Bevat de `Pydantic`-modellen die de datastructuren voor de Web API definiëren.
* **Inhoud:** Python-bestanden (`*_schema.py`) die de "contracten" voor API-requests en responses vastleggen.

---

## 3.3. De `backtest_pipeline` in Detail

De `backtest_pipeline` sectie in een `run`-blueprint is het hart van het systeem en illustreert hoe de locaties samenwerken. Deze sectie stuurt de `BacktestPipelineFactory` aan en bestaat uit twee hoofdonderdelen: de `TASKBOARD` en de `WORKFORCE`.

### **`TASKBOARD` (Het "Wat")**
De `TASKBOARD` definieert **wat** er voor een specifieke run gebouwd moet worden. Het bevat een sleutel voor elke **taak** in de pipeline (bv. `pattern_detection`, `exit_planning`).
* Je hoeft hier alleen de "workers" (componenten) te specificeren die **afwijken** van de standaardinstelling. Als een taak niet wordt genoemd, gebruikt de factory de `default` die is vastgelegd in `platform.yaml`.

### **`WORKFORCE` (Het "Wie" en "Hoe")**
De `WORKFORCE` is de complete bibliotheek van alle beschikbare "workers" en de regels om ze te bouwen.

#### **`definitions` (De "CV's")**
* Dit is het belangrijkste onderdeel. Het bevat de definities van alle beschikbare workers, gegroepeerd per taak.
* De `ConfigLoader` verrijkt deze sectie automatisch door de `class_name` voor elke worker af te leiden uit de conventies in `platform.yaml`, voordat validatie plaatsvindt.
* In de `params` sectie van elke worker kan de gebruiker de standaardparameters overschrijven die in het Pydantic-model (`strategy_schema.py`) zijn gedefinieerd.

### **Voorbeeld**
```yaml
# In: config/runs/mss_base.yaml
backtest:
  TASKBOARD:
    pattern_detection: [mss_bull, mss_bear]
    match_filtering: [volume, adx]
    # exit_planning wordt niet genoemd, dus de default ('atr_exit') wordt geladen.

  WORKFORCE:
    definitions:
      pattern_detection:
        mss_bull:
          # class_name wordt automatisch ingevoegd door de loader
          params:
            peak_distance: 24
            prominence_pct: 0.005
            # ...andere params...
      exit_planning:
        atr_exit:
          params:
            atr_multiplier: 3.0
            rr_ratio: 4.0
```