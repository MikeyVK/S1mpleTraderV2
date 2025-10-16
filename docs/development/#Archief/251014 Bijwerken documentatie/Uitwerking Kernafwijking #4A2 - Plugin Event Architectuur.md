# **Diepgaande Analyse: De Plugin Event Architectuur**

Dit document is een gedetailleerde uitwerking van **Capaciteit 2: Event Communication** uit het PLUGIN\_CAPABILITIES\_DEEP\_DIVE.md document. Het beschrijft de volledige architectuur die "expert" plugins in staat stelt om onderling te communiceren via een event-gedreven model, met behoud van de kernprincipes van isolatie, abstractie en testbaarheid.

## **1\. Filosofie: Gecontroleerde Autonomie**

De kernfilosofie is om plugins **gecontroleerde autonomie** te geven. Een plugin moet kunnen reageren op en bijdragen aan het grotere "gesprek" binnen een strategie, maar op een manier die:

1. **Expliciet en Zelf-Documenterend is:** De communicatiebehoeften van een plugin zijn vastgelegd in zijn manifest.yaml.  
2. **Volledig Bus-Agnostisch is:** De plugin-code zelf is perfect geïsoleerd en heeft geen enkele kennis van de onderliggende EventBus-technologie.  
3. **Veilig en Robuust is:** Het systeem valideert de events en hun datastructuren (DTO's) om runtime-fouten te voorkomen.

Dit wordt bereikt door een symbiotische relatie tussen drie componenten: de **Configuratie** (het manifest), de **Interface** (de basisklasse) en de **Motor** (de adapter).

## **2\. De Lagen van de Event Architectuur**

### **Laag 1: De Configuratie (manifest.yaml) \- Het "Communicatiepaspoort"**

Dit is waar de plugin zijn communicatieve "vingerafdruk" definieert. Het manifest.yaml krijgt twee optionele, maar krachtige secties.

* **publishes:** Een lijst van custom events die deze plugin *kan publiceren*. Dit fungeert als een **lokale event\_map**. Voor elk event definieert de plugin een unieke naam en het payload\_dto dat het zal gebruiken.  
* **listens\_to:** Een lijst van events waarop deze plugin *wil reageren*. Dit fungeert als een **lokale wiring\_map**. Het koppelt een event\_name (dit kan een systeem-event of een custom plugin-event zijn) aan een specifieke methode binnen de worker-klasse.

Dit maakt de plugin een volledig zelf-beschrijvend en autonoom component.

\# plugins/smart\_dca\_worker/manifest.yaml

identification:

  name: "smart\_dca\_worker"

  type: "ExecutionWorker"

  description: "Een geavanceerde DCA worker die reageert op tijd en marktdips."

  author: "S1mpleTrader Core"

  version: "1.0.0"

\# Deze sectie definieert de 'taal' die deze plugin spreekt.

\# Het fungeert als een lokale, plugin-specifieke event\_map.

publishes:

  \- event\_name: "DCA\_PURCHASE\_EXECUTED"

    payload\_dto: "DcaPurchaseConfirmation" \# Verwijst naar een DTO gedefinieerd binnen deze plugin

\# Deze sectie definieert de 'reflexen' van de plugin.

\# Het fungeert als een lokale, plugin-specifieke wiring\_map.

listens\_to:

  \# Luistert naar een Systeem-Event (van de Scheduler)

  \- event\_name: "DAILY\_MARKET\_OPEN\_TICK"

    invokes: "on\_trading\_window\_opened"

  \# Luistert naar een Custom Event (van een andere plugin, bv. MarketDipMonitor)

  \- event\_name: "MARKET\_IS\_DIPPING"

    invokes: "on\_market\_dip\_detected"

### **Laag 2: De Interface (BaseEventAwareWorker) \- Het "Dashboard"**

Dit is de abstracte basisklasse waar een event-bewuste plugin van erft. Het biedt een extreem simpele en **bus-agnostische** interface voor de ontwikkelaar.

* **self.publish\_event(event\_name: str, payload: BaseModel):** De "verzendknop". De ontwikkelaar geeft de naam en de data, en de basisklasse delegeert de rest.  
* **on\_\<event\_name\>(...) methodes:** De "ontvangst-handlers". De ontwikkelaar implementeert simpelweg een methode met een naam die overeenkomt met de invokes-waarde in zijn manifest.

De worker-code zelf blijft puur, testbaar en volledig gefocust op businesslogica.

\# backend/core/workers/base\_event\_aware\_worker.py

"""

Bevat de BaseEventAwareWorker, de interface-laag voor event-communicatie.

"""

from pydantic import BaseModel

\# Aanname: PluginEventAdapter is een Protocol/Interface

from backend.core.interfaces import IPluginEventAdapter

class BaseEventAwareWorker:

    """

    Een basisklasse die een simpele, bus-agnostische interface biedt

    voor event publicatie en afhandeling.

    

    Deze klasse is zelf 'dom' en delegeert alle daadwerkelijke communicatie

    aan de geïnjecteerde PluginEventAdapter.

    """

    \_event\_adapter: IPluginEventAdapter

    def \_\_init\_\_(self, event\_adapter: IPluginEventAdapter):

        """

        De IPluginEventAdapter wordt geïnjecteerd door de ComponentBuilder.

        """

        self.\_event\_adapter \= event\_adapter

    def publish\_event(self, event\_name: str, payload: BaseModel) \-\> None:

        """

        Publiceert een event. Delegeert de validatie en publicatie

        volledig aan de adapter.

        

        Args:

            event\_name: De naam van het event, moet overeenkomen met \`manifest.yaml\`.

            payload: Het Pydantic DTO-object dat de data bevat.

        """

        self.\_event\_adapter.publish(event\_name, payload)

### **Laag 3: De Motor (PluginEventAdapter) \- De "Vertaler"**

Dit is de onzichtbare maar cruciale "motor" die het dashboard van de worker verbindt met de EventBus. Het is een aparte, gespecialiseerde klasse die de worker volledig isoleert.

* **Verantwoordelijkheid:**  
  1. Leest bij initialisatie het manifest.yaml van zijn toegewezen worker.  
  2. Valideert de publishes-definities.  
  3. Abonneert zich op de daadwerkelijke EventBus voor alle events in de listens\_to-sectie.  
  4. Wanneer een event binnenkomt, roept het de juiste on\_\<event\_name\>-methode aan op de worker-instantie met de correcte payload.  
  5. Wanneer de worker publish\_event aanroept, valideert de adapter of dit event is toegestaan en plaatst het op de bus.

\# backend/assembly/plugin\_event\_adapter.py

"""

Bevat de PluginEventAdapter, de 'motor' die een worker-instantie

verbindt met de centrale EventBus.

"""

from pydantic import BaseModel

\# Aannames: Worker- en EventBus-interfaces zijn importeerbaar

from backend.core.interfaces import IWorker, IEventBus

from typing import Dict, Any, List

class PluginEventAdapter:

    """

    De 'vertaler' die de bus-agnostische worker verbindt met de EventBus.

    Implementeert de IPluginEventAdapter interface.

    """

    def \_\_init\_\_(self, worker\_instance: IWorker, manifest\_config: Dict\[str, Any\], event\_bus: IEventBus):

        self.\_worker \= worker\_instance

        self.\_manifest \= manifest\_config

        self.\_bus \= event\_bus

        self.\_allowed\_publications: set\[str\] \= {

            p\['event\_name'\] for p in manifest\_config.get('publishes', \[\])

        }

        self.\_subscribe\_to\_events()

    def \_subscribe\_to\_events(self) \-\> None:

        """Leest de 'listens\_to' sectie en abonneert zich op de EventBus."""

        subscriptions: List\[Dict\[str, str\]\] \= self.\_manifest.get('listens\_to', \[\])

        for subscription in subscriptions:

            event\_name \= subscription\['event\_name'\]

            method\_name \= subscription\['invokes'\]

            

            handler \= getattr(self.\_worker, method\_name, None)

            

            if handler and callable(handler):

                \# De wrapper zorgt ervoor dat de payload correct wordt doorgegeven.

                \# In een echte implementatie zou hier de context ook worden meegegeven.

                def handler\_wrapper(payload: BaseModel) \-\> None:

                    handler(payload=payload)

                self.\_bus.subscribe(event\_name, handler\_wrapper)

                print(f"Adapter: Subscribing '{event\_name}' to '{self.\_worker.\_\_class\_\_.\_\_name\_\_}.{method\_name}'")

            else:

                \# Log een waarschuwing als de methode niet bestaat

                print(f"Warning: Method '{method\_name}' not found on worker '{self.\_worker.\_\_class\_\_.\_\_name\_\_}'")

    def publish(self, event\_name: str, payload: BaseModel) \-\> None:

        """Valideert en publiceert een event namens de worker."""

        if event\_name not in self.\_allowed\_publications:

            raise PermissionError(

                f"Worker '{self.\_worker.\_\_class\_\_.\_\_name\_\_}' has no permission to publish event '{event\_name}'. "

                f"Declare it in the 'publishes' section of the manifest."

            )

        

        self.\_bus.publish(event\_name, payload)

        print(f"Adapter: Publishing '{event\_name}' from '{self.\_worker.\_\_class\_\_.\_\_name\_\_}'")

