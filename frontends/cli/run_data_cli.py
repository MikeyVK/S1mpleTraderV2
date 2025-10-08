# In bestand: frontends/cli/run_data_cli.py
"""
Entrypoint for all data-related CLI operations.

This script provides a command-line interface to interact with the
DataCommandService, allowing for real-world testing and execution of data
fetching and synchronization tasks.
"""
import sys
from pathlib import Path
import logging

# Voeg de project root toe aan het pad zodat we de backend/services kunnen importeren
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# pylint: disable=wrong-import-position
import pandas as pd
from typing_extensions import Annotated
import typer
import yaml

from backend.config.schemas.connectors.kraken_schema import KrakenPublicConfig
from backend.config.schemas.platform_schema import PlatformConfig
from backend.config.schemas.connectors_schema import ConnectorsConfig
from backend.utils.translator import Translator
from backend.utils.app_logger import configure_logging, LogEnricher
from backend.data.persistors.parquet_persistor import ParquetPersistor
from backend.environments.api_connectors.kraken_connector import KrakenAPIConnector
from backend.dtos.commands import FetchPeriodCommand, SynchronizationCommand
from services.data_command_service import DataCommandService
# pylint: enable=wrong-import-position

# --- Bootstrap Functie (Het opbouwen van de service) ---

def bootstrap_service() -> DataCommandService:
    """Loads all configs and instantiates the full DataCommandService."""
    # 1. Laad configuratiebestanden
    with open(project_root / "config/platform.yaml", 'r', encoding="utf-8") as f:
        platform_conf_raw = yaml.safe_load(f)
    platform_config = PlatformConfig(**platform_conf_raw)

    with open(project_root / "config/connectors.yaml", 'r', encoding="utf-8") as f:
        connectors_conf_raw = yaml.safe_load(f)
    connectors_config = ConnectorsConfig(connectors_conf_raw)

    # 2. Initialiseer basis-dependencies
    translator = Translator(platform_config=platform_config, project_root=project_root)
    configure_logging(logging_config=platform_config.core.logging, translator=translator)  # pylint: disable=no-member
    root_logger = logging.getLogger()
    logger = LogEnricher(root_logger)

    # 3. Initialiseer de specifieke componenten
    persistor = ParquetPersistor(data_dir=Path(platform_config.data.source_dir))  # pylint: disable=no-member

    kraken_conf = connectors_config.root.get('kraken_public')  # pylint: disable=no-member
    if not kraken_conf:
        raise ValueError("Connector 'kraken_public' not found in connectors.yaml")

    if not isinstance(kraken_conf, KrakenPublicConfig):
        raise TypeError("The 'kraken_public' connector is not of type 'KrakenPublicConfig'")

    connector = KrakenAPIConnector(logger=logger, config=kraken_conf)

    # 4. Bouw en retourneer de uiteindelijke service
    return DataCommandService(
        persistor=persistor,
        connector=connector,
        limits=platform_config.services.data_collection.limits,  # pylint: disable=no-member
        logger=logger
    )

# --- CLI Applicatie ---
app = typer.Typer(
    help="CLI tool for managing S1mpleTraderV2 data archives.",
    add_completion=False
)
# Initialiseer de service eenmalig bij het opstarten
service_instance = bootstrap_service()

@app.command()
def synchronize(
    pair: Annotated[str, typer.Option(help="The trading pair to synchronize, e.g., 'BTC/EUR'.")]
):
    """Synchronizes the archive for a pair with the latest trades."""
    typer.echo(f"🚀 Starting synchronization for {pair}...")
    command = SynchronizationCommand(pair=pair)
    try:
        service_instance.synchronize(command)
        typer.secho("✅ Synchronization complete!", fg=typer.colors.GREEN)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
    except NotImplementedError as e:
        typer.secho(f"Functionality Error: {e}", fg=typer.colors.YELLOW)
    except RuntimeError as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)

@app.command()
def fetch_period(
    pair: Annotated[str, typer.Option(help="The trading pair to fetch, e.g., 'XRP/EUR'.")],
    start_date: Annotated[str, typer.Option(help="Start date in YYYY-MM-DD format.")]
):
    """Fetches a historical period for a new or existing archive."""
    typer.echo(f"🚀 Starting historical fetch for {pair} from {start_date}...")
    try:
        start_ts = pd.to_datetime(start_date, utc=True)
        command = FetchPeriodCommand(pair=pair, start_date=start_ts, end_date=None)

        service_instance.fetch_period(command)
        typer.secho("✅ Historical fetch complete!", fg=typer.colors.GREEN)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
    except NotImplementedError as e:
        typer.secho(f"Functionality Error: {e}", fg=typer.colors.YELLOW)
    except RuntimeError as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
