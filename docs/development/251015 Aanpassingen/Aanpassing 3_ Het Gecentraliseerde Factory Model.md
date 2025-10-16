# **Aanpassing 3: Het Gecentraliseerde Factory Model**

Versie: 3.1  
Status: Definitief Amendement  
Dit document beschrijft de architecturale wijziging om de creatie van complexe, herbruikbare componenten, zoals adapters en persistors, te centraliseren in gespecialiseerde factories. Dit versterkt het Single Responsibility Principle (SRP) en het Don't Repeat Yourself (DRY) principe in de gehele assembly-laag.

### **1\. Omschrijving van de Wijziging**

Samenvatting:  
In de vorige architectuur hadden meerdere "builder"-componenten (zoals de WorkerBuilder en EventWiringFactory) de kennis en verantwoordelijkheid om zelf EventAdapter-instanties te creëren. Dit leidde tot gedupliceerde logica en een schending van het SRP.  
Deze wijziging introduceert een **Gecentraliseerd Factory Model**. De verantwoordelijkheid voor het creëren van een specifiek type component wordt toegewezen aan **één enkele, gespecialiseerde factory**. Andere componenten die dit type component nodig hebben, worden "klanten" van deze specialistische factory.

**Concreet betekent dit:**

1. Er wordt een nieuwe EventAdapterFactory geïntroduceerd. Dit is de **enige** component die weet hoe een EventAdapter wordt geïnstantieerd, geconfigureerd en (indien nodig) geïnjecteerd in een doelcomponent.  
2. De WorkerBuilder en EventWiringFactory worden "klanten". Hun taak wordt gereduceerd tot het **vertalen** van hun specifieke configuratiebron (manifest.yaml of wiring\_map.yaml) naar een universeel dataformaat en het aanroepen van de EventAdapterFactory.  
3. Dit patroon wordt consistent toegepast op alle vergelijkbare scenario's, zoals de PersistorFactory die de enige is die IStatePersistor en IJournalPersistor-instanties mag creëren.

**Rationale (De "Waarom"):**

* **Single Responsibility Principle (SRP):** Elke factory heeft nu één duidelijke, afgebakende taak.  
  * WorkerBuilder: Weet hoe workers te bouwen.  
  * EventAdapterFactory: Weet hoe event adapters te bouwen.  
  * PersistorFactory: Weet hoe persistors te bouwen.  
* **Don't Repeat Yourself (DRY):** De logica voor het bouwen van een adapter, inclusief de complexe "injectie" van de emit-methode, bevindt zich nu op één enkele, onderhoudbare plek.  
* **Duidelijkheid en Onderhoudbaarheid:** De stroom van afhankelijkheden wordt een heldere "keten van commando". De ContextBuilder (de hoofd-orkestrator) configureert en injecteert de specialistische factories in de builders die ze nodig hebben.

### **2\. De Architectuur in de Praktijk**

#### **De Rol van de Gespecialiseerde Factories**

* **EventAdapterFactory (De Specialist):** Zijn enige taak is het ontvangen van een target\_component (een worker of operator) en een lijst WiringInstruction DTOs, en het produceren van een volledig geconfigureerde EventAdapter.  
* **PersistorFactory (Bestaand Voorbeeld):** Deze past al perfect in dit model. Zijn enige taak is het creëren van IStatePersistor, IJournalPersistor en IDataPersistor-instanties op basis van een worker\_id of strategy\_id.

#### **De Rol van de "Klanten" (Builders & Orkestrators)**

* **WorkerBuilder & EventWiringFactory (De Vertalers):** Deze componenten zijn nu ontdaan van de bouwlogica voor adapters. Hun verantwoordelijkheid is gereduceerd tot het **vertalen** van hun specifieke configuratiebron naar een universeel formaat en het aanroepen van de juiste specialistische factory.  
* **ContextBuilder (De Hoofd-Orkestrator):** Creëert de specialistische factories en injecteert ze als dependencies in de builders die ze nodig hebben.

#### **Visueel Stroomdiagram van de Samenwerking**

graph TD  
    subgraph "Configuratie (De Bron)"  
        Manifest\["manifest.yaml"\]  
        WiringMap\["wiring\_map.yaml"\]  
    end

    subgraph "Assembly Laag (De Vertalers & Specialist)"  
        A\[WorkerBuilder\] \-- Vertaling \--\> B(List\[WiringInstruction\])  
        C\[EventWiringFactory\] \-- Vertaling \--\> B  
        B \-- "Geef mij een adapter voor\<br/\>deze instructies en dit component" \--\> D{EventAdapterFactory}  
    end

    subgraph "Resultaat"  
        E\[EventAdapter Instantie\]  
    end

    Manifest \-- leest \--\> A  
    WiringMap \-- leest \--\> C  
    D \-- creëert \--\> E

    style D fill:\#FFE082,stroke:\#333

### **3\. De WiringTranslator Utility**

Om de vertaallogica (van YAML-structuur naar WiringInstruction DTOs) te centraliseren en herbruikbaar te maken, introduceren we een WiringTranslator.

* **Doel:** Een stateless utility die een events- en wirings-configuratielijst accepteert en een lijst WiringInstruction DTOs retourneert.  
* **Locatie (backend/assembly/):** We plaatsen deze utility bewust in de assembly-laag, en niet in backend/utils/.  
  * **Reden:** Een util is per definitie generiek en breed inzetbaar in de hele applicatie (bv. een data\_utils.py voor pandas-operaties). De WiringTranslator daarentegen is een **hoog-gespecialiseerde tool** die **exclusief wordt gebruikt door de componenten in de assembly-laag** (WorkerBuilder, EventWiringFactory). Zijn enige doel is het ondersteunen van het *assemblageproces*. Hij hoort daarom thuis in de "gereedschapskist" van de "bouwploeg": de assembly-laag.

### **4\. Lijst van Geraakte Documenten**

De implementatie van dit model vereist aanpassingen in de volgende documenten om consistentie te waarborgen:

1. 2\_ARCHITECTURE.md  
2. 4\_DE\_PLUGIN\_ANATOMIE.md  
3. 8\_DEVELOPMENT\_STRATEGY.md  
4. 10\_CODING\_STANDAARDS\_DESIGN\_PRINCIPLES.md  
5. A\_BIJLAGE\_TERMINOLOGIE.md  
6. V3\_COMPLETE\_SYSTEM\_DESIGN.md