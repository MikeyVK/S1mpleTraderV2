# **Diepgaande Analyse: De Plugin Journaling Architectuur**

Dit document is een gedetailleerde uitwerking van **Capaciteit 3: Historical Journaling** uit het PLUGIN\_CAPABILITIES\_DEEP\_DIVE.md document. Het beschrijft de volledige, zuivere architectuur die elke plugin in staat stelt om op een gestructureerde en ontkoppelde manier bij te dragen aan het StrategyJournal.

## **1\. Filosofie: De Plugin als Intelligente Bron, De Persistor als "Domme" Notulist**

De kernfilosofie is een radicale scheiding van verantwoordelijkheden, gebaseerd op het inzicht dat **de enige intelligentie in het systeem afkomstig is van de plugins**.

* **De Plugin (De Bron):** De plugin is de specialist en "heer en meester binnen zijn eigen cosmos". Alleen de plugin weet *waarom* een beslissing wordt genomen. Het is daarom de **exclusieve verantwoordelijkheid van de plugin** om de context en rationale van zijn acties te formuleren in de vorm van journal\_entries.  
* **De Persistence Laag (De Notulist):** De componenten die de data opslaan zijn "dom". Ze interpreteren niets. Hun enige taak is het onveranderlijk en betrouwbaar wegschrijven van de informatie die hen wordt aangeleverd.

Er is geen StrategyJournal service of JournalAdapter meer nodig. De communicatie is direct, ontkoppeld en wordt gefaciliteerd door **Dependency Injection**, exact volgens hetzelfde patroon als de StatePersistence.

## **2\. De Lagen van de Journaling Architectuur**

### **Laag 1: De Interface (BaseJournalingWorker) \- Het "Dashboard"**

Dit is de abstracte basisklasse die de journaling-capaciteit aan een worker toevoegt. Het biedt een simpele en **persistentie-agnostische** interface aan de ontwikkelaar.

* **self.log\_entries(entries: List\[Dict\], context: TradingContext):** De enige methode die de ontwikkelaar hoeft te kennen. Hij levert de "wat" (de entries) en de "waar/wanneer" (de context), en de basisklasse delegeert de rest.

### **Laag 2: De Motor (JournalPersistenceAdapter) \- De Specialist**

Dit is de "motor" die het daadwerkelijke schrijfwerk doet. Het is een concrete implementatie van de IJournalPersistor interface.

* **Verantwoordelijkheid:** Het ontvangen van journaal-regels, het toevoegen van de laatste metadata (timestamp, strategy\_link\_id uit de context), en het wegschrijven naar de juiste opslaglocatie (bv. een JSON-bestand).  
* **Injectie:** Deze component wordt door de ComponentBuilder **geïnjecteerd** in de BaseJournalingWorker tijdens de creatie van de worker. Dit is de cruciale stap die de ontkoppeling mogelijk maakt.

### **Laag 3: De Context (TradingContext) \- De Datadrager**

Zoals we eerder concludeerden, is de TradingContext de drager van de essentiële metadata die nodig is om de journaal-entry correct te archiveren.

* **Verantwoordelijkheid:** Het bevat de strategy\_link\_id en de timestamp van de huidige tick. Door dit object mee te geven aan de log\_entries methode, heeft de BaseJournalingWorker alle informatie die hij nodig heeft om de JournalPersistenceAdapter correct aan te sturen.

## **3\. Concrete Implementatie & Workflow**

Hieronder volgt de code die deze architectuur tot leven brengt.

#### **Stap 1: De Basisklasse (BaseJournalingWorker)**

Dit is de interface die de ontwikkelaar gebruikt. Het is een dunne laag die de aanroep delegeert aan de geïnjecteerde persistor.

\# backend/core/workers/base\_journaling\_worker.py

"""

Bevat de BaseJournalingWorker, de interface-laag voor het bijdragen

aan het StrategyJournal.

"""

from typing import List, Dict, Any

from backend.core.interfaces.persistors import IJournalPersistor

from backend.dtos.trading\_context import TradingContext

