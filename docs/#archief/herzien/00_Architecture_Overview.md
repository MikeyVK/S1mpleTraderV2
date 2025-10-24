# 0_Architecture_Overview.md

# **S1mpleTrader: Architectonische Blauwdruk**

Dit document dient als de centrale gids voor een systeem dat is ontworpen als een agnostisch **besturingssysteem** voor kwantitatieve strategen.

De kernvisie is dat het platform zelf geen specifieke manier van handelen afdwingt. Zijn enige doel is het bieden van een extreem robuust, flexibel en schaalbaar **framework**. Binnen dit framework kan een quant alle mogelijke kwantitatieve en operationele functionaliteit implementeren via zelfstandige, specialistische plugins.

**Paradigma: "Configuratie is Koning"**

De architectuur benadrukt de configuratie-gedreven natuur van het systeem. Het 5-categorie worker ecosysteem (Context, Opportunity, Threat, Planning, Execution) wordt aangestuurd door data-gedreven operators die hun gedrag volledig ontlenen aan configuratie. De Persistence Suite garandeert atomische betrouwbaarheid, terwijl het Causale ID Framework volledige traceerbaarheid biedt van elke beslissing.

De configuratie is het draaiboek; de plugins zijn de acteurs; het platform is het podium.

Deze documentatie beschrijft de architectuur die deze visie mogelijk maakt.

## **De Architectuur in Hoofdstukken**

### **Hoofdstuk 1: De Communicatie Architectuur**

De kern van de architectuur is de radicale scheiding tussen business- en communicatielogica. Dit hoofdzakelijk beschrijft het EventAdapter-patroon en de rol van de `wiring_map.yaml`, die samen het "zenuwstelsel" van het platform vormen.

**→ Lees de volledige uitwerking in: `1_Bus_communicatie_structuur.md`**

### **Hoofdstuk 2: Architectuur & Componenten**

Dit hoofdzakelijk beschrijft de strikt gelaagde opbouw (Backend, Service, Frontend) en introduceert het **5-categorie worker ecosysteem** (Context, Opportunity, Threat, Planning, Execution) met 27 sub-categorieën. Centraal staat het concept van **data-gedreven operators** en de geïntegreerde **Persistence Suite** voor atomische betrouwbaarheid.

**→ Lees de volledige uitwerking in: `2_Architectuur_Componenten.md`**

### **Hoofdstuk 3: De Configuratie Trein**

Configuratie is de kern van het systeem. Dit document is een gedetailleerde gids voor de volledige hiërarchie van YAML-bestanden, van `platform.yaml` tot `plugin_manifest.yaml`, die samen een volledige Operation definiëren. Inclusief de `operators.yaml` voor operator gedragsconfiguratie.

**→ Lees de volledige uitwerking in: `3_Configuratie_Trein.md`**

### **Hoofdstuk 4: De Anatomie van een Plugin**

Een plugin is de fundamentele, zelfstandige en testbare eenheid van logica. Dit hoofdzakelijk beschrijft de mappenstructuur, het `manifest.yaml`, het `schema.py` en de vijf worker types met **27 sub-categorieën**. Ook worden de **gelaagde plugin capabilities** beschreven (Pure Logic, Stateful, Event-Aware, Journaling).

**→ Lees de volledige uitwerking in: `4_Plugin_Anatomie.md`**

### **Hoofdstuk 5: De Analytische Pijplijn**

De kern van elke analytische strategie is de pijplijn die een idee stapsgewijs valideert. Dit hoofdzakelijk beschrijft het **parallel event-driven model** over 3 abstractieniveaus (Workers → Operators → Engine) en de workflow van opportuniteit detectie naar trade executie via het 5-categorie ecosysteem.

**→ Lees de volledige uitwerking in: `5_Workflow_Orkestratie.md`**

### **Hoofdstuk 6: Frontend Integration**

Dit hoofdzakelijk beschrijft de web-based frontend architectuur voor S1mpleTrader, inclusief de **Operator Configuration UI** voor visueel configureren van worker ecosystemen, de **Causale Trade Explorer** voor post-mortem analyse met volledige causale tracking, en de Plugin IDE voor ontwikkeling en testing.

**→ Lees de volledige uitwerking in: `6_Frontend_Integration.md`**

### **Hoofdstuk 7: Robuustheid & Operationele Betrouwbaarheid**

Een live trading-systeem moet veerkrachtig zijn. Dit hoofdzakelijk beschrijft de verdedigingslinies: de **Persistence Suite** met atomische schrijfacties (journaling), protocollen voor netwerkveerkracht, het Supervisor-model voor crash recovery, en het **Traceability Framework** voor volledige causale analyse.

**→ Lees de volledige uitwerking in: `7_Robuustheid_Operations.md`**

### **Hoofdstuk 8: Ontwikkelstrategie & Tooling**

Dit document beschrijft de workflow en tooling, van de visuele 'Strategy Builder' tot de 'Causale Trade Explorer' en de cruciale rol van het Causale ID Framework voor volledige traceerbaarheid van elke beslissing in het systeem.

**→ Lees de volledige uitwerking in: `8_Development_Strategy.md`**

### **Hoofdstuk 9: Meta Workflows**

Bovenop de executie van een enkele strategie draaien "Meta Workflows" om geavanceerde analyses uit te voeren. Dit hoofdzakelijk beschrijft de `OptimizationService` en `VariantTestService`.

**→ Lees de volledige uitwerking in: `9_Meta_Workflows.md`**

### **Hoofdstuk 10: Coding Standaarden & Design Principles**

Een consistente codebase is essentieel. Dit hoofdzakelijk beschrijft de verplichte standaarden (PEP 8, Type Hinting) en de kern design principles (SOLID, Factory Pattern, DTO's), inclusief de interface-driven Persistence Suite architectuur.

**→ Lees de volledige uitwerking in: `10_Coding_Standards.md`**

## **Bijlages**

*   **Bijlage A: Terminologie**: Een uitgebreid, alfabetisch naslagwerk met beschrijvingen van alle belangrijke concepten en componenten. [→ `A_Bijlage_Terminologie.md`](A_Bijlage_Terminologie.md)
*   **Bijlage B: Openstaande Vraagstukken**: Een overzicht van bekende "onbekenden" die tijdens de implementatie verder onderzocht moeten worden. [→ `B_Bijlage_Openstaande_Vraagstukken.md`](B_Bijlage_Openstaande_Vraagstukken.md)
*   **Bijlage C: MVP**: De scope en componenten van het Minimum Viable Product. [→ `C_Bijlage_MVP.pdf`](C_Bijlage_MVP.pdf)
*   **Bijlage D: Plugin IDE**: De architectuur en UX voor de web-based IDE voor plugins. [→ `D_Bijlage_Plugin_IDE.md`](D_Bijlage_Plugin_IDE.md)

---

**Einde Document**