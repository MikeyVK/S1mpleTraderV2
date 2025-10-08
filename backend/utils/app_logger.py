# utils/app_logger.py
"""
Configures and provides the application's logging system.

This module is the single source of truth for all logging-related setup.
It is designed to be configured once at the application's entry point.

@layer: Utility
@dependencies:
    - Translator: The `LogFormatter` receives a `Translator` instance to translate log message keys.
    - Constants: Uses `core.constants` for log level definitions and default profile names.
@responsibilities:
    - Defines the custom `LogFormatter` to handle translation and indentation of log messages.
    - Defines the `LogEnricher` adapter, which is the standard logger interface for the application.
    - Defines the `LogProfiler` to filter logs based on the configured profile.
    - Provides the central `configure_logging` function to bootstrap the logging system.
@inputs:
    - The application `config` dictionary.
    - A `Translator` instance.
@outputs:
    - A fully configured root logger (side-effect).
"""

# 1. Standard Library Imports
import logging
import sys
from typing import Any, Dict, List, Literal, MutableMapping, Optional, Tuple

# 3. Our Application Imports
from backend.utils.translator import Translator
from backend.core.enums import LogLevel
from backend.config.schemas.platform_schema import LoggingConfig

class LogFormatter(logging.Formatter):
    """A custom log formatter that handles translation, value formatting, and indentation.

    This formatter intercepts the log record, translates the message key if
    applicable, formats the translated string with any provided values, and
    applies an indentation level based on the record's context.
    """

    def __init__(self,
                 fmt: Optional[str] = None,
                 datefmt: Optional[str] = None,
                 style: Literal['%', '{', '$'] = '%',
                 translator: Optional[Translator] = None):
        """Initializes the LogFormatter.

        Args:
            fmt (str, optional): The format string for the log. Defaults to None.
            datefmt (str, optional): The format string for dates. Defaults to None.
            style (str, optional): The formatting style. Defaults to '%'.
            translator (Translator, optional): The translator instance for
                                               translating log keys. Defaults to None.
        """
        super().__init__(fmt, datefmt, style)
        self.translator = translator

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record by translating, populating, and indenting it.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            The fully formatted log message string.
        """
        key = record.msg
        translated_template = key
        values_dict = getattr(record, 'values', {})

        # Step 1: Translate the message key, if it's a valid key.
        if self.translator and isinstance(key, str) and '.' in key and ' ' not in key:
            translated_template = self.translator.get(key, default=key)

        # Step 2: Format the template with any provided values.
        final_message = translated_template
        if values_dict:
            try:
                final_message = translated_template.format(**values_dict)
            except (KeyError, TypeError):
                final_message = f"{translated_template} [FORMATTING ERROR]"

        record.msg = final_message
        record.args = ()

        # Step 3: Apply our custom indentation directly to the message content.
        indent_level = getattr(record, 'indent', 0)
        indented_message = "  " * indent_level + final_message

        # Place the fully prepared (and indented) message back into the record.
        record.msg = indented_message

        # Step 4: Let the original Formatter handle the primary layout (e.g., [INFO   ]).
        return super().format(record)

class LogEnricher(logging.LoggerAdapter[logging.Logger]):
    """A logger adapter that enriches log records with indentation and context.

    This adapter provides the standard logging interface for the application. Its
    main purpose is to shuttle contextual data (like 'indent' or 'values') into
    the 'extra' payload of a log record, which can then be used by the
    `LogFormatter`. It also provides convenience methods for custom log levels.
    """

    def __init__(self, logger: logging.Logger, indent: int = 0):
        """Initializes the LogEnricher adapter.

        Args:
            logger: The logger instance to wrap.
            indent: The indentation level for messages from this logger.
        """
        super().__init__(logger, {'indent': indent})

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        """Merges the adapter's contextual information into the kwargs.

        Args:
            msg: The log message.
            kwargs: Keyword arguments to the logging call.

        Returns:
            A tuple containing the message and the modified keyword arguments.
        """
        # Ensure 'extra' dictionary exists and merge adapter's context into it.
        kwargs["extra"] = kwargs.get("extra", {})
        kwargs["extra"].update(self.extra)

        # Move 'values' from kwargs into the 'extra' dict for the formatter.
        if 'values' in kwargs:
            kwargs['extra']['values'] = kwargs.pop('values')

        return msg, kwargs

    # --- Convenience methods for custom levels ---
    def setup(self, key: str, **values: Any) -> None:
        """Logs a message with the SETUP level."""
        self.log(CUSTOM_LEVELS[LogLevel.SETUP], key, values=values)

    def match(self, key: str, **values: Any) -> None:
        """Logs a message with the MATCH level."""
        self.log(CUSTOM_LEVELS[LogLevel.MATCH], key, values=values)

    def filter(self, key: str, **values: Any) -> None:
        """Logs a message with the FILTER level."""
        self.log(CUSTOM_LEVELS[LogLevel.FILTER], key, values=values)

    def policy(self, key: str, **values: Any) -> None:
        """Logs a message with the POLICY level."""
        self.log(CUSTOM_LEVELS[LogLevel.POLICY], key, values=values)

    def result(self, key: str, **values: Any) -> None:
        """Logs a message with the RESULT level."""
        self.log(CUSTOM_LEVELS[LogLevel.RESULT], key, values=values)

    def trade(self, key: str, **values: Any) -> None:
        """Logs a message with the TRADE level."""
        self.log(CUSTOM_LEVELS[LogLevel.TRADE], key, values=values)

class LogProfiler(logging.Filter):
    """A logging filter that allows messages based on the active profile."""

    def __init__(self, profile: str, profile_definitions: Dict[str, List[LogLevel]]):
        """Initializes the filter.

        Args:
            profile: The name of the active logging profile.
            profile_definitions: A dictionary defining all available profiles
                                 and their allowed log level names.
        """
        super().__init__()
        allowed_levels_for_profile = profile_definitions.get(profile, [])
        self.allowed_levels = {level.value for level in allowed_levels_for_profile}

    def filter(self, record: logging.LogRecord) -> bool:
        """Determines if a log record should be processed.

        Args:
            record: The log record to check.

        Returns:
            True if the record's level name is in the allowed set for the
            active profile, False otherwise.
        """
        return record.levelname in self.allowed_levels

# Define and register custom log levels. This mapping is an implementation
# detail of the logger and is therefore defined here, not in core.constants.
CUSTOM_LEVELS = {
    LogLevel.SETUP: 15,
    LogLevel.MATCH: 22,
    LogLevel.FILTER: 23,
    LogLevel.POLICY: 24,
    LogLevel.RESULT: 25,
    LogLevel.TRADE: 26,
}

def configure_logging(logging_config: LoggingConfig, translator: Translator):
    """Configures the central, root logger for the entire application.

    This function should be called only once from `main.py`. It sets up custom
    log levels, creates a handler, attaches the custom `LogFormatter` and
    `LogProfiler` filter, and adds the handler to the root logger.

    Args:
        logging_config: The Pydantic model for the logging configuration.
        translator: An existing translator instance to be used by the formatter.
    """
    for level_enum, level_value in CUSTOM_LEVELS.items():
        logging.addLevelName(level_value, level_enum.value)

    # Use dotted access on the Pydantic model
    log_profile = logging_config.profile
    profile_definitions = logging_config.profiles
    log_format = '[%(levelname)-8s] %(message)s'

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers to prevent duplicate logs.
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    # The Formatter is the only component that needs the translator.
    handler.setFormatter(LogFormatter(log_format, translator=translator))
    handler.addFilter(LogProfiler(log_profile, profile_definitions))
    logger.addHandler(handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)