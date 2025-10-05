# plugins/{{PluginType}}/{{SnakeName}}/worker.py
"""
Contains the main logic for the {{PascalName}} plugin.

@layer: Plugin
@dependencies: [] # Voeg hier je dependencies toe, bv. [pandas]
"""
from backend.core.interfaces import {{InterfaceName}}
from .schema import {{PascalName}}Params

class {{PascalName}}({{InterfaceName}}):
    """Main logic for the {{PascalName}} plugin."""

    def __init__(self, name: str, params: {{PascalName}}Params, logger):
        self.name = name
        self.params = params
        self.logger = logger

    def process(self, *args, **kwargs):
        """De core logica van de plugin."""
        # TODO: Implementeer de logica hier
        pass