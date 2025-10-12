# backend/config/schemas/plugin_manifest_schema.py
"""
Pydantic schema for validating the plugin_manifest.yaml file.

This schema acts as the single source of truth for the structure and data
types required for a plugin to be considered valid by the platform.

@layer: Backend (Config)
@dependencies: [Pydantic, backend.core.enums]
@responsibilities:
    - Defines the data contract for a plugin's manifest.
    - Enables automatic validation of manifests during plugin registration.
"""
from typing import Annotated, List, Literal

from pydantic import BaseModel, Field, StringConstraints

from backend.core.enums import PipelinePhase

# --- Nested Models for Grouping and Clarity ---

class CoreIdentity(BaseModel):
    """System-level fields for versioning and schema identification."""
    apiVersion: Literal["s1mpletrader.io/v1"] = Field(
        description="manifest.core_identity.apiVersion.desc"
    )
    kind: Literal["PluginManifest"] = Field(
        description="manifest.core_identity.kind.desc"
    )

class PluginIdentification(BaseModel):
    """Descriptive metadata for identifying the plugin."""
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, to_lower=True, pattern=r"^[a-z0-9_]+$")
    ] = Field(description="manifest.identification.name.desc")

    display_name: str = Field(
        description="manifest.identification.display_name.desc"
    )
    type: PipelinePhase = Field(
        description="manifest.identification.type.desc"
    )
    version: Annotated[
        str,
        StringConstraints(pattern=r"^\d+\.\d+\.\d+$")
    ] = Field(description="manifest.identification.version.desc")

    description: str = Field(
        description="manifest.identification.description.desc"
    )
    author: str = Field(
        description="manifest.identification.author.desc"
    )

class Dependencies(BaseModel):
    """Defines the data contract for the plugin's interaction with context."""
    requires: List[str] = Field(
        description="manifest.dependencies.requires.desc",
        default_factory=list
    )
    provides: List[str] = Field(
        description="manifest.dependencies.provides.desc",
        default_factory=list
    )
    produces_events: List[str] = Field(
        description="manifest.dependencies.produces_events.desc",
        default_factory=list
    )

class Permissions(BaseModel):
    """Defines the security permissions required by the plugin."""
    network_access: List[str] = Field(
        description="manifest.permissions.network_access.desc",
        default_factory=list
    )
    filesystem_access: List[str] = Field(
        description="manifest.permissions.filesystem_access.desc",
        default_factory=list
    )

# --- The Main Manifest Model ---

class PluginManifest(BaseModel):
    """The complete, validated Pydantic model for a plugin's manifest.yaml."""
    core_identity: CoreIdentity = Field(..., description="manifest.core_identity.desc")
    identification: PluginIdentification = Field(..., description="manifest.identification.desc")
    dependencies: Dependencies = Field(..., description="manifest.dependencies.desc")
    permissions: Permissions = Field(..., description="manifest.permissions.desc")
