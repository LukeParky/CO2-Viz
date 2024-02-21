import logging
import time
from typing import List, Union

import gspread
import pandas as pd
import sqlalchemy
from config import EnvVariable, get_db_engine
from tqdm import tqdm

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


def get_workbook_config_page(urban_area_name: str, columns: List[str]) -> pd.DataFrame:
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


def save_flow_map_to_gsheet(gspread_client: gspread.Client,
                            spreadsheet_name: str,
                            config_sheet: pd.DataFrame,
                            sa2_locations: pd.DataFrame,
                            flows: pd.DataFrame,
                            flow_columns: list) -> str:
    def df_to_gspread_list(df: pd.DataFrame) -> List[Union[str, List]]:
        # noinspection PyTypeChecker
        return [df.columns.values.tolist()] + df.values.tolist()

    log.info(f"Uploading Google Sheet {spreadsheet_name}")
    if len(gspread_client.openall(spreadsheet_name)) > 0:
        spreadsheet = gspread_client.open(spreadsheet_name)
    else:
        spreadsheet = gspread_client.create(spreadsheet_name)
    for worksheet in spreadsheet.worksheets():
        worksheet.clear()
        if worksheet.index == 0:
            worksheet.update_title("properties")
        else:
            spreadsheet.del_worksheet(worksheet)

    properties_sheet = spreadsheet.sheet1
    properties_sheet.update(df_to_gspread_list(config_sheet))

    locations_sheet = spreadsheet.add_worksheet("locations",
                                                rows=len(sa2_locations) + 1,
                                                cols=len(sa2_locations.columns))
    locations_sheet.update(df_to_gspread_list(sa2_locations))

    for column_name in flow_columns:
        flow_data = flows[['origin', 'dest', column_name]].rename(columns={column_name: "count"})
        flow_sheet = spreadsheet.add_worksheet(column_name,
                                               rows=len(flow_data) + 1,
                                               cols=len(sa2_locations.columns))
        flow_sheet.update(df_to_gspread_list(flow_data))

    spreadsheet.share(email_address=None, perm_type="anyone", role="reader", with_link=True).raise_for_status()
    transfer_ownership_response = spreadsheet.share(email_address=EnvVariable.ADMIN_EMAIL,
                                                    perm_type="user",
                                                    role="writer",
                                                    notify=True)
    transfer_ownership_response.raise_for_status()
    owner_permission_id = transfer_ownership_response.json()["id"]
    spreadsheet.transfer_ownership(owner_permission_id).raise_for_status()
    return spreadsheet.url


def save_flow_map_sheets(engine: sqlalchemy.engine.Engine) -> None:
    flow_sheets_table_name = "flow_sheets"
    if sqlalchemy.inspect(engine).has_table(flow_sheets_table_name):
        log.info(f"Table {flow_sheets_table_name} exists, skipping.")
        return
    log.info(f"Initialising table {flow_sheets_table_name}.")

    gspread_client = gspread.service_account_from_dict(EnvVariable.GOOGLE_CREDENTIALS)
    urban_areas = pd.read_sql('SELECT DISTINCT "UR2023_V1_00_NAME" FROM sa2s',
                              engine).to_numpy().flatten()
    flow_sheet_url_data = []
    for urban_area in urban_areas:
        sa2_locations = find_sa2_locations(engine, urban_area)
        flows = find_flows(engine, urban_area)
        spreadsheet_name = f"flows_{urban_area}"
        flow_columns = [col for col in flows.columns if col not in {'origin', 'dest'}]
        workbook_config_sheet = get_workbook_config_page(urban_area, flow_columns)
        num_attempts = 3
        for attempt in range(num_attempts):
            try:
                sheet_url = save_flow_map_to_gsheet(gspread_client,
                                                    spreadsheet_name,
                                                    workbook_config_sheet,
                                                    sa2_locations,
                                                    flows,
                                                    flow_columns)
                flow_sheet_url_data.append({"urban_area": urban_area, "sheet_url": sheet_url})
                break
            except gspread.exceptions.APIError as e:
                if attempt >= num_attempts - 1:
                    raise e
                refresh_time = 500
                for _ in tqdm(range(refresh_time), desc="Google Sheets API limit hit, waiting for limit refresh..."):
                    time.sleep(1)

    flow_sheet_df = pd.DataFrame(flow_sheet_url_data).set_index("urban_area")
    flow_sheet_df.to_sql(flow_sheets_table_name, engine, if_exists="replace", index=True)


if __name__ == '__main__':
    engine = get_db_engine()
    save_flow_map_sheets(engine)
