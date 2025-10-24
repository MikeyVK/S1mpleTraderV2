# **S1mpleTrader V2 Development: Architectonische Blauwdruk**

Versie: 3.0 (Architectuur Blauwdruk v5)
Status: Definitief

## **Voorwoord: Kernfilosofie \- Het Platform als Framework**

Welkom bij de architectonische blauwdruk voor S1mpleTrader V2. Dit document dient als de centrale gids voor een systeem dat is geëvolueerd van een applicatie naar een agnostisch **besturingssysteem** voor kwantitatieve strategen.

De kernvisie is dat het platform zelf geen specifieke manier van handelen afdwingt. Zijn enige doel is het bieden van een extreem robuust, flexibel en schaalbaar **framework**. Binnen dit framework kan een quant alle mogelijke kwantitatieve en operationele functionaliteit implementeren via zelfstandige, specialistische plugins.

**V3 Paradigma: "Operators zijn dom, configuratie is slim"**

De evolutie naar V3 benadrukt de configuratie-gedreven natuur van het systeem nog sterker. Het 5-categorie worker ecosysteem (Context, Opportunity, Threat, Planning, Execution) wordt aangestuurd door data-gedreven operators die hun gedrag volledig ontlenen aan configuratie. De Persistence Suite garandeert atomische betrouwbaarheid, terwijl het Causale ID Framework volledige traceerbaarheid biedt van elke beslissing.

De configuratie is het draaiboek; de plugins zijn de acteurs; het platform is het podium.

Deze documentatie beschrijft de architectuur die deze visie mogelijk maakt.

## **De Architectuur in Hoofdstukken**

### **Hoofdstuk 1: De Communicatie Architectuur**

De kern van de V2-architectuur is de radicale scheiding tussen business- en communicatielogica. Dit hoofdstuk beschrijft het EventAdapter-patroon en de rol van de wiring\_map.yaml, die samen het "zenuwstelsel" van het platform vormen.

**→ Lees de volledige uitwerking in: system/1\_BUS\_COMMUNICATION\_ARCHITECTURE.md**

### **Hoofdstuk 2: Architectuur & Componenten**

Dit hoofdstuk beschrijft de strikt gelaagde opbouw (Backend, Service, Frontend) en introduceert het **5-categorie worker ecosysteem** (Context, Opportunity, Threat, Planning, Execution) met 27 sub-categorieën. Centraal staat het concept van **data-gedreven operators** en de geïntegreerde **Persistence Suite** voor atomische betrouwbaarheid.

**→ Lees de volledige uitwerking in: [`2_ARCHITECTURE.md`](2_ARCHITECTURE.md)**

### **Hoofdstuk 3: De Configuratie Trein**

Configuratie is koning in V2. Dit document is een gedetailleerde gids voor de volledige hiërarchie van YAML-bestanden, van [`platform.yaml`](../../config/platform.yaml) tot [`plugin_manifest.yaml`](../../plugins/structural_context/ema_detector/manifest.yaml), die samen een volledige Operation definiëren. Inclusief de nieuwe [`operators.yaml`](../../config/operators.yaml) voor operator gedragsconfiguratie.

**→ Lees de volledige uitwerking in: [`3_DE_CONFIGURATIE_TREIN.md`](3_DE_CONFIGURATIE_TREIN.md)**

### **Hoofdstuk 4: De Anatomie van een Plugin**

Een plugin is de fundamentele, zelfstandige en testbare eenheid van logica. Dit hoofdstuk beschrijft de mappenstructuur, het [`manifest.yaml`](../../plugins/structural_context/ema_detector/manifest.yaml), het [`schema.py`](../../plugins/structural_context/ema_detector/schema.py) en de vijf worker types met **27 sub-categorieën**. Ook worden de **gelaagde plugin capabilities** beschreven (Pure Logic, Stateful, Event-Aware, Journaling).

**→ Lees de volledige uitwerking in: [`4_DE_PLUGIN_ANATOMIE.md`](4_DE_PLUGIN_ANATOMIE.md)**

### **Hoofdstuk 5: De Analytische Pijplijn**

De kern van elke analytische strategie is de pijplijn die een idee stapsgewijs valideert. Dit hoofdstuk beschrijft het **parallel event-driven model** over 3 abstractieniveaus (Workers → Operators → Engine) en de workflow van opportuniteit detectie naar trade executie via het 5-categorie ecosysteem.

**→ Lees de volledige uitwerking in: [`5_DE_WORKFLOW_ORKESTRATIE.md`](5_DE_WORKFLOW_ORKESTRATIE.md)**

### **Hoofdstuk 6: Frontend Integration**

