import os

import geoapis.vector
import geopandas as gpd
import shapely
from dotenv import load_dotenv


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

    load_dotenv(".env.local")
    stats_key = os.getenv("STATS_API_KEY")
    vector_fetcher = geoapis.vector.StatsNz(key=stats_key, bounding_polygon=selected_polygon, verbose=True)

    # All SA1s in bbox
    sa1s = vector_fetcher.run(92210)
    sa1s.set_index("SA12018_V1_00", verify_integrity=True, inplace=True)

    # Filter to remove SA1s that represent inlets and other non-mainland features.
    sa1s_no_water = sa1s.loc[sa1s["LANDWATER_NAME"] == "Mainland"]

    # Remove unnecessary columns
    sa1s_filtered = sa1s_no_water[["LAND_AREA_SQ_KM", "AREA_SQ_KM", "geometry"]]

    # Urban/Rural area polygons
    urban_rural = vector_fetcher.run(111198)
    # Find SA1s that are within the urban Christchurch Polygon
    chch = urban_rural.loc[urban_rural['UR2023_V1_00_NAME'] == "Christchurch"]
    sa1s_join_chch = sa1s_filtered.sjoin(chch, how='inner', predicate='intersects')

    # Filter sa1s for those values that exist in the spatial join above
    # Keeps data more simple than using the spatial join
    return sa1s_filtered.loc[sa1s_filtered.index.isin(sa1s_join_chch.index)]


sa1s_in_chch = find_sa1s_in_chch()
sa1s_in_chch.to_file("public/sa1s_in_chch.geojson")
