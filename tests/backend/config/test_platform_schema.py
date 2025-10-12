# tests/backend/config/schemas/test_platform_schema.py
"""
Comprehensive unit tests for the platform_schema.py.

@layer: Tests (Backend/Config/Schemas)
@dependencies: [pytest, pydantic]
@responsibilities:
    - Verify that valid platform configurations are successfully parsed
    - Test all nested configuration structures (core, services, data, portfolio)
    - Validate data ingestion profiles and buffer configurations
    - Test logging configuration and profile definitions
    - Ensure proper default value application
    - Test validation rules for all numeric and structural constraints
    - Validate error messages and edge cases
    - Test real-world configuration scenarios
"""
import pytest
from pydantic import ValidationError
from typing import List

# Import the LogLevel enum for proper typing
from backend.core.enums import LogLevel

# Import all platform schema models
from backend.config.schemas.platform_schema import (
    PlatformConfig,
    CoreConfig,
    LoggingConfig,
    DataCollectionLimits,
    DataIngestionConfig,
    DataIngestionDefaults,
    DataIngestionBufferConfig,
    DataConfig,
    PortfolioDefaults,
)

def test_data_ingestion_buffer_config_valid():
    """Test DataIngestionBufferConfig with valid parameters."""
    # Arrange & Act
    buffer_config = DataIngestionBufferConfig(max_records=100000, max_seconds=3600)

    # Assert
    assert buffer_config.max_records == 100000
    assert buffer_config.max_seconds == 3600


def test_data_ingestion_buffer_config_validation_errors():
    """Test DataIngestionBufferConfig validation rule enforcement."""
    # Test zero max_records
    with pytest.raises(ValidationError):
        DataIngestionBufferConfig(max_records=0, max_seconds=300)

    # Test negative max_records
    with pytest.raises(ValidationError):
        DataIngestionBufferConfig(max_records=-1000, max_seconds=300)

    # Test zero max_seconds
    with pytest.raises(ValidationError):
        DataIngestionBufferConfig(max_records=10000, max_seconds=0)

    # Test negative max_seconds
    with pytest.raises(ValidationError):
        DataIngestionBufferConfig(max_records=10000, max_seconds=-60)


def test_data_ingestion_defaults_valid():
    """Test DataIngestionDefaults with valid nested buffer configurations."""
    # Arrange
    historical_buffer = DataIngestionBufferConfig(max_records=250000, max_seconds=3600)
    live_buffer = DataIngestionBufferConfig(max_records=10000, max_seconds=300)

    # Act
    defaults = DataIngestionDefaults(
        historical_task=historical_buffer,
        live_task=live_buffer
    )

    # Assert
    assert defaults.historical_task.max_records == 250000
    assert defaults.live_task.max_seconds == 300


def test_data_ingestion_config_with_profiles():
    """Test DataIngestionConfig with custom profiles."""
    # Arrange
    defaults = DataIngestionDefaults(
        historical_task=DataIngestionBufferConfig(max_records=100000, max_seconds=1800),
        live_task=DataIngestionBufferConfig(max_records=5000, max_seconds=150)
    )

    profiles = {
        "power_user": DataIngestionBufferConfig(max_records=1000000, max_seconds=7200),
        "minimal": DataIngestionBufferConfig(max_records=1000, max_seconds=60)
    }

    # Act
    ingestion_config = DataIngestionConfig(defaults=defaults, profiles=profiles)

    # Assert
    assert len(ingestion_config.profiles) == 2
    assert "power_user" in ingestion_config.profiles
    assert ingestion_config.profiles["power_user"].max_records == 1000000
    assert ingestion_config.profiles["minimal"].max_seconds == 60


