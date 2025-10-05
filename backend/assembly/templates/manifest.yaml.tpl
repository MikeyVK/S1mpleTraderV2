# backend/assembly/templates/manifest.yaml.tpl
#
# TEMPLATE FILE
# The PluginCreator uses this template to generate a new plugin's manifest.yaml.
# The header below describes this template file; a new, correct header will
# be generated for the final manifest.yaml file itself.
#
# @layer: Backend (Assembly Template)

# --- Core Identity & Versioning ---
# Defines the schema version for forward/backward compatibility.
core_identity:
  apiVersion: "s1mpletrader.io/v1"
  kind: "PluginManifest"

# --- Plugin Identification ---
# Unique identifier and descriptive metadata for the plugin.
identification:
  name: "{{ name }}"
  display_name: "{{ display_name }}"
  type: "{{ plugin_type }}"
  version: "0.1.0"
  description: "{{ description }}"
  author: "{{ author }}"

# --- Dataframe Dependencies ---
# Defines the data contract for the plugin's interaction with the context.
dependencies:
  # Columns/artefacts this plugin requires as input.
  requires: []
  # New columns/artefacts this plugin provides as output.
  provides: []

# --- Security & Permissions ---
# An explicit list of permissions the plugin requires. "Secure by default."
permissions:
  network_access: []
  filesystem_access: []
