# backend/utils/dynamic_loader.py
"""
Handles the dynamic loading of classes from plugin modules.

@layer: Backend (Utility)
@dependencies: [importlib]
@responsibilities:
    - Provides a single function to dynamically import a class from a module
      using a string-based path and class name.
"""

import importlib
from typing import Any

def load_class_from_module(module_path: str, class_name: str) -> Any:
    """
    Dynamically imports a module and returns a specific class from it.

    Args:
        module_path (str): The full, dot-separated path to the Python module
                           (e.g., "plugins.signal_generators.my_plugin.worker").
        class_name (str): The exact name of the class to load from the module.

    Raises:
        ImportError: If the module cannot be found.
        AttributeError: If the class does not exist within the module.

    Returns:
        The loaded class object (not an instance).
    """
    try:
        module = importlib.import_module(module_path)
        loaded_class = getattr(module, class_name)
        return loaded_class
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_path}': {e}") from e
    except AttributeError as e:
        raise AttributeError(
            f"Class '{class_name}' not found in module '{module_path}': {e}"
        ) from e
