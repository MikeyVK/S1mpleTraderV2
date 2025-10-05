# plugins/{{PluginType}}/{{SnakeName}}/context_schema.py
"""
Contains the Pydantic model for the visualization context of the {{PascalName}} plugin.

@layer: Plugin
@dependencies: [Pydantic]
"""
from pydantic import BaseModel

class {{PascalName}}Context(BaseModel):
    """
    Defines the data required by the frontend to visualize this plugin's context.
    """
    # Voorbeeld: voeg hier de velden toe die je wilt visualiseren
    # some_value: float
    # some_label: str
    pass