class BaseJournalingWorker:

    """

    Een basisklasse die een simpele, persistentie-agnostische interface biedt

    voor het loggen van journaal-regels.

    """

    \_journal\_persistor: IJournalPersistor

    def \_\_init\_\_(self, journal\_persistor: IJournalPersistor):

        """

        De IJournalPersistor wordt geïnjecteerd door de ComponentBuilder,

        afkomstig van de PersistorFactory.

        """

        self.\_journal\_persistor \= journal\_persistor

    def log\_entries(

        self,

        entries: List\[Dict\[str, Any\]\],

        context: TradingContext

    ) \-\> None:

        """

        Logt een lijst van entries naar het journaal.

        De worker levert de inhoudelijke 'entries', en de TradingContext

        levert de metadata (strategy\_id, timestamp). De methode delegeert

        vervolgens de volledige opslag aan de geïnjecteerde persistor.

        Args:

            entries: Een lijst van dicts die de journaal-regels representeren.

            context: De actuele TradingContext.

        """

        if not entries:

            return

        \# Verrijk de entries met de laatste, cruciale metadata uit de context.

        \# De Causal IDs worden door de worker zelf al aan de entries toegevoegd.

        for entry in entries:

            entry\['timestamp'\] \= context.timestamp

        \# Delegeer de opslag aan de specialist.

        self.\_journal\_persistor.append(

            strategy\_id=context.strategy\_link\_id,

            entries=entries

        )

#### **Stap 2: Een Voorbeeld Worker (RiskGovernor)**

Dit voorbeeld toont hoe een ExecutionWorker de BaseJournalingWorker gebruikt om een cruciale beslissing vast te leggen: het afwijzen van een kans.

\# plugins/risk\_governor/worker.py

from typing import List, Dict, Any

from backend.core.workers.base\_journaling\_worker import BaseJournalingWorker

from backend.dtos.trading\_context import TradingContext

from backend.dtos.opportunity\_signal import OpportunitySignal

from backend.dtos.threat\_signal import ThreatSignal

class RiskGovernor(BaseJournalingWorker):

    """

    Deze ExecutionWorker fungeert als een 'poortwachter'. Hij wijst een

    opportunity af als er een actieve dreiging is.

    """

    def process(

        self,

        opportunity: OpportunitySignal,

        active\_threats: List\[ThreatSignal\],

        context: TradingContext

    ) \-\> OpportunitySignal | None:

        """

        Keurt een opportunity goed of af op basis van actieve dreigingen.

        """

        if active\_threats:

            \# Er is een dreiging. Wijs de kans af en LOG deze beslissing.

            rejection\_entry \= {

                "event\_type": "OPPORTUNITY\_REJECTED",

                "causal\_id": opportunity.causal\_id,

                "rejection\_reason": {

                    "threat\_type": active\_threats\[0\].threat\_type,

                    "threat\_id": active\_threats\[0\].causal\_id

                }

            }

            

            \# Gebruik de geërfde methode om de beslissing te journaliseren.

            self.log\_entries(\[rejection\_entry\], context)

            

            return None \# Geef geen payload door; de workflow stopt hier.

        \# Geen dreiging. Keur de kans goed.

        approval\_entry \= {

            "event\_type": "OPPORTUNITY\_APPROVED",

            "causal\_id": opportunity.causal\_id,

        }

        self.log\_entries(\[approval\_entry\], context)

        return opportunity \# Geef de opportunity door aan de volgende stap (Planning).

### **4\. Conclusie**

Deze architectuur is de ultieme manifestatie van onze kernprincipes:

* **Consistentie:** Journaling volgt exact hetzelfde, bewezen dependency-injection patroon als state-persistentie.  
* **Ontkoppeling:** De BaseJournalingWorker is 100% persistentie-agnostisch. We kunnen de JsonJournalPersistor morgen vervangen door een DatabaseJournalPersistor zonder dat een enkele plugin hoeft te veranderen.  
* **SRP:** Elke component heeft één, perfect gedefinieerde taak. De plugin levert de intelligentie, de BaseWorker de interface, en de Persistor de implementatie.

Dit is de sluitende, robuuste en elegante oplossing voor het vastleggen van het volledige verhaal van elke strategie.