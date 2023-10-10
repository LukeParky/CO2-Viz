import os

import geoapis.vector
import geopandas as gpd
import pandas as pd
import shapely
import sqlalchemy as sqla
from dotenv import load_dotenv
from sqlalchemy.engine import Engine, create_engine


def find_sa1s_in_chch() -> gpd.GeoDataFrame:
    stats_native_crs = 4326
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
    selected_polygon.to_crs(stats_native_crs, inplace=True)

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


def get_emissions_data(sa1s: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    emissions_data = pd.read_excel("data/RAW_SA1_emissions.xlsx", header=1, index_col=0)
    emissions_with_geom = sa1s.join(emissions_data)
    return emissions_with_geom[["geometry", 'VKT (`000,000 km/Year)', 'CO2 (Tonnes/Year)']]


def get_db_engine() -> Engine:
    pg_user, pg_pass, pg_host, pg_port, pg_db = (os.getenv(key) for key in (
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB"
    ))
    return create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')


def add_sa1_pkey_constraint(engine: Engine) -> None:
    meta = sqla.MetaData()
    sa1_table = sqla.Table('sa1s', meta, autoload=True, autoload_with=engine)
    if sa1_table.primary_key is None:
        engine.execute(r'ALTER TABLE sa1s ADD CONSTRAINT sa1s_pk PRIMARY KEY ("SA12018_V1_00")')


def main() -> None:
    load_dotenv()
    engine = get_db_engine()
    sa1s = find_sa1s_in_chch()
    sa1s.to_postgis("sa1s", engine, if_exists="append", index=True)
    add_sa1_pkey_constraint(engine)


main()
