import dataclasses
import logging
import os

import geoapis.vector
import geopandas as gpd
import pandas as pd
import shapely
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.engine import Engine, create_engine

from config import EnvVariable as Env
from initialise_geoserver import initialise_geoserver
from setup_logging import setup_logging

log = logging.getLogger(__name__)


def find_sa1s_in_areas_of_interest() -> gpd.GeoDataFrame:
    sa1_dfs = [
        find_sa1s_in_area("Auckland", approx_area=Bbox(-37.11973, 174.56626, -36.66668, 175.00701)),
        find_sa1s_in_area("Wellington", approx_area=Bbox(-41.36836, 174.69794, -41.13047, 174.90839)),
        find_sa1s_in_area("Christchurch", approx_area=Bbox(-43.62712, 172.36059, -43.41766, 172.81524)),
        find_sa1s_in_area("Oamaru", approx_area=Bbox(-45.11886, 170.912129, -45.04020,  171.02564))
    ]
    return pd.concat(sa1_dfs)


@dataclasses.dataclass
class Bbox:
    lat1: float
    lng1: float
    lat2: float
    lng2: float
    crs: int = 4326

    def as_shapely_polygon(self) -> shapely.Polygon:
        xmin = min([self.lng1, self.lng2])
        ymin = min([self.lat1, self.lat2])
        xmax = max([self.lng1, self.lng2])
        ymax = max([self.lat1, self.lat2])
        return shapely.box(xmin, ymin, xmax, ymax)

    def as_gdf(self) -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(index=[0], crs=self.crs, geometry=[shapely.from_wkt(self.as_shapely_polygon().wkt)])


def find_sa1s_in_area(area_name: str, approx_area: Bbox) -> gpd.GeoDataFrame:
    log.info(f"Adding {area_name} sa1s to database")
    vector_fetcher = geoapis.vector.StatsNz(key=Env.STATS_API_KEY, bounding_polygon=approx_area.as_gdf(), verbose=True)

    # All SA1s in bbox
    sa1s = vector_fetcher.run(92210)
    sa1s.set_index("SA12018_V1_00", verify_integrity=True, inplace=True)
    sa1s.index = sa1s.index.astype('int64')

    # Filter to remove SA1s that represent inlets and other non-mainland features.
    sa1s_filtered_no_water = sa1s.loc[sa1s["LANDWATER_NAME"] == "Mainland"]

    # Urban/Rural area polygons
    urban_rural = vector_fetcher.run(111198)
    # Find SA1s that are within the urban area Polygon
    urban_area = urban_rural.loc[urban_rural['UR2023_V1_00_NAME'] == area_name]
    sa1s_join_urban_area = sa1s_filtered_no_water.sjoin(urban_area, how='inner', predicate='intersects')

    # Filter sa1s for those values that exist in the spatial join above
    # Keeps data more simple than using the spatial join
    sa1s_in_urban_area = sa1s_filtered_no_water.loc[sa1s_filtered_no_water.index.isin(sa1s_join_urban_area.index)]
    # Add urban area name
    sa1s_in_urban_area['UR2023_V1_00_NAME'] = sa1s_join_urban_area["UR2023_V1_00_NAME"]
    return sa1s_in_urban_area


def get_db_engine() -> Engine:
    pg_user = Env.POSTGRES_USER
    pg_pass = Env.POSTGRES_PASSWORD
    pg_host = Env.POSTGRES_HOST
    pg_port = Env.POSTGRES_PORT
    pg_db = Env.POSTGRES_DB
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}', pool_pre_ping=True)
    log.info(f"Attempting to connect to {engine}")
    with engine.connect():
        log.info(f"Connection to {engine} successful")
    return engine


def read_emissions_and_filter_by_sa1s(sa1s: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    data_file = Env.DATA_FILE
    log.info(f"Reading {data_file} into memory")
    emissions_data = pd.read_excel(data_file, header=[0, 1], index_col=0, sheet_name=3)
    log.info("Filtering data for relevant SA1s")
    return emissions_data.loc[emissions_data.index.isin(sa1s.index)]


def get_long_format_sa1_emissions(emissions_data) -> pd.DataFrame:
    log.info("Converting to long format DataFrame")
    vehicle_types, variables = (level.values.tolist() for level in emissions_data.columns.levels)
    melts = []
    for var in variables:
        if var.startswith("Unnamed"):
            break
        melt = emissions_data.melt(ignore_index=False, var_name="Vehicle Type", value_name=var,
                                   value_vars=[(vehicle_type, var) for vehicle_type in vehicle_types])
        melt.set_index('Vehicle Type', append=True, inplace=True)
        melts.append(melt)
    merged = pd.merge(melts[0], melts[1], left_index=True, right_index=True)
    return merged.rename(columns=lambda name: name.replace("\n", " "))


def split_vehicle_type(df: pd.DataFrame) -> pd.DataFrame:
    def split_fuel_type(row):
        for f_type in fuel_types:
            if row.endswith(f_type):
                vehicle_class = row.replace(f_type, '').strip().title()
                return pd.Series([vehicle_class, f_type], index=['Vehicle Class', 'Fuel Type'])
        # If a row does not have a desginated fuel type from fuel_types, assume it to be Diesel.
        return pd.Series([row, "Diesel"], index=['Vehicle Class', 'Fuel Type'])

    fuel_types = ["Petrol", "Diesel", "Electric", "Plugin Hybrid", "Hybrid"]
    df.reset_index(inplace=True)
    log.info("Splitting vehicle class and fuel type")
    df[['vehicle_class', 'fuel_type']] = df['Vehicle Type'].apply(split_fuel_type)
    df.drop("Vehicle Type", axis=1, inplace=True)
    df.rename(columns={"level_0": "SA12018_V1_00"}, inplace=True)
    df.set_index(["SA12018_V1_00", "vehicle_class", "fuel_type"], inplace=True)
    return df


def main() -> None:
    setup_logging()
    log.info(f"Checking database initialisation")
    load_dotenv()
    engine = get_db_engine()
    log.info(f"Initialising database {engine}")

    sa1s_table_name = "sa1s"
    index_col = "SA12018_V1_00"
    if sqlalchemy.inspect(engine).has_table(sa1s_table_name):
        log.info(f"Table {sa1s_table_name} exists, reading")
        sa1_ids = pd.read_sql(f'SELECT "{index_col}" FROM {sa1s_table_name}', engine, index_col=index_col)
    else:
        log.info(f"Table {sa1s_table_name} does not exist, initialising")
        sa1s = find_sa1s_in_areas_of_interest()
        sa1s.to_postgis(sa1s_table_name, engine, if_exists="replace", index=True)
        sa1_ids = sa1s[[]]  # Only save the index since its all we need
    vehicle_stats_table_name = "vehicle_stats"
    if sqlalchemy.inspect(engine).has_table(vehicle_stats_table_name):
        log.info(f"Table {vehicle_stats_table_name} exists, skipping")
    else:
        log.info(f"Table {vehicle_stats_table_name} does not exist, initialising")
        emissions = read_emissions_and_filter_by_sa1s(sa1_ids)
        emissions = get_long_format_sa1_emissions(emissions)
        emissions = split_vehicle_type(emissions)
        emissions.to_sql(vehicle_stats_table_name, engine, if_exists="replace", index=True,
                         index_label=[index_col, "vehicle_class", "fuel_type"])

    log.info("Database initialised")
    log.info("Initialising geoserver")
    initialise_geoserver()


if __name__ == '__main__':
    main()
