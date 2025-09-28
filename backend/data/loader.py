# backend/data/loader.py
"""
Handles loading raw data from CSV files and performing initial cleaning.

@layer: Backend (Data)
@dependencies: [pathlib, pandas, backend.utils.app_logger]
@responsibilities:
    - Loads raw OHLCV data from a specific CSV file.
    - Performs initial data cleaning, sets the timestamp index, and handles NA values.
"""
from pathlib import Path
import pandas as pd
from backend.utils.app_logger import LogEnricher

class DataLoader:
    """Loads and performs initial preparation of OHLCV data from a CSV file."""

    def __init__(self, file_path: str, logger: LogEnricher):
        """Initializes the DataLoader."""
        self.file_path = Path(file_path)
        self.logger = logger
        if not self.file_path.is_file():
            raise FileNotFoundError(f"Data file not found at path: {self.file_path}")

    def load(self) -> pd.DataFrame:
        """Loads data from the CSV, sets the index, and cleans the data."""
        self.logger.info('loader.loading_from', values={'filename': self.file_path.name})

        df: pd.DataFrame = pd.read_csv(self.file_path) # pyright: ignore[reportUnknownMemberType]

        # Converteer timestamp naar datetime objecten, stel in als index en sorteer.
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
        df = df.set_index('timestamp').sort_index()

        # Verwijder rijen met ontbrekende waarden om de datakwaliteit te garanderen.
        df = df.dropna() # pyright: ignore[reportUnknownMemberType]

        self.logger.info('loader.load_success')
        return df
