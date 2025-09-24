# 6. Robuustheid & Operationele Betrouwbaarheid in V2

Dit document beschrijft de strategieën om S1mpleTrader V2 veerkrachtig te maken tegen technische fouten, met name in een live-omgeving.

### 6.1. Atomische Schrijfacties (Journaling)

Om corrupte staat-bestanden (`state.json`) bij een crash te voorkomen, wordt een "write-ahead log" of "journaling" patroon gebruikt.

1.  **Schrijf naar Journaal:** Wijzigingen worden eerst naar een tijdelijk `state.json.journal` bestand geschreven.
2.  **Forceer Sync:** Het besturingssysteem wordt gedwongen dit journaalbestand volledig naar de schijf te flushen.
3.  **Atomische Hernoeming:** Alleen na een succesvolle sync wordt het `.journal` bestand atomisch hernoemd naar `state.json`.
4.  **Herstel-Logica:** Bij het opstarten controleert het systeem op de aanwezigheid van een `.journal`-bestand en voltooit de hersteloperatie indien nodig.

### 6.2. Beheer van Dataverbindingen (Live/Paper)

De `ExecutionEnvironment` is verantwoordelijk voor de verbinding met externe databronnen.

1.  **Heartbeat & Reconnect:** De `DataSource` implementeert een heartbeat-mechanisme. Bij het uitblijven van data treedt een automatisch, exponentieel backoff reconnect-protocol in werking.
2.  **State Reconciliation:** Na een succesvolle reconnect moet de `ExecutionHandler` de exchange API bevragen naar de *werkelijke* status van alle open orders en posities en zijn interne `Portfolio`-staat synchroniseren.
3.  **Circuit Breaker:** Bij aanhoudende verbindingsproblemen treedt een noodstop in werking, die het openen van nieuwe posities stopt en een kritieke alert verstuurt.

### 6.3. Crash Recovery van de Applicatie

Voor een live-omgeving wordt een supervisor-proces (watchdog) aanbevolen.

* **Supervisor Proces:** Een lichtgewicht proces dat de `StrategyOrchestrator` start en monitort.
* **Herstart & Herstel:** Bij een crash van de orchestrator, kan de supervisor deze herstarten. De orchestrator start dan in een "herstelmodus" die de journaling en state reconciliation uitvoert alvorens de normale operaties te hervatten.