import dataclasses
from typing import NamedTuple

import geoapis.vector
import geopandas as gpd
import shapely


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


class AreaOfInterest(NamedTuple):
    ua_name: str
    display_name: str
    bbox: Bbox


AREAS_OF_INTEREST = [
    AreaOfInterest("Auckland", "Auckland | Tāmaki Makaurau", Bbox(-37.11973, 174.56626, -36.66668, 175.00701)),
    AreaOfInterest("Hamilton", "Hamilton | Kirikiriroa", Bbox(-37.84833, 175.18301, -37.69678, 175.34657)),
    AreaOfInterest("Wellington", "Wellington | Te Whanganui-a-Tara", Bbox(-41.36836, 174.69794, -41.13047, 174.90839)),
    AreaOfInterest("Christchurch", "Christchurch | Ōtautahi", Bbox(-43.62712, 172.36059, -43.41766, 172.81524)),
    AreaOfInterest("Oamaru", "Oamaru | Oāmaru", Bbox(-45.11886, 170.912129, -45.04020, 171.02564)),
    AreaOfInterest("Queenstown", "Tāhuna", Bbox(-45.39727, 168.07669, -43.90287, 169.72412)),
]


def filter_gdf_by_urban_rural_area(gdf_to_filter: gpd.GeoDataFrame,
                                   area_name: str,
                                   vector_fetcher: geoapis.vector.StatsNz,
                                   predicate: str = "intersects"
                                   ):
    # Urban/Rural area polygons
    urban_rural = vector_fetcher.run(111198)
    # Find gdf polygons that are within the urban area Polygon
    urban_area = urban_rural.loc[urban_rural['UR2023_V1_00_NAME'] == area_name]
    gdf_join_urban_area = gdf_to_filter.sjoin(urban_area, how='inner', predicate=predicate)
    # Filter gdf polygons for those values that exist in the spatial join above
    # Keeps data more simple than using the spatial join
    polygons_in_urban_area = gdf_to_filter.loc[gdf_to_filter.index.isin(gdf_join_urban_area.index)]
    # Add urban area name
    polygons_in_urban_area['UR2023_V1_00_NAME'] = gdf_join_urban_area["UR2023_V1_00_NAME"]
    return polygons_in_urban_area
