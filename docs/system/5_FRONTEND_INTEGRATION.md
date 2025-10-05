# 5. Frontend Integratie: De UI als Ontwikkelomgeving

Dit document beschrijft de volledige gebruikersworkflow en de frontend-architectuur die nodig is om de "supercharged" V2-ervaring te realiseren. Het is de directe vertaling van de User Story Map naar een concreet, technisch plan.

---
## 5.1. De Filosofie: De UI als IDE

De kern van de V2-frontendstrategie is een paradigmaverschuiving: de web-UI is niet langer een simpele presentatielaag, maar de **primaire, geïntegreerde ontwikkelomgeving (IDE)** voor de kwantitatieve strateeg. Elke stap in de workflow, van het bouwen van een strategie tot het diepgaand analyseren van de resultaten, vindt plaats binnen een naadloze, interactieve webapplicatie.

Dit maximaliseert de efficiëntie en verkort de **"Bouwen -> Meten -> Leren"**-cyclus van dagen of uren naar minuten.

---
## 5.2. De Werkruimtes: Van User Story Map naar Applicatie

De ruggengraat van de User Story Map (`USM_DEV_ROADMAP.md`) vertaalt zich direct naar de hoofdnavigatie (de "werkruimtes" of "tabbladen") van het S1mpleTrader-dashboard.

| PLUGIN DEVELOPMENT | STRATEGY BUILDER | BACKTESTING & ANALYSIS | PAPER TRADING | LIVE MONITORING |
| :--- | :--- | :--- | :--- | :--- |
| :--- | :--- | :--- | :--- | :--- |

Elk van deze secties representeert een "werkruimte" binnen de applicatie, met een eigen set aan gespecialiseerde tools en visualisaties.

---
## 5.3. Gedetailleerde Workflow per Werkruimte

### **Werkruimte 1: PLUGIN DEVELOPMENT**

* **User Goal:** Het snel en betrouwbaar ontwikkelen, testen en beheren van de herbruikbare bouwblokken (plugins) van het systeem.
* **UI Componenten:**
    * **Plugin Registry Viewer:** Een overzichtstabel van alle door de backend ontdekte plugins, met details uit hun `plugin_manifest.yaml` (versie, type, dependencies).
    * **Plugin Creator Wizard:** Een formulier dat de gebruiker helpt een nieuwe plugin-map aan te maken met de correcte boilerplate-code (`worker.py`, `schema.py`, `manifest.yaml`).
    * **Unit Test Runner:** Een UI-knop per plugin die de bijbehorende `test_worker.py` op de backend uitvoert en het resultaat (pass/fail) direct terugkoppelt.
* **Backend Interactie:** De UI communiceert met de `PluginQueryService` om de lijst van plugins op te halen en met een nieuwe `PluginEditorService` om de boilerplate aan te maken.

### **Werkruimte 2: STRATEGY BUILDER**

* **User Goal:** Het intuïtief en foutloos samenstellen van een complete handelsstrategie (`run.yaml`) door plugins te combineren.
* **UI Componenten:**
    * **Visuele Pijplijn:** Een grafische weergave van de analytische pijplijn, opgedeeld in de logische fasen (bv. `Context`, `Signaal`, `Risico`, etc.) zoals gedefinieerd in de architectuur.
    * **Plugin Bibliotheek:** Een zijbalk toont alle beschikbare plugins, slim gegroepeerd op basis van het `type`-veld uit hun manifest (bv. `regime_filters`, `signal_generators`).
    * **Configuratie Paneel:** Dit is waar de magie gebeurt. Wanneer een plugin in een slot wordt geplaatst, verschijnt er een paneel met een **automatisch gegenereerd formulier**.
        * **Voorbeeld:** Als de `schema.py` van een EMA-plugin `length: int = Field(default=20, gt=1)` definieert, genereert de UI een numeriek inputveld, vooraf ingevuld met "20", met een validatieregel die afdwingt dat de waarde groter dan 1 moet zijn. Foutieve input wordt onmogelijk gemaakt.
* **Backend Interactie:** De UI haalt de plugins op via de `PluginQueryService`. Bij het opslaan stuurt de UI een `JSON`-representatie van de samengestelde strategie naar de `BlueprintEditorService`, die het als een `YAML`-bestand wegschrijft in de `config/runs/` map.

