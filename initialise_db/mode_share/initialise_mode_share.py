import abc
import logging
import pathlib
from typing import NamedTuple

import geoapis.vector
import geopandas as gpd
import numpy as np
import pandas as pd
import sqlalchemy

from config import EnvVariable as Env, get_db_engine
from setup_logging import setup_logging
import stats_nz_geographies

log = logging.getLogger(__name__)


class SA2(NamedTuple):
    layer_id: int
    index_name: str
    name_code: str


class ModeShareInitialiser(abc.ABC):
    @property
    @abc.abstractmethod
    def sa2(self) -> SA2:
        raise NotImplementedError("sa2 must be instantiated in the child class")

    @property
    @abc.abstractmethod
    def mode_share_table_name(self) -> str:
        raise NotImplementedError("mode_share_table_name must be instantiated in the child class")

    @property
    @abc.abstractmethod
    def sa2_table_name(self) -> str:
        raise NotImplementedError("sa2_table_name must be instantiated in the child class")

    @abc.abstractmethod
    def find_mode_shares_in_areas_of_interest(self, sa2_ids: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("find_mode_shares_in_areas_of_interest must be instantiated in the child class")

    @staticmethod
    def set_suppressed_values_as_zero(mode_shares: pd.DataFrame) -> pd.DataFrame:
        return mode_shares.replace(-999, 0)

    def find_sa2s_in_area(self, area_of_interest: stats_nz_geographies.AreaOfInterest) -> gpd.GeoDataFrame:
        # All SA2s in bbox
        vector_fetcher = geoapis.vector.StatsNz(key=Env.STATS_API_KEY,
                                                bounding_polygon=area_of_interest.bbox.as_gdf())
        sa2s = vector_fetcher.run(self.sa2.layer_id)
        sa2s.set_index(self.sa2.index_name, verify_integrity=True, inplace=True)
        sa2s.index = sa2s.index.astype('int64')
        sa2s_in_urban_area = stats_nz_geographies.filter_gdf_by_urban_rural_area(sa2s, area_of_interest.ua_name,
                                                                                 vector_fetcher)
        # Filter to remove SA1s that represent inlets and other non-mainland features.
        return sa2s_in_urban_area.loc[
            ~sa2s_in_urban_area[self.sa2.name_code].str.startswith(("Inlet", "Inland water", "Oceanic"))
        ]

    @staticmethod
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

    def initialise_mode_share(self, engine: sqlalchemy.engine.Engine) -> None:
        index_col = self.sa2.index_name
        if sqlalchemy.inspect(engine).has_table(self.sa2_table_name):
            log.info(f"Table {self.sa2_table_name} exists, reading")
            sa2_ids = pd.read_sql(f'SELECT "{index_col}" FROM {self.sa2_table_name}', engine, index_col=index_col)
        else:
            log.info(f"Table {self.sa2_table_name} does not exist, initialising...")
            sa2s = pd.concat([self.find_sa2s_in_area(aoi) for aoi in stats_nz_geographies.AREAS_OF_INTEREST])
            sa2s.to_postgis(self.sa2_table_name, engine, if_exists="replace", index=True)
            sa2_ids = sa2s[[]]  # Only save the index since its all we need
            log.info(f"Table {self.sa2_table_name} initialised.")
        if sqlalchemy.inspect(engine).has_table(self.mode_share_table_name):
            log.info(f"Table {self.mode_share_table_name} exists, skipping")
        else:
            log.info(f"Table {self.mode_share_table_name} does not exist, initialising...")
            mode_shares = self.find_mode_shares_in_areas_of_interest(sa2_ids)
            mode_shares.to_sql(self.mode_share_table_name,
                               engine,
                               if_exists="replace",
                               index=True)

            log.info(f"Table {self.mode_share_table_name} initialised.")


class ModeShareFlowInitialiser(ModeShareInitialiser):
    sa2 = SA2(92212, "SA22018_V1_00", "SA22018_V1_NAME")
    mode_share_table_name = "mode_share"
    sa2_table_name = "sa2"

    def find_mode_shares_in_areas_of_interest(self, sa2_ids: pd.DataFrame) -> pd.DataFrame:
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
        mode_shares = mode_shares.set_index(["SA2_code_usual_residence_address", "SA2_code_workplace_address"],
                                            verify_integrity=True)
        return self.set_suppressed_values_as_zero(mode_shares)


class ModeShare2023Initialiser(ModeShareInitialiser):
    sa2 = SA2(111227, "SA22023_V1_00", "SA22023_V1_00_NAME")
    mode_share_table_name = "mode_share_2023"
    sa2_table_name = "sa2_2023"

    def _read_means_of_travel_dataset(self, dataset_path: pathlib.Path, sa2_ids: pd.DataFrame) -> pd.DataFrame:
        relevant_cols = ["Variable codes", "CEN23_TBT_GEO_006", "OBS_VALUE", "Observation Status"]

        means_of_travel = pd.read_csv(dataset_path, usecols=relevant_cols)
        means_of_travel = means_of_travel[means_of_travel["CEN23_TBT_GEO_006"] != "SA2Total"]
        means_of_travel = means_of_travel.rename(columns={
            "Variable codes": "means_of_travel",
            "CEN23_TBT_GEO_006": "SA2_code",
            "OBS_VALUE": "count"
        }).astype({"means_of_travel": str, "SA2_code": int, "count": float})
        return means_of_travel.set_index(["SA2_code", "means_of_travel"])

    def find_mode_shares_in_areas_of_interest(self, sa2_ids: pd.DataFrame) -> pd.DataFrame:
        mode_shares = self._read_means_of_travel_dataset(Env.MEANS_OF_TRAVEL_USUAL_RES_2023_DATA, sa2_ids)
        mode_shares = mode_shares.loc[mode_shares.index.get_level_values("SA2_code").isin(sa2_ids.index)]

        mode_shares = self.set_suppressed_values_as_zero(mode_shares)

        wide_mode_shares = self.convert_mode_share_to_wide_format(mode_shares)

        non_flow_contributing_columns = ["Did_not_go_to_work_today", "Work_at_home", "Total_stated_-_main_means_of_travel_to_work_by_usual_residence_address", "Main_means_of_travel_to_work_by_usual_residence_address_-_total_employed_census_usually_resident_population_count_aged_15_years_and_over"]
        wide_mode_shares["Net_flow"] = wide_mode_shares.drop(columns=non_flow_contributing_columns).sum(axis=1)
        return wide_mode_shares

    @staticmethod
    def convert_mode_share_to_wide_format(mode_shares: pd.DataFrame) -> pd.DataFrame:
        mode_shares = mode_shares.drop(columns=["Observation Status"])
        groups = mode_shares.groupby(["SA2_code", "means_of_travel"])
        flows = groups.sum()
        unstacked = flows.unstack(fill_value=0).reset_index()
        flattened_columns = [multicol[-1] if multicol[-1] else multicol[0] for multicol in unstacked.columns]
        underscored_columns = [col.replace(" ", "_").replace(",", "") for col in flattened_columns]
        unstacked.columns = underscored_columns

        return unstacked.set_index("SA2_code")

    @staticmethod
    def set_suppressed_values_as_zero(mode_shares: pd.DataFrame) -> pd.DataFrame:
        mode_shares[["count"]] = mode_shares[["count"]].fillna(0)
        return mode_shares


if __name__ == '__main__':
    setup_logging()
    engine = get_db_engine()
    ModeShareFlowInitialiser().initialise_mode_share(engine)
    ModeShare2023Initialiser().initialise_mode_share(engine)
