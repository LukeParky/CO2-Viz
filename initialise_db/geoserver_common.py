import logging
from http import HTTPStatus

import requests

from config import EnvVariable as Env

log = logging.getLogger(__name__)


def get_geoserver_url() -> str:
    """
    Retrieves full GeoServer URL from environment variables.

    Returns
    -------
    str
        The full GeoServer URL
    """
    return f"{Env.GEOSERVER_HOST}:{Env.GEOSERVER_PORT}/geoserver/rest"


def create_workspace_if_not_exists(workspace_name: str) -> None:
    """
    Creates a geoserver workspace if it does not currently exist.

    Parameters
    ----------
    workspace_name : str
        The name of the workspace to create if it does not exists.

    Returns
    -------
    None
        This function does not return anything.
    """

    # Create the geoserver REST API request to create the workspace
    log.info(f"Creating geoserver workspace {workspace_name} if it does not already exist.")
    req_body = {
        "workspace": {
            "name": workspace_name
        }
    }
    response = requests.post(
        f"{get_geoserver_url()}/workspaces",
        json=req_body,
        auth=(Env.GEOSERVER_ADMIN_NAME, Env.GEOSERVER_ADMIN_PASSWORD)
    )
    if response.status_code == HTTPStatus.CREATED:
        log.info(f"Created new workspace {workspace_name}.")
    elif response.status_code == HTTPStatus.CONFLICT:
        log.info(f"Workspace {workspace_name} already exists.")
    else:
        # If it does not meet the expected results then raise an error
        # Raise error manually so we can configure the text
        raise requests.HTTPError(response.text, response=response)


def create_datastore_layer(workspace_name, data_store_name: str, layer_name, metadata_elem: str = "") -> None:
    db_exists_response = requests.get(
        f'{get_geoserver_url()}/workspaces/{workspace_name}/datastores/{data_store_name}/featuretypes.json',
        auth=(Env.GEOSERVER_ADMIN_NAME, Env.GEOSERVER_ADMIN_PASSWORD),
    )
    response_data = db_exists_response.json()
    # Parse JSON structure to get list of feature names
    top_layer_node = response_data["featureTypes"]
    # defaults to empty list if no layers exist
    layers = top_layer_node["featureType"] if top_layer_node else []
    layer_names = [layer["name"] for layer in layers]
    if layer_name in layer_names:
        # If the layer already exists, we don't have to add it again, and can instead return
        return
    # Construct new layer request
    data = f"""
        <featureType>
            <name>{layer_name}</name>
            <title>{layer_name}</title>
            <srs>EPSG:4326</srs>
            <nativeBoundingBox>
                <minx>170.0</minx>
                <maxx>176.0</maxx>
                <miny>-46.0</miny>
                <maxy>-37.0</maxy>
                <crs>EPSG:4326</crs>
            </nativeBoundingBox>
            <latLonBoundingBox>
                <minx>170.0</minx>
                <maxx>176.0</maxx>
                <miny>-46.0</miny>
                <maxy>-37.0</maxy>
                <crs>EPSG:4326</crs>
            </latLonBoundingBox>
            <store>
                <class>dataStore</class>
                <name>{data_store_name}</name>
            </store>
            <numDecimals>8</numDecimals>
            {metadata_elem}
        </featureType>
        """

    response = requests.post(
        f"{get_geoserver_url()}/workspaces/{workspace_name}/datastores/{data_store_name}/featuretypes",
        params={"configure": "all"},
        headers={"Content-type": "text/xml"},
        data=data,
        auth=(Env.GEOSERVER_ADMIN_NAME, Env.GEOSERVER_ADMIN_PASSWORD),
    )
    if response.status_code == HTTPStatus.CREATED:
        log.info(f"Created new datastore layer {workspace_name}:{layer_name}.")
    else:
        # If it does not meet the expected results then raise an error
        # Raise error manually so we can configure the text
        raise requests.HTTPError(response.text, response=response)


def create_db_store_if_not_exists(db_name: str, workspace_name: str, new_data_store_name: str) -> None:
    """
    Creates PostGIS database store in a geoserver workspace for a given database.
    If it already exists, does not do anything.

    Parameters
    ----------
    workspace_name : str
        The name of the workspace to create views for

    Returns
    -------
    None
        This function does not return anything
    """
    # Create request to check if database store already exists
    db_exists_response = requests.get(
        f'{get_geoserver_url()}/workspaces/{workspace_name}/datastores',
        auth=(Env.GEOSERVER_ADMIN_NAME, Env.GEOSERVER_ADMIN_PASSWORD),
    )
    response_data = db_exists_response.json()

    # Parse JSON structure to get list of data store names
    top_data_store_node = response_data["dataStores"]
    # defaults to empty list if no data stores exist
    data_stores = top_data_store_node["dataStore"] if top_data_store_node else []
    data_store_names = [data_store["name"] for data_store in data_stores]

    if new_data_store_name in data_store_names:
        # If the data store already exists we don't have to do anything
        return

    # Create request to create database store
    create_db_store_data = f"""
        <dataStore>
          <name>{new_data_store_name}</name>
          <connectionParameters>
            <host>postgis</host>
            <port>5432</port>
            <database>{db_name}</database>
            <user>{Env.POSTGRES_USER}</user>
            <passwd>{Env.POSTGRES_PASSWORD}</passwd>
            <dbtype>postgis</dbtype>
          </connectionParameters>
        </dataStore>
        """
    # Send request to add datastore
    response = requests.post(
        f'{get_geoserver_url()}/workspaces/{workspace_name}/datastores',
        params={"configure": "all"},
        headers={"Content-type": "text/xml"},
        data=create_db_store_data,
        auth=(Env.GEOSERVER_ADMIN_NAME, Env.GEOSERVER_ADMIN_PASSWORD),
    )
    if response.status_code == HTTPStatus.CREATED:
        log.info(f"Created new db store {workspace_name}.")
    # Expected responses are CREATED if the new store is created or CONFLICT if one already exists.
    else:
        # If it does not meet the expected results then raise an error
        # Raise error manually so we can configure the text
        raise requests.HTTPError(response.text, response=response)
