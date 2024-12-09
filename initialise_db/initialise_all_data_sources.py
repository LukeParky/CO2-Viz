import logging

from dotenv import load_dotenv

from config import get_db_engine
from emissions.emissions_geoserver import initialise_geoserver_emissions
from emissions.initialise_co2_sa1s import initialise_co2_sa1s
from mode_share.flowmap import save_flow_map_sheets
from mode_share.initialise_mode_share import ModeShareFlowInitialiser, ModeShare2023Initialiser
from mode_share.mode_share_geoserver import initialise_geoserver_mode_share
from setup_logging import setup_logging

log = logging.getLogger(__name__)


def main():
    setup_logging()
    log.info(f"Checking database initialisation")
    load_dotenv()
    engine = get_db_engine()
    log.info(f"Initialising database {engine}")
    initialise_co2_sa1s(engine)
    ModeShareFlowInitialiser().initialise_mode_share(engine)
    ModeShare2023Initialiser().initialise_mode_share(engine)
    log.info("Database initialised")
    log.info("Initialising flow map Google Sheets")
    save_flow_map_sheets(engine)
    log.info("Flow map Google Sheets initialised")
    log.info("Initialising geoserver")
    initialise_geoserver_emissions()
    initialise_geoserver_mode_share()
    log.info("Geoserver initialised")


if __name__ == '__main__':
    main()