def test_logging_config_valid():
    """Test LoggingConfig with valid profile definitions."""
    # Arrange
    profiles: dict[str, List[LogLevel]] = {
        "developer": [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR],
        "production": [LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
    }

    # Act
    logging_config = LoggingConfig(profile="analysis", profiles=profiles)

    # Assert
    assert logging_config.profile == "analysis"
    assert len(logging_config.profiles) == 2
    assert LogLevel.DEBUG in logging_config.profiles["developer"]


def test_core_config_valid():
    """Test CoreConfig with valid platform settings."""
    # Arrange
    logging_config = LoggingConfig(
        profile="analysis",
        profiles={
            "analysis": [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.TRADE]
        }
    )

    # Act
    core_config = CoreConfig(
        language="nl",
        plugins_root_path="custom_plugins",
        logging=logging_config
    )

    # Assert
    assert core_config.language == "nl"
    assert core_config.plugins_root_path == "custom_plugins"
    assert core_config.logging.profile == "analysis"


def test_core_config_defaults():
    """Test CoreConfig default value application."""
    # Arrange & Act
    core_config = CoreConfig()

    # Assert
    assert core_config.language == "en"
    assert core_config.plugins_root_path == "plugins"
    assert core_config.logging.profile == "analysis"


def test_data_collection_limits_valid():
    """Test DataCollectionLimits with valid safety constraints."""
    # Arrange & Act
    limits = DataCollectionLimits(max_history_days=2000, warn_history_days=365)

    # Assert
    assert limits.max_history_days == 2000
    assert limits.warn_history_days == 365


def test_data_collection_limits_validation():
    """Test DataCollectionLimits validation rules."""
    # Test zero max_history_days
    with pytest.raises(ValidationError):
        DataCollectionLimits(max_history_days=0, warn_history_days=30)

    # Test negative warn_history_days
    with pytest.raises(ValidationError):
        DataCollectionLimits(max_history_days=1000, warn_history_days=-10)


def test_portfolio_defaults_valid():
    """Test PortfolioDefaults with valid financial parameters."""
    # Arrange & Act
    defaults = PortfolioDefaults(initial_capital=50000.0, fees_pct=0.002)

    # Assert
    assert defaults.initial_capital == 50000.0
    assert defaults.fees_pct == 0.002


def test_portfolio_defaults_validation():
    """Test PortfolioDefaults validation rules."""
    # Test zero initial_capital
    with pytest.raises(ValidationError):
        PortfolioDefaults(initial_capital=0.0, fees_pct=0.001)

    # Test negative initial_capital
    with pytest.raises(ValidationError):
        PortfolioDefaults(initial_capital=-10000.0, fees_pct=0.001)

    # Test negative fees_pct
    with pytest.raises(ValidationError):
        PortfolioDefaults(initial_capital=10000.0, fees_pct=-0.001)


def test_full_valid_platform_config_succeeds():
    """
    Tests that a complete and valid platform.yaml structure is successfully
    validated by the PlatformConfig model. This is the "happy path" test.
    """
    # Arrange
    valid_config_dict = {
        "core": {
            "language": "en",
            "plugins_root_path": "plugins",
            "logging": {
                "profile": "analysis",
                "profiles": {
                    "analysis": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "TRADE"]
                }
            }
        },
        "services": {
            "data_collection": {
                "limits": {
                    "max_history_days": 1000,
                    "warn_history_days": 365
                }
            },
            "data_ingestion": {
                "defaults": {
                    "historical_task": {"max_records": 250000, "max_seconds": 3600},
                    "live_task": {"max_records": 10000, "max_seconds": 300}
                },
                "profiles": {
                    "local_power_user": {"max_records": 1000000, "max_seconds": 7200}
                }
            }
        },
        "data": {
            "source_dir": "source_data"
        },
        "portfolio": {
            "defaults": {
                "initial_capital": 50000.0,
                "fees_pct": 0.002
            }
        }
    }

    # Act & Assert
    try:
        PlatformConfig.model_validate(valid_config_dict)
    except ValidationError as e:
        pytest.fail(f"A valid configuration failed validation: {e}")