* **Hint naar frontend implementatie:**
+----------------------------------------------------------------------+
| Fase 1: Regime Context (Selecteer de "Weerman" plugins)              |
| +-----------------+   +-----------------+                            |
| | ADXContext      |   | VolatilityContext | ...                      |
| +-----------------+   +-----------------+                            |
+----------------------------------------------------------------------+
| Fase 2: Structurele Context (Selecteer de "Cartograaf" plugins)    |
| +----------------------+   +-------------------------+               |
| | MarketStructure      |   | SupportResistanceFinder | ...           |
| +----------------------+   +-------------------------+               |
+----------------------------------------------------------------------+

### **Werkruimte 3: BACKTESTING & ANALYSIS**

* **User Goal:** Het rigoureus testen van strategieën onder verschillende condities en het diepgaand analyseren van de resultaten om inzichten te verkrijgen.
* **UI Componenten:**
    1.  **Run Launcher:** Een sectie waar de gebruiker een opgeslagen strategie-blueprint selecteert en een backtest, optimalisatie of varianten-test kan starten.
    2.  **Live Progress Dashboard:** Na het starten van een run, toont de UI een live-updating dashboard met de voortgang (bv. voortgangsbalken voor de `ParallelRunService` bij een optimalisatie).
    3.  **Resultaten Hub:** Een centrale plek waar alle voltooide runs worden getoond. Vanuit hier kan de gebruiker doorklikken naar:
        * **Optimization Results:** Een interactieve tabel (sorteren, filteren, zoeken) met de resultaten van een optimalisatierun, om snel de beste parameter-sets te vinden.
        * **Comparison Arena:** Een grafische vergelijking van varianten, met overlappende equity curves en een heatmap van key metrics om de robuustheid te beoordelen.
        * **Trade Explorer:** De meest krachtige analyse-tool. Hier kan de gebruiker door individuele trades van een *enkele* run klikken en op een grafiek precies zien wat de context was op het moment van de trade: welke indicatoren waren actief, waar lag de marktstructuur, waarom werd de entry getriggerd, etc.
* **Backend Interactie:** De UI roept de `StrategyOperator`, `OptimizationService` en `VariantTestService` aan. De resultaten worden opgehaald via de `VisualizationService`, die kant-en-klare "visualisatie-pakketten" (JSON-data voor grafieken en tabellen) levert.

### **Werkruimte 4 & 5: PAPER TRADING & LIVE MONITORING**

* **User Goal:** Een gevalideerde strategie naadloos overzetten naar een gesimuleerde en vervolgens een live-omgeving, en de prestaties continu monitoren.
* **UI Componenten:**
    * **Deployment Manager:** Een scherm waar een gebruiker een succesvolle strategie-configuratie kan "promoveren" naar Paper of Live trading.
    * **Live Dashboard:** Een real-time dashboard dat data leest uit de gedeelde datastore (bv. Redis) van de live-omgeving. Het toont:
        * Huidige PnL.
        * Open posities en orders.
        * Een live log-stream.
        * Alerts en notificaties.
        * Een prominente **"Noodstop"-knop** om de strategie onmiddellijk te deactiveren.
* **Backend Interactie:** De UI communiceert met de `LiveEnvironment` via een `Command Queue` (voor acties als "start" of "stop") en leest de live-staat via API-endpoints die gekoppeld zijn aan de real-time datastore.

---
## 5.4. Het Frontend-Backend Contract: BFF & TypeScript

De naadloze ervaring wordt technisch mogelijk gemaakt door twee kernprincipes:

1.  **Backend-for-Frontend (BFF):** De `frontends/web/api/` is geen generieke API, maar een **backend die exclusief voor de `frontends/web/ui/` werkt**. Hij levert data in exact het formaat dat de UI-componenten nodig hebben. Dit voorkomt complexe data-manipulatie in de frontend en houdt de UI-code schoon en gefocust op presentatie.

2.  **Contractuele Zekerheid met TypeScript:** We formaliseren het contract tussen de BFF en de UI om robuustheid te garanderen.
    * **Automatische Type Generatie:** Een tool in de ontwikkel-workflow leest de Pydantic-modellen (uit `schema.py` en DTO-bestanden) in de backend.
    * **Resultaat:** Het genereert automatisch corresponderende **TypeScript `interfaces`**. De frontend-code weet hierdoor al tijdens het ontwikkelen (*compile-time*) exact hoe elk data-object eruitziet. Een wijziging in de backend (bv. een veld hernoemen in een Pydantic-model) die niet in de frontend wordt doorgevoerd, leidt onmiddellijk tot een **compile-fout**, niet tot een onverwachte bug in productie.

Deze aanpak zorgt voor een robuust, ontkoppeld en tegelijkertijd perfect gesynchroniseerd ecosysteem, wat essentieel is voor de "supercharged" en efficiënte workflow die we voor ogen hebben.