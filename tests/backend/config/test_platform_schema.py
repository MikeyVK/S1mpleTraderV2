# tests/backend/config/schemas/test_platform_schema.py
"""
Unit tests for the platform_schema.py.

@layer: Tests (Backend/Config/Schemas)
@dependencies: [pytest, pydantic]
@responsibilities:
    - Verify that a valid platform configuration, including the new
      data_ingestion structure, is successfully parsed.
    - Verify that an invalid configuration raises a ValidationError.
"""
import pytest
from pydantic import ValidationError

# Het schema dat we gaan testen (bestaat nog niet in de juiste vorm)
from backend.config.schemas.platform_schema import PlatformConfig

def test_full_valid_platform_config_succeeds():
    """
    Tests that a complete and valid platform.yaml structure is successfully
    validated by the PlatformConfig model. This is the "happy path" test.
    """
    # Arrange
    valid_config_dict = {
        "core": {
            "language": "en",
            "plugins_root_path": "plugins"
        },
        "services": {
            "data_collection": {
                "limits": {
                    "max_history_days": 1000
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
                "initial_capital": 5000.0
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
