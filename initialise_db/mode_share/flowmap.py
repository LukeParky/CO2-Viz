import logging
import time
from typing import List, Union

import gspread
import pandas as pd
import sqlalchemy
import stats_nz_geographies
from config import EnvVariable
from tqdm import tqdm

log = logging.getLogger(__name__)


def find_sa2_locations(engine: sqlalchemy.engine.Engine, urban_area_name: str) -> pd.DataFrame:
    all_sa2s_query = """
        SELECT DISTINCT "SA22018_V1_00"               AS id,
                        "SA22018_V1_NAME"             as ua_name,
                        ST_Y(ST_CENTROID("geometry")) as lat,
                        ST_X(ST_CENTROID("geometry")) as lon
        
        FROM sa2
        WHERE "UR2023_V1_00_NAME" ILIKE %(urban_area_name)s
    """
    return pd.read_sql(all_sa2s_query, engine, index_col="id", params={"urban_area_name": urban_area_name})


def find_flows(engine: sqlalchemy.engine.Engine, urban_area_name: str) -> pd.DataFrame:
    all_flows_query = """
            SELECT "SA2_code_usual_residence_address"                                        AS origin,
                   "SA2_code_workplace_address"                                              AS dest,
                   ("Walk_or_jog" + "Bicycle")                                               AS "Active Transport",
                   ("Public_bus" + "Train" + "Ferry")                                        AS "Public Transport",
                   ("Drive_a_private_car_truck_or_van" + "Drive_a_company_car_truck_or_van") AS "Drive",
                   "Passenger_in_a_car_truck_van_or_company_bus"                             AS "Passenger",
                   "Other",
                   "Total"
            
            FROM mode_share
                JOIN sa2 AS workplace ON workplace."SA22018_V1_00"="SA2_code_workplace_address"
                JOIN sa2 AS residence ON residence."SA22018_V1_00"="SA2_code_usual_residence_address"
            
            WHERE workplace."UR2023_V1_00_NAME"=%(urban_area_name)s 
            AND residence."UR2023_V1_00_NAME"=%(urban_area_name)s
            
            ORDER BY "SA2_code_usual_residence_address", "SA2_code_workplace_address"
        """
    return pd.read_sql(all_flows_query, engine, params={"urban_area_name": urban_area_name})


def get_workbook_config_page(urban_area_name: str, columns: List[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=["property", "value"], data=[
        ["title", f"{urban_area_name} Mode Shares"],
        ["description", f"Means of travel to work for the {urban_area_name} area"],
        ["source.name", "2018 Census Main means of travel to work by Statistical Area 2"],
        ["source.url",
         "https://datafinder.stats.govt.nz/table/104720-2018-census-main-means-of-travel-to-work-by-statistical-area-2/"],
        ["createdBy.name", "Geospatial Research Institute | Toi Hangarau"],
        ["createdBy.url", "http://geospatial.ac.nz"],
        ["mapbox.mapStyle", ""],
        ["colors.schme", "Default"],
        ["colors.darkMode", "no"],
        ["animate.flows", "no"],
        ["clustering", "no"],
        ["flows.sheets", ','.join(columns)],
        ["msg.locationTooltip.incoming", "Inbound commuters"],
        ["msg.locationTooltip.outgoing", "Outbound commuters"],
        ["msg.locationTooltip.internal", "Internal commuters"],
        ["msg.flowTooltip.numOfTrips", "Number of commuters"],
        ["msg.totalCount.allTrips", "{0} commuters"],
        ["msg.totalCount.countOfTrips", "{0} of {1} commuters"],
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
    locations_sheet.update(df_to_gspread_list(sa2_locations.reset_index(drop=False)))

    for column_name in flow_columns:
        flow_data = flows[['origin', 'dest', column_name]].rename(columns={column_name: "count"})
        flow_sheet = spreadsheet.add_worksheet(column_name,
                                               rows=len(flow_data) + 1,
                                               cols=len(sa2_locations.columns))
        flow_sheet.update(df_to_gspread_list(flow_data))

    permissions = spreadsheet.list_permissions()
    if not any(permission["id"] == "anyoneWithLink" and permission["role"] == "reader"
               for permission in permissions):
        spreadsheet.share(email_address=None, perm_type="anyone", role="reader", with_link=True).raise_for_status()
    if not any(permission["emailAddress"] == EnvVariable.ADMIN_EMAIL and (
            permission["role"] == "writer" or permission["pendingOwner"])
               for permission in permissions):
        transfer_ownership_response = spreadsheet.share(email_address=EnvVariable.ADMIN_EMAIL,
                                                        perm_type="user",
                                                        role="writer",
                                                        notify=True)
        transfer_ownership_response.raise_for_status()
        owner_permission_id = transfer_ownership_response.json()["id"]
        spreadsheet.transfer_ownership(owner_permission_id).raise_for_status()
    return spreadsheet.url


def save_flow_map_sheets(engine: sqlalchemy.engine.Engine) -> None:
    if not EnvVariable.IS_FLOWMAP_ENABLED:
        return
    flow_sheets_table_name = "flow_sheets"
    if sqlalchemy.inspect(engine).has_table(flow_sheets_table_name):
        log.info(f"Table {flow_sheets_table_name} exists, skipping.")
        return
    log.info(f"Initialising table {flow_sheets_table_name}.")

    gspread_client = gspread.service_account_from_dict(EnvVariable.GOOGLE_CREDENTIALS)
    flow_sheet_url_data = []
    for aoi in stats_nz_geographies.AREAS_OF_INTEREST:
        urban_area = aoi.ua_name
        sa2_locations = find_sa2_locations(engine, urban_area)
        flows = find_flows(engine, urban_area)
        spreadsheet_name = f"flows_{urban_area}"
        flow_columns = [col for col in flows.columns if col not in {'origin', 'dest'}]
        workbook_config_sheet = get_workbook_config_page(aoi.display_name, flow_columns)
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
                    raise gspread.exceptions.APIError from e
                refresh_time = 500
                progress_bar = tqdm(range(refresh_time),
                                    desc="Google Sheets API limit hit, waiting for limit refresh...")
                for _ in progress_bar:
                    time.sleep(1)
                    log_interval_s = 10
                    if progress_bar.n % log_interval_s == 0:
                        log.info(str(progress_bar))

    flow_sheet_df = pd.DataFrame(flow_sheet_url_data).set_index("urban_area")
    flow_sheet_df.to_sql(flow_sheets_table_name, engine, if_exists="replace", index=True)


if __name__ == '__main__':
    engine = get_db_engine()
    save_flow_map_sheets(engine)
