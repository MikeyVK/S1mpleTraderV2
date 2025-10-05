# plugins/{{PluginType}}/{{SnakeName}}/schema.py
"""
Contains the Pydantic validation schema for the {{PascalName}} plugin.

@layer: Plugin
@dependencies: [Pydantic]
"""
from pydantic import BaseModel

class {{PascalName}}Params(BaseModel):
    """Validation schema for {{PascalName}} parameters."""
    pass