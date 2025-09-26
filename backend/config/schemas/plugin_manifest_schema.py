# backend/config/schemas/plugin_manifest_schema.py
"""
Contains the Pydantic model that defines the structure of a plugin_manifest.yaml file.
This schema acts as the contract for what makes a plugin discoverable and valid.

@layer: Backend (Config)
@dependencies: [Pydantic]
@responsibilities:
    - Defines the validated structure for a plugin's metadata.
    - Enforces the presence of critical fields for the PluginRegistry.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class PluginManifest(BaseModel):
    """
    Validates the structure and content of a plugin's manifest.yaml file.
    This is the "ID card" of any plugin in the S1mpleTrader V2 ecosystem.
    """
    # === Core Identity (Verplicht) ===
    name: str
    version: str
    description: str
    type: Literal[
        'regime_filter',
        'structural_context',
        'signal_generator',
        'signal_refiner',
        'trade_constructor',
        'portfolio_overlay'
    ]

    # === Code Contract (Verplicht) ===
    entry_class: str
    schema_path: str
    params_class: str

    # === Optionele Features ===
    # Data-contract: welke kolommen verwacht de plugin in de DataFrame?
    dependencies: Optional[List[str]] = None

    # Visualisatie-contract: welke Pydantic-klasse definieert de context en het render-recept?
    context_schema_class: Optional[str] = None

    provides: List[str] = Field(default_factory=list)
