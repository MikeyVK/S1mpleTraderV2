# **Bijlage D: De Plugin Development Experience & IDE**

**Versie:** 1.0 · **Status:** Concept

Dit document beschrijft de architectuur en de gebruikerservaring (UX) voor de web-based Integrated Development Environment (IDE) voor plugins binnen S1mpleTrader V2. Het doel van deze IDE is om het ontwikkelen van plugins te transformeren van een puur technische taak naar een laagdrempelige, creatieve en domein-specifieke functie voor kwantitatieve analisten ("quants").

---

## **F.1. Kernfilosofie: Abstractie & Glijdende Schaal**

De fundamentele uitdaging van elk plugin-systeem is de balans tussen gebruiksgemak en de kracht van code. Om dit op te lossen, hanteren we twee kernprincipes:

1. **Abstractie van Complexiteit**: De quant wordt volledig ontlast van de onderliggende technische en beveiligingscomplexiteit van het platform. Concepten als `Protocols`, `sandboxing`, `Pydantic-validatie` en `code signing` zijn de verantwoordelijkheid van het platform en worden onzichtbaar op de achtergrond afgehandeld.  
2. **Glijdende Schaal van Abstractie**: De IDE is geen "one-size-fits-all" oplossing. Het biedt een gelaagd model met verschillende abstractieniveaus. De quant kan zelf kiezen hoe diep hij in de code wil duiken, afhankelijk van zijn vaardigheden en de complexiteit van de strategie die hij wil bouwen.

---

## **F.2. De MVP: De "Slimme Boilerplate Generator"**

De eerste, meest cruciale stap is het bouwen van een Minimum Viable Product (MVP) dat het grootste pijnpunt voor de ontwikkelaar oplost: het handmatig aanmaken van de repetitieve boilerplate-code.

### **F.2.1. De "Nieuwe Plugin" Wizard**

Het hart van de MVP is een eenvoudig, gebruiksvriendelijk formulier in de Web IDE dat de ontwikkelaar door de creatie van een nieuwe plugin leidt. De focus ligt op de *intentie* van de plugin, niet op de technische implementatie.

**Velden in het Formulier:**

* **Display Naam**  
  * **UI Element**: Tekstveld.  
  * **Doel**: De mens-leesbare naam van de plugin zoals deze overal in de UI (strategie-bouwer, rapporten, grafieken) zal verschijnen.  
  * **Voorbeeld**: `Snelle EMA Crossover`  
* **Technische Naam**  
  * **UI Element**: *Read-only* tekstveld dat dynamisch wordt bijgewerkt.  
  * **Doel**: De `snake_case` identifier die intern wordt gebruikt voor map- en bestandsnamen. Dit veld wordt automatisch afgeleid van de Display Naam, waardoor de quant `snake_case` niet hoeft te kennen.  
  * **Voorbeeld**: `snelle_ema_crossover`  
* **Plugin Type**  
  * **UI Element**: Dropdown-menu.  
  * **Doel**: Bepaalt de rol van de plugin in de strategie-pijplijn.  
  * **Abstractie**: De opties in de dropdown zijn mensvriendelijke, vertaalde beschrijvingen (bv. "Signaal Generator (De Verkenner)"), niet de technische `enum`\-waarden (`signal_generator`). Het platform vertaalt de keuze van de gebruiker op de achtergrond naar de juiste technische waarde.  
* **Beschrijving & Auteur (Optioneel)**  
  * **UI Element**: Tekstvelden.  
  * **Doel**: Verrijken de `plugin_manifest.yaml` en de docstrings direct bij de creatie.

### **F.2.2. De Template-gedreven `PluginCreator`**

Op de backend wordt een `PluginCreator` in de `assembly` module verantwoordelijk voor het genereren van de bestanden. Deze service gebruikt een set van template-bestanden (`.tpl`) die de volledige, correcte en linter-vriendelijke boilerplate bevatten, inclusief:

* Een `plugin_manifest.yaml` met een standaard restrictief `permissions` blok.  
* Een `worker.py` met de correcte klasse-definitie en interface.  
* Lege `schema.py` en `context_schema.py` bestanden.  
* Een `tests/test_worker.py` met een placeholder-test.

