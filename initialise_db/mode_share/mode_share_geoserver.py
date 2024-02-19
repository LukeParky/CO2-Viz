import logging

from config import EnvVariable
from geoserver_common import create_workspace_if_not_exists, create_datastore_layer, create_db_store_if_not_exists

log = logging.getLogger(__name__)


def create_sa2_view(workspace_name: str, data_store_name: str):
    create_datastore_layer(workspace_name, data_store_name, layer_name="sa2s")


def create_mode_share_view(workspace_name: str, data_store_name: str):
    mode_share_layer_name = "mode_share"
    mode_share_query = f"""
        <metadata>
            <entry key="JDBC_VIRTUAL_TABLE">
                <virtualTable>
                    <name>{mode_share_layer_name}</name>
                    <sql>SELECT &quot;SA2_code_usual_residence_address&quot;,&#xd;
                        &quot;SA2_code_workplace_address&quot;,&#xd;
                        &quot;Work_at_home&quot;,&#xd;
                        &quot;Passenger_in_a_car_truck_van_or_company_bus&quot;,&#xd;
                        (&quot;Drive_a_private_car_truck_or_van&quot; + &quot;Drive_a_company_car_truck_or_van&quot;) as Drive,&#xd;
                        (&quot;Public_bus&quot; + &quot;Train&quot; + &quot;Ferry&quot;)                                        as Public_transport,&#xd;
                        (&quot;Walk_or_jog&quot; + &quot;Bicycle&quot;)                                               as Active_transport,&#xd;
                        &quot;Other&quot;,&#xd;
                        &quot;Total&quot;&#xd;
                        &#xd;
                        &#xd;
                        FROM mode_share
                    </sql>
                    <escapeSql>false</escapeSql>
                </virtualTable>
            </entry>
        </metadata>
    """
    create_datastore_layer(workspace_name, data_store_name, layer_name=mode_share_layer_name,
                           metadata_elem=mode_share_query
)


def initialise_geoserver_mode_share():
    log.info("Creating SA2 mode share database views if they do not exist")

    workspace_name = "sa2_mode_share"
    create_workspace_if_not_exists(workspace_name)

    db_name = EnvVariable.POSTGRES_DB
    data_store_name = f"{db_name} PostGIS"
    create_db_store_if_not_exists(db_name, workspace_name, data_store_name)

    create_sa2_view(workspace_name, data_store_name)
    create_mode_share_view(workspace_name, data_store_name)
    log.info("SA2 mode share database views initialised")
