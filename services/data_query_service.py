# In bestand: services/data_query_service.py
"""
Contains the DataQueryService, responsible for orchestrating read-only
actions (Queries) against the data archives.

This service acts as the "Inquiry" layer for data access, adhering to the
CQRS principle by strictly separating read operations from write operations.

@layer: Service
@dependencies: [IDataPersistor, IAPIConnector, LogEnricher]
"""
from typing import List

from backend.core.interfaces.persistors import IDataPersistor
from backend.dtos.market.data_coverage import DataCoverage
from backend.dtos.queries.coverage_query import CoverageQuery


class DataQueryService:
    """Orchestrates read-only inquiries for the historical data archive."""

    def __init__(self, persistor: IDataPersistor):
        """Initializes the DataQueryService.

        Args:
            persistor (IDataPersistor): The data persistence component that
                provides access to the stored data.
        """
        self._persistor = persistor

    def get_coverage(self, query: CoverageQuery) -> List[DataCoverage]:
        """Retrieves the data coverage map for a specific trading pair.

        This method acts as a simple "pass-through" to the persistence layer.
        It takes a query object, extracts the trading pair, and calls the
        corresponding method on the persistor to get the data coverage.

        Args:
            query (CoverageQuery): A DTO containing the 'pair' for which to
                retrieve the coverage map.

        Returns:
            A list of DataCoverage DTOs, where each object represents a
            contiguous block of available historical data.
        """
        # Delegeer de aanroep direct naar de persistor.
        # De service is hier verantwoordelijk voor de 'orkestratie',
        # zelfs als dat in dit geval een simpele 1-op-1 aanroep is.
        return self._persistor.get_data_coverage(query.pair)
