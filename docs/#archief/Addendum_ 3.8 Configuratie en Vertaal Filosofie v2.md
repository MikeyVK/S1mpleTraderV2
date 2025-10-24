# **De Finale Systeemarchitectuur: De Centrale Vertaler**

Dit document consolideert de finale architecturale besluiten voor de S1mpleTrader opstart- en orkestratieprocedure. Het beschrijft een fundamentele verfijning van de architectuur, gericht op het versterken van het Single Responsibility Principle (SRP). De kern van dit ontwerp is een heldere hiërarchie van configuratielagen en een centrale vertaalslag, wat de OperationService transformeert tot een pure levenscyclus-manager.

## **1. Impact op Bestaande Documentatie**

Deze nieuwe filosofie heeft een significante impact op de conceptuele beschrijving van de orkestratie in de gehele documentatieset. De volgende secties in de originele documenten zijn door dit addendum achterhaald en moeten worden gelezen in de context van deze nieuwe architectuur.

**Hoofdstuk 1: 1_BUS_COMMUNICATION_ARCHITECTURE.md**

* **Paragraaf 1.5. De Levenscyclus in de Praktijk:** De sub-paragraaf *De Bootstrap Fase* is volledig vervangen door de nieuwe, meer gedetailleerde fases (Hydratatie, Assemblage, Bedrading) die worden georkestreerd door de OperationService en zijn specialisten. De oude beschrijving van de ContextBootstrapper en EventWiringFactory is niet langer correct.

**Hoofdstuk 2: 2_ARCHITECTURE.md**

* **Paragraaf 2.3. De Gelaagde Architectuur:** De beschrijving van de *SERVICE LAAG* is onvolledig. De rol van de OperationService als de enige, centrale orkestrator en levenscyclus-manager is hierin niet adequaat beschreven.  
* **Paragraaf 2.10. Componenten in Detail:** De sub-paragraaf *Assembly Components* is grotendeels achterhaald. De ContextBuilder bestaat niet meer in die vorm. De interactie en verantwoordelijkheden van de OperatorFactory, WorkerBuilder (WorkerFactory), en andere assemblage-componenten worden nu direct aangestuurd door de OperationService op basis van BuildSpecs.  
* **Paragraaf 2.11. Dataflow & Orchestratie:** De beschrijving van de opstart-dataflow en de rol van de ContextBuilder is incorrect. De OperationService is nu de start van alle orkestratie.

**Hoofdstuk 3: 3_DE_CONFIGURATIE_TREIN.md**

* **Paragraaf 3.8. De Onderlinge Samenhang - De "Configuratie Trein" in Actie:** Deze paragraaf is volledig vervangen door de filosofie in dit document. De oude beschrijving van hoe Operations de bestanden koppelt en de ContextBuilder aanroept, is achterhaald.  
* **Concepten operators.yaml en wiring_map.yaml als globale bestanden:** Onze nieuwe filosofie stelt dat deze configuraties onderdeel zijn van de StrategyConfig (afkomstig uit strategy_blueprint.yaml), en dus niet globaal. De paragrafen 3.3.2, 3.3.6 en 3.3.7 moeten in dit licht herzien worden.

## **2. De Architectuurfilosofie**

We hebben een architectuur ontworpen die gebaseerd is op een strikte scheiding van verantwoordelijkheden. De filosofie definieert een heldere hiërarchie om een perfecte scheiding van verantwoordelijkheden (SRP) te garanderen.

### **2.1. De Drie Gescheiden Configuratielagen**

Om SRP te waarborgen, splitsen we de configuratie op in drie strikt gescheiden, hiërarchische lagen, elk met een eigen doel en levenscyclus.

**Laag 1: PlatformConfig (De Fundering)**

* **Doel:** Bevat alle globale, statische en run-onafhankelijke configuratie van het platform. Dit is de context waarin alle operaties draaien.  
* **Bron:** platform.yaml.  
* **Inhoud:** Logging-instellingen, paden (zoals plugins_root_path), taalinstellingen.  
* **Levenscyclus:** Wordt één keer geladen bij de start van de OperationService.  
* **Belangrijk:** Deze laag bevat geen connectors, data_sources, environments of schedules. Deze zijn operationeel van aard.

