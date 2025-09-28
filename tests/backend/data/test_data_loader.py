# tests/backend/data/test_data_loader.py
"""Unit tests for the DataLoader."""

import os
import re # <-- Importeer de 're' module
from pathlib import Path
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from backend.data.loader import DataLoader

def test_data_loader_successfully_loads_csv(tmp_path: Path, mocker: MockerFixture):
    """
    Tests if the DataLoader correctly reads a valid CSV file, sets the index,
    and returns a DataFrame.
    """
    # Arrange
    csv_content = "timestamp,open,high,low,close,volume\n" \
                  "2023-01-01 10:00:00,100,105,99,102,1000\n" \
                  "2023-01-01 10:01:00,102,103,101,102,500"
    
    data_file = tmp_path / "test_data.csv"
    data_file.write_text(csv_content)
    
    mock_logger = mocker.MagicMock()

    # Act
    loader = DataLoader(file_path=str(data_file), logger=mock_logger)
    df = loader.load()

    # Assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "timestamp"
    mock_logger.info.assert_called_with('loader.load_success')

def test_data_loader_raises_error_for_nonexistent_file(mocker: MockerFixture):
    """
    Tests if the DataLoader raises a FileNotFoundError when the file does not exist.
    This test is now platform-independent.
    """
    # Arrange
    # Bouw het pad op een platform-onafhankelijke manier.
    non_existent_path = os.path.join("path", "that", "does", "not", "exist.csv")
    mock_logger = mocker.MagicMock()

    # CORRECTIE: "Escape" de pad-string zodat de regex-engine backslashes
    # als letterlijke tekens behandelt en niet als speciale codes.
    expected_error_pattern = re.escape(non_existent_path)

    # Act & Assert
    with pytest.raises(FileNotFoundError, match=expected_error_pattern):
        DataLoader(file_path=non_existent_path, logger=mock_logger)
