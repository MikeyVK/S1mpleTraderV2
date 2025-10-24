# Coding Standaarden & Design Principles

**Versie:** 3.0
**Status:** Definitief

Dit document beschrijft de verplichte standaarden en best practices voor het schrijven van alle code binnen het S1mpleTrader-project.

---

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Code Kwaliteit & Stijl](#code-kwaliteit--stijl)
3. [Contract-Gedreven Ontwikkeling](#contract-gedreven-ontwikkeling)
4. [Dependency Injection Principes](#dependency-injection-principes)
5. [Configuratie-Gedreven Design](#configuratie-gedreven-design)
6. [Design Principles & Kernconcepten](#design-principles--kernconcepten)

---

## **Executive Summary**

Dit document legt de fundering voor een consistente, leesbare, onderhoudbare en robuuste codebase voor S1mpleTrader. Het naleven van deze standaarden is niet optioneel en is cruciaal voor het succes van het project.

### **Kernprincipes**

**1. Strikte Code Kwaliteit en Stijl**
-   Alle code is **PEP 8 compliant** met een maximale regellengte van 100 tekens.
-   **Volledige type hinting** is verplicht.
-   **Engelse docstrings** in Google Style zijn de standaard voor alle bestanden, klassen en functies.

**2. Contract-Gedreven Ontwikkeling**
-   Alle data die tussen componenten wordt uitgewisseld, wordt ingekapseld in **Pydantic BaseModels**.
-   Uitwisselbare componenten erven van **abstracte basisklassen (Interfaces)**.

**3. Dependency Injection als Kernpatroon**
-   **Constructor Injection** is de standaard voor alle dependencies.
-   Componenten zijn afhankelijk van **abstracties (interfaces)**, niet van concrete implementaties.
-   Een **Gecentraliseerd Factory Model** (`PersistorFactory`, `EventAdapterFactory`, `OperatorFactory`) beheert de creatie van complexe objecten.

**4. Scheiding van ROL en CAPABILITIES**
-   De **ROL** van een worker wordt bepaald door de keuze van de basisklasse (`StandardWorker` of `EventDrivenWorker`).
-   De **CAPABILITIES** (extra vaardigheden) worden expliciet aangevraagd in het `manifest.yaml` en dynamisch geïnjecteerd.

**5. Configuratie-Gedreven Design**
-   Het principe **"YAML is intelligentie, code is mechanica"** is leidend.

### **Design Patterns**

-   **SOLID**: Strikt toegepast.
-   **Factory Pattern**: Voor het creëren van complexe objecten.
-   **Adapter Pattern**: Om plugins "bus-agnostisch" te maken.
-   **CQRS**: Strikte scheiding tussen lees- en schrijfbewerkingen.

---

## **Code Kwaliteit & Stijl**

### **Fundamenten**

*   **PEP 8 Compliant:** Alle Python-code moet strikt voldoen aan de [PEP 8](https://peps.python.org/pep-0008/) stijlgids.
    *   **Regellengte:** Maximaal 100 tekens.
    *   **Naamgeving:** snake_case voor variabelen/functies, PascalCase voor klassen.
*   **Volledige Type Hinting:** Alle functies, methodes en variabelen moeten volledig getypeerd zijn.
*   **Commentaar in het Engels:** Alle commentaar en docstrings moeten in het Engels zijn.

### **Gestructureerde Docstrings**

*   **Bestands-Header Docstring:** Elk .py-bestand begint met een gestandaardiseerde header.
*   **Imports:** Standaard bibliotheek, dan third-party, dan applicatie-specifiek.
*   **Functie & Methode Docstrings (Google Style):** Gebruik Google Style voor alle functies en methodes.

### **Naamgevingsconventies**

*   **Interfaces:** Prefix met `I` (bv. `IAPIConnector`).
*   **Interne Attributen:** Prefix met `_` (bv. `_app_config`).

---

## **Contract-Gedreven Ontwikkeling**

### **Pydantic voor alle Data-Structuren**

Alle data die tussen componenten wordt doorgegeven, moet worden ingekapseld in een **Pydantic BaseModel**.

### **Abstracte Basisklassen (Interfaces)**

Componenten die uitwisselbaar moeten zijn, moeten erven van een gemeenschappelijke abstracte basisklasse (ABC).

---

## **Dependency Injection Principes**

### **Constructor Injection als Standaard**

Alle dependencies worden geïnjecteerd via de constructor.

### **ROL-definitie en Capability-injectie**

Componenten hangen af van abstracties, niet van concrete implementaties. De architectuur scheidt de **ROL** van een worker van zijn **CAPABILITIES**.

### **Gecentraliseerd Factory Model**

Complexe object-constructie gebeurt via **gespecialiseerde, gecentraliseerde factories**.

---

## **Configuratie-Gedreven Design**

"**YAML is intelligentie, code is mechanica**"

Het gedrag van het systeem wordt gedefinieerd in configuratie, niet in de code.

---

## **Design Principles & Kernconcepten**

### **SOLID in de Praktijk**

*   **SRP:** Elke klasse heeft één duidelijke taak.
*   **OCP:** Uitbreidbaar zonder bestaande code te wijzigen.
*   **DIP:** Hoge-level modules hangen af van abstracties.

### **Kernpatronen**

*   **Factory Pattern:** Voor het creëren van complexe objecten.
*   **Strategy Pattern:** Plugins als uitwisselbare strategieën.
*   **Adapter Pattern:** Maakt componenten "bus-agnostisch".
*   **DTO's:** Pydantic-modellen voor voorspelbare dataflow.
*   **CQRS:** Scheiding tussen lees- en schrijfbewerkingen.

---

## **Referenties**

- **[Component Architectuur](04_System_Architecture/01_Component_Architecture.md)** - Systeemlagen
- **[Data Architectuur](04_System_Architecture/02_Data_Architecture.md)** - DTOs en persistence
- **[Plugin Anatomy](03_Development/01_Plugin_Anatomy.md)** - Plugin structuur

---

**Einde Document**