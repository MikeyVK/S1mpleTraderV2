# **2\. Architectuur & Componenten**

Versie: 2.1 (Gecorrigeerd & Aangevuld)  
Status: Definitief

## **2.1. De Configuratie: De Bron van Waarheid**

De S1mpleTrader V2 architectuur is fundamenteel **configuratie-gedreven**. De YAML-bestanden zijn niet slechts instellingen; ze vormen het **draaiboek** dat de volledige operatie van het trading-ecosysteem beschrijft.

Een gedetailleerde gids over de hiërarchie, de rol van elk bestand en hun onderlinge samenhang is vastgelegd in een apart document om dit hoofdstuk gefocust te houden op de softwarecomponenten.

**→ Lees de volledige uitwerking in: system/3\_DE\_CONFIGURATIE\_TREIN.md**

## **2.2. De Gelaagde Architectuur: Een Strikte Scheiding**

De applicatie is opgebouwd uit drie strikt gescheiden lagen die een **eenrichtingsverkeer** van afhankelijkheden afdwingen.

* **Backend Laag (/backend)**: De **"Motor & Gereedschapskist"**. Bevat alle herbruikbare, agnostische en pure businesslogica (klassen, DTO's, interfaces). Deze laag is volledig onafhankelijk en heeft geen kennis van de Service Laag of de EventBus. Het is een pure, importeerbare library.  
* **Service Laag (/services)**: De **"Orkestratielaag"**. Dit is de enige laag die de EventBus kent en beheert via de EventAdapters. Componenten hier orkestreren complete business workflows door de "gereedschappen" uit de Backend-laag aan te roepen in reactie op events.  
* **Frontend Laag (/frontends)**: De **"Gebruikersinterface"**. Verantwoordelijk voor alle gebruikersinteractie en communiceert uitsluitend met de Service Laag via een BFF (Backend-for-Frontend) API.

## **2.3. De Functionele Pijlers: De Vier Rollen**

Alle businesslogica in het systeem is ondergebracht in vier duidelijk gescheiden, functionele categorieën. Elke categorie bestaat uit een **Worker** (de plugin met de daadwerkelijke logica) en een **Operator** (de manager in de Service Laag die de workers aanstuurt).

| Quant's Doel | Hoofdverantwoordelijkheid | Plugin Categorie (De "Worker") | De Manager (De "Operator") |
| :---- | :---- | :---- | :---- |
| "Ik wil mijn data voorbereiden" | **Contextualiseren** | ContextWorker | ContextOperator |
| "Ik wil een handelsidee ontwikkelen" | **Analyseren** | AnalysisWorker | AnalysisOperator |
| "Ik wil de situatie in de gaten houden" | **Monitoren** | MonitorWorker | MonitorOperator |
| "Ik wil een regel direct laten uitvoeren" | **Executeren** | ExecutionWorker | ExecutionOperator |

## **2.4. Componenten in Detail**

### **Context Pijler (Voorbereiden)**

* **ContextWorker (Plugin, Backend)**: Verrijkt ruwe marktdata met analytische context (indicatoren, marktstructuur, etc.).  
* **ContextOperator (Service Laag)**: Orkestreert de executie van de ContextWorker-pijplijn.

### **Analysis Pijler (Analyseren)**

* **AnalysisWorker (Plugin, Backend)**: Genereert **niet-deterministische, analytische handelsvoorstellen**.  
* **AnalysisOperator (Service Laag)**: Orkestreert de AnalysisWorker-pijplijn.

### **Monitor Pijler (Monitoren)**

* **MonitorWorker (Plugin, Backend)**: Observeert de operatie en publiceert informatieve, **strategische events**. Handelt **nooit** zelf.  
* **MonitorOperator (Service Laag)**: Zorgt ervoor dat de juiste MonitorWorkers worden aangeroepen.

### **Execution Pijler (Executeren)**

* **ExecutionWorker (Plugin, Backend)**: Voert **deterministische, op regels gebaseerde acties** uit.  
* **ExecutionOperator (Service Laag)**: Keurt voorstellen goed en geeft de definitieve opdracht aan de ExecutionEnvironment.

### **Ondersteunende Componenten**

* **ComponentBuilder (Backend Laag)**: Een specialist binnen het Assembly Team. Verantwoordelijk voor het lezen van de strategy\_blueprint.yaml en het daadwerkelijk assembleren en instantiëren van alle benodigde Operator- en Worker-componenten voor een specifieke strategy\_link. Dit is de opvolger van de RunOrchestrator.  
* **ContextBootstrapper (Backend Laag)**: Een essentieel component dat ervoor zorgt dat de ContextOperator een compleet en historisch correct "rollend venster" van data heeft *voordat* de eerste live tick wordt verwerkt. Dit voorkomt beslissingen op basis van onvolledige data.  
* **ExecutionEnvironment (Backend Laag)**: De technische "wereld" waarin een strategie draait (Backtest, Paper, of Live). Verantwoordelijk voor marktdata en het uitvoeren van trades.  
* **StrategyLedger (Backend Laag)**: Het "domme" financiële grootboek dat de staat (kapitaal, posities, PnL) bijhoudt voor één enkele, geïsoleerde strategie-run.  
* **Assembly Team (Backend Laag)**: De verzameling componenten (PluginRegistry, WorkerBuilder, ComponentBuilder) die verantwoordelijk is voor het ontdekken, valideren en bouwen van alle plugins en componenten.