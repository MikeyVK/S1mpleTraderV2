# **6\. Robuustheid & Operationele Betrouwbaarheid**

Versie: 2.0 (Architectuur Blauwdruk v4)  
Status: Definitief  
Dit document beschrijft de strategieën en architectonische patronen die S1mpleTrader V2 veerkrachtig maken tegen technische fouten. Deze principes zijn essentieel voor de betrouwbaarheid van het systeem, met name in een live trading-omgeving waar kapitaal op het spel staat.

## **6.1. Integriteit van de Staat: Atomiciteit en Persistentie**

Een trading-systeem is inherent 'stateful'. De huidige staat (open posities, kapitaal, de interne staat van een stateful plugin) is de basis voor toekomstige beslissingen. Het corrumperen van deze staat is catastrofaal.

### **6.1.1. Atomische Schrijfacties (Journaling)**

* **Probleem:** Een applicatiecrash of stroomuitval tijdens het schrijven van een state-bestand (bv. state.json voor een stateful ExecutionWorker) kan leiden tot een half geschreven, corrupt bestand, met permanent dataverlies tot gevolg.  
* **Architectonische Oplossing:** We implementeren een **Write-Ahead Log (WAL)** of **Journaling**\-patroon, een techniek die door professionele databases wordt gebruikt.  
* **Gedetailleerde Workflow:**  
  1. **Schrijf naar Journaal:** De save\_state()-methode van een stateful plugin schrijft de nieuwe staat **nooit** direct naar state.json. Het serialiseert de data naar een tijdelijk bestand: state.json.journal.  
  2. **Forceer Sync naar Schijf:** Na het schrijven roept de methode os.fsync() aan op het .journal-bestands-handle. Dit is een cruciale, expliciete instructie aan het besturingssysteem om alle databuffers onmiddellijk naar de fysieke schijf te schrijven.  
  3. **Atomische Hernoeming:** Alleen als de sync succesvol is, wordt de os.rename()-operatie uitgevoerd om state.json.journal te hernoemen naar state.json. Deze rename-operatie is op de meeste moderne bestandssystemen een **atomische handeling**: het slaagt in zijn geheel, of het faalt in zijn geheel.  
  4. **Herstel-Logica:** De load\_state()-methode van de plugin bevat de herstel-logica. Bij het opstarten controleert het: "Bestaat er een .journal-bestand?". Zo ja, dan weet het dat de applicatie is gecrasht na stap 2 maar vóór stap 3\. De herstelprocedure is dan het voltooien van de rename-operatie.

## **6.2. Netwerkveerkracht en Staatssynchronisatie**

Een live-systeem is afhankelijk van een stabiele verbinding en moet kunnen omgaan met de onvermijdelijke instabiliteit van het internet. De kernfilosofie is: **de exchange is de enige bron van waarheid.** Ons platform onderhoudt slechts een real-time cache van die waarheid.

* **Architectonische Oplossing:** De verantwoordelijkheid voor het managen van de verbinding en de staatssynchronisatie ligt bij de **LiveEnvironment** en wordt aangestuurd door gespecialiseerde MonitorWorkers en ExecutionWorkers. We gebruiken een tweeledige strategie van "push" en "pull".

### **6.2.1. Mechanisme 1: Real-time Synchronisatie via 'Push' (WebSocket)**

* **Doel:** De interne staat (StrategyLedgers) met minimale latency synchroon houden tijdens de normale operatie.  
* **Componenten:** De LiveEnvironment en zijn IAPIConnector.  
* **Proces:**  
  1. De LiveEnvironment zet via de IAPIConnector een **private WebSocket-verbinding** (start\_user\_data\_stream()) op.  
  2. Wanneer een door S1mpleTrader geplaatste order wordt gevuld, *pusht* de exchange onmiddellijk een TradeExecuted-bericht.  
  3. De IAPIConnector vangt dit bericht op en vertaalt het naar een intern LedgerStateChanged-event.  
  4. Een MonitorWorker die de LedgerState observeert, wordt geactiveerd door dit event en kan indien nodig andere componenten informeren.

### **6.2.2. Mechanisme 2: Herstel & Verificatie via 'Pull' (State Reconciliation)**

