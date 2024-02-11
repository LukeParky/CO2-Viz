import logging
from http import HTTPStatus

import requests

from config import EnvVariable as Env
from setup_logging import setup_logging

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
                <minx>172.35427856445312</minx>
                <maxx>172.80812072753906</maxx>
                <miny>-43.65361404418945</miny>
                <maxy>-43.40265655517578</maxy>
                <crs>EPSG:4326</crs>
            </nativeBoundingBox>
            <latLonBoundingBox>
                <minx>172.35427856445312</minx>
                <maxx>172.80812072753906</maxx>
                <miny>-43.65361404418945</miny>
                <maxy>-43.40265655517578</maxy>
                <crs>EPSG:4326</crs>
            </latLonBoundingBox>
            <store>
                <class>dataStore</class>
                <name>{data_store_name}</name>
            </store>
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


def create_building_layers(workspace_name: str, data_store_name: str) -> None:
    """
    Creates dynamic geoserver layers "nz_building_outlines" and "building_flood_status" for the given workspace.
    If they already exist then does nothing.
    "building_flood_status" required viewparam=scenario:{model_id} to dynamically fetch correct flood statuses.

    Parameters
    ----------
    workspace_name : str
        The name of the workspace to create views for

    Returns
    -------
    None
        This function does not return anything
    """
    # Simple layer that is just displaying the nz_building_outlines database table
    create_datastore_layer(workspace_name, data_store_name, layer_name="nz_building_outlines")

    # More complex layer that has to do dynamic sql queries against model output ID to fetch
    flood_status_layer_name = "building_flood_status"
    flood_status_xml_query = f"""
      <metadata>
        <entry key="JDBC_VIRTUAL_TABLE">
          <virtualTable>
            <name>{flood_status_layer_name}</name>
            <sql>
                SELECT * &#xd;
                FROM nz_building_outlines&#xd;
                LEFT OUTER JOIN (&#xd;
                    SELECT *&#xd;
                    FROM building_flood_status&#xd;
                    WHERE flood_model_id=%scenario%&#xd;
                ) AS flood_statuses&#xd;
                USING (building_outline_id)&#xd;
                WHERE building_outline_lifecycle ILIKE &apos;current&apos;
            </sql>
            <escapeSql>false</escapeSql>
            <geometry>
              <name>geometry</name>
              <type>Polygon</type>
              <srid>2193</srid>
            </geometry>
            <parameter>
              <name>scenario</name>
              <defaultValue>-1</defaultValue>
              <regexpValidator>^(-)?[\d]+$</regexpValidator>
            </parameter>
          </virtualTable>
        </entry>
      </metadata>
    """
    create_datastore_layer(workspace_name, data_store_name, layer_name="building_flood_status",
                           metadata_elem=flood_status_xml_query)


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


def create_sa1_view(workspace_name: str, data_store_name: str):
    create_datastore_layer(workspace_name, data_store_name, layer_name="sa1s")


def create_vkt_sum_view(workspace_name: str, data_store_name: str):
    vkt_sum_layer_name = "vkt_sum"
    vkt_sum_xml_query = f"""
        <metadata>
            <entry key="JDBC_VIRTUAL_TABLE">
                <virtualTable>
                    <name>{vkt_sum_layer_name}</name>
                    <sql>SELECT&#xd;
                        fuel_type,&#xd;
                        SUM(&quot;VKT (&apos;000 km/Year)&quot;) AS &quot;VKT&quot;&#xd;
                        &#xd;
                        FROM sa1s inner join vehicle_stats vs &#xd;
                        ON sa1s.&quot;SA12018_V1_00&quot; = vs.&quot;SA12018_V1_00&quot;&#xd;
                        &#xd;
                        GROUP BY fuel_type&#xd;
                        ORDER BY &quot;VKT&quot; DESC
                    </sql>
                    <escapeSql>false</escapeSql>
                </virtualTable>
            </entry>
        </metadata>
       """
    create_datastore_layer(workspace_name, data_store_name, layer_name=vkt_sum_layer_name,
                           metadata_elem=vkt_sum_xml_query)


