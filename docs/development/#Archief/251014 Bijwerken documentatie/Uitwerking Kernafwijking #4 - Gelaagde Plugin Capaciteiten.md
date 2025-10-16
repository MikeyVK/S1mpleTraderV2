# **Diepgaande Analyse: Gelaagde Plugin Capaciteiten via Basisklassen**

Dit document is een gedetailleerde uitwerking van **Kernafwijking \#4** uit het architectuur addendum. Het beschrijft de evolutie van een enkele, monolithische BaseWorker naar een modulair systeem van gespecialiseerde basisklassen. Deze verfijning stelt een plugin-ontwikkelaar in staat om alleen de functionaliteit te erven die hij daadwerkelijk nodig heeft, wat leidt tot schonere, veiligere en beter testbare plugins.

## **1\. Filosofie: De "Glijdende Schaal" en "Opt-In" Complexiteit**

De kernfilosofie is **"opt-in complexiteit"**, een direct gevolg van het "Glijdende Schaal van Abstractie"-principe uit de Plugin IDE-visie \[cite: system/D\_BIJLAGE\_PLUGIN\_IDE.md\]. Een simpele, stateless ContextWorker heeft geen toegang nodig tot state-persistentie of de event bus. Door deze capaciteiten op te sluiten in specifieke basisklassen, dwingt de architectuur de ontwikkelaar om een bewuste keuze te maken en wordt de standaard plugin zo simpel en veilig mogelijk gehouden.

We definiëren drie fundamentele, "cross-cutting" capaciteiten die een plugin kan bezitten:

1. **State Persistence:** Het vermogen om een intern "geheugen" te hebben.  
2. **Event Communication:** Het vermogen om met andere plugins te "praten" en te "luisteren".  
3. **Historical Journaling:** Het vermogen om bij te dragen aan het officiële "verhaal" van de strategie.

Elk van deze capaciteiten wordt gefaciliteerd door een eigen, perfect ontkoppelde architectuur, gebaseerd op het patroon van een **Interface-laag (Base...Worker)** en een **Motor (Adapter/Persistor)**.

## **2\. De Drie Kerncapaciteiten & Hun Architectuur**

### **Capaciteit 1: State Persistence (Het Geheugen)**

* **Doel:** Plugins in staat stellen om hun interne staat (bv. de high-water mark van een TrailingStopWorker) op een atomische en crash-bestendige manier te beheren.  
* **Architectuur:**  
  1. **De Interface (BaseStatefulWorker):** Biedt een simpele, **persistentie-agnostische** interface aan de ontwikkelaar: self.state om de staat te lezen/wijzigen en self.commit\_state() om deze op te slaan. De worker heeft geen kennis van *hoe* of *waar* de data wordt opgeslagen.  
  2. **De Motor (StatePersistenceAdapter):** Dit is de specialist. Deze component, die de IStatePersistor-interface implementeert, bevat de volledige, complexe journaling-logica (.journal, fsync, rename) \[cite: system/6\_RESILIENCE\_AND\_OPERATIONS v2.md\]. Hij wordt door de ComponentBuilder **geïnjecteerd** in de BaseStatefulWorker.  
* **Workflow:**  
  1. Een worker erft van BaseStatefulWorker.  
  2. De ComponentBuilder ziet dit en injecteert de StatePersistenceAdapter (van de PersistorFactory).  
  3. De worker roept self.commit\_state() aan.  
  4. De BaseStatefulWorker delegeert deze aanroep aan de geïnjecteerde adapter, die het zware werk doet.

### **Capaciteit 2: Event Communication (De Communicator)**

* **Doel:** "Expert" plugins in staat stellen om onderling te communiceren door custom events te publiceren en erop te reageren, zonder de EventBus direct aan te hoeven spreken.  
* **Architectuur:**  
  1. **De Interface (BaseEventAwareWorker):** Biedt een simpele, **bus-agnostische** interface: self.publish\_event(...) om te zenden en on\_\<event\_name\>(...) methodes om te ontvangen. De worker is volledig onwetend van de event bus implementatie.  
  2. **De Motor (PluginEventAdapter):** Dit is de "vertaler". Deze component wordt door de ComponentBuilder gecreëerd voor elke event-aware worker. Hij leest de publishes en listens\_to secties uit het manifest.yaml van de plugin, abonneert zich op de daadwerkelijke EventBus, en roept de on\_\<event\_name\> methodes op de worker aan wanneer nodig.  
* **Workflow:**  
  1. Een worker erft van BaseEventAwareWorker.  
  2. De ComponentBuilder creëert een bijbehorende PluginEventAdapter.  
  3. De worker roept self.publish\_event(...) aan.  
  4. De BaseEventAwareWorker geeft dit door aan zijn PluginEventAdapter, die het event valideert en op de bus plaatst.

### **Capaciteit 3: Historical Journaling (De Notulist)**

* **Doel:** Elke plugin in staat stellen om op een gestructureerde manier bij te dragen aan het StrategyJournal, zodat elke beslissing en observatie traceerbaar is.  
* **Architectuur:** Dit volgt exact hetzelfde, zuivere patroon als State Persistence.  
  1. **De Interface (BaseJournalingWorker):** Biedt een simpele, **persistentie-agnostische** interface: self.log\_entries(entries, context).  
  2. **De Motor (JournalPersistenceAdapter):** De specialist die de IJournalPersistor-interface implementeert. Hij is verantwoordelijk voor het toevoegen van metadata (timestamp, strategy\_link\_id uit de context) en het wegschrijven van de log-regels naar het juiste (JSON) bestand. Hij wordt, net als de state adapter, **geïnjecteerd** door de ComponentBuilder.  
* **Workflow:**  
  1. Een worker erft van BaseJournalingWorker.  
  2. De ComponentBuilder injecteert de JournalPersistenceAdapter.  
  3. De worker roept self.log\_entries(...) aan.  
  4. De BaseJournalingWorker delegeert deze aanroep aan de geïnjecteerde adapter.

## **3\. De "Ladder van Complexiteit"**

Deze drie capaciteiten resulteren in een duidelijke "ladder" waaruit een ontwikkelaar kan kiezen, afhankelijk van de taak.

1. **BaseWorker (De Pure Specialist):** De basis. Geen geheugen, geen event-communicatie, geen journaling. Perfect voor simpele, stateless Context- en OpportunityWorkers.  
2. **BaseStatefulWorker (De Boekhouder):** Erft van BaseWorker. Voegt de state-capaciteit toe.  
3. **BaseEventAwareWorker (De Communicator):** Erft van BaseWorker. Voegt de event-capaciteit toe.  
4. **BaseJournalingWorker (De Rapporteur):** Erft van BaseWorker. Voegt de journaling-capaciteit toe.  
5. Combinaties: Een ontwikkelaar kan via multiple inheritance de exacte mix van capaciteiten kiezen die hij nodig heeft, bijvoorbeeld:  
   class MyAdvancedAgent(BaseStatefulWorker, BaseEventAwareWorker, BaseJournalingWorker):  
   Deze agent heeft een geheugen, kan communiceren én kan rapporteren.

Deze gelaagde aanpak is de ultieme manifestatie van de V2-filosofie: het biedt maximale kracht en flexibiliteit aan experts, terwijl het de instapdrempel voor beginners zo laag en veilig mogelijk houdt.