# tests/backend/assembly/test_context_builder.py
"""Unit tests for the ContextBuilder."""

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from backend.assembly.context_builder import ContextBuilder

# --- Test Setup: Maak een paar "nep"-workers ---

class MockWorkerAddColumn:
    """Een nep-worker die simpelweg een kolom toevoegt."""
    def __init__(self, new_col_name: str, value: int):
        self.new_col_name = new_col_name
        self.value = value

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.new_col_name] = self.value
        return df

class MockWorkerModifyColumn:
    """Een nep-worker die een bestaande kolom aanpast."""
    def __init__(self, target_col: str, multiplier: int):
        self.target_col = target_col
        self.multiplier = multiplier

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.target_col] = df[self.target_col] * self.multiplier
        return df

# --- De Tests ---

def test_context_builder_runs_pipeline_sequentially():
    """
    Tests of de ContextBuilder de workers in de juiste, sequentiële
    volgorde uitvoert.
    """
    # Arrange (De Voorbereiding)
    # 1. Maak een simpele start-DataFrame.
    initial_df = pd.DataFrame({'close': [10, 20, 30]})

    # 2. Maak instanties van onze nep-workers.
    worker1 = MockWorkerAddColumn(new_col_name="EMA_50", value=15)
    worker2 = MockWorkerModifyColumn(target_col="EMA_50", multiplier=2)

    # 3. Stel de ContextBuilder in met deze workers.
    context_builder = ContextBuilder()
    pipeline = [worker1, worker2]

    # Act (De Actie)
    # Voer de pijplijn uit.
    result_df = context_builder.build(initial_df, pipeline)

    # Assert (De Controle)
    # We controleren of het eindresultaat correct is.
    # Worker 1 zou de kolom "EMA_50" met waarde 15 moeten toevoegen.
    # Worker 2 zou die kolom moeten vermenigvuldigen met 2, dus de eindwaarde moet 30 zijn.
    assert "EMA_50" in result_df.columns
    assert result_df["EMA_50"].tolist() == [30, 30, 30]

def test_context_builder_returns_copy_of_dataframe():
    """
    Tests of de ContextBuilder een kopie van de DataFrame retourneert en
    de originele niet aanpast. Dit is belangrijk om onverwachte bijeffecten
    in de rest van de applicatie te voorkomen.
    """
    # Arrange
    initial_df = pd.DataFrame({'close': [10]})
    initial_df_copy = initial_df.copy() # Maak een kopie voor de controle achteraf.

    worker = MockWorkerAddColumn(new_col_name="EMA_50", value=15)
    context_builder = ContextBuilder()

    # Act
    result_df = context_builder.build(initial_df, [worker])

    # Assert
    # Controleer of de geretourneerde DataFrame de nieuwe kolom heeft.
    assert "EMA_50" in result_df.columns
    # Controleer of de *originele* DataFrame ongewijzigd is.
    assert "EMA_50" not in initial_df.columns
    # Vergelijk de originele DataFrame met zijn kopie om zeker te zijn.
    pd.testing.assert_frame_equal(initial_df, initial_df_copy)