* **Doel:** Het cruciale veiligheidsnet voor periodieke verificatie en, belangrijker nog, voor **herstel na een crash** of netwerkonderbreking.  
* **Componenten:** Een ReconciliationMonitor (een MonitorWorker) en de LiveEnvironment.  
* **Proces:**  
  1. **Trigger**: De Scheduler publiceert een periodiek event (bv. five\_minute\_reconciliation\_tick) zoals gedefinieerd in schedule.yaml.  
  2. De ReconciliationMonitor luistert naar dit event en start de reconcile\_state()-procedure. Dit gebeurt **altijd** bij het opstarten van een live Operation.  
  3. **Pull**: De monitor instrueert de LiveEnvironment om via de IAPIConnector de REST API van de exchange aan te roepen (get\_open\_orders(), get\_open\_positions()) om de "absolute waarheid" op te halen.  
  4. **Vergelijk**: Het vergelijkt deze lijst van "echte" posities en orders met de staat van de StrategyLedgers die het beheert.  
  5. **Corrigeer**: Bij discrepanties wordt de StrategyLedger geforceerd gecorrigeerd om de staat van de exchange te weerspiegelen, en wordt een CRITICAL-waarschuwing gelogd.

### **6.2.3. Verbindingsbeheer & Circuit Breaker**

* **Componenten:** Een ConnectionMonitor (MonitorWorker), een CircuitBreakerWorker (ExecutionWorker), en de LiveEnvironment's DataSource.  
* **Proces:**  
  1. **Heartbeat & Reconnect**: De DataSource monitort de verbinding. Bij een onderbreking start het een automatisch reconnect-protocol met een **exponential backoff**\-algoritme.  
  2. **Event Publicatie**: Als de DataSource na een configureerbaar aantal pogingen geen verbinding kan herstellen, publiceert het een CONNECTION\_LOST-event.  
  3. De **ConnectionMonitor** vangt dit event op en publiceert een strategisch event, bijvoorbeeld CONNECTION\_UNSTABLE\_DETECTED.  
  4. De **CircuitBreakerWorker** luistert naar CONNECTION\_UNSTABLE\_DETECTED en activeert de **Circuit Breaker**:  
     * Het publiceert een HALT\_NEW\_SIGNALS-event.  
     * Het stuurt een kritieke alert naar de gebruiker.  
     * Het kan (optioneel) proberen alle open posities die door S1mpleTrader worden beheerd, te sluiten door een EXECUTE\_EMERGENCY\_EXIT-event te publiceren.

## **6.3. Applicatie Crash Recovery (Supervisor Model)**

* **Probleem:** Het hoofdproces van het platform (de Operations-service) kan crashen door een onverwachte bug.  
* **Architectonische Oplossing:** We scheiden het *starten* van de applicatie van de *applicatie zelf* door middel of een **Supervisor (Watchdog)**\-proces, aangestuurd door run\_supervisor.py.  
* **Gedetailleerde Workflow:**  
  1. **Entrypoint run\_supervisor.py:** Dit is het enige script dat je handmatig start in een live-omgeving.  
  2. **Supervisor Proces:** Dit script start een lichtgewicht "supervisor"-proces dat een *kind-proces* voor de daadwerkelijke Operations-service start en monitort.  
  3. **Herstart & Herstel Cyclus:**  
     * Als het Operations-proces onverwacht stopt, detecteert de Supervisor dit.  
     * De Supervisor start de Operations-service opnieuw.  
     * De *nieuwe* Operations-instantie start in een **"herstelmodus"**:  
       * **Stap A (Plugin State Herstel):** Via de ComponentBuilder worden alle stateful plugins geladen met hun load\_state()-methodes, die de journaling-logica (zie 6.1) gebruiken om een consistente staat te herstellen.  
       * **Stap B (Ledger Herstel):** De **State Reconciliation**\-procedure (zie 6.2.2) wordt onmiddellijk uitgevoerd om alle StrategyLedgers te synchroniseren met de exchange.  
       * **Stap C (Hervatting):** Alleen als beide stappen succesvol zijn, gaat de Operation verder met de normale-tick verwerking.