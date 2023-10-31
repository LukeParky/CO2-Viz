import os

import geoapis.vector
import geopandas as gpd
import pandas as pd
import shapely
from dotenv import load_dotenv
from sqlalchemy.engine import Engine, create_engine


def find_sa1s_in_chch() -> gpd.GeoDataFrame:
    wgs_84 = 4326
    # Approximate bounding box of chch in WGS84
    lat1, lng1 = -43.41766, 172.36059
    lat2, lng2 = -43.62712, 172.81524

    xmin = min([lng1, lng2])
    ymin = min([lat1, lat2])
    xmax = max([lng1, lng2])
    ymax = max([lat1, lat2])

    bbox_wkt = shapely.box(xmin, ymin, xmax, ymax).wkt

    # bbox as GeoDataFrame in epsg:2193 for use by geoapis
    selected_polygon = gpd.GeoDataFrame(index=[0], crs=wgs_84, geometry=[shapely.from_wkt(bbox_wkt)])

    stats_key = os.getenv("STATS_API_KEY")
    vector_fetcher = geoapis.vector.StatsNz(key=stats_key, bounding_polygon=selected_polygon, verbose=True)

    # All SA1s in bbox
    sa1s = vector_fetcher.run(92210)
    sa1s.set_index("SA12018_V1_00", verify_integrity=True, inplace=True)
    sa1s.index = sa1s.index.astype('int64')

    # Filter to remove SA1s that represent inlets and other non-mainland features.
    sa1s_filtered = sa1s.loc[sa1s["LANDWATER_NAME"] == "Mainland"]

    # Urban/Rural area polygons
    urban_rural = vector_fetcher.run(111198)
    # Find SA1s that are within the urban Christchurch Polygon
    chch = urban_rural.loc[urban_rural['UR2023_V1_00_NAME'] == "Christchurch"]
    sa1s_join_chch = sa1s_filtered.sjoin(chch, how='inner', predicate='intersects')

    # Filter sa1s for those values that exist in the spatial join above
    # Keeps data more simple than using the spatial join
    return sa1s_filtered.loc[sa1s_filtered.index.isin(sa1s_join_chch.index)]


def get_db_engine() -> Engine:
    pg_user, pg_pass, pg_host, pg_port, pg_db = (os.getenv(key) for key in (
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB"
    ))
    return create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')


def get_long_format_sa1_emissions() -> pd.DataFrame:
    emissions_data = pd.read_excel("data/RAW_SA1_emissions(2).xlsx", header=[0, 1], index_col=0, sheet_name=2)
    vehicle_types, variables = (level.values.tolist() for level in emissions_data.columns.levels)
    # emissions_data.reset_index(inplace=True)
    melts = []
    for var in variables:
        melt = emissions_data.melt(ignore_index=False, var_name="Vehicle Type", value_name=var,
                                   value_vars=[(vehicle_type, var) for vehicle_type in vehicle_types])
        melt.set_index('Vehicle Type', append=True, inplace=True)
        melts.append(melt)
    merged = pd.merge(melts[0], melts[1], left_index=True, right_index=True)
    return merged.rename(columns=lambda name: name.replace("\n", " "))


def main() -> None:
    load_dotenv()
    engine = get_db_engine()

    emissions = get_long_format_sa1_emissions()
    emissions.to_sql("vehicle_stats", engine, if_exists="replace", index=True,
                     index_label=["SA12018_V1_00", "vehicle_type"])

    sa1s = find_sa1s_in_chch()
    sa1s_table_name = "sa1s"
    sa1s.to_postgis(sa1s_table_name, engine, if_exists="replace", index=True)


main()
