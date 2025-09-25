# 1. S1mpleTrader Systeemarchitectuur

Dit document beschrijft de fundamentele architectuur, de kernprincipes en de leidende design patterns van de S1mpleTrader applicatie. Het is de blauwdruk voor alle ontwikkeling.

## 1.1. De Drie-Lagen Architectuur

De applicatie is opgebouwd uit drie strikt gescheiden lagen.

```
+-------------------------------------------------------------+
|   Frontend Laag (Gebruikersinterface)                       |
|   - CLI, Web API, etc.                                      |
+--------------------------+----------------------------------+
                           |
                           ▼ (Afhankelijkheid)
+--------------------------+----------------------------------+
|   Service Laag (Applicatie-API & Business Workflows)        |
+--------------------------+----------------------------------+
                           |
                           ▼ (Afhankelijkheid)
+--------------------------+----------------------------------+
|   Backend Laag (De Engine)                                  |
|   - Strategie, Portfolio, Data, etc.                        |
+-------------------------------------------------------------+
```

Deze structuur dwingt een **eenrichtingsverkeer** van afhankelijkheden af (`Frontend -> Service -> Backend`), wat de lagen ontkoppelt en de herbruikbaarheid van de `Backend` garandeert.

---

## 1.2. De Lagen en Hun Principes

### 1.2.1. Backend Laag (De Engine)

Dit is het hart van de applicatie. Het is ontworpen als een volledig onafhankelijke library.

* **Principes & Patterns:**
    * **Single Responsibility Principle (SRP):** Elke klasse heeft één specifieke taak (bv. `PatternDetector`, `MatchFilter`).
    * **Strategy Pattern:** Componenten zijn uitwisselbare "strategieën" die via configuratie worden gekozen (bv. meerdere `ExitPlanner` implementaties).
    * **Factory Pattern:** De `BacktestPipelineFactory` is verantwoordelijk voor het bouwen van de strategie-pipeline op basis van de configuratie.
    * **Facade Pattern:** `backend/__init__.py` dient als een schone, publieke API voor de `Service` laag, en verbergt de interne complexiteit.

### 1.2.2. Service Laag (De Publieke API)

Deze laag fungeert als de "lijm" en orkestreert de `Backend` componenten om complete business workflows uit te voeren.

* **Principes & Patterns:**
    * **Orkestratie:** Een service zoals `BacktestService` roept de `Backend` componenten in de juiste volgorde aan. Het bevat geen kern-businesslogica zelf.
    * **Dependency Injection (DI):** Services zoals `LogEnricher` en `Translator` worden hier geïnitialiseerd en doorgegeven (geïnjecteerd) aan de lagen die ze nodig hebben.

### 1.2.3. Frontend Laag (CLI)

De Command-Line Interface is een "dunne" laag die gebruikersinput vertaalt naar aanroepen van de `Service` laag.

* **Principes & Patterns:**
    * **Model-View-Controller (MVC) / Presenter:** De `_app.py` is de `Controller`, de `Service` is het `Model`, en de `Presenter` is de `View` die de output formatteert.

### **1.2.4. Frontend Laag (Web API met FastAPI)**

De Web API is de interface voor programmatische toegang tot de applicatie. Het volgt strikte patronen om de scheiding der lagen te handhaven.

* **Principe 1: De Router is een 'Verkeersregelaar', geen 'Fabriek'**
    * De code in een API router (`frontends/web/api/routers/`) moet **extreem dun** zijn. De enige verantwoordelijkheden zijn:
        1.  HTTP request data (pad, query parameters, body) ontvangen en valideren.
        2.  De juiste `Service`-methode aanroepen met de gevalideerde data.
        3.  Het resultaat van de `Service` teruggeven in een HTTP response.
    * **Anti-Pattern:** Een router-functie mag **nooit** zelf complexe logica bevatten of direct de `Backend` aanroepen.

* **Principe 2: Pydantic voor Alles (Contract First)**
    * Net zoals we Pydantic gebruiken voor de `YAML`-configuratie, gebruiken we het voor de API-laag.
    * **Request Models:** Definieer Pydantic-modellen voor de JSON-body van `POST`/`PUT` requests. FastAPI valideert de inkomende data hier automatisch tegen.
    * **Response Models:** Gebruik de `response_model` parameter in de decorator (`@router.get(...)`) om de structuur van de uitgaande data te garanderen. Dit zorgt voor een expliciet en gedocumenteerd "contract" en filtert per ongeluk gelekte data weg.

* **Principe 3: Gebruik FastAPI's Dependency Injection voor Services**
    * De `Service`-laag is een afhankelijkheid van de `API`-laag. We gebruiken FastAPI's ingebouwde DI-systeem om dit te beheren.
    * **Toepassing:** Creëer een "dependency" functie die een instance van een service (bv. `VisualizationService`) aanmaakt en `yield`. Deze functie kan dan worden meegegeven aan een `Depends()` in de router-functie. Dit zorgt ervoor dat de service per request wordt geïnstantieerd en ontkoppelt de router van de creatie-logica.

    ```python
    # In een dependency file, bv. frontends/web/api/dependencies.py
    def get_visualization_service() -> VisualizationService:
        # Hier wordt de service (en diens afhankelijkheden) opgebouwd
        yield VisualizationService(...)

    # In de router, bv. frontends/web/api/routers/charts.py
    @router.get("/charts/{chart_id}")
    def get_chart(
        chart_id: str,
        service: VisualizationService = Depends(get_visualization_service)
    ):
        chart_data = service.get_chart_by_id(chart_id)
        # ...
    ```

* **Principe 4: Gestructureerde Mappen**
    * `main.py`: De root van de FastAPI app, initialiseert de app en koppelt de routers.
    * `api/routers/`: Elk `.py` bestand hier is een `APIRouter` voor een specifieke resource (bv. `backtests.py`, `charts.py`).
    * `api/models/`: Bevat alle Pydantic-modellen voor requests en responses.
    * `api/dependencies.py`: Bevat de herbruikbare `Depends()` functies.

---

## 1.3. Gerelateerde Documentatie

* **Code Standaarden:** Voor de concrete regels over hoe we code schrijven, zie **`2_CODING_STANDARDS.md`**.
* **Configuratie:** Voor de werking van de YAML-configuratie, zie **`3_SYSTEM_CONFIG.md`**.
* **Workflows:** Voor de stap-voor-stap dataflow, zie **`../workflows/1_BACKTEST.md`**.