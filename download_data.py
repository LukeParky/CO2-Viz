import os

from dotenv import load_dotenv
import geoapis.vector
import geopandas as gpd
import shapely

load_dotenv(".env.local")
lat1, lng1 = -43.41766, 172.36059
lat2, lng2 = -43.62712, 172.81524
xmin = min([lng1, lng2])
ymin = min([lat1, lat2])
xmax = max([lng1, lng2])
ymax = max([lat1, lat2])

bbox_wkt = shapely.box(xmin, ymin, xmax, ymax).wkt

selected_polygon = gpd.GeoDataFrame(index=[0], crs="epsg:4326", geometry=[shapely.from_wkt(bbox_wkt)])
selected_polygon.to_crs(2193, inplace=True)

stats_key = os.getenv("STATS_API_KEY")
vector_fetcher = geoapis.vector.StatsNz(key=stats_key, bounding_polygon=selected_polygon, verbose=True)

sa1s = vector_fetcher.run(92210)
urban_rural = vector_fetcher.run(111198)
chch = urban_rural.loc[urban_rural['UR2023_V1_00_NAME'] == "Christchurch"]
sa1s_in_chch = sa1s.sjoin(chch, how='inner', predicate='intersects')

# chch.to_file("public/chch.geojson")
# sa1s_in_chch.to_file("public/sa1s-chch.geojson")

sa1s_no_water = sa1s_in_chch.loc[sa1s_in_chch["LANDWATER_NAME"] == "Mainland"]
sa1s_no_water.to_crs(4326).to_file("public/sa1s-no-water.geojson")
