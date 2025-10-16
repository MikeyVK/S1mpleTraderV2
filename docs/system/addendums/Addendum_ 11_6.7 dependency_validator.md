### **6.7. backend/assembly/dependency\_validator.py**

Bestandsnaam: dependency\_validator.py  
Plek in architectuur: Backend \> Assembly  
Type: Validator  
Layer: Backend (Assembly)  
Dependencies: \[backend.config.schemas, backend.assembly.plugin\_registry, typing\]  
Beschrijving: Systeembrede validator die garandeert dat data-afhankelijkheden tussen workers consistent zijn met de geconfigureerde executie-volgorde en strategieën van de operators.  
**Responsibilities:**

* Bouwt een complete data-afhankelijkheidsgrafiek voor alle workers in de strategie.  
* Analyseert de operator-configuratie (operators.yaml) en wiring\_map.yaml om de executie-volgorde te bepalen.  
* Detecteert conflicten waar een data-afhankelijkheid bestaat tussen workers die (potentieel) parallel worden uitgevoerd.  
* Valideert de logische volgorde van ContextWorkers in een sequentiële pijplijn.  
* Voorkomt 'race conditions' door configuratiefouten tijdens de bootstrap-fase (Fail Fast).

\# backend/assembly/dependency\_validator.py  
"""  
Contains the system-aware DependencyValidator.

@layer: Backend (Assembly)  
@dependencies: \[backend.config.schemas, backend.assembly.plugin\_registry, typing\]  
@responsibilities:  
    \- Builds a complete data dependency graph for all workers in the strategy.  
    \- Analyzes operator configuration (operators.yaml) to determine execution strategies.  
    \- Detects conflicts where a data dependency exists between workers that  
      are configured to run in parallel.  
    \- Prevents configuration-induced race conditions during the bootstrap phase.  
"""  
from typing import List, Dict, Set, Any  
from backend.assembly.plugin\_registry import PluginRegistry  
from backend.config.schemas.strategy\_blueprint\_schema import StrategyBlueprintConfig  
from backend.config.schemas.operators\_schema import OperatorSuiteConfig

