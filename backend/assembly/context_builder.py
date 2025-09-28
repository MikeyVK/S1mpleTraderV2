# backend/assembly/context_builder.py
"""
Contains the ContextBuilder, responsible for executing a sequence of
context-providing plugins to enrich a DataFrame.

@layer: Backend (Assembly)
@dependencies: [pandas]
@responsibilities:
    - Sequentially applies a list of instantiated context workers to a DataFrame.
    - Ensures the original DataFrame is not modified (works on a copy).
    - Returns the final, enriched DataFrame.
"""
from typing import List

import pandas as pd

from backend.core.interfaces import ContextWorker

class ContextBuilder:
    """Executes a pipeline of context workers to enrich a DataFrame."""

    def build(self,
              initial_df: pd.DataFrame,
              context_pipeline: List[ContextWorker]
        ) -> pd.DataFrame:
        """
        Applies a list of context workers sequentially to a DataFrame.

        This method takes a starting DataFrame and a list of worker objects
        (which are expected to have a 'process' method). It creates a copy of
        the DataFrame and then passes it through each worker in order, with the
        output of one worker becoming the input for the next.

        Args:
            initial_df (pd.DataFrame): The raw OHLCV DataFrame.
            context_pipeline (List[object]): An ordered list of instantiated
                                             context worker objects.

        Returns:
            pd.DataFrame: The final, enriched DataFrame after all workers
                          have been executed.
        """
        # Werk altijd op een kopie om onverwachte bijeffecten te voorkomen.
        enriched_df = initial_df.copy()

        for worker in context_pipeline:
            # We gaan ervan uit dat elke 'worker' een .process(df) methode heeft.
            # De test die we hebben geschreven, valideert deze aanname.
            enriched_df = worker.process(enriched_df)

        return enriched_df
