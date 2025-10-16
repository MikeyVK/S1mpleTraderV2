# **Diepgaande Analyse: De Data-Gedreven Operator Architectuur**

Dit document is een gedetailleerde uitwerking van **Kernafwijking \#3A** uit het architectuur addendum. Het beschrijft de transitie van vijf hard-gecodeerde Operator-klassen naar een enkele, generieke BaseOperator die zijn gedrag volledig laat dicteren door configuratie.

## **1\. Filosofie: Scheiding van Intentie en Implementatie**

De kern van deze verfijning is het maximaliseren van het DRY-principe en het SRP. In plaats van de orkestratie-logica (bv. "voer workers parallel uit") te dupliceren in meerdere klassen, centraliseren we de *implementatie* in één herbruikbare klasse en *externaliseren* we de *intentie* naar een configuratiebestand.

* **De Code (BaseOperator):** Implementeert de *mechanica* van alle mogelijke orkestratiestrategieën.  
* **De Configuratie (operators.yaml):** Beschrijft de *intentie* voor elke specifieke operator.

Dit maakt het systeem extreem flexibel: een wijziging in de orkestratiestrategie vereist geen codewijziging, maar een simpele aanpassing in een YAML-bestand.

## **2\. De Drie Lagen van het Ontwerp**

Het ontwerp bestaat uit drie lagen die perfect op elkaar aansluiten: de **Configuratie** (de blauwdruk), het **Contract** (de validatie), en de **Code** (de bouwers en de motor).

### **Laag 1: De Configuratie (operators.yaml) \- De Blauwdruk**

Dit nieuwe, centrale configuratiebestand definieert de "persoonlijkheid" en het gedrag van elke operator in het systeem. Het is de "enkele bron van waarheid" voor alle orkestratie.

**Bestand:** config/operators.yaml

\# Dit bestand definieert het gedrag van elke Operator in het systeem.  
operators:  
  \- operator\_id: "ContextOperator"  
    manages\_worker\_type: "ContextWorker"  
    execution\_strategy: "SEQUENTIAL"  
    aggregation\_strategy: "CHAIN\_THROUGH"  
  \- operator\_id: "OpportunityOperator"  
    manages\_worker\_type: "OpportunityWorker"  
    execution\_strategy: "PARALLEL"  
    aggregation\_strategy: "COLLECT\_ALL"  
  \- operator\_id: "ThreatOperator"  
    manages\_worker\_type: "ThreatWorker"  
    execution\_strategy: "PARALLEL"  
    aggregation\_strategy: "COLLECT\_ALL"  
  \- operator\_id: "PlanningOperator"  
    manages\_worker\_type: "PlanningWorker"  
    execution\_strategy: "SEQUENTIAL"  
    aggregation\_strategy: "CHAIN\_THROUGH"  
  \- operator\_id: "ExecutionOperator"  
    manages\_worker\_type: "ExecutionWorker"  
    execution\_strategy: "EVENT\_DRIVEN"  
    aggregation\_strategy: "NONE"

### **Laag 2: Het Contract (Pydantic Schema's) \- De Validatie**

Om de integriteit van de configuratie te garanderen, wordt operators.yaml gevalideerd door een strikt Pydantic-schema. Dit voorkomt typefouten en ongeldige strategieën voordat de applicatie zelfs maar start.

**Bestand:** backend/assembly/schemas/operator\_schema.py

### **Laag 3: De Code \- De Bouwers & De Motor**

Dit is waar de configuratie tot leven komt. Het bestaat uit een OperatorFactory (de bouwer) en de generieke BaseOperator (de motor).

#### **A. De OperatorFactory**

Deze component in de assembly-laag is de "hoofdaannemer". Hij leest de operators.yaml, valideert deze met het Pydantic-schema, en is verantwoordelijk voor het creëren van de geconfigureerde operator-instanties.

\# backend/assembly/operator\_factory.py

"""

Bevat de OperatorFactory, die de volledige suite van Operators bouwt

op basis van de centrale operators.yaml configuratie.

"""

from typing import Dict

\# Aannames: Schema's en BaseOperator zijn importeerbaar

from .schemas.operator\_schema import OperatorSuiteConfig, OperatorConfig

from backend.core.operators import BaseOperator 

class OperatorFactory:

    """Bouwt de volledige suite van Operators op basis van configuratie."""

    def \_\_init\_\_(self, suite\_config: OperatorSuiteConfig, component\_builder, \*\*kwargs):

        """

        Args:

            suite\_config: Het gevalideerde Pydantic-object van operators.yaml.

            component\_builder: De builder die nodig is om de workforce op te halen.

            \*\*kwargs: Andere services die geïnjecteerd moeten worden (bv. persistor).

        """

        self.\_configs: Dict\[str, OperatorConfig\] \= {

            cfg.operator\_id: cfg for cfg in suite\_config.operators

        }

        self.\_component\_builder \= component\_builder

        self.\_injected\_services \= kwargs

      


    def create\_operator(self, operator\_id: str) \-\> BaseOperator:

        """Creëert een enkele, geconfigureerde BaseOperator instantie."""

        if operator\_id not in self.\_configs:

            raise ValueError(f"Geen configuratie gevonden voor operator: {operator\_id}")

        config \= self.\_configs\[operator\_id\]

        \# Creëer een generieke BaseOperator en geef hem zijn "persoonlijkheid"

        \# (de configuratie) en zijn gereedschappen (geïnjecteerde services) mee.

        return BaseOperator(

            config=config,

            component\_builder=self.\_component\_builder,

            \*\*self.\_injected\_services

        )

    def create\_all\_operators(self) \-\> Dict\[str, BaseOperator\]:

        """Creëert een dictionary met alle geconfigureerde operators."""

        return {

            op\_id: self.create\_operator(op\_id) for op\_id in self.\_configs

        }

