import logging

import geoapis.vector
import geopandas as gpd
import pandas as pd
import sqlalchemy
import stats_nz_geographies
from config import EnvVariable as Env
from config import get_db_engine

log = logging.getLogger(__name__)


def find_sa2s_in_area(area_of_interest: stats_nz_geographies.AreaOfInterest) -> gpd.GeoDataFrame:
    # All SA2s in bbox
    vector_fetcher = geoapis.vector.StatsNz(key=Env.STATS_API_KEY,
                                            bounding_polygon=area_of_interest.bbox.as_gdf())
    sa2s = vector_fetcher.run(111227)
    sa2s.set_index("SA22023_V1_00", verify_integrity=True, inplace=True)
    sa2s.index = sa2s.index.astype('int64')
    sa2s_in_urban_area = stats_nz_geographies.filter_gdf_by_urban_rural_area(sa2s, area_of_interest.ua_name,
                                                                             vector_fetcher)
    # Filter to remove SA1s that represent inlets and other non-mainland features.
    return sa2s_in_urban_area.loc[
        ~sa2s_in_urban_area["SA22023_V1_00_NAME"].str.startswith(("Inlet", "Inland water", "Oceanic"))
    ]


def find_mode_shares_in_areas_of_interest(sa2_ids: pd.DataFrame) -> pd.DataFrame:
    mode_shares = pd.read_csv(Env.MEANS_OF_TRAVEL_DATA)
    # Drop info that is duplicated in SA2 table to keep data normalised
    mode_shares = mode_shares.drop(columns=[
        "SA2_name_usual_residence_address",
        "SA2_usual_residence_easting",
        "SA2_usual_residence_northing",
        "SA2_name_workplace_address",
        "SA2_workplace_easting",
        "SA2_workplace_northing",
    ])
    mode_shares = mode_shares.loc[
        mode_shares["SA2_code_usual_residence_address"].isin(sa2_ids.index)
        & mode_shares["SA2_code_workplace_address"].isin(sa2_ids.index)]
    return mode_shares.set_index(["SA2_code_usual_residence_address", "SA2_code_workplace_address"],
                                 verify_integrity=True)


def set_suppressed_values_as_zero(mode_shares: pd.DataFrame) -> pd.DataFrame:
    return mode_shares.replace(-999, 0)


def convert_mode_share_df_to_gdf(mode_shares: pd.DataFrame) -> gpd.GeoDataFrame:
    mode_share_data_crs = 2193
    wgs_84 = 4326
    usual_residence_points = gpd.points_from_xy(mode_shares["SA2_usual_residence_easting"],
                                                mode_shares["SA2_usual_residence_northing"],
                                                crs=mode_share_data_crs).to_crs(wgs_84)
    usual_workplace_points = gpd.points_from_xy(mode_shares["SA2_workplace_easting"],
                                                mode_shares["SA2_workplace_northing"],
                                                crs=mode_share_data_crs).to_crs(wgs_84)
    mode_shares = mode_shares.drop(columns=["SA2_usual_residence_easting",
                                            "SA2_usual_residence_northing",
                                            "SA2_workplace_easting",
                                            "SA2_workplace_northing"])
    mode_shares["SA2_usual_residence"] = usual_residence_points
    mode_shares["SA2_workplace"] = usual_workplace_points
    return gpd.GeoDataFrame(mode_shares, geometry="SA2_usual_residence")


def initialise_mode_share(engine: sqlalchemy.engine.Engine) -> None:
    sa2s_table_name = "sa2s"
    index_col = "SA22023_V1_00"
    if sqlalchemy.inspect(engine).has_table(sa2s_table_name):
        log.info(f"Table {sa2s_table_name} exists, reading")
        sa2_ids = pd.read_sql(f'SELECT "{index_col}" FROM {sa2s_table_name}', engine, index_col=index_col)
    else:
        log.info(f"Table {sa2s_table_name} does not exist, initialising...")
        sa2s = pd.concat([find_sa2s_in_area(aoi) for aoi in stats_nz_geographies.AREAS_OF_INTEREST])
        sa2s.to_postgis(sa2s_table_name, engine, if_exists="replace", index=True)
        sa2_ids = sa2s[[]]  # Only save the index since its all we need
        log.info(f"Table {sa2s_table_name} initialised.")
    mode_share_table_name = "mode_share"
    if sqlalchemy.inspect(engine).has_table(mode_share_table_name):
        log.info(f"Table {mode_share_table_name} exists, skipping")
    else:
        log.info(f"Table {mode_share_table_name} does not exist, initialising...")
        mode_shares = find_mode_shares_in_areas_of_interest(sa2_ids)
        mode_shares = set_suppressed_values_as_zero(mode_shares)
        mode_shares.to_sql(mode_share_table_name,
                           engine,
                           if_exists="replace",
                           index=True,
                           index_label=["SA2_code_usual_residence_address", "SA2_code_workplace_address"])

        log.info(f"Table {mode_share_table_name} initialised.")


if __name__ == '__main__':
    engine = get_db_engine()
    initialise_mode_share(engine)