**Laag 2: OperationConfig (De Werkruimte)**

* **Doel:** Definieert een specifieke "werkruimte" of "campagne". Het groepeert alle technische middelen (connectors, data_sources, environments), de te draaien strategieën (strategy_links) en de timing (schedule).  
* **Bron:** Het operation.yaml bestand zelf, plus de bestanden waarnaar het verwijst (connectors.yaml, data_sources.yaml, environments.yaml, schedule.yaml).  
* **Inhoud:** De volledige definitie van alle beschikbare technische middelen, de scheduler-configuratie en de lijst van strategy_links.  
* **Levenscyclus:** Wordt geladen wanneer de OperationService een specifieke operatie start.

**Laag 3: StrategyConfig (De Blauwdruk)**

* **Doel:** Vertegenwoordigt de volledige, gebruikersvriendelijke intentie voor één specifieke, uit te voeren strategie-instantie.  
* **Bron:** Wordt per strategy_link samengesteld uit het corresponderende strategy_blueprint.yaml.  
* **Inhoud:** De workforce, en de strategie-specifieke operator_config en wiring_config.  
* **Levenscyclus:** Wordt "just-in-time" geladen binnen de start_strategy methode voor elke strategie die wordt opgestart.

### **2.2. Specialisten voor Laden en Valideren**

Om deze lagen schoon te houden, definiëren we gespecialiseerde backend-componenten voor het laden en valideren.

* **ConfigLoader (config/loader.py):** Een component met drie duidelijke, SRP-conforme methoden:  
  * load_platform_config() -> PlatformConfig: Laadt en valideert de schema van platform.yaml.  
  * load_operation_config(operation_name) -> OperationConfig: Laadt het operation.yaml en de bijbehorende connectors.yaml, data_sources.yaml, etc.  
  * load_strategy_config(blueprint_id) -> StrategyConfig: Laadt het specifieke strategy_blueprint.yaml.  
* **ConfigValidator (config/validator.py):** Een component die de consistentie tussen en binnen de geladen configuratie-objecten controleert.  
  * validate_platform_config(platform_config): Valideert basisinstellingen zoals of de gedefinieerde paden bestaan.  
  * validate_operation_config(operation_config): Valideert de OperationConfig. Controleert bijvoorbeeld of de connector_id in een environment ook daadwerkelijk is gedefinieerd in connectors.yaml.  
  * validate_strategy_config(strategy_config, operation_config): Valideert de StrategyConfig binnen de context van de operatie. Cruciaal, want hier controleert het of de execution_environment_id van een strategie ook echt bestaat in de OperationConfig.

### **2.3. De Centrale Vertaler: ConfigTranslator (config/translator.py)**

Dit is de geniale vondst die de hele architectuur samensmeedt. De ConfigTranslator is de specialist die de brug slaat tussen de gebruikersintentie en de machine-instructies.

* **Single Responsibility:** Zijn enige taak is het vertalen van de drie gevalideerde configuratielagen naar één enkele, machinevriendelijke BuildSpecCollection.  
* **De "Mise en Place":** De ConfigTranslator doet al het "denkwerk" en de interpretatie vooraf. Hij leest de complexe, gebruikersvriendelijke YAML-structuren en creëert een set van simpele, directe "werkbonnen" voor elke factory.  
* **Input & Rationale:** De collect_build_specs-methode heeft alle drie de configuratielagen nodig om zijn werk te kunnen doen:  
  * **StrategyConfig:** De primaire input. Bevat de workforce en strategie-specifieke orkestratie die vertaald moet worden.  
  * **PlatformConfig:** Nodig voor globale context, zoals paden (plugins_root_path) om de manifesten van de plugins te kunnen vinden en lezen.  
  * **OperationConfig:** Essentieel om de execution_environment_id van de strategie te kunnen opzoeken en te bepalen welke connector of data_source gebouwd moet worden.  
* **Output:** Een BuildSpecCollection-object. Dit object is een container met daarin alle specifieke "werkbonnen", zoals PersistorBuildSpec, WorkforceBuildSpec, OperatorBuildSpec, etc.

### **2.4. Factories als "Domme" Specialisten**

De BuildSpecs maken elke factory radicaal eenvoudiger en 100% SRP-conform.

* **De Workflow:** De OperationService roept een factory aan en geeft hem alleen zijn eigen, specifieke BuildSpec (bv. persistor_factory.build_from_spec(build_specs.persistor_spec)).  
* **De Logica van de Factory:** De factory hoeft niet meer door complexe configuraties te bladeren. Hij ontvangt een simpele DTO met een duidelijke opdracht (bv. "bouw een state persistor voor worker X en Y") en voert deze blindelings uit. Hij is een pure, "domme" uitvoerder geworden.

Deze aanpak garandeert dat de OperationService een pure dirigent blijft, de ConfigTranslator de enige denker is, en de factories pure bouwers zijn.

## **3. De Verfijnde OperationService als Levenscyclus-Manager**

Met deze heldere structuur wordt de OperationService een pure levenscyclus-manager ("state machine") voor actieve strategie-instanties.

### **Bij Initialisatie:**

1. **Initialiseer alle specialisten:**  
   * Configuratie-specialisten: ConfigLoader, ConfigValidator, ConfigTranslator.  
   * Platform-Singletons: Scheduler, AggregatedLedger, MultiTimeframeProvider, PluginRegistry, DependencyValidator.  
   * Alle Factories: PersistorFactory, ConnectorFactory, DataSourceFactory, EnvironmentFactory, WorkerFactory, OperatorFactory, EventAdapterFactory, EventWiringFactory.  
2. **Laad en valideer basisconfiguraties:** De platform_config en operation_config worden geladen en gevalideerd.  
3. **Houd interne staat bij:** self.actieve_strategieen: Dict[str, StrategieInstantie] = {}.

### **De Levenscyclus Methoden:**

* start_all_strategies()  
  Ittereert door de strategy_links in de operation_config en roept voor elke link self.start_strategy(strategy_link) aan.  
* start_strategy(strategy_link) -> strategy_instance_id  
  Dit is de enige, universele en atomaire startprocedure.  
  * **Stap 1: Laden & Valideren:**  
    * strategy_config = config_loader.load_strategy_config(strategy_link.blueprint_id)  
    * config_validator.validate_strategy_config(strategy_config, operation_config)  
  * **Stap 2: Vertalen:**  
    * build_specs = config_translator.collect_build_specs(strategy_config, platform_config, operation_config)  
  * **Stap 3: Assembleren & Starten (de "Factory Chain"):**  
    * **A: Bouw Technische Bronnen:** connector_map = connector_factory.build_from_spec(build_specs.connector_spec), data_source_map = data_source_factory.build_from_spec(build_specs.data_source_spec)  
    * **B: Bouw de Omgeving:** environment = environment_factory.build_from_spec(build_specs.environment_spec, connectors=connector_map, data_sources=data_source_map)  
    * **C: Bouw Strategie-Componenten:** persistor_map = ..., event_handler_map = ..., worker_instances = worker_factory.build_from_spec(...), operator_map = operator_factory.build_from_spec(...)  
    * **D: Bedraad het Systeem:** event_wiring_factory.wire_all_from_spec(build_specs.wiring_spec, operator_map, worker_instances, event_bus)  
    * **E: Start de Executie:** environment.start()  
  * **Stap 4: Registreer Instantie:** Creëert een StrategieInstantie-object, voegt deze toe aan de actieve lijst en retourneert de unieke ID.  
* stop_strategy(strategy_instance_id)  
  Zoekt de instantie op, roept environment.stop() aan, geeft resources vrij en zet de status op Stopped.  
* restart_strategy(strategy_instance_id)  
  Roept stop_strategy() en vervolgens start_strategy() aan met de originele strategy_link.  
* get_strategy_status(strategy_instance_id)  
  Retourneert de status (Running, Stopped, Error) en relevante runtime-statistieken uit de StrategyLedger.

## **4. Scenario Toetsing: Dynamisch Strategieën Toevoegen**

**Scenario:** De OperationService draait. In de Web UI bouwt een gebruiker een nieuwe strategie met een connector die nog niet is opgenomen in de actieve OperationConfig. De gebruiker klikt op 'Run strategy'.

Analyse & Knelpunt:  
Met de huidige opzet gaat het laden niet goed. De start_strategy-methode zal falen bij validate_strategy_config (stap 1), omdat de connector_id waarnaar de strategie verwijst niet bestaat in de OperationConfig die in het geheugen is geladen. De filosofie mist een mechanisme voor het dynamisch aanpassen van de operationele context.  
De Oplossing: Een "Hot-Reload" Mechanisme  
Om dit scenario te ondersteunen, moet de OperationService worden uitgebreid met de mogelijkheid om zijn eigen context te vernieuwen.

1. **Persisteer de Wijziging:** Een API-endpoint schrijft de nieuwe configuratie (connector, strategy link) naar de respectievelijke .yaml-bestanden.  
2. **Herlaad de Operationele Context:** De API roept een speciale methode aan (bv. operation_service.reload_operation_config()) om de bijgewerkte OperationConfig in het geheugen te laden en te valideren.  
3. **Start de Nieuwe Strategie:** De API roept nu de reguliere, universele operation_service.start_strategy(new_strategy_link) aan, die nu zal slagen omdat de context up-to-date is.

## **5. Stresstest: De Architectuur Getoetst aan Geavanceerde Quant-Scenario's**

### **Scenario 1: De "Smart DCA" Strategie**

* **Doel:** Conditionele DCA-aankopen (bv. elke maandag) gebaseerd op parallelle input van een OpportunityWorker en een ThreatWorker. De aankoop mag alleen doorgaan als de kans hoog is én het risico laag.  
* **Architecturale Toets:** Vereist een Scheduler, EventDrivenWorkers en een "fan-in" event-patroon (requires_all: true).  
* **Oordeel: ✅ Geslaagd met Vlag en Wimpel.** De architectuur is hier perfect voor ontworpen. De EventChainValidator controleert de complexe logica en de scheiding tussen de platform-Scheduler en strategie-specifieke workers zorgt voor een schone implementatie.

### **Scenario 2: De "Portfolio Heatmap"**

* **Doel:** Een 'noodrem' die alle strategieën beïnvloedt als het totale portfolio-risico een drempel overschrijdt (bv. >15% drawdown).  
* **Architecturale Toets:** Vereist een singleton AggregatedLedger die luistert naar events van alle strategieën en een systeembreed PORTFOLIO_RISK_HIGH event kan publiceren, waarop workers binnen elke strategie kunnen reageren.  
* **Oordeel: ✅ Geslaagd.** De architectuur ondersteunt dit scenario elegant. De scheiding tussen geïsoleerde StrategieInstanties en gedeelde Platform-Singleton Services, gecombineerd met een centrale EventBus, maakt dit mogelijk.

### **Scenario 3: De "Multi-Asset Arbitrage" Strategie**

* **Doel:** Een enkele strategie die tegelijkertijd data van twee verschillende connectors (bv. Kraken en Binance) verwerkt om arbitragekansen te vinden.  
* **Architecturale Toets:** Stuit op de grens van het TradingContext (ontworpen voor één asset) en de ExecutionEnvironment (gekoppeld aan één bron).  
* **Oordeel: ⚠️ Geslaagd, maar vereist een aanpassing (Zwakke Plek Blootgelegd).** De architectuur is flexibel genoeg om dit op te lossen door een gespecialiseerde MultiAssetEnvironment te introduceren. Deze environment kan meerdere connectors geïnjecteerd krijgen en publiceert aparte events per bron (bv. KrakenContextReady, BinanceContextReady). Een EventDrivenWorker kan zich op beide abonneren. Dit legt een waardevol punt voor verdere ontwikkeling bloot.

### **Scenario 4: De "Walk-Forward Optimizer"**

* **Doel:** Een complexe backtest-routine die training- en testperiodes door de tijd heen verschuift om de strategie robuust te valideren.  
* **Architecturale Toets:** Test de flexibiliteit van de meta-workflow laag. Kan de OperationService programmatisch worden aangeroepen met wisselende configuraties?  
* **Oordeel: ✅ Geslaagd.** De architectuur is hier perfect geschikt voor. De OperationService en OptimizationService zijn modulaire "motoren". Een nieuwe, overkoepelende WalkForwardService kan deze in een lus aanroepen met de juiste configuraties (datumbereiken) voor elke trainings- en testperiode. Dit vereist geen aanpassingen aan de kernarchitectuur.