#### **B. De BaseOperator**

Dit is de generieke motor. Er is maar één BaseOperator-klasse. Een instantie van deze klasse gedraagt zich als een ContextOperator of OpportunityOperator puur op basis van de config die hem bij de creatie wordt meegegeven.

\# backend/core/operators/base\_operator.py

"""

Bevat de generieke, data-gedreven BaseOperator die de orkestratie

van elke worker-categorie aanstuurt.

"""

\# Aannames: Benodigde DTO's en services zijn importeerbaar

from backend.assembly.schemas.operator\_schema import OperatorConfig, ExecutionStrategy, AggregationStrategy

from typing import List, Any, Dict

import concurrent.futures

class BaseOperator:

    """

    Een generieke, data-gedreven Operator. Zijn gedrag wordt

    volledig bepaald door de configuratie die wordt geïnjecteerd.

    """

    def \_\_init\_\_(self, config: OperatorConfig, component\_builder, \*\*kwargs):

        self.config \= config

        self.\_component\_builder \= component\_builder

        \# ... sla andere geïnjecteerde services op ...

    def run(self, context: Any, \*\*kwargs) \-\> Any:

        """

        De generieke 'entrypoint' methode die wordt aangeroepen door de EventAdapter.

        Het delegeert de taak aan de juiste strategie-implementatie.

        """

        workforce \= self.\_component\_builder.get\_workforce\_for\_strategy(

            self.config.manages\_worker\_type, context.strategy\_link\_id

        )

        if not workforce:

            return None

        \# \--- Delegatie naar de Execution Strategy \---

        results: List\[Any\]

        if self.config.execution\_strategy \== ExecutionStrategy.SEQUENTIAL:

            results \= self.\_execute\_sequential(workforce, context)

        elif self.config.execution\_strategy \== ExecutionStrategy.PARALLEL:

            results \= self.\_execute\_parallel(workforce, context)

        elif self.config.execution\_strategy \== ExecutionStrategy.EVENT\_DRIVEN:

            results \= self.\_execute\_event\_driven(workforce, context, \*\*kwargs)

        else:

            raise NotImplementedError(f"Executiestrategie {self.config.execution\_strategy} is niet geïmplementeerd.")

        

        \# \--- Delegatie naar de Aggregation Strategy \---

        aggregated\_result: Any

        if self.config.aggregation\_strategy \== AggregationStrategy.COLLECT\_ALL:

            aggregated\_result \= self.\_aggregate\_collect\_all(results)

        elif self.config.aggregation\_strategy \== AggregationStrategy.CHAIN\_THROUGH:

            aggregated\_result \= self.\_aggregate\_chain\_through(results)

        elif self.config.aggregation\_strategy \== AggregationStrategy.NONE:

            aggregated\_result \= None

        else:

             raise NotImplementedError(f"Aggregatiestrategie {self.config.aggregation\_strategy} is niet geïmplementeerd.")

        

        return aggregated\_result

    \# \--- Private implementaties van de strategieën \---

    def \_execute\_sequential(self, workforce: List\[Any\], context: Any) \-\> List\[Any\]:

        """Voert workers één voor één uit en 'ketent' de context/data."""

        results \= \[\]

        current\_input \= context

        for worker in workforce:

            \# Aanname: worker.process retourneert het (mogelijk aangepaste) resultaat

            result \= worker.process(current\_input, worker.config)

            results.append(result)

            \# Voor CHAIN\_THROUGH, wordt de output de nieuwe input

            if self.config.aggregation\_strategy \== AggregationStrategy.CHAIN\_THROUGH:

                current\_input \= result

        return results

    def \_execute\_parallel(self, workforce: List\[Any\], context: Any) \-\> List\[Any\]:

        """Voert workers tegelijkertijd uit met een thread pool."""

        results \= \[\]

        with concurrent.futures.ThreadPoolExecutor() as executor:

            \# Start de 'process' methode voor elke worker

            future\_to\_worker \= {executor.submit(worker.process, context, worker.config): worker for worker in workforce}

            for future in concurrent.futures.as\_completed(future\_to\_worker):

                try:

                    result \= future.result()

                    results.append(result)

                except Exception as exc:

                    \# Voeg hier error handling toe

                    print(f'{future\_to\_worker\[future\]} generated an exception: {exc}')

        return results

    

    def \_execute\_event\_driven(self, workforce: List\[Any\], context: Any, \*\*kwargs) \-\> List\[Any\]:

        """Selecteert en activeert de juiste worker op basis van het inkomende event."""

        \# Aanname: het getriggerde event is beschikbaar in kwargs

        incoming\_event \= kwargs.get("event")

        if not incoming\_event:

            return \[\]

        

        results \= \[\]

        for worker in workforce:

            \# Aanname: worker manifest specificeert naar welk event het luistert

            if worker.config.get("listens\_to\_event") \== incoming\_event.name:

                result \= worker.process(incoming\_event.payload, context)

                results.append(result)

        return results

    

    def \_aggregate\_collect\_all(self, results: List\[Any\]) \-\> List\[Any\]:

        """Verzamelt alle (niet-None) resultaten in een lijst."""

        return \[res for res in results if res is not None\]

    def \_aggregate\_chain\_through(self, results: List\[Any\]) \-\> Any:

        """Retourneert het resultaat van de laatste worker in de keten."""

        return results\[-1\] if results else None

