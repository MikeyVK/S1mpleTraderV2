# 7. Ontwikkelstrategie & Tooling

Dit document beschrijft de methodiek, de workflow en de tooling voor het ontwikkelen, testen en debuggen van het S1mpleTrader V2 ecosysteem. Het is de blauwdruk voor een snelle, efficiënte en data-gedreven ontwikkelomgeving.

---
## 7.1. Filosofie: Rapid, Lean & User-Centered

We stappen af van een traditionele, op de CLI gerichte workflow. De nieuwe filosofie is gebaseerd op een combinatie van **Lean UX** en **User-Centered Design (UCD)**, met als doel een "supercharged" ontwikkelcyclus te creëren.

* **De Gebruiker staat Centraal:** De primaire gebruiker ("De Kwantitatieve Strateeg") en diens workflow bepalen wat we bouwen en in welke volgorde. De Web UI is het centrale instrument.
* **Compact Ontwikkelen:** We bouwen in de kleinst mogelijke, onafhankelijke eenheden (een plugin) en testen deze geïsoleerd.
* **Direct Testen:** Elke plugin wordt vergezeld van unit tests. Geen enkele component wordt als "klaar" beschouwd zonder succesvolle, geautomatiseerde tests.
* **Snelle Feedback Loop (Bouwen -> Meten -> Leren):** De tijd tussen een idee, een codewijziging en het zien van het visuele resultaat moet minimaal zijn. De Web UI is de motor van deze cyclus.

---
## 7.2. De "Supercharged" Ontwikkelcyclus in de Praktijk

De gehele workflow, van het bouwen van een strategie tot het analyseren van de resultaten, vindt plaats binnen de naadloze, visuele webapplicatie.

### **Fase 1: Visuele Strategie Constructie (De "Strategy Builder")**
* **Doel:** Snel en foutloos een nieuwe strategie (`run.yaml`) samenstellen.
* **Proces:**
    1.  De gebruiker opent de "Strategy Builder" in de Web UI.
    2.  In een zijbalk verschijnen alle beschikbare plugins, opgehaald via een API en gegroepeerd per `type` (bv. `signal_generators`).
    3.  De gebruiker sleept plugins naar de "slots" in een visuele weergave van de 9-fasen (fase 1-2 en fase 3-9) trechter/pijplijn.
    4.  Voor elke geplaatste plugin genereert de UI automatisch een configuratieformulier op basis van de `schema.py` van de plugin. Input wordt direct in de browser gevalideerd.
    5.  Bij het opslaan wordt de configuratie als `YAML` op de server aangemaakt.

### **Fase 2: Interactieve Analyse (De "Backtesting Hub")**
* **Doel:** De gebouwde strategieën rigoureus testen en de resultaten diepgaand analyseren.
* **Proces:**
    1.  **Run Launcher:** Vanuit de UI start de gebruiker een backtest of optimalisatie.
    2.  **Live Progress:** Een dashboard toont de live voortgang.
    3.  **Resultaten Analyse:**
        * **Optimalisatie:** Resultaten verschijnen in een interactieve tabel (sorteren, filteren).
        * **Diepgaande Analyse (Trade Explorer):** De gebruiker kan doorklikken naar een enkele run en door individuele trades bladeren, waarbij een interactieve grafiek alle contextuele data (marktstructuur, indicatoren, etc.) toont op het moment van de trade.

### **Fase 3: De Feedback Loop**
* **Doel:** Een inzicht uit de analysefase direct omzetten in een verbetering.
* **Proces:** Vanuit de "Trade Explorer" klikt de gebruiker op "Bewerk Strategie". Hij wordt direct teruggebracht naar de "Strategy Builder" met de volledige configuratie al ingeladen, klaar om een aanpassing te doen. De cyclus begint opnieuw.

---
## 7.3. De Tooling in Detail

### **7.3.1. Gespecialiseerde Entrypoints**
De applicatie kent drie manieren om gestart te worden, elk met een eigen doel:
* **`run_web.py` (De IDE):** Het primaire entrypoint voor de ontwikkelaar. Start de FastAPI-server die de Web UI en de bijbehorende API's serveert.
* **`run_backtest_cli.py` (De Robot):** De "headless" entrypoint voor automatisering, zoals regressietesten en Continuous Integration (CI/CD) workflows.
* **`run_supervisor.py` (De Productie-schakelaar):** De minimalistische, robuuste starter voor de live trading-omgeving.

### **7.3.2. Testen als Integraal Onderdeel**
* **Unit Tests per Plugin:** Elke plugin-map krijgt een `tests/test_worker.py`. Deze test laadt een stukje voorbeeld-data, draait de `worker.py` erop, en valideert of de output (bv. de nieuwe kolom of de `Signal` DTO) correct is. Dit gebeurt volledig geïsoleerd.
* **Integratietests:** Testen de samenwerking tussen de service laag componenten en de `Assembly`-componenten.
* **End-to-End Tests:** Een klein aantal tests die via `run_backtest_cli.py` een volledige backtest draaien op een vaste dataset en controleren of het eindresultaat (de PnL) exact overeenkomt met een vooraf berekende waarde.

### **7.3.3. Gelaagde Logging & Debugging**
Logging is een multi-inzetbare tool, geen eenheidsworst. We onderscheiden drie lagen:

1.  **Laag 1: `stdio` (De Console)**
    * **Doel:** Alleen voor *initiële, basic development* van een geïsoleerde plugin. Gebruik `print()` voor de snelle, "vuile" check. Dit is vluchtig en wordt niet bewaard.

2.  **Laag 2: Gestructureerde Logs (`JSON`)**
    * **Doel:** De primaire output voor **backtests en paper trading**. Dit is de *databron* voor analyse.
    * **Implementatie:** Een `logging.FileHandler` die log-records als gestructureerde `JSON`-objecten wegschrijft naar `run.log.json`.
    * **Principe:** De console blijft schoon. De *echte* output is het log-bestand.

3.  **Laag 3: De "Log Explorer" (Web UI)**
    * **Doel:** De primaire interface voor **analyse en debugging**.
    * **Implementatie:** Een tool in de frontend die `run.log.json` inleest en interactief presenteert, waardoor je kunt filteren op `plugin_name` of een `Correlation ID`.

#### **Traceability met de `Correlation ID`**
Elk `Signal` DTO dat wordt gecreëerd, krijgt een unieke ID (bv. een UUID). Elke plugin die dit signaal (of een afgeleid object zoals een `Trade` DTO) verwerkt, voegt deze `Correlation ID` toe aan zijn log-berichten. Door in de "Log Explorer" op deze ID te filteren, kan de gebruiker de volledige levenscyclus en beslissingsketen van één specifieke trade volgen, door alle fasen en parallelle processen heen.