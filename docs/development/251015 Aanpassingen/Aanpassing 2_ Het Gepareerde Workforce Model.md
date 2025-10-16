# **Aanpassing 2: Het "Geprepareerde Workforce Model"**

**Versie:** 3.1

**Status:** Definitief Amendement

Dit document beschrijft de architecturale wijziging die de verantwoordelijkheid voor het classificeren van workers verplaatst van de operationele BaseOperator naar de setup-laag. Dit resulteert in een zuivere scheiding van verantwoordelijkheden (SRP) en maakt de Operator een pure, "domme" uitvoerder.

### **1\. Omschrijving van de Wijziging**

Samenvatting:  
De BaseOperator is niet langer verantwoordelijk voor het 'ontdekken' of sorteren van verschillende soorten workers (standaard vs. event-driven) tijdens runtime. Deze verantwoordelijkheid verschuift volledig naar de setup-laag. De OperatorFactory roept de WorkerBuilder aan, die nu een Workforce DTO retourneert met daarin twee gescheiden lijsten: standard\_workers en event\_driven\_workers. De BaseOperator ontvangt bij zijn creatie alleen de lijst met standard\_workers die hij moet orkestreren en past zijn geconfigureerde ExecutionStrategy uitsluitend op die lijst toe. De event-gedreven workers worden tijdens de setup-fase al direct via hun adapter aan de EventBus gekoppeld en leiden daarna een autonoom leven.  
Rationale (De "Waarom"):  
Dit model lost een fundamentele SRP-schending op die in een eerder model was geslopen:

1. **Zuivere Scheiding van Verantwoordelijkheden:** De Operator is een **operationele** component; zijn enige taak is het *uitvoeren* van een vooraf gedefinieerde pijplijn. Het inspecteren van configuraties en het sorteren van workers is een **setup**\-taak. Deze wijziging plaatst de setup-logica daar waar die hoort: in de factories (OperatorFactory en WorkerBuilder) van de assembly-laag.  
2. **Verhoogde Performance en Eenvoud:** De Operator wordt eenvoudiger en sneller. Zijn run\_pipeline methode hoeft niet bij elke aanroep de workers te filteren. Hij ontvangt een kant-en-klare lijst en voert zijn taak uit.  
3. **Robuustheid:** De logica voor het classificeren van workers bevindt zich nu op één enkele, voorspelbare plek (WorkerBuilder), wat het systeem robuuster en makkelijker te onderhouden maakt. Het voorkomt "gestuntel" en onduidelijke regels binnen de Operator.

### **2\. Technische Implementatie & Gevolgen**

De Rol van de Workforce DTO:  
Er wordt een Workforce DTO geïntroduceerd. Dit DTO dient als het expliciete data contract voor de output van de WorkerBuilder. Het bevat de gescheiden lijsten van geclassificeerde workers.  
\# backend/dtos/assembly/workforce.py  
class Workforce(BaseModel):  
    standard\_workers: List\[BaseWorker\] \= Field(default\_factory=list)  
    event\_driven\_workers: List\[BaseWorker\] \= Field(default\_factory=list)

De Rol van de WorkerBuilder (De Chef-kok):  
De WorkerBuilder krijgt een nieuwe hoofd-methode, build\_workforce\_for\_operator, die een lijst van worker-configuraties accepteert en één Workforce DTO retourneert, waarin de workers al correct zijn geclassificeerd op basis van de capabilities-sectie in hun manifest.  
De Rol van de OperatorFactory (De Hoofdaannemer):  
De OperatorFactory orkestreert het proces. Hij roept de WorkerBuilder aan om de Workforce te prepareren. Vervolgens creëert hij de BaseOperator-instantie en geeft alleen de standard\_workers uit het Workforce DTO door aan de constructor. De event\_driven\_workers worden met rust gelaten, aangezien hun levenscyclus al is gestart door de WorkerBuilder (die hun adapters heeft aangemeld bij de EventBus).  
De Rol van de BaseOperator (De "Domme" Uitvoerder):  
De BaseOperator wordt extreem simpel. Hij ontvangt in zijn constructor een enkele lijst met workers die hij moet beheren. Zijn run\_pipeline methode past zijn ExecutionStrategy direct toe op deze lijst, zonder enige kennis van of logica voor het bestaan van andere (event-gedreven) workers.

### **3\. Lijst van Geraakte Documenten**

De implementatie van dit model vereist aanpassingen in de volgende documenten:

1. 2\_ARCHITECTURE.md (Update van de rol van de Operator en de Assembly-laag)  
2. 5\_DE\_WORKFLOW\_ORKESTRATIE.md (Verduidelijking van de Operator-interactie)  
3. 8\_DEVELOPMENT\_STRATEGY.md (Beschrijving van de zuivere Operator-teststrategie)  
4. 10\_CODING\_STANDAARDS\_DESIGN\_PRINCIPLES.md (Benadrukken van dit SRP-patroon)  
5. A\_BIJLAGE\_TERMINOLOGIE.md (Toevoegen/bijwerken van Workforce DTO, OperatorFactory)  
6. V3\_COMPLETE\_SYSTEM\_DESIGN.md (Update van de pseudo-code voor BaseOperator, WorkerBuilder en OperatorFactory)