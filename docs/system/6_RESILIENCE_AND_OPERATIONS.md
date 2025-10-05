# 6. Robuustheid & Operationele Betrouwbaarheid

Dit document beschrijft de strategieën en architectonische patronen die S1mpleTrader V2 veerkrachtig maken tegen technische fouten. Deze principes zijn essentieel voor de betrouwbaarheid van het systeem, met name in een live trading-omgeving waar kapitaal op het spel staat.

---
## 6.1. Integriteit van de Staat: Atomiciteit en Persistentie

Een trading-systeem is inherent 'stateful'. De huidige staat (open posities, kapitaal, state van een plugin) is de basis voor toekomstige beslissingen. Het corrumperen van deze staat is catastrofaal.

### **6.1.1. Atomische Schrijfacties (Journaling)**

* **Probleem:** Een applicatiecrash of stroomuitval tijdens het schrijven van een state-bestand (bv. `state.json` voor een stateful plugin) kan leiden tot een half geschreven, corrupt bestand, met permanent dataverlies tot gevolg.
* **Architectonische Oplossing:** We implementeren een **Write-Ahead Log (WAL)** of **Journaling**-patroon, een techniek die door professionele databases wordt gebruikt.

* **Gedetailleerde Workflow:**
    1.  **Schrijf naar Journaal:** De `save_state()`-methode van een stateful plugin schrijft de nieuwe staat **nooit** direct naar `state.json`. Het serialiseert de data naar een tijdelijk bestand: `state.json.journal`.
    2.  **Forceer Sync naar Schijf:** Na het schrijven roept de methode `os.fsync()` aan op het `.journal`-bestands-handle. Dit is een cruciale, expliciete instructie aan het besturingssysteem om alle databuffers onmiddellijk naar de fysieke schijf te schrijven. Dit voorkomt dat de data alleen in het geheugen blijft en verloren gaat bij een stroomstoring.
    3.  **Atomische Hernoeming:** Alleen als de sync succesvol is, wordt de `os.rename()`-operatie uitgevoerd om `state.json.journal` te hernoemen naar `state.json`. Deze `rename`-operatie is op de meeste moderne bestandssystemen een **atomische handeling**: het slaagt in zijn geheel, of het faalt in zijn geheel.
    4.  **Herstel-Logica:** De `load_state()`-methode van de plugin bevat de herstel-logica. Bij het opstarten controleert het: "Bestaat er een `.journal`-bestand?". Zo ja, dan weet het dat de applicatie is gecrasht na stap 2 maar vóór stap 3. De herstelprocedure is dan het voltooien van de `rename`-operatie, waarmee de laatste succesvol geschreven staat wordt hersteld.

---
## 6.2. Netwerkveerkracht (Live/Paper Trading)

Een live-systeem is afhankelijk van een stabiele verbinding met externe databronnen en brokers. De architectuur moet ontworpen zijn om met de onvermijdelijke instabiliteit van het internet om te gaan.

* **Probleem:** Een tijdelijke of langdurige onderbreking van de WebSocket-verbinding kan leiden tot gemiste data, een incorrecte portfolio-staat en het onvermogen om posities te beheren.
* **Architectonische Oplossing:** De verantwoordelijkheid voor het managen van de verbinding ligt volledig bij de `LiveEnvironment` en zijn componenten.

* **Gedetailleerde Componenten:**
    1.  **`LiveDataSource` (met Heartbeat & Reconnect):**
        * **Heartbeat:** De `DataSource` verwacht niet alleen data, maar ook periodieke "heartbeat"-berichten van de exchange. Als er gedurende een configureerbare periode (bv. 30 seconden) geen enkel bericht binnenkomt, wordt de verbinding als verbroken beschouwd.
        * **Reconnect Protocol:** Zodra een verbreking wordt gedetetecteerd, start een automatisch reconnect-protocol. Dit gebruikt een **exponential backoff**-algoritme: het wacht 1s, dan 2s, 4s, 8s, etc., om de server van de exchange niet te overbelasten.

    2.  **`LiveExecutionHandler` (met State Reconciliation):**
        * **Principe:** Na een reconnect is de interne staat van het `Portfolio`-object **onbetrouwbaar**. Het systeem moet uitgaan van de "single source of truth": de exchange zelf.
        * **Proces:** De `ExecutionHandler` voert een **reconciliation**-procedure uit. Het roept de REST API van de exchange aan met de vragen: "Geef mij de status van al mijn openstaande orders" en "Geef mij al mijn huidige posities". Het vergelijkt dit antwoord met de data in het `Portfolio`-object en corrigeert eventuele discrepanties.

    3.  **`StrategyOperator` (met Circuit Breaker):**
        * **Principe:** Als de `LiveDataSource` na een configureerbaar aantal pogingen geen verbinding kan herstellen, moet het systeem in een veilige modus gaan om verdere schade te voorkomen.
        * **Proces:** De `DataSource` stuurt een `CONNECTION_LOST`-event naar de `Operator`. De `Operator` activeert dan de **Circuit Breaker**:
            * Het stopt onmiddellijk met het verwerken van nieuwe signalen.
            * Het stuurt een kritieke alert (via e-mail, Telegram, etc.) naar de gebruiker.
            * Het kan (optioneel) proberen alle open posities te sluiten als laatste redmiddel.

---
## 6.3. Applicatie Crash Recovery (Supervisor Model)

* **Probleem:** Het hoofdproces van de `StrategyOperator` kan crashen door een onverwachte bug in een plugin of een geheugenprobleem.
* **Architectonische Oplossing:** We scheiden het *starten* van de applicatie van de *applicatie zelf* door middel van een **Supervisor (Watchdog)**-proces, aangestuurd door `run_supervisor.py`.

* **Gedetailleerde Workflow:**
    1.  **Entrypoint `run_supervisor.py`:** Dit is het enige script dat je handmatig start in een live-omgeving.
    2.  **Supervisor Proces:** Dit script start een extreem lichtgewicht en robuust "supervisor"-proces. Zijn enige taak is het spawnen van een *kind-proces* voor de daadwerkelijke `StrategyOperator` en het monitoren van dit kind-proces.
    3.  **Herstart & Herstel Cyclus:**
        * Als het `Orchestrator`-proces onverwacht stopt, detecteert de `Supervisor` dit.
        * De `Supervisor` start de `Orchestrator` opnieuw.
        * De *nieuwe* `Orchestrator`-instantie start in een **"herstelmodus"**:
            * **Stap A (State Herstel):** Het roept de `load_state()`-methodes aan van al zijn stateful plugins, die de journaling-logica (zie 6.1) gebruiken om een consistente staat te herstellen.
            * **Stap B (Portfolio Herstel):** Het voert de **State Reconciliation**-procedure uit (zie 6.2) om zijn `Portfolio` te synchroniseren met de exchange.
            * **Stap C (Hervatting):** Alleen als beide stappen succesvol zijn, gaat de `Orchestrator` over naar de normale, live-operatie en begint het weer met het verwerken van marktdata.