# In bestand: tests/backend/assembly/test_connector_factory.py
"""
Unit tests for the ConnectorFactory.

@layer: Tests (Backend/Assembly)
@dependencies: [pytest, pytest-mock]
@responsibilities:
    - Verify that the factory correctly builds connector instances from config.
    - Verify that the factory handles requests for unknown connectors gracefully.
    - Verify that the factory caches instances for efficiency (lazy loading).
"""
from unittest.mock import MagicMock
from pytest_mock import MockerFixture

from backend.config.schemas.connectors_schema import ConnectorsConfig
from backend.config.schemas.connectors.kraken_schema import KrakenPublicConfig
from backend.environments.api_connectors.kraken_connector import KrakenAPIConnector

# De klasse die we gaan testen (bestaat nog niet)
from backend.assembly.connector_factory import ConnectorFactory


def test_factory_creates_known_connector_successfully(mocker: MockerFixture):
    """
    Tests if the factory correctly instantiates a connector based on a
    valid configuration.
    """
    # Arrange
    # 1. We simuleren de configuratie die de fabriek zal inlezen.
    mock_kraken_config = KrakenPublicConfig(type='kraken_public')
    mock_config = ConnectorsConfig.model_validate({
        'kraken_public': mock_kraken_config
    })

    # 2. We 'patchen' de KrakenAPIConnector klasse. Dit betekent dat we
    #    voorkomen dat de test de ECHTE connector probeert te bouwen.
    #    In plaats daarvan houden we bij OF hij wordt aangeroepen.
    mock_connector_class = mocker.patch(
        'backend.assembly.connector_factory.KrakenAPIConnector'
    )

    mock_logger = MagicMock()
    factory = ConnectorFactory(config=mock_config, logger=mock_logger)

    # Act
    connector_instance = factory.get_connector('kraken_public')

    # Assert
    # 1. Is de connector klasse aangeroepen met de juiste config en logger?
    mock_connector_class.assert_called_once_with(
        logger=mock_logger, config=mock_kraken_config
    )
    # 2. Geeft de fabriek de gemaakte instantie terug?
    assert connector_instance is not None


def test_factory_returns_none_for_unknown_connector():
    """
    Tests if the factory returns None when a non-existent connector
    name is requested.
    """
    # Arrange
    # Een lege configuratie.
    empty_config = ConnectorsConfig.model_validate({})
    mock_logger = MagicMock()
    factory = ConnectorFactory(config=empty_config, logger=mock_logger)

    # Act
    result = factory.get_connector('unknown_connector')

    # Assert
    assert result is None
    # Controleer of er een duidelijke foutmelding wordt gelogd.
    mock_logger.error.assert_called_once_with(
        "Connector 'unknown_connector' not found in configuration."
    )


def test_factory_uses_lazy_loading_and_caches_instances(mocker: MockerFixture):
    """
    Tests that a connector is only built once and then retrieved from a cache
    on subsequent requests for the same name.
    """
    # Arrange
    mock_kraken_config = KrakenPublicConfig(type='kraken_public')
    mock_config = ConnectorsConfig.model_validate({
        'kraken_public': mock_kraken_config
    })

    # We geven een specifieke mock instantie terug zodat we kunnen vergelijken.
    mock_instance = MagicMock(spec=KrakenAPIConnector)
    mock_connector_class = mocker.patch(
        'backend.assembly.connector_factory.KrakenAPIConnector',
        return_value=mock_instance
    )

    factory = ConnectorFactory(config=mock_config, logger=MagicMock())

    # Act
    # Vraag dezelfde connector twee keer aan.
    first_call_result = factory.get_connector('kraken_public')
    second_call_result = factory.get_connector('kraken_public')

    # Assert
    # 1. De bouwer (de klasse __init__) mag maar EEN keer zijn aangeroepen.
    mock_connector_class.assert_called_once()

    # 2. Beide aanroepen moeten exact dezelfde instantie teruggeven.
    assert first_call_result is mock_instance
    assert second_call_result is first_call_result

def test_factory_closes_specific_connector(mocker: MockerFixture):
    """
    Tests that close_connector(name) closes the correct instance and
    removes it from the cache, forcing a rebuild on the next call.
    """
    # Arrange
    mock_kraken_config = KrakenPublicConfig(type='kraken_public')
    mock_config = ConnectorsConfig.model_validate({'kraken_public': mock_kraken_config})

    # Mock de klasse en de instantie die het teruggeeft
    mock_instance = MagicMock(spec=KrakenAPIConnector)
    mock_connector_class = mocker.patch(
        'backend.assembly.connector_factory.KrakenAPIConnector',
        return_value=mock_instance
    )

    factory = ConnectorFactory(config=mock_config, logger=MagicMock())

    # Maak de connector aan en plaats hem in de cache.
    connector_to_close = factory.get_connector('kraken_public')
    assert connector_to_close is mock_instance

    # Act
    factory.close_connector('kraken_public')

    # Assert
    # 1. Is de .close() methode op de juiste instantie aangeroepen?
    mock_instance.close.assert_called_once()

    # 2. Vraag de connector opnieuw aan. De fabriek zou een NIEUWE moeten bouwen.
    factory.get_connector('kraken_public')

    # De bouwer (Klasse.__init__) zou nu in totaal TWEE keer moeten zijn aangeroepen.
    assert mock_connector_class.call_count == 2


def test_factory_closes_all_created_instances(mocker: MockerFixture):
    """
    Tests that the factory's close_all method calls .close() on every
    connector instance it has created and cached.
    """
    # Arrange
    mock_kraken_config = KrakenPublicConfig(type='kraken_public')
    mock_config = ConnectorsConfig.model_validate({'kraken_public': mock_kraken_config})
    
    mock_instance = MagicMock(spec=KrakenAPIConnector)
    mocker.patch(
        'backend.assembly.connector_factory.KrakenAPIConnector',
        return_value=mock_instance
    )
    factory = ConnectorFactory(config=mock_config, logger=MagicMock())

    # Activeer de connector.
    factory.get_connector('kraken_public')
    
    # Act
    factory.close_all()

    # Assert
    # Is de .close() methode op onze gemaakte instantie aangeroepen?
    mock_instance.close.assert_called_once()
