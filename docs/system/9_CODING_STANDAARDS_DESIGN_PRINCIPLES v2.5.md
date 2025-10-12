# **9\. Coding Standaarden & Design Principles**

Versie: 2.5 (Scope Details Hersteld)  
Status: Definitief  
Dit document beschrijft de verplichte standaarden en best practices voor het schrijven van alle code binnen het S1mpleTrader V2 project. Het doel is een consistente, leesbare, onderhoudbare en robuuste codebase. Het naleven van deze standaarden is niet optioneel.

## **9.1. Code Kwaliteit & Stijl**

### **9.1.1. Fundamenten**

* **PEP 8 Compliant:** Alle Python-code moet strikt voldoen aan de [PEP 8](https://peps.python.org/pep-0008/) stijlgids. Een linter wordt gebruikt om dit te handhaven.  
  * **Regellengte:** Maximaal 100 tekens.  
  * **Naamgeving:** snake\_case voor variabelen, functies en modules; PascalCase voor klassen.  
* **Volledige Type Hinting:** Alle functies, methodes, en variabelen moeten volledig en correct getypeerd zijn. We streven naar een 100% getypeerde codebase om runtime-fouten te minimaliseren.  
* **Commentaar in het Engels:** Al het commentaar in de code (\# ...) en docstrings moeten in het Engels zijn voor universele leesbaarheid en onderhoudbaarheid.

### **9.1.2. Gestructureerde Docstrings**

Elk bestand, elke klasse en elke functie moet een duidelijke docstring hebben.

* **Bestands-Header Docstring:** Elk .py-bestand begint met een gestandaardiseerde header die de inhoud en de plaats in de architectuur beschrijft.  
  \# backend/assembly/component\_builder.py  
  """  
  Contains the ComponentBuilder, responsible for assembling and instantiating  
  all required Operator and Worker components for a given strategy\_link.

  @layer: Backend (Assembly)  
  @dependencies: \[PyYAML, Pydantic\]  
  @responsibilities:  
      \- Reads the strategy\_blueprint.yaml.  
      \- Validates the workforce configuration.  
      \- Instantiates all required plugin workers and operators.  
  """

* **Imports:** Alle imports staan bovenaan het bestand. Het is van belang dat deze in de juiste volgorde staan. We zullen hiervoor ten alle tijden een onderverdeling gebruiken in de volgende drie groepen en volgorde:  
  * **1\. Standard Library Imports**  
  * **2\. Third-Party Imports**  
  * 3\. Our Application Imports  
    Alle imports zullen absoluut zijn en opbouwen vanaf de project root.

Indien mogelijk worden imports gegroepeerd om lange regels te voorkomen en te blijven voldoen aan de PEP 8\.

* **Functie & Methode Docstrings (Google Style):** Voor alle functies en methodes hanteren we de **Google Style Python Docstrings**. Dit is een leesbare en gestructureerde manier om parameters, return-waarden en voorbeelden te documenteren.  
  def process\_data(df: pd.DataFrame, length: int \= 14\) \-\> pd.DataFrame:  
      """Calculates an indicator and adds it as a new column.

      Args:  
          df (pd.DataFrame): The input DataFrame with OHLCV data.  
          length (int, optional): The lookback period for the indicator.  
              Defaults to 14\.

      Returns:  
          pd.DataFrame: The DataFrame with the new indicator column added.  
      """  
      \# ... function logic ...  
      return df

### **9.1.3. Naamgevingsconventies**

Naast de algemene \[PEP 8\]-richtlijnen hanteren we een aantal strikte, aanvullende conventies om de leesbaarheid en de architectonische zuiverheid van de code te vergroten.

* **Interfaces (Contracten):**  
  * **Principe:** Elke abstracte klasse (ABC) of Protocol die een contract definieert, moet worden voorafgegaan door een hoofdletter I.  
  * **Doel:** Dit maakt een onmiddellijk en ondubbelzinnig onderscheid tussen een abstract contract en een concrete implementatie.  
  * Voorbeeld:  
    \`\`\`Python  
    \# Het contract (de abstractie)  
    class IAPIConnector(Protocol):  
    ...  
    \# De concrete implementatie  
    class KrakenAPIConnector(IAPIConnector):  
        ...  
    \`\`\`

* **Interne Attributen en Methodes:**  
  * **Principe:** Attributen of methodes die niet bedoeld zijn voor gebruik buiten de klasse, moeten worden voorafgegaan door een enkele underscore (\_).  
  * **Doel:** Dit communiceert duidelijk de publieke API van een klasse.  
  * Voorbeeld:  
    \`\`\`Python  
    class AnalysisOperator:  
    def init(self):  
    self.\_app\_config \= ... \# Intern  
        def run\_pipeline(self): \# Publiek  
            self.\_prepare\_workers() \# Intern

        def \_prepare\_workers(self):  
            ...  
    \`\`\`

## **9.2. Contract-Gedreven Ontwikkeling**

### **9.2.1. Pydantic voor alle Data-Structuren**

* **Principe:** Alle data die tussen componenten wordt doorgegeven, moet worden ingekapseld in een **Pydantic BaseModel**. Dit geldt voor DTO's, configuraties en plugin-parameters.  
* **Voordeel:** Dit garandeert dat data van het juiste type en de juiste structuur is *voordat* het wordt verwerkt.

### **9.2.2. Abstracte Basisklassen (Interfaces)**

* **Principe:** Componenten die uitwisselbaar moeten zijn (zoals plugins), moeten erven van een gemeenschappelijke abstracte basisklasse (ABC) die een consistent contract afdwingt.

## **9.3. Gelaagde Logging & Traceability**

### **9.3.1. Drie Lagen van Logging**

1. **Laag 1: stdio (Console via print()):** Uitsluitend voor snelle, lokale, vluchtige debugging. Mag nooit gecommit worden.  
2. **Laag 2: Gestructureerde JSON-logs:** De standaard output voor alle runs, bedoeld voor analyse.  
3. **Laag 3: De Web UI (Log Explorer):** De primaire interface voor het analyseren en debuggen van runs.

### **9.3.2. Traceability via Correlation ID**

* **Principe:** Elk Signal DTO krijgt een unieke UUID. Elke volgende plugin die dit signaal verwerkt, neemt deze correlation\_id over in zijn log-berichten. Dit maakt de volledige levenscyclus van een trade traceerbaar.

## **9.4. Testen als Voorwaarde**

* **Principe:** Code zonder tests wordt beschouwd als onvolledig.  
* **Implementatie:** Elke plugin is **verplicht** om een tests/test\_worker.py-bestand te bevatten. Continue Integratie (CI) voert alle tests automatisch uit na elke push.

## **9.5. Overige Standaarden**

* **Internationalisatie (i18n):**  
  * **Principe:** *Alle* tekst die direct of indirect aan een gebruiker kan worden getoond, moet via de internationalisatie-laag lopen. Hardgecodeerde, gebruikersgerichte strings in de Python-code zijn niet toegestaan.  
  * **Implementatie:** Een centrale Translator-klasse laadt YAML-bestanden uit de /locales map. Code gebruikt vertaalsleutels in "dot-notation" (bv. log.backtest.complete).  
  * **Scope van de Regel:** Deze regel is van toepassing op, maar niet beperkt tot, de volgende onderdelen:  
    1. Log Berichten: Alle log-berichten die bedoeld zijn om de gebruiker te informeren over de voortgang of status van de applicatie (voornamelijk INFO-niveau en hoger). Foutmeldingen voor ontwikkelaars (DEBUG-niveau) mogen wel hardcoded zijn.  
       Correct: logger.info('run.starting', pair=pair\_name)  
       Incorrect: logger.info(f'Starting run for {pair\_name}...')  
    2. Pydantic Veldbeschrijvingen: Alle description velden binnen Pydantic-modellen (DTO's, configuratie-schema's). Deze beschrijvingen kunnen direct in de UI of in documentatie worden getoond.  
       Correct: equity: float \= Field(..., description="ledger\_state.equity.desc")  
       Incorrect: equity: float \= Field(..., description="The total current value...")  
    3. **Plugin Manifesten:** Alle beschrijvende velden in een plugin\_manifest.yaml, zoals description en display\_name. Een PluginQueryService moet deze velden door de Translator halen voordat ze naar de frontend worden gestuurd.  
  * **Interactie met Logger:** De Translator wordt één keer geïnitialiseerd en geïnjecteerd in de LogFormatter. De formatter is de enige component binnen het logsysteem die sleutels vertaalt naar leesbare berichten. Componenten die direct output genereren (zoals UI Presenters) krijgen de Translator ook apart geïnjecteerd.

### **9.5.1. Structuur van i18n Dotted Labels**

Om de locales/\*.yaml bestanden georganiseerd en onderhoudbaar te houden, hanteren we een strikte, hiërarchische structuur voor alle vertaalsleutels. De structuur volgt over het algemeen het pad van de component of het datamodel waar de tekst wordt gebruikt.

* **Principe:** component\_of\_laag.specifieke\_context.naam\_van\_de\_tekst

**Voorbeelden van de Structuur:**

1. Log Berichten:  
   De sleutel begint met de naam van de module of de belangrijkste klasse waarin de log wordt aangeroepen.  
   **Structuur:** component\_name.actie\_of\_gebeurtenis  
   **Voorbeelden:**  
   \# Voor backend/assembly/plugin\_registry.py  
   plugin\_registry:  
     scan\_start: "Scanning for plugins in '{path}'..."  
     scan\_complete: "Scan complete. Found {count} valid plugins."

   \# Voor services/operators/analysis\_operator.py  
   analysis\_operator:  
     run\_start: "AnalysisOperator run starting..."  
     critical\_event: "Critical event detected: {event\_type}"

2. Pydantic Veldbeschrijvingen (description):  
   De sleutel weerspiegelt het pad naar het veld binnen het DTO of schema. De sleutel eindigt altijd op .desc om aan te geven dat het een beschrijving is.  
   **Structuur:** schema\_naam.veld\_naam.desc  
   **Voorbeelden:**  
   \# Voor backend/dtos/ledger\_state.py  
   ledger\_state:  
     equity:  
       desc: "The total current value of the ledger."  
     available\_cash:  
       desc: "The amount of cash available for new positions."

   \# Voor een plugin's schema.py  
   ema\_detector\_params:  
     period:  
       desc: "The lookback period for the EMA calculation."

3. Plugin Manifesten (plugin\_manifest.yaml):  
   Voor de beschrijvende velden van een plugin gebruiken we een structuur die de plugin uniek identificeert.  
   **Structuur:** plugins.plugin\_naam.veld\_naam  
   **Voorbeelden:**  
   plugins:  
     ema\_detector:  
       display\_name: "EMA Detector"  
       description: "Calculates and adds an Exponential Moving Average."  
     fvg\_detector:  
       display\_name: "FVG Detector"  
       description: "Detects a Fair Value Gap after a Market Structure Shift."

* **Configuratie Formaat:** YAML is de standaard voor alle door mensen geschreven configuratie. JSON wordt gebruikt voor machine-naar-machine data-uitwisseling.

## **9.6. Design Principles & Kernconcepten**

De architectuur is gebouwd op de **SOLID**\-principes en een aantal kern-ontwerppatronen die de vier kernprincipes (Plugin First, Scheiding van Zorgen, Configuratie-gedreven, Contract-gedreven) tot leven brengen.

### **9.6.1. De Synergie: Configuratie- & Contract-gedreven Executie**

Het meest krachtige concept van V2 is de combinatie van configuratie- en contract-gedreven werken. De code is de motor; **de configuratie is de bestuurder, en de contracten zijn de verkeersregels die zorgen dat de bestuurder binnen de lijntjes blijft.**

* **Configuratie-gedreven:** De *volledige samenstelling* van een strategie (welke plugins, in welke volgorde, met welke parameters) wordt gedefinieerd in een strategy\_blueprint.yaml. Dit maakt het mogelijk om strategieën drastisch te wijzigen zonder één regel code aan te passen.  
* **Contract-gedreven:** Elk stukje configuratie en data wordt gevalideerd door een strikt **Pydantic-schema**. Dit werkt op twee niveaus:  
  1. **Algemene Schema's:** De hoofdstructuur van een operation.yaml wordt gevalideerd door een algemeen schema. Dit contract dwingt af dat er bijvoorbeeld altijd een strategy\_links sectie aanwezig is.  
  2. **Plugin-Specifieke Schema's:** De parameters voor een specifieke plugin (bv. de length van een EMA-indicator) worden gevalideerd door de Pydantic-klasse in de schema.py van *die ene plugin*.

Bij het starten van een Operation, leest de applicatie de YAML-bestanden en bouwt een set gevalideerde configuratie-objecten. Als een parameter ontbreekt, een verkeerd type heeft, of een plugin wordt aangeroepen die niet bestaat, faalt de applicatie *onmiddellijk* met een duidelijke foutmelding. Dit voorkomt onvoorspelbare runtime-fouten en maakt het systeem extreem robuust en voorspelbaar.

### **9.6.2. SOLID in de Praktijk**

* **SRP (Single Responsibility Principle):** Elke klasse heeft één duidelijke taak.  
  * ***V2 voorbeeld:*** Een FvgDetector-plugin (AnalysisWorker) detecteert alleen Fair Value Gaps. Het bepalen van de positiegrootte gebeurt in een aparte PositionSizer (AnalysisWorker).  
* **OCP (Open/Closed Principle):** Uitbreidbaar zonder bestaande code te wijzigen.  
  * ***V2 voorbeeld:*** Wil je een nieuwe exit-strategie toevoegen? Je maakt simpelweg een nieuwe exit\_planner-plugin (AnalysisWorker); de AnalysisOperator hoeft hiervoor niet aangepast te worden.  
* **DIP (Dependency Inversion Principle):** Hoge-level modules hangen af van abstracties.  
  * ***V2 voorbeeld:*** De Operations-service hangt af van de IAPIConnector-interface, niet van de specifieke KrakenAPIConnector. Hierdoor kan de connector\_id in de configuratie eenvoudig worden gewisseld.

### **9.6.3. Kernpatronen**

* **Factory Pattern:** Het Assembly Team (met ComponentBuilder) centraliseert het ontdekken, valideren en creëren van alle plugins.  
* **Strategy Pattern:** De "Plugin First"-benadering is de puurste vorm van dit patroon. Elke plugin is een uitwisselbare strategie voor een specifieke taak.  
* **DTO’s (Data Transfer Objects):** Pydantic-modellen (Signal, TradePlan, ClosedTrade) zorgen voor een voorspelbare en type-veilige dataflow tussen alle componenten.

### **9.6.4. CQRS (Command Query Responsibility Segregation)**

* **Principe:** We hanteren een strikte scheiding tussen operaties die data lezen (Queries) en operaties die de staat van de applicatie veranderen (Commands). Een methode mag óf data retourneren, óf data wijzigen, maar nooit beide tegelijk. Dit principe voorkomt onverwachte bijeffecten en maakt het gedrag van het systeem glashelder en voorspelbaar.  
* **Implementatie in de Service Laag:** Dit principe is het meest expliciet doorgevoerd in de architectuur van onze data-services, waar we een duidelijke scheiding hebben tussen *lezers* en *schrijvers*:  
  1. **Query Services (Lezers):**  
     * **Naamgeving:** Services die uitsluitend data lezen, krijgen de QueryService-suffix (bv. PluginQueryService).  
     * **Methodes:** Alle publieke methodes in een Query Service zijn "vragen" en beginnen met het get\_ prefix (bv. get\_coverage).  
     * **Contract:** De DTO's die deze methodes accepteren, krijgen de Query-suffix (bv. CoverageQuery).  
  2. **Command Services (Schrijvers):**  
     * **Naamgeving:** Services die de staat van de data veranderen, krijgen de CommandService-suffix (bv. DataCommandService).  
     * **Methodes:** Alle publieke methodes in een Command Service zijn "opdrachten" en hebben een actieve, werkwoordelijke naam die de actie beschrijft (bv. synchronize, fetch\_period).  
     * **Contract:** De DTO's die deze methodes accepteren, krijgen de Command-suffix (bv. SynchronizationCommand).  
* **Scope:** Deze CQRS-naamgevingsconventie is de standaard voor alle services binnen de Service-laag die direct interacteren met de staat van data of het systeem. Het naleven van deze conventie is verplicht om de voorspelbaarheid en onderhoudbaarheid van de codebase te garanderen.