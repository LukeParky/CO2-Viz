import base64
import json
import logging
import os
import pathlib
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.engine import create_engine, Engine

load_dotenv("..")
load_dotenv()

log = logging.getLogger(__name__)


def get_env_variable(var_name: str, default: str = None, allow_empty: bool = False) -> str:
    """
    Reads a string environment variable, with settings to allow defaults, empty values.
    To read a boolean user get_bool_env_variable

    Parameters
    ----------
    var_name : str
        The name of the environment variable to retrieve.
    default : T = None
        Default return value if the environment variable does not exist.
    allow_empty : bool
        If False then a ValueError will be raised if the environment variable is empty.

    Returns
    -------
    The environment variable, or default if it does not exist, as type T.

    Raises
    ------
    KeyError
        If allow_empty is False and the environment variable is empty string or None
    """
    env_var = os.getenv(var_name)
    if default is not None and env_var in (None, ""):
        # Set env_var to default, but do not override empty str with None
        env_var = default
    if not allow_empty and env_var in (None, ""):
        raise KeyError(f"Environment variable {var_name} not set, and allow_empty is False")
    return env_var


def get_bool_env_variable(var_name: str, default: Optional[bool] = None, allow_empty: bool = False) -> bool:
    """
    Reads an environment variable and attempts to cast to bool, with settings to allow defaults, empty values.
    For bool we have the problem where bool("False") == True but we want this function to return False

    Parameters
    ----------
    var_name : str
        The name of the environment variable to retrieve.
    default : Optional[bool] = None
        Default return value if the environment variable does not exist.
    allow_empty : bool
        If False then a KeyError will be raised if the environment variable is empty.

    Returns
    -------
    bool
        The environment variable, or default if it does not exist

    Raises
    ------
    ValueError
        If allow_empty is False and the environment variable is empty string or None
    """
    env_variable = get_env_variable(var_name, default, allow_empty)
    truth_values = {"true", "t", "1"}
    false_values = {"false", "f", "0"}
    if env_variable.lower() in truth_values:
        return True
    elif env_variable.lower() in false_values:
        return False
    raise ValueError(f"Environment variable {var_name}={env_variable} being casted to bool "
                     f"but is not in {truth_values} or {false_values}")


class EnvVariable:
    ADMIN_EMAIL = get_env_variable("ADMIN_EMAIL", default="luke.parkinson@canterbury.ac.nz")
    EMISSIONS_DATA = pathlib.Path(get_env_variable("EMISSIONS_DATA"))
    MEANS_OF_TRAVEL_DATA = pathlib.Path(get_env_variable("MEANS_OF_TRAVEL_DATA"))

    POSTGRES_HOST = get_env_variable("POSTGRES_HOST")
    POSTGRES_PORT = get_env_variable("POSTGRES_PORT")
    POSTGRES_DB = get_env_variable("POSTGRES_DB")
    POSTGRES_USER = get_env_variable("POSTGRES_USER")
    POSTGRES_PASSWORD = get_env_variable("POSTGRES_PASSWORD")

    GEOSERVER_HOST = get_env_variable("GEOSERVER_HOST")
    GEOSERVER_PORT = get_env_variable("GEOSERVER_PORT")
    GEOSERVER_ADMIN_NAME = get_env_variable("GEOSERVER_ADMIN_NAME")
    GEOSERVER_ADMIN_PASSWORD: str = get_env_variable("GEOSERVER_ADMIN_PASSWORD")

    STATS_API_KEY: str = get_env_variable("STATS_API_KEY")
    GOOGLE_CREDENTIALS: dict = json.loads(base64.b64decode(get_env_variable("GOOGLE_CREDENTIALS_BASE64")))


def get_db_engine() -> Engine:
    pg_user = EnvVariable.POSTGRES_USER
    pg_pass = EnvVariable.POSTGRES_PASSWORD
    pg_host = EnvVariable.POSTGRES_HOST
    pg_port = EnvVariable.POSTGRES_PORT
    pg_db = EnvVariable.POSTGRES_DB
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}', pool_pre_ping=True)
    log.info(f"Attempting to connect to {engine}")
    with engine.connect():
        log.info(f"Connection to {engine} successful")
    return engine