def test_minimal_config_applies_defaults_correctly():
    """
    Tests that a minimal config (missing optional sections) is correctly
    populated with default values by Pydantic's `default_factory`.
    """
    # Arrange
    # Een minimale config die alleen de verplichte 'services' sectie bevat.
    minimal_config_dict = {
        "services": {
            "data_ingestion": {
                "defaults": {
                    "historical_task": {"max_records": 1, "max_seconds": 1},
                    "live_task": {"max_records": 1, "max_seconds": 1}
                }
            }
        }
    }

    # Act
    config = PlatformConfig.model_validate(minimal_config_dict)

    # Assert
    # Controleer of de standaardwaarden voor de 'core' sectie zijn toegepast.
    assert config.core.language == 'en'
    assert config.core.plugins_root_path == 'plugins'

    # Controleer of de standaardwaarden voor de 'portfolio' sectie zijn toegepast.
    assert config.portfolio.defaults.initial_capital == 10000.0
    assert config.portfolio.defaults.fees_pct == 0.001

def test_invalid_value_in_nested_config_fails():
    """
    Tests that validation rules (e.g., gt=0) are enforced even in
    deeply nested parts of the configuration, like portfolio defaults.
    """
    # Arrange
    invalid_config_dict = {
        "services": { # Verplichte sectie
            "data_ingestion": {
                "defaults": {
                    "historical_task": {"max_records": 1, "max_seconds": 1},
                    "live_task": {"max_records": 1, "max_seconds": 1}
                }
            }
        },
        "portfolio": {
            "defaults": {
                # Deze waarde schendt de 'gt=0' (greater than zero) regel.
                "initial_capital": -100.0
            }
        }
    }

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        PlatformConfig.model_validate(invalid_config_dict)

    # Controleer of de foutmelding duidelijk aangeeft wat er mis is.
    assert "portfolio.defaults.initial_capital" in str(exc_info.value)
    assert "Input should be greater than 0" in str(exc_info.value)

def test_platform_config_missing_required_nested_field_fails():
    """
    Tests that a configuration missing a required nested field (like
    'historical_task') raises a ValidationError.
    """
    # Arrange
    invalid_config_dict = {
        "services": {
            "data_ingestion": {
                "defaults": {
                    # 'historical_task' ontbreekt hier.
                    "live_task": {"max_records": 10000, "max_seconds": 300}
                }
            }
        }
    }

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        PlatformConfig.model_validate(invalid_config_dict)

    assert "services.data_ingestion.defaults.historical_task" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)

def test_valid_platform_config_with_ingestion_profiles_succeeds():
    """
    Tests that a valid platform.yaml structure, including the new flexible
    ingestion profiles, is successfully validated by the PlatformConfig model.
    """
    # Arrange
    # Dit is een Python-representatie van een complete en geldige platform.yaml
    valid_config_dict = {
        "core": {
            "language": "en",
            "plugins_root_path": "plugins"
        },
        "services": {
            "data_ingestion": {
                "defaults": {
                    "historical_task": {
                        "max_records": 250000,
                        "max_seconds": 3600
                    },
                    "live_task": {
                        "max_records": 10000,
                        "max_seconds": 300
                    }
                },
                "profiles": {
                    "local_power_user": {
                        "max_records": 1000000,
                        "max_seconds": 7200
                    }
                }
            }
        },
        "data": {
            "source_dir": "source_data"
        },
        "portfolio": {
            "defaults": {
                "initial_capital": 10000.0
            }
        }
    }

    # Act & Assert
    # Deze aanroep zou moeten slagen zonder een error.
    try:
        PlatformConfig.model_validate(valid_config_dict)
    except ValidationError as e:
        pytest.fail(f"A valid configuration failed validation: {e}")


def test_platform_config_missing_default_ingestion_profile_fails():
    """
    Tests that a configuration missing a required default ingestion profile
    (e.g., 'historical_task') raises a ValidationError.
    """
    # Arrange
    invalid_config_dict = {
        "services": {
            "data_ingestion": {
                "defaults": {
                    # 'historical_task' ontbreekt hier
                    "live_task": {
                        "max_records": 10000,
                        "max_seconds": 300
                    }
                }
            }
        }
    }

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        PlatformConfig.model_validate(invalid_config_dict)

    # Controleer of de foutmelding nuttig is.
    assert "services.data_ingestion.defaults.historical_task" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)
