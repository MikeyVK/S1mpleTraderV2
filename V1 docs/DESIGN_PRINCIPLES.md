S1mpleTrader: Design Principles
Dit document beschrijft de architectuur, design principles en best practices die zijn toegepast in het S1mpleTrader-project. Het dient als een gids en samenvatting van de filosofie achter de code.

1. High-Level Architectuur
1.1. Three-Layer Architecture
De applicatie volgt een strikte scheiding in drie lagen, waarbij afhankelijkheden slechts in één richting stromen: Frontend -> Service -> Backend.

Frontend Layer (/frontends): Verantwoordelijk voor alle gebruikersinteractie. De run_cli functie en de apps (zoals BacktesterApp) initialiseren de juiste workflow en presenteren de resultaten.

Service Layer (/services): Fungeert als de publieke API en "lijm" van de applicatie. Services zoals BacktestService orkestreren complexe processen door componenten uit de backend in de juiste volgorde aan te roepen.

Backend Layer (/backend): De motor van de applicatie. Bevat alle kernlogica, strategieën, en dataverwerking. Deze laag is volledig onafhankelijk van de andere lagen.

1.2. Model-View-Controller / Presenter Patroon
Binnen de Frontend Layer wordt een variant van het MVC-patroon gebruikt om logica, data en presentatie te scheiden.

Controller (/frontends/cli/apps): De _app.py bestanden (bv. OptimizerApp) sturen de flow aan. Ze roepen een service aan om data te verkrijgen en geven deze door aan een Presenter.

Presenter (/frontends/cli/presentation): Het "slimme" deel van de view. Klassen zoals OptimizationPresenter weten hoe ze de complexe data-objecten moeten formatteren voor weergave.

View (CliReporter): Het "domme" deel van de view. De CliReporter is enkel verantwoordelijk voor het printen van voorgeformatteerde strings en tabellen naar de console.

2. SOLID Principles
De codebase demonstreert een sterke naleving van de SOLID-principes.

Single Responsibility Principle (SRP): Elke klasse heeft één, duidelijke taak. Bijvoorbeeld, DataLoader laadt data, en PerformanceAnalyzer analyseert resultaten.

Open/Closed Principle (OCP): De applicatie is uitbreidbaar zonder bestaande code te wijzigen. Een nieuw patroon kan worden toegevoegd door een klasse te maken die erft van BasePatternDetector en deze te activeren in de configuratie. De BacktestPipelineFactory hoeft hiervoor niet aangepast te worden.

Liskov Substitution Principle (LSP): Alle subklassen van een basisklasse zijn onderling uitwisselbaar. Elke exit_planner erft van BaseExitPlanner en kan door het systeem op dezelfde manier worden gebruikt.

Dependency Inversion Principle (DIP): Hoge-level modules zijn afhankelijk van abstracties, niet van concrete implementaties. De BacktestHandler is afhankelijk van de Tradable interface, niet direct van de Portfolio klasse.

3. Design Patterns & Best Practices
3.1. Kernpatronen
Factory Pattern: Centraliseert en verbergt de complexiteit van het creëren van objecten. BacktestPipelineFactory en DatasetFactory zijn hier de voornaamste voorbeelden van.

Strategy Pattern & Dynamic Loading: Strategie-componenten (patterns, filters, planners) worden behandeld als uitwisselbare "plug-ins". De dynamic_loader laadt de juiste klasse op basis van een string-naam uit de configuratie, wat het systeem extreem flexibel maakt.

Data Transfer Objects (DTOs): Het gebruik van dataclasses (bv. PatternMatch, Trade, BacktestResult) zorgt voor gestructureerde en voorspelbare datastromen tussen de verschillende componenten.

Dependency Injection: Afhankelijkheden (zoals de logger en translator) worden van buitenaf geïnjecteerd (meestal via de __init__), wat componenten ontkoppelt en de testbaarheid verhoogt.

3.2. Internationalisatie (i18n)
Key-Based Systeem: De applicatie gebruikt vertaalsleutels (bv. optimizer.results_header) in de code in plaats van hardgecodeerde tekst.

Centrale Translator: De Translator klasse is verantwoordelijk voor het laden van de taalbestanden en het omzetten van sleutels naar de uiteindelijke, eventueel geformatteerde, tekst.

3.3. Interactie tussen Logger en Translator
De samenwerking tussen de AppLogger en Translator volgt strikte regels:

Creatie en Injectie: De Translator wordt één keer geïnitialiseerd in run.py. Dit object wordt vervolgens meegegeven aan configure_logging.

Rol van LogFormatter: Binnen het logsysteem is LogFormatter de enige component die de Translator gebruikt, specifiek om log-sleutels te vertalen.

Direct Gebruik: Componenten die gebruikers-output genereren (zoals Presenters) krijgen de Translator ook direct geïnjecteerd, los van de logger.

3.4. Code Kwaliteit en Standaarden
PEP 8 Compliant: Het doel is om de code volledig te laten voldoen aan de PEP 8-stijl gids.

Linting: Lokaal wordt pylint gebruikt om de codekwaliteit en consistentie te valideren.

Gestructureerd Commentaar: Elk bestand bevat een gestandaardiseerde header-docstring die de laag, afhankelijkheden, en verantwoordelijkheden beschrijft. Dit verhoogt de leesbaarheid en het onderhoud van de codebase significant.