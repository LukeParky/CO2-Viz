import logging
import pathlib

import pandas as pd
import sqlalchemy
from config import get_db_engine

log = logging.getLogger(__name__)


def find_sa2_locations(engine: sqlalchemy.engine.Engine, urban_area_name: str) -> pd.DataFrame:
    all_sa2s_query = """
        SELECT DISTINCT "SA22018_V1_00"               AS id,
                        "SA22018_V1_NAME"             as name,
                        ST_Y(ST_CENTROID("geometry")) as lat,
                        ST_X(ST_CENTROID("geometry")) as lon
        
        FROM sa2s
        WHERE "UR2023_V1_00_NAME" ILIKE %(urban_area_name)s
    """
    return pd.read_sql(all_sa2s_query, engine, index_col="id", params={"urban_area_name": urban_area_name})


def find_flows(engine: sqlalchemy.engine.Engine, urban_area_name: str) -> pd.DataFrame:
    all_flows_query = """
            SELECT "SA2_code_usual_residence_address"                                        AS origin,
                   "SA2_code_workplace_address"                                              AS dest,
                   ("Walk_or_jog" + "Bicycle")                                               AS "Active_Transport",
                   ("Public_bus" + "Train" + "Ferry")                                        AS "Public_Transport",
                   ("Drive_a_private_car_truck_or_van" + "Drive_a_company_car_truck_or_van") AS "Drive",
                   "Passenger_in_a_car_truck_van_or_company_bus"                             AS "Passenger_Car_Truck_Van_Co_Bus",
                   "Other",
                   "Total"
            
            FROM mode_share
                JOIN sa2s AS workplace ON workplace."SA22018_V1_00"="SA2_code_workplace_address"
                JOIN sa2s AS residence ON residence."SA22018_V1_00"="SA2_code_usual_residence_address"
            
            WHERE workplace."UR2023_V1_00_NAME"=%(urban_area_name)s 
            AND residence."UR2023_V1_00_NAME"=%(urban_area_name)s
            
            ORDER BY "SA2_code_usual_residence_address", "SA2_code_workplace_address"
        """
    return pd.read_sql(all_flows_query, engine, params={"urban_area_name": urban_area_name})


def get_workbook_config_page(urban_area_name: str, columns: list) -> pd.DataFrame:
    return pd.DataFrame(columns=["property", "value"], data=[
        ["title", f"{urban_area_name} Mode Shares"],
        ["description", "description"],
        ["source.name", "source.name"],
        ["source.url", "soruce.url"],
        ["createdBy.name", "Geospatial Research Institute | Toi Hangarau"],
        ["createdBy.url", "http://geospatial.ac.nz"],
        ["mapbox.mapStyle", ""],
        ["colors.schme", "Default"],
        ["colors.darkMode", "no"],
        ["animate.flows", "no"],
        ["clustering", "no"],
        ["flows.sheets", ','.join(columns)]
    ])


def save_flow_map_to_workbook(file_path: pathlib.Path, config_sheet: pd.DataFrame, sa2_locations: pd.DataFrame,
                              flows: pd.DataFrame, flow_columns: list):
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as excel_writer:
        config_sheet.to_excel(excel_writer, sheet_name="properties", index=False)
        sa2_locations.to_excel(excel_writer, sheet_name="locations")

        for column_name in flow_columns:
            sheet = flows[['origin', 'dest', column_name]].rename(columns={column_name: "count"})
            sheet.to_excel(excel_writer, sheet_name=column_name, index=False)


def save_flow_map_files(engine: sqlalchemy.engine.Engine) -> None:
    urban_areas = pd.read_sql('SELECT DISTINCT "UR2023_V1_00_NAME" FROM sa2s', engine).to_numpy().flatten()
    data_dir = pathlib.Path("./data/flows")
    data_dir.mkdir(parents=True, exist_ok=True)
    for urban_area in urban_areas:
        sa2_locations = find_sa2_locations(engine, urban_area)
        flows = find_flows(engine, urban_area)
        file_path = data_dir / f"{urban_area}.xlsx"
        flow_columns = [col for col in flows.columns if col not in {'origin', 'dest'}]
        workbook_config_sheet = get_workbook_config_page(urban_area, flow_columns)
        save_flow_map_to_workbook(file_path, workbook_config_sheet, sa2_locations, flows, flow_columns)


if __name__ == '__main__':
    engine = get_db_engine()
    save_flow_map_files(engine)
