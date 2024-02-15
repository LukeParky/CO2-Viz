import logging

from dotenv import load_dotenv

from config import get_db_engine
from emissions.initialise_geoserver import initialise_geoserver
from emissions.initialise_co2_sa1s import initialise_co2_sa1s
from mode_share.initialise_mode_share import initialise_mode_share
from setup_logging import setup_logging

log = logging.getLogger(__name__)


def main():
    setup_logging()
    log.info(f"Checking database initialisation")
    load_dotenv()
    engine = get_db_engine()
    log.info(f"Initialising database {engine}")
    initialise_co2_sa1s(engine)
    initialise_mode_share(engine)
    log.info("Database initialised")
    log.info("Initialising geoserver")
    initialise_geoserver()
    log.info("Geoserver initialised")


if __name__ == '__main__':
    main()
