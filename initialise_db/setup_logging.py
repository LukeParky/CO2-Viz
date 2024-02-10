import logging
import warnings
from enum import IntEnum

log = logging.getLogger(__name__)


class LogLevel(IntEnum):
    """
    Enum class representing different logging levels mapped to their corresponding numeric values from the
    logging library.

    Attributes
    ----------
    CRITICAL : int
        The critical logging level. Corresponds to logging.CRITICAL (50).
    ERROR : int
        The error logging level. Corresponds to logging.ERROR (40).
    WARNING : int
        The warning logging level. Corresponds to logging.WARNING (30).
    INFO : int
        The info logging level. Corresponds to logging.INFO (20).
    DEBUG : int
        The debug logging level. Corresponds to logging.DEBUG (10).
    NOTSET : int
        The not-set logging level. Corresponds to logging.NOTSET (0).
    """
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


def setup_logging(log_level: LogLevel = LogLevel.DEBUG) -> None:
    """
    Configures the root logger with the specified log level and formats, captures warnings, and excludes specific
    loggers from propagating their messages to the root logger. Additionally, logs a debug message indicating the
    execution of the function in the script.

    Parameters
    ----------
    log_level : LogLevel = LogLevel.DEBUG
        The log level to set for the root logger. Defaults to LogLevel.DEBUG.
        The available logging levels and their corresponding numeric values are:
        - LogLevel.CRITICAL (50)
        - LogLevel.ERROR (40)
        - LogLevel.WARNING (30)
        - LogLevel.INFO (20)
        - LogLevel.DEBUG (10)
        - LogLevel.NOTSET (0)

    Returns
    -------
    None
        This function does not return any value.
    """
    # Define the logging format and date format
    logging_format = "%(asctime)s | %(levelname)-6s | %(name)-8s %(lineno)4d | %(funcName)-35s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    # Create and configure the root logger with the specified log level and formats
    logging.basicConfig(level=log_level, format=logging_format, datefmt=date_format)
    # Enable capturing Python warnings and redirect them to the logging system
    logging.captureWarnings(True)
    # Suppress (ignore) Python warnings from appearing in the console
    warnings.simplefilter("ignore")
    # List of loggers to prevent messages from reaching the root logger
    loggers_to_exclude = [
        "urllib3", "fiona", "pyproj"
    ]
    # Iterate through the loggers to exclude
    for logger_name in loggers_to_exclude:
        # Get the logger instance for each name in the list
        logger = logging.getLogger(logger_name)
        # Disable log message propagation from these loggers to the root logger
        logger.propagate = False