Voor de MVP stopt de verantwoordelijkheid van de IDE hier. De ontwikkelaar opent de gegenereerde bestanden in zijn favoriete lokale IDE (bv. VS Code) om de daadwerkelijke logica te schrijven en de tests uit te voeren via de command-line.

---

## **F.3. De Toekomstvisie: Een Gelaagde Web IDE**

Na de MVP wordt de Web IDE uitgebreid tot een volwaardige ontwikkelomgeving door de volgende drie lagen van abstractie aan te bieden voor het bewerken van de `worker.py` en `test_worker.py`.

### **Laag 1: De "No-Code" Strategie Bouwer**

* **Concept**: Het bouwen van een strategie door logische "LEGO-blokjes" op een visueel canvas met elkaar te verbinden.  
* **Interface**: Een drag-and-drop interface met een bibliotheek van door het platform aangeboden functies (Indicatoren, Vergelijkingen, Signaal Acties).  
* **Voorbeeld**: `[EMA(10)]` \-\> `[Kruist Boven]` \-\> `[EMA(50)]` \-\> `[Genereer Long Signaal]`.  
* **Testen**: Volledig geautomatiseerd via een scenario-bouwer ("Gegeven *dit* scenario, verwacht ik *deze* uitkomst").  
* **Doelgroep**: Quants zonder programmeerervaring; snelle prototyping van veelvoorkomende strategieën.

### **Laag 2: De "Low-Code" Scripting Helper**

* **Concept**: Een "Mad Libs" benadering waarbij de ontwikkelaar alleen de kernlogica invult in een gestructureerd script-venster, terwijl het platform de complexiteit van de S1mpleTrader-architectuur (DTO's, interfaces) volledig abstraheert.  
* **Interface**: Een formulier-achtige editor die de ontwikkelaar begeleidt. Indicatoren worden aangevraagd via een UI, en de kernlogica wordt geschreven in een klein Python-script dat gebruik maakt van simpele, door het platform aangeboden functies zoals `generate_signal()`.  
* **Testen**: Begeleid via een "Test Data Generator" UI en een "Assertie Helper" formulier.  
* **Doelgroep**: De gemiddelde quant die basis Python kent en zich puur wil focussen op de `if-then` logica van zijn strategie.

### **Laag 3: De "Pro-Code" Embedded IDE**

* **Concept**: Een volwaardige, in de browser geïntegreerde code-editor (zoals de Monaco Editor van VS Code) voor maximale vrijheid.  
* **Interface**: Een complete, in-browser IDE met syntax highlighting, IntelliSense voor S1mpleTrader-specifieke code, real-time linting, en de mogelijkheid om de `worker.py` en `test_worker.py` bestanden direct te bewerken.  
* **Testen**: Handmatig schrijven van `pytest` code in een apart tabblad van de editor.  
* **Doelgroep**: Ervaren ontwikkelaars of quants die zeer complexe, unieke strategieën willen bouwen die niet passen in de gestructureerde mallen van de hogere lagen.

---

## **F.4. Architectuur voor Plugin Internationalisatie (i18n)**

Om een uitwisselbaar ecosysteem te ondersteunen, moet de IDE de creatie van meertalige plugins faciliteren.

* **Structuur**: Elke plugin krijgt een eigen `locales/` map met `en.yaml`, `nl.yaml`, etc.  
* **Abstractie in de IDE**:  
  * De wizard voor het aanmaken van parameters (`schema.py`) en visualisaties (`context_schema.py`) zal geen code tonen, maar UI-formulieren.  
  * Voor elke parameter of visueel element (bv. een lijn in een grafiek) zal de UI, naast de technische configuratie, tekstvelden aanbieden voor "Display Label" en "Hulptekst".  
  * Op de achtergrond schrijft de `PluginEditorService` deze teksten niet hardcoded weg, maar genereert het de correcte `key-value` paren in de respectievelijke `locales/*.yaml` bestanden.  
* **Resultaat**: De quant vult simpele tekstvelden in, en het platform zorgt automatisch voor de volledige i18n-infrastructuur. Dit maakt het voor hem triviaal om zijn plugin meertalig te maken, wat essentieel is voor de bruikbaarheid binnen de bredere S1mpleTrader community.

