import logging

from config import EnvVariable
from geoserver_common import create_workspace_if_not_exists, create_datastore_layer, create_db_store_if_not_exists

log = logging.getLogger(__name__)


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
                        &quot;UR2023_V1_00_NAME&quot;,&#xd;
                        SUM(&quot;VKT (&apos;000 km/Year)&quot;) AS &quot;VKT&quot;,&#xd;
                        SUM(&quot;CO2 (Tonnes/Year)&quot;) AS &quot;CO2&quot;&#xd;
                        &#xd;
                        FROM sa1s&#xd;
                            inner join vehicle_stats vs&#xd;
                                ON sa1s.&quot;SA12018_V1_00&quot; = vs.&quot;SA12018_V1_00&quot;&#xd;
                        &#xd;
                        GROUP BY fuel_type,&#xd;
                             &quot;UR2023_V1_00_NAME&quot;&#xd;
                        ORDER BY &quot;UR2023_V1_00_NAME&quot;, &quot;VKT&quot; DESC
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
                                &quot;UR2023_V1_00_NAME&quot;,&#xd;
                                sum(&quot;VKT (&apos;000 km/Year)&quot;)
                                AS &quot;VKT&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Petrol&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END)        AS &quot;CO2_Petrol&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Diesel&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END)        AS &quot;CO2_Diesel&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Electric&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END)      AS &quot;CO2_Electric&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Hybrid&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END)        AS &quot;CO2_Hybrid&quot;,&#xd;
                                sum(CASE WHEN fuel_type ILIKE &apos;Plugin Hybrid&apos; THEN &quot;CO2 (Tonnes/Year)&quot; END) AS &quot;CO2_Plugin_Hybrid&quot;&#xd;
                        &#xd;
                        FROM vehicle_stats&#xd;
                            join sa1s&#xd;
                                on vehicle_stats.&quot;SA12018_V1_00&quot; = sa1s.&quot;SA12018_V1_00&quot;&#xd;
                        &#xd;
                        GROUP BY sa1s.&quot;SA12018_V1_00&quot;, &quot;geometry&quot;, &quot;AREA_SQ_KM&quot;, &quot;UR2023_V1_00_NAME&quot;
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
                        &quot;UR2023_V1_00_NAME&quot;,&#xd;
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


def initialise_geoserver_emissions():
    log.info("Creating SA1 emissions database views if they do not exist")

    workspace_name = "sa1_emissions"
    create_workspace_if_not_exists(workspace_name)

    db_name = EnvVariable.POSTGRES_DB
    data_store_name = f"{db_name} PostGIS"
    create_db_store_if_not_exists(db_name, workspace_name, data_store_name)

    create_sa1_view(workspace_name, data_store_name)
    create_vkt_sum_view(workspace_name, data_store_name)
    create_sa1_emissions_all_cars_view(workspace_name, data_store_name)
    create_sa1_emissions_fuel_type_view(workspace_name, data_store_name)
    log.info("SA1 emissions database views initialised")