Dit hoofdstuk beschrijft de web-based frontend architectuur voor S1mpleTrader V2, inclusief de **Operator Configuration UI** voor visueel configureren van worker ecosystemen, de **Causale Trade Explorer** voor post-mortem analyse met volledige causale tracking, en de Plugin IDE voor ontwikkeling en testing.

**→ Lees de volledige uitwerking in: [`6_FRONTEND_INTEGRATION.md`](6_FRONTEND_INTEGRATION.md)**

### **Hoofdstuk 7: Robuustheid & Operationele Betrouwbaarheid**

Een live trading-systeem moet veerkrachtig zijn. Dit hoofdstuk beschrijft de verdedigingslinies: de **Persistence Suite** met atomische schrijfacties (journaling), protocollen voor netwerkveerkracht, het Supervisor-model voor crash recovery, en het **Traceability Framework** voor volledige causale analyse.

**→ Lees de volledige uitwerking in: [`7_RESILIENCE_AND_OPERATIONS.md`](7_RESILIENCE_AND_OPERATIONS.md)**

### **Hoofdstuk 8: Ontwikkelstrategie & Tooling**

Dit document beschrijft de workflow en tooling, van de visuele 'Strategy Builder' tot de 'Causale Trade Explorer' en de cruciale rol van het Causale ID Framework voor volledige traceerbaarheid van elke beslissing in het systeem.

**→ Lees de volledige uitwerking in: [`8_DEVELOPMENT_STRATEGY.md`](8_DEVELOPMENT_STRATEGY.md)**

### **Hoofdstuk 9: Meta Workflows**

Bovenop de executie van een enkele strategie draaien "Meta Workflows" om geavanceerde analyses uit te voeren. Dit hoofdstuk beschrijft de [`OptimizationService`](../../services/optimization_service.py) en [`VariantTestService`](../../services/variant_test_service.py).

**→ Lees de volledige uitwerking in: [`9_META_WORKFLOWS.md`](9_META_WORKFLOWS.md)**

### **Hoofdstuk 10: Coding Standaarden & Design Principles**

Een consistente codebase is essentieel. Dit hoofdstuk beschrijft de verplichte standaarden (PEP 8, Type Hinting) en de kern design principles (SOLID, Factory Pattern, DTO's), inclusief de nieuwe interface-driven Persistence Suite architectuur.

**→ Lees de volledige uitwerking in: [`10_CODING_STANDAARDS_DESIGN_PRINCIPLES.md`](10_CODING_STANDAARDS_DESIGN_PRINCIPLES.md)**

## **Bijlages**

* **Bijlage A: Terminologie**: Een uitgebreid, alfabetisch naslagwerk met beschrijvingen van alle belangrijke concepten en componenten. [→ `A_BIJLAGE_TERMINOLOGIE.md`](A_BIJLAGE_TERMINOLOGIE.md)
* **Bijlage B: Openstaande Vraagstukken**: Een overzicht van bekende "onbekenden" die tijdens de implementatie verder onderzocht moeten worden. [→ `B_BIJLAGE_OPENSTAANDE_VRAAGSTUKKEN.md`](B_BIJLAGE_OPENSTAANDE_VRAAGSTUKKEN.md)
* **Bijlage C: MVP**: De scope en componenten van het Minimum Viable Product. [→ `C_BIJLAGE_MVP.pdf`](C_BIJLAGE_MVP.pdf)
* **Bijlage D: Plugin IDE**: De architectuur en UX voor de web-based IDE voor plugins. [→ `D_BIJLAGE_PLUGIN_IDE.md`](D_BIJLAGE_PLUGIN_IDE.md)

## **Referenties**

* **Migratie Map**: Volledige mapping van V2 naar V3 concepten en terminologie. [→ `MIGRATION_MAP.md`](MIGRATION_MAP.md)
* **Worker Taxonomie V3**: Gedetailleerde uitwerking van het 5-categorie ecosysteem met 27 sub-types. [→ `../development/251014 Bijwerken documentatie/WORKER_TAXONOMIE_V3.md`](../development/251014%20Bijwerken%20documentatie/WORKER_TAXONOMIE_V3.md)
* **Verfijningen & Afwijkingen**: Overdrachtsdocument met alle architectonische verfijningen. [→ `../development/251014 Bijwerken documentatie/Overdrachtsdocument_ Verfijningen en Afwijkingen op de S1mpleTrader V2 Architectuur.md`](../development/251014%20Bijwerken%20documentatie/Overdrachtsdocument_%20Verfijningen%20en%20Afwijkingen%20op%20de%20S1mpleTrader%20V2%20Architectuur.md)