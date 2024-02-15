import logging

import geoapis.vector
import geopandas as gpd
import pandas as pd
import sqlalchemy
import stats_nz_geographies
from config import EnvVariable as Env
from config import get_db_engine

log = logging.getLogger(__name__)


def find_sa1s_in_areas_of_interest() -> gpd.GeoDataFrame:
    return pd.concat([find_sa1s_in_area(aoi) for aoi in stats_nz_geographies.AREAS_OF_INTEREST])


def find_sa1s_in_area(area_of_interest: stats_nz_geographies.AreaOfInterest) -> gpd.GeoDataFrame:
    # All SA1s in bbox
    vector_fetcher = geoapis.vector.StatsNz(key=Env.STATS_API_KEY,
                                            bounding_polygon=area_of_interest.bbox.as_gdf())
    sa1s = vector_fetcher.run(92210)
    sa1s.set_index("SA12018_V1_00", verify_integrity=True, inplace=True)
    sa1s.index = sa1s.index.astype('int64')
    sa1s_in_urban_area = stats_nz_geographies.filter_gdf_by_urban_rural_area(sa1s,
                                                                             area_of_interest.name,
                                                                             vector_fetcher)
    # Filter to remove SA1s that represent inlets and other non-mainland features.
    return sa1s_in_urban_area.loc[sa1s_in_urban_area["LANDWATER_NAME"] == "Mainland"]


def read_emissions_and_filter_by_sa1s(sa1s: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    data_file = Env.EMISSIONS_DATA
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
    fuel_types = ["Petrol", "Diesel", "Electric", "Plugin Hybrid", "Hybrid"]
    log.info("Splitting vehicle class and fuel type")
    df = df.reset_index()
    # Splitting vehicle class and fuel type
    # Regular expression pattern to capture both vehicle class and fuel type
    pattern = f'(?P<vehicle_class>.*?)\s*({"|".join(fuel_types)})$'

    # Extracting vehicle class and fuel type
    df[['vehicle_class', 'fuel_type']] = df['Vehicle Type'].str.extract(pattern)

    # Values that don't specify a valid fuel type are set to na, so replace these with valid values.
    df['fuel_type'].fillna("Diesel", inplace=True)
    df['vehicle_class'].fillna(df['Vehicle Type'], inplace=True)

    # Clean up dataframe, renaming columns and deleting redundant columns
    df = df.drop(columns=["Vehicle Type"])
    df = df.rename(columns={"level_0": "SA12018_V1_00"})
    return df.set_index(["SA12018_V1_00", "vehicle_class", "fuel_type"])


def initialise_co2_sa1s(engine: sqlalchemy.engine.Engine) -> None:
    sa1s_table_name = "sa1s"
    index_col = "SA12018_V1_00"
    if sqlalchemy.inspect(engine).has_table(sa1s_table_name):
        log.info(f"Table {sa1s_table_name} exists, reading")
        sa1_ids = pd.read_sql(f'SELECT "{index_col}" FROM {sa1s_table_name}', engine, index_col=index_col)
    else:
        log.info(f"Table {sa1s_table_name} does not exist, initialising...")
        sa1s = find_sa1s_in_areas_of_interest()
        sa1s.to_postgis(sa1s_table_name, engine, if_exists="replace", index=True)
        sa1_ids = sa1s[[]]  # Only save the index since its all we need
        log.info(f"Table {sa1s_table_name} initialised.")
    vehicle_stats_table_name = "vehicle_stats"
    if sqlalchemy.inspect(engine).has_table(vehicle_stats_table_name):
        log.info(f"Table {vehicle_stats_table_name} exists, skipping")
    else:
        log.info(f"Table {vehicle_stats_table_name} does not exist, initialising...")
        emissions = read_emissions_and_filter_by_sa1s(sa1_ids)
        emissions = get_long_format_sa1_emissions(emissions)
        emissions = split_vehicle_type(emissions)
        log.info(f"Saving {vehicle_stats_table_name} to database.")
        emissions.to_sql(vehicle_stats_table_name, engine, if_exists="replace", index=True,
                         index_label=[index_col, "vehicle_class", "fuel_type"])
        log.info(f"Table {vehicle_stats_table_name} initialised.")


if __name__ == '__main__':
    engine = get_db_engine()
    initialise_co2_sa1s()