class DependencyValidator:  
    """  
    Validates the dataflow integrity across the entire workforce,  
    considering operator execution strategies.  
    """

    def \_\_init\_\_(self, plugin\_registry: PluginRegistry):  
        """  
        Initializes the DependencyValidator.

        Args:  
            plugin\_registry (PluginRegistry): The registry to fetch manifests from.  
        """  
        self.\_registry \= plugin\_registry

    def validate(  
        self,  
        blueprint: StrategyBlueprintConfig,  
        operator\_config: OperatorSuiteConfig  
    ) \-\> None:  
        """  
        Validates the entire workforce for dependency and execution conflicts.

        Args:  
            blueprint (StrategyBlueprintConfig): The strategy blueprint defining the workforce.  
            operator\_config (OperatorSuiteConfig): The configuration defining operator behavior.

        Raises:  
            ValueError: If a dependency conflict is found.  
        """  
        \# Creëer een map van operator ID naar zijn execution strategy voor snelle lookup.  
        operator\_strategies \= {  
            op.operator\_id: op.execution\_strategy  
            for op in operator\_config.operators  
        }

        \# Bouw een map van elke worker naar zijn parent operator.  
        worker\_to\_operator\_map \= self.\_map\_workers\_to\_operators(blueprint)

        \# De initiële set van kolommen die beschikbaar is.  
        available\_columns \= {"open", "high", "low", "close", "volume"}

        \# We verwerken de workers per operator-fase (conceptueel).  
        \# We beginnen met de ContextWorkers.  
        context\_workers \= blueprint.workforce.context\_workers  
        context\_op\_strategy \= operator\_strategies.get("ContextOperator", "SEQUENTIAL")

        if context\_op\_strategy \== "SEQUENTIAL":  
            \# Als de strategie sequentieel is, valideren we de keten stap voor stap.  
            self.\_validate\_sequential\_pipeline(context\_workers, available\_columns)  
        else: \# PARALLEL  
            \# Als de strategie parallel is, mogen er GEEN inter-dependencies zijn.  
            self.\_validate\_parallel\_execution(context\_workers, "ContextOperator")

        \# Update de beschikbare kolommen met alles wat de context-fase heeft geproduceerd.  
        for worker\_config in context\_workers:  
            manifest, \_ \= self.\_registry.get\_plugin\_data(worker\_config.plugin)  
            if manifest.dependencies and manifest.dependencies.provides:  
                available\_columns.update(manifest.dependencies.provides)

        \# Valideer nu de volgende fases (Opportunity, Threat, etc.)  
        \# Deze workers draaien na de context-fase en hebben toegang tot de 'available\_columns'.  
        \# Voorbeeld voor OpportunityWorkers:  
        opportunity\_workers \= blueprint.workforce.opportunity\_workers  
        opportunity\_op\_strategy \= operator\_strategies.get("OpportunityOperator", "PARALLEL")

        if opportunity\_op\_strategy \== "PARALLEL":  
            \# Controleer of alle dependencies worden geleverd door de \*vorige\* (context) fase.  
            self.\_validate\_parallel\_dependencies(opportunity\_workers, available\_columns, "OpportunityOperator")  
        else: \# SEQUENTIAL  
            self.\_validate\_sequential\_pipeline(opportunity\_workers, available\_columns.copy())  
              
        \# ... Herhaal dit proces voor Threat, Planning, en Execution workers ...

    def \_validate\_sequential\_pipeline(self, pipeline\_configs: List\[Any\], initial\_columns: Set\[str\]) \-\> None:  
        """Valideert een pijplijn die sequentieel wordt uitgevoerd."""  
        available \= initial\_columns.copy()  
        for worker\_config in pipeline\_configs:  
            manifest, \_ \= self.\_registry.get\_plugin\_data(worker\_config.plugin)  
            if manifest.dependencies and manifest.dependencies.requires:  
                for dep in manifest.dependencies.requires:  
                    if dep not in available:  
                        raise ValueError(  
                            f"Sequential Dependency Error: Plugin '{worker\_config.plugin}' requires '{dep}', "  
                            f"which is not provided by preceding workers. Available: {sorted(list(available))}"  
                        )  
            if manifest.dependencies and manifest.dependencies.provides:  
                available.update(manifest.dependencies.provides)

    def \_validate\_parallel\_execution(self, worker\_configs: List\[Any\], operator\_id: str) \-\> None:  
        """  
        Valideert dat er geen onderlinge afhankelijkheden zijn tussen workers  
        die parallel worden uitgevoerd binnen dezelfde operator.  
        """  
        all\_provides \= set()  
        for worker\_config in worker\_configs:  
            manifest, \_ \= self.\_registry.get\_plugin\_data(worker\_config.plugin)  
            if manifest.dependencies and manifest.dependencies.provides:  
                all\_provides.update(manifest.dependencies.provides)

        for worker\_config in worker\_configs:  
            manifest, \_ \= self.\_registry.get\_plugin\_data(worker\_config.plugin)  
            if manifest.dependencies and manifest.dependencies.requires:  
                for dep in manifest.dependencies.requires:  
                    if dep in all\_provides:  
                        raise ValueError(  
                            f"Configuration Conflict in '{operator\_id}': "  
                            f"Execution strategy is PARALLEL, but a dependency exists. "  
                            f"Plugin '{worker\_config.plugin}' requires '{dep}', which is provided by another "  
                            f"worker within the same parallel group. This is not allowed."  
                        )

    def \_validate\_parallel\_dependencies(self, worker\_configs: List\[Any\], available\_columns: Set\[str\], operator\_id: str) \-\> None:  
        """  
        Valideert dat alle dependencies voor een parallelle groep workers  
        al beschikbaar zijn \*voordat\* de groep start.  
        """  
        for worker\_config in worker\_configs:  
            manifest, \_ \= self.\_registry.get\_plugin\_data(worker\_config.plugin)  
            if manifest.dependencies and manifest.dependencies.requires:  
                for dep in manifest.dependencies.requires:  
                    if dep not in available\_columns:  
                        raise ValueError(  
                            f"Dependency Error in '{operator\_id}': Plugin '{worker\_config.plugin}' requires '{dep}', "  
                            f"but it is not available from the preceding sequential phases (e.g., Context phase)."  
                        )

    def \_map\_workers\_to\_operators(self, blueprint: StrategyBlueprintConfig) \-\> Dict\[str, str\]:  
        """Creëert een mapping van plugin naam naar de ID van de beherende operator."""  
        mapping \= {}  
        for worker in blueprint.workforce.context\_workers:  
            mapping\[worker.plugin\] \= "ContextOperator"  
        for worker in blueprint.workforce.opportunity\_workers:  
            mapping\[worker.plugin\] \= "OpportunityOperator"  
        \# ... etc. for all worker types ...  
        return mapping  
