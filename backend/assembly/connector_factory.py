# In bestand: backend/assembly/connector_factory.py
"""
Contains the factory responsible for creating and managing API connector instances.

@layer: Backend (Assembly)
@dependencies: [backend.config.schemas, backend.environments.api_connectors]
@responsibilities:
    - Instantiates specific API connectors based on configuration.
    - Manages the lifecycle of connector instances (creation, caching).
    - Decouples services from the concrete implementation of connectors.
"""
from typing import Dict, Optional, Protocol

from backend.config.schemas.connectors_schema import ConnectorsConfig, AnyConnectorConfig
from backend.core.interfaces.connectors import IAPIConnector
from backend.environments.api_connectors.kraken_connector import KrakenAPIConnector
from backend.utils.app_logger import LogEnricher


class IConnectorFactory(Protocol):
    """An interface for any component that can build and manage API connectors."""
    def get_connector(self, name: str) -> Optional[IAPIConnector]:
        """Builds and returns a connector instance by its configured name."""
        ...

    def close_connector(self, name: str) -> None:
        """Closes and removes a specific connector instance from the cache."""
        ...

    def close_all(self) -> None:
        """Closes all cached connector instances."""
        ...

class ConnectorFactory(IConnectorFactory):
    """A factory for creating API connector instances based on configuration."""

    def __init__(self, config: ConnectorsConfig, logger: LogEnricher):
        """Initializes the ConnectorFactory.

        Args:
            config (ConnectorsConfig): The validated connectors configuration,
                mapping names to connector definitions.
            logger (LogEnricher): The application's configured logger instance.
        """
        self._config = config
        self._logger = logger
        # De cache om reeds gemaakte instanties te bewaren voor hergebruik.
        self._instances: Dict[str, IAPIConnector] = {}

    def get_connector(self, name: str) -> Optional[IAPIConnector]:
        """Builds and returns a connector instance using lazy loading.

        The first time a connector is requested, it is built, cached, and
        returned. Subsequent requests for the same connector name will return
        the cached instance, preventing redundant object creation.

        Args:
            name (str): The unique name of the connector as defined in
                connectors.yaml (e.g., 'kraken_public').

        Returns:
            An instance of a component that adheres to the IAPIConnector
            interface if found and successfully built, otherwise None.
        """
        # Stap 1: Controleer de cache voor een bestaande instantie.
        if name in self._instances:
            return self._instances[name]

        # Stap 2: Zoek de configuratie voor de gevraagde connector.
        connector_config = self._config.root.get(name)
        if not connector_config:
            self._logger.error(
                f"Connector '{name}' not found in configuration."
            )
            return None

        # Stap 3: Delegeer de daadwerkelijke bouw naar een private helper.
        instance = self._build(connector_config)
        if instance:
            # Stap 4: Sla de nieuwe instantie op in de cache voor de volgende keer.
            self._instances[name] = instance
        return instance

    def close_connector(self, name: str) -> None:
        """Closes a specific connector and removes it from the cache."""
        if name in self._instances:
            self._logger.info(f"Closing connector instance '{name}'...")
            instance = self._instances[name]
            try:
                instance.close()
            except Exception as e:
                self._logger.error(
                    f"Failed to gracefully close connector '{name}': {e}"
                )
            del self._instances[name]
        else:
            self._logger.warning(
                f"Attempted to close non-existent or non-cached connector '{name}'."
            )

    def close_all(self) -> None:
        """Closes all cached connector instances gracefully."""
        self._logger.info("Closing all active connector instances...")
        # We itereren over een kopie van de keys, omdat close_connector de dictionary aanpast.
        for name in list(self._instances.keys()):
            self.close_connector(name)
        self._instances.clear()

    def _build(self, config: AnyConnectorConfig) -> Optional[IAPIConnector]:
        """Internal builder method that maps a config type to a concrete class."""
        # Dit is het hart van de fabriek: het 'if/elif/else'-blok dat
        # de juiste klasse kiest op basis van het 'type' veld.
        if config.type == 'kraken_public':
            return KrakenAPIConnector(logger=self._logger, config=config)

        # Hier kunnen in de toekomst andere types worden toegevoegd:
        # if config.type == 'binance_public':
        #     return BinanceAPIConnector(logger=self._logger, config=config)

        self._logger.error(f"Unknown connector type '{config.type}' in _build method.")
        return None
