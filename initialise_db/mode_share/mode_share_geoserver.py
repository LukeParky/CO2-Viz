import logging

from config import EnvVariable
from geoserver_common import create_workspace_if_not_exists, create_datastore_layer, create_db_store_if_not_exists

log = logging.getLogger(__name__)


def create_sa2_view(workspace_name: str, data_store_name: str):
    create_datastore_layer(workspace_name, data_store_name, layer_name="sa2s")


def create_mode_share_view(workspace_name: str, data_store_name: str):
    mode_share_layer_name = "mode_share"

    # Construct query linking medusa_table_class to its geometry table
    mode_share_sql_query = f"""
        SELECT
            "SA2_code_usual_residence_address",
            "SA2_code_workplace_address",
            "Work_at_home",
            "Passenger_in_a_car_truck_van_or_company_bus",
            ("Drive_a_private_car_truck_or_van", "Drive_a_company_car_truck_or_van") AS "Drive",
            ("Public_bus" + "Train" + "Ferry") AS "Public_transport",
            ("Walk_or_jog" + "Bicycle") AS "Active_transport",
            "Other",
            "Total"
        FROM {mode_share_layer_name}
    """
    # Escape characters in SQL query so that it is valid Geoserver XML
    xml_escaped_sql = saxutils.escape(mode_share_sql_query, entities={r"'": "&apos;", "\n": "&#xd;"})

    mode_share_query = f"""
        <metadata>
            <entry key="JDBC_VIRTUAL_TABLE">
                <virtualTable>
                    <name>{mode_share_layer_name}</name>
                    <sql>
                        {xml_escaped_sql}
                    </sql>
                    <escapeSql>false</escapeSql>
                </virtualTable>
            </entry>
        </metadata>
    """
    create_datastore_layer(workspace_name, data_store_name, layer_name=mode_share_layer_name,
                           metadata_elem=mode_share_query
                           )


def create_flow_sheets_view(workspace_name: str, data_store_name: str) -> None:
    create_datastore_layer(workspace_name, data_store_name, layer_name="flow_sheets")


def initialise_geoserver_mode_share():
    log.info("Creating SA2 mode share database views if they do not exist")

    workspace_name = "sa2_mode_share"
    create_workspace_if_not_exists(workspace_name)

    db_name = EnvVariable.POSTGRES_DB
    data_store_name = f"{db_name} PostGIS"
    create_db_store_if_not_exists(db_name, workspace_name, data_store_name)

    create_sa2_view(workspace_name, data_store_name)
    create_mode_share_view(workspace_name, data_store_name)
    create_flow_sheets_view(workspace_name, data_store_name)
    log.info("SA2 mode share database views initialised")