def create_sa1_emissions_all_cars_view(workspace_name: str, data_store_name: str):
    all_cars_layer_name = "sa1_emissions_all_cars"
    all_cars_query = f"""
        <metadata>
            <entry key="JDBC_VIRTUAL_TABLE">
                <virtualTable>
                    <name>sa1_emissions_all_cars</name>
                    <sql>SELECT sa1s.&quot;SA12018_V1_00&quot;,&#xd;
                                &quot;geometry&quot;,&#xd;
                                &quot;AREA_SQ_KM&quot;,&#xd;
                                sum(&quot;VKT (&apos;000 km/Year)&quot;)                                            AS &quot;VKT&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Petrol&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END) AS &quot;CO2_Petrol&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Diesel&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END) AS &quot;CO2_Diesel&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Electric&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END) AS &quot;CO2_Electric&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Hybrid&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END) AS &quot;CO2_Hybrid&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Plugin Hybrid&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END) AS &quot;CO2_Plugin_Hybrid&quot;&#xd;
                        &#xd;
                        FROM vehicle_stats&#xd;
                            join sa1s&#xd;
                                on vehicle_stats.&quot;SA12018_V1_00&quot; = sa1s.&quot;SA12018_V1_00&quot;&#xd;
                        &#xd;
                        GROUP BY sa1s.&quot;SA12018_V1_00&quot;, &quot;geometry&quot;, &quot;AREA_SQ_KM&quot;
                    </sql>
                    <escapeSql>false</escapeSql>
                    <geometry>
                        <name>geometry</name>
                        <type>Geometry</type>
                        <srid>-1</srid>
                    </geometry>
                </virtualTable>
            </entry>
        </metadata>
    """
    create_datastore_layer(workspace_name, data_store_name, layer_name=all_cars_layer_name,
                           metadata_elem=all_cars_query)


def create_sa1_emissions_fuel_type_view(workspace_name, data_store_name):
    fuel_type_layer_name = "sa1_emissions_fuel_type"
    fuel_type_query = f"""
        <metadata>
            <entry key="JDBC_VIRTUAL_TABLE">
                <virtualTable>
                    <name>{fuel_type_layer_name}</name>
                    <sql>SELECT sa1s.&quot;SA12018_V1_00&quot;,&#xd;
                        geometry,&#xd;
                        &quot;AREA_SQ_KM&quot;,&#xd;
                        &quot;CO2 (Tonnes/Year)&quot; AS &quot;CO2&quot;,&#xd;
                        &quot;VKT (&apos;000 km/Year)&quot; AS &quot;VKT&quot;&#xd;
                        &#xd;
                        FROM sa1s INNER JOIN vehicle_stats vs&#xd;
                        ON sa1s.&quot;SA12018_V1_00&quot; = vs.&quot;SA12018_V1_00&quot;&#xd;
                        WHERE fuel_type ILIKE &apos;%FUEL_TYPE%%&apos;
                    </sql>
                    <escapeSql>false</escapeSql>
                    <geometry>
                        <name>geometry</name>
                        <type>Geometry</type>
                        <srid>-1</srid>
                    </geometry>
                    <parameter>
                        <name>FUEL_TYPE</name>
                        <regexpValidator>^[\w\s]+$</regexpValidator>
                    </parameter>
                </virtualTable>
            </entry>
        </metadata>
    """
    create_datastore_layer(workspace_name, data_store_name, layer_name=fuel_type_layer_name,
                           metadata_elem=fuel_type_query)


def initialise_geoserver():
    log.info("Creating sa1 database views if they do not exist")

    workspace_name = "carbon_neutral"
    create_workspace_if_not_exists(workspace_name)

    db_name = Env.POSTGRES_DB
    data_store_name = f"{db_name} PostGIS"
    create_db_store_if_not_exists(db_name, workspace_name, data_store_name)

    create_sa1_view(workspace_name, data_store_name)
    create_vkt_sum_view(workspace_name, data_store_name)
    create_sa1_emissions_all_cars_view(workspace_name, data_store_name)
    create_sa1_emissions_fuel_type_view(workspace_name, data_store_name)
    log.info("Geoserver initialised")


if __name__ == '__main__':
    initialise_geoserver()
