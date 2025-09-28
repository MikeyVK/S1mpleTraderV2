# S1mpleTrader V2 - AI Assistent Instructies

Hallo! Ik ben een AI-assistent die je helpt met het ontwikkelen van de S1mpleTrader V2 applicatie. Dit document geeft me de nodige context over de architectuur, de belangrijkste ontwerpprincipes en de codeerstandaarden.

## 1. Visie & Kernprincipes

Mijn primaire doel is om je te helpen bij het bouwen en onderhouden van een uniforme, plugin-gedreven architectuur die de volledige levenscyclus van een handelsstrategie ondersteunt. Ik houd me aan de volgende vier kernprincipes:

* **Plugin First**: Alle strategische logica is ingekapseld in zelfstandige, onafhankelijk testbare plugins. Dit is de kern van het systeem.
* **Scheiding van Zorgen (Separation of Concerns)**: Er is een strikte scheiding tussen de `StrategyOrchestrator` (de wat), de `ExecutionEnvironment` (de waar), het `Assembly Team` (de hoe) en het `Portfolio` (de financiële staat).
* **Configuratie-gedreven**: Het gedrag van de applicatie wordt volledig bestuurd door mens-leesbare `YAML`-bestanden. De code is de motor, de configuratie is de bestuurder.
* **Contract-gedreven**: Alle data-uitwisseling wordt gevalideerd door strikte Pydantic-schema's (backend) en TypeScript-interfaces (frontend). Dit zorgt voor voorspelbaarheid en type-veiligheid.

## 2. Architectuur Overzicht

De applicatie heeft een strikt gelaagde architectuur met een eenrichtingsverkeer van afhankelijkheden.

+-------------------------------------------------------------+
|  Frontend (CLI, Web API, Web UI)                            |
+--------------------------+----------------------------------+
|
v
+--------------------------+----------------------------------+
|  Service (Orchestratie & Business Workflows)                |
|  - StrategyOrchestrator, OptimizationService                |
+--------------------------+----------------------------------+
|
v
+--------------------------+----------------------------------+
|  Backend (Engine)                                           |
|  - Portfolio, ExecutionEnvironments, Assembly Team          |
+-------------------------------------------------------------+


* **Backend (`/backend`)**: De "engine". Bevat alle kernlogica en is ontworpen als een onafhankelijke library.
* **Service (`/services`)**: De "lijm". Orkestreert backend-componenten tot complete business workflows. Hier leeft de `StrategyOrchestrator`.
* **Frontend (`/frontends`)**: De gebruikersinterface (Web UI, API, CLI).

## 3. De 6-Fasen Quant Workflow

De kern van elke strategie-executie is een 6-fasen trechter die een idee omzet in een concrete trade. Ik moet deze flow begrijpen en respecteren bij het schrijven van code.

1.  **Fase 1: Regime Analyse**: Bepaalt of de marktomstandigheden geschikt zijn (bv. trending).
2.  **Fase 2: Structurele Context**: Maakt de markt leesbaar door context toe te voegen (bv. marktstructuur, trends).
3.  **Fase 3: Signaal Generatie**: Identificeert de precieze, actiegerichte trigger voor een trade.
4.  **Fase 4: Signaal Verfijning**: Valideert het signaal met extra bevestiging (bv. volume).
5.  **Fase 5: Trade Constructie**: Creëert een concreet handelsplan (entry, stop-loss, take-profit).
6.  **Fase 6: Portfolio Overlay**: Voert een finale risicocheck uit op basis van de huidige portfoliostaat.

De `StrategyOrchestrator` is de regisseur die deze 6 fasen aanstuurt, terwijl het `Assembly Team` (in de backend) verantwoordelijk is voor het technisch ontdekken, bouwen en uitvoeren van de juiste plugins voor elke fase.

## 4. Anatomie van een Plugin

Plugins zijn de fundamentele bouwstenen. Elke plugin is een zelfstandige Python package met een vaste structuur.

* `plugins/[plugin_naam]/`:
    * `plugin_manifest.yaml`: De "ID-kaart" die de plugin vindbaar maakt. Het definieert het `type` (dat bepaalt in welke van de 6 fasen de plugin past), de `dependencies` en andere metadata.
    * `worker.py`: Bevat de Python-klasse met de daadwerkelijke businesslogica.
    * `schema.py`: Bevat het Pydantic-model dat de configuratieparameters en validatieregels definieert.
    * `state.json` (optioneel): Wordt gebruikt door stateful plugins om hun staat te bewaren.

## 5. Codeerstandaarden & Best Practices

Ik zal me strikt houden aan de volgende standaarden bij het schrijven van code:

1.  **Code Stijl**:
    * Alle Python-code moet **PEP 8 compliant** zijn.
    * **Volledige Type Hinting** is verplicht.
    * Commentaar en docstrings zijn in het **Engels**.
    * Gebruik **Google Style Python Docstrings** voor alle functies en klassen.

2.  **Contract-gedreven Ontwikkeling**:
    * Alle data die tussen componenten wordt doorgegeven (DTO's, configs) moet worden ingekapseld in een **Pydantic `BaseModel`**.

3.  **Logging**:
    * De primaire output voor analyse is een gestructureerd **`run.log.json`**-bestand.
    * Gebruik een **`Correlation ID`** (UUID) om de volledige levenscyclus van een trade traceerbaar te maken door alle logs heen.

4.  **Testen**:
    * Code zonder tests is incompleet. Elke plugin is **verplicht** om een `tests/test_worker.py` te hebben.

5.  **Configuratie Formaat**:
    * Gebruik **`YAML`** voor alle door mensen geschreven configuratie.
    * Gebruik **`JSON`** voor machine-naar-machine data-uitwisseling (bv. API's, state-bestanden).

## 6. Snelle Referentie: Kernterminologie

* **Assembly Team**: De backend-componenten (`PluginRegistry`, `WorkerBuilder`, `ContextPipelineRunner`) die de technische orkestratie van plugins verzorgen.
* **Run**: Een `YAML`-bestand (`run_schema.yaml`) dat een complete strategie-configuratie beschrijft.
* **DTO (Data Transfer Object)**: Een Pydantic-model (`Signal`, `Trade`) dat als strikt contract dient voor data-uitwisseling.
* **ExecutionEnvironment**: De backend-laag die de "wereld" definieert waarin een strategie draait (`Backtest`, `Paper`, `Live`).
* **StrategyOrchestrator**: De "regisseur" in de Service-laag die de 6-fasen trechter uitvoert voor één enkele run.

Door deze principes en structuren te volgen, help ik je om een consistente, robuuste en onderhoudbare codebase te bouwen. Laten we beginnen!
