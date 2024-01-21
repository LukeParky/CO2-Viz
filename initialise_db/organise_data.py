import os

import geoapis.vector
import geopandas as gpd
import pandas as pd
import shapely
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.engine import Engine, create_engine


def find_sa1s_in_chch() -> gpd.GeoDataFrame:
    print("Adding chch sa1s to database")
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
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}', pool_pre_ping=True)
    print(f"Attempting to connect to {engine}")
    with engine.connect():
        print(f"Connection to {engine} successful")
    return engine


def get_long_format_sa1_emissions() -> pd.DataFrame:
    data_file = "data/RAW_SA1_emissions(2).xlsx"
    print("Converting to long format DataFrame")
    emissions_data = pd.read_excel(data_file, header=[0, 1], index_col=0, sheet_name=2)
    vehicle_types, variables = (level.values.tolist() for level in emissions_data.columns.levels)
    melts = []
    for var in variables:
        melt = emissions_data.melt(ignore_index=False, var_name="Vehicle Type", value_name=var,
                                   value_vars=[(vehicle_type, var) for vehicle_type in vehicle_types])
        melt.set_index('Vehicle Type', append=True, inplace=True)
        melts.append(melt)
    merged = pd.merge(melts[0], melts[1], left_index=True, right_index=True)
    return merged.rename(columns=lambda name: name.replace("\n", " "))


def split_vehicle_type(df: pd.DataFrame) -> pd.DataFrame:
    def split_vehicle_class(row):
        for v_class in vehicle_classes:
            if row.startswith(v_class):
                fuel_type = row.replace(v_class, '').strip().title()
                return pd.Series([v_class, fuel_type], index=['Vehicle Class', 'Fuel Type'])
        return pd.Series([None, None], index=['Vehicle Class', 'Fuel Type'])

    vehicle_classes = ["Bus", "Car", "Light Vehicle", "Light Commercial Vehicle", "Commercial Vehicle"]
    df.reset_index(inplace=True)
    print("Splitting vehicle class and fuel type")
    df[['vehicle_class', 'fuel_type']] = df['Vehicle Type'].apply(split_vehicle_class)
    df.drop("Vehicle Type", axis=1, inplace=True)
    df.rename(columns={"level_0": "SA12018_V1_00"}, inplace=True)
    df.set_index(["SA12018_V1_00", "vehicle_class", "fuel_type"], inplace=True)
    return df


def main() -> None:
    print(f"Checking database initialisation")
    load_dotenv()
    engine = get_db_engine()
    print(f"Initialising database {engine}")

    vehicle_stats_table_name = "vehicle_stats"
    if sqlalchemy.inspect(engine).has_table(vehicle_stats_table_name):
        print(f"Table {vehicle_stats_table_name} exists, skipping")
    else:
        print(f"Table {vehicle_stats_table_name} does not exist, initialising")
        emissions = get_long_format_sa1_emissions()
        emissions = split_vehicle_type(emissions)
        emissions.to_sql(vehicle_stats_table_name, engine, if_exists="replace", index=True,
                         index_label=["SA12018_V1_00", "vehicle_class", "fuel_type"])

    sa1s_table_name = "sa1s"
    if sqlalchemy.inspect(engine).has_table(sa1s_table_name):
        print(f"Table {sa1s_table_name} exists, skipping")
    else:
        print(f"Table {sa1s_table_name} does not exist, initialising")
        sa1s = find_sa1s_in_chch()
        sa1s.to_postgis(sa1s_table_name, engine, if_exists="replace", index=True)

    print("Database initialised")


if __name__ == '__main__':
    main()
