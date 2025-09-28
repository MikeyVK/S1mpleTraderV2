# backend/core/base_worker.py
"""
Contains a basic, non-abstract base class that plugin workers can inherit from
to reduce boilerplate code for initialization.

@layer: Backend (Core)
@dependencies: [pydantic, backend.utils.app_logger]
@responsibilities:
    - Provides a standard __init__ method for all workers.
"""
from pydantic import BaseModel
from backend.utils.app_logger import LogEnricher

class BaseWorker:
    """A simple, concrete base class providing a shared __init__ for workers.

    Plugin workers can optionally inherit from this class to get a standardized
    initializer that handles the storing of name, parameters, and a logger.
    This is a tool for code reuse, not a formal contract. The formal
    behavioral contract is defined by the Protocols in `interfaces.py`.
    """
    def __init__(self, name: str, params: BaseModel, logger: LogEnricher):
        """
        Initializes the base worker.

        Args:
            name (str): The unique name of the plugin instance, provided by the
                        WorkerBuilder.
            params (BaseModel): The validated Pydantic model containing the
                                worker's specific parameters.
            logger (LogEnricher): The logger instance, injected by the
                                  WorkerBuilder, often with added context.
        """
        self.name = name
        self.params = params
        self.logger = logger
