from typing import Union

import pandas as pd

from logs import general_log
from services.notion_api import NotionRequestFactory


def update_notion(
    df: pd.DataFrame,
    page_code_map: dict[str, Union[str, list[str]]],
    notion_factory: NotionRequestFactory,
    table_type: str = "main",
):
    """
    Main function to update Notion pages based on the table type.

    Parameters:
        df (DataFrame): The DataFrame containing the data to update.
        page_code_map (dict): A dictionary mapping codes to Notion page IDs or lists of page IDs.
        notion_factory (NotionRequestFactory): An instance of the NotionRequestFactory.
        table_type (str): The type of table to update ("main", "rr", "timeline").
    """
    if table_type == "main":
        update_main_notion(df, page_code_map, notion_factory)
    elif table_type == "rr":
        update_rr_notion(df, page_code_map, notion_factory)
    elif table_type == "timeline":
        update_timeline_notion(df, page_code_map, notion_factory)
    else:
        general_log.logger.error(
            f"Unknown table type: {table_type}. No update performed."
        )


def update_main_notion(
    df: pd.DataFrame,
    page_code_map: dict[str, Union[str, list[str]]],
    notion_factory: NotionRequestFactory,
):
    """
    Updates Notion pages with the corresponding data from the DataFrame.

    Parameters:
        df (DataFrame): The DataFrame containing the data to update.
        page_code_map (dict): A dictionary mapping codes to Notion page IDs or lists of page IDs.
        notion_factory (NotionRequestFactory): An instance of the NotionRequestFactory.
    """
    general_log.logger.info("Starting update for main Notion table.")
    for code, page_ids in page_code_map.items():
        general_log.logger.info(f"Processing code {code}.")
        filtered_rows = get_filtered_rows(df, "CÓDIGO", code)
        if filtered_rows.empty:
            general_log.logger.info(f"No data found for code {code}, skipping update.")
            continue

        sorted_rows = sort_rows_by_priority(filtered_rows)
        page_ids = ensure_page_ids_is_list(page_ids)
        update_pages_with_rows(sorted_rows, page_ids, code, notion_factory)
    general_log.logger.info("Finished updating main Notion table.")


def update_rr_notion(
    df: pd.DataFrame,
    page_code_map: dict[str, Union[str, list[str]]],
    notion_factory: NotionRequestFactory,
):
    """
    Verifies if all rows with RES = 'RR' are present in the Notion table. Creates or updates pages accordingly.

    Parameters:
        df (DataFrame): The DataFrame containing the data to update.
        page_code_map (dict): A dictionary mapping codes to Notion page IDs or lists of page IDs.
        notion_factory (NotionRequestFactory): An instance of the NotionRequestFactory.
    """
    general_log.logger.info("Starting update for rejection Notion table.")
    filtered_rows = get_filtered_rows(df, "RES", "RR")
    rr_rows = sort_rows_by_priority(filtered_rows, ["RR"])
    general_log.logger.info(
        f"Filtered and sorted rows. Total rows available: {rr_rows.shape[0]}."
    )
    grouped_rr = rr_rows.groupby("CÓDIGO")
    general_log.logger.info(
        f"Grouped rows by 'CÓDIGO'. Found {len(grouped_rr)} unique codes."
    )

    for code, group in grouped_rr:
        general_log.logger.info(f"Processing code {code}.")
        for _, row in group.iterrows():
            data = {
                "CÓDIGO": {"title": [{"text": {"content": code}}]},
                "NOTA": {"number": row["NOTA"]},
                "CH": {"number": row["CH"]},
            }
            process_code_page(code, page_code_map, row, notion_factory, data)
    general_log.logger.info("Finished processing all codes.")


def update_timeline_notion(
    df: pd.DataFrame,
    page_code_map: dict[str, Union[str, list[str]]],
    notion_factory: NotionRequestFactory,
):
    """
    Updates Notion pages for the timeline table by processing each period in the given DataFrame.
    For each period, the function creates or updates pages in Notion based on the provided mapping and factory.

    Args:
        df (pd.DataFrame): DataFrame containing data with columns 'PERÍODO', 'CÓDIGO', 'MATÉRIA', 'CH', and 'NOTA'.
        page_code_map (dict[str, Union[str, list[str]]]): Dictionary mapping periods to Notion page IDs or lists of page IDs.
        notion_factory (NotionRequestFactory): Instance of NotionRequestFactory used to interact with Notion API.
    """
    general_log.logger.info("Starting update for timeline Notion table.")
    df_cleaned = df[df['CÓDIGO'].str.strip() != ''].copy()
    grouped_by_period = df_cleaned.groupby("PERÍODO")
    semester = 1
    for period, group in grouped_by_period:
        general_log.logger.info(f"Processing period {period}.")
        process_period(period, group, semester, page_code_map, notion_factory)
        semester += 1
    general_log.logger.info("Finished processing all periods.")


def create_new_period_page(
    period: str, semester: int, notion_factory: NotionRequestFactory
) -> str:
    """
    Creates a new page for the specified period and returns the page ID if successful.

    Parameters:
        period (str): The period name.
        semester (int): The current semester number.
        notion_factory (NotionRequestFactory): An instance of the NotionRequestFactory.

    Returns:
        Optional[str]: The newly created page ID, or None if creation failed.
    """
    period_data = {
        "PERÍODO": {"rich_text": [{"text": {"content": period}}]},
        "CÓDIGO": {"title": [{"text": {"content": f"{semester}°"}}]},
        "MATÉRIA": {"rich_text": [{"text": {"content": "SEMESTRE"}}]},
    }

    response = notion_factory.create_page(period_data)
    if response.status_code == 200:
        return response.json().get("id")
    else:
        general_log.logger.error(
            f"Failed to create page for period '{period}'. Status code: {response.status_code}"
        )
        return None


def process_period(
    period: str,
    group: pd.DataFrame,
    semester: int,
    page_code_map: dict[str, Union[str, list[str]]],
    notion_factory: NotionRequestFactory,
):
    """
    Handles the creation or update of Notion pages for a given period. If a page for the period does not exist,
    it creates a new page and updates the mapping accordingly.

    Args:
        period (str): The period to process.
        group (pd.DataFrame): DataFrame containing rows for the given period.
        semester (int): The semester number associated with the period.
        page_code_map (dict[str, Union[str, list[str]]]): Dictionary mapping periods to Notion page IDs or lists of page IDs.
        notion_factory (NotionRequestFactory): Instance of NotionRequestFactory used to interact with Notion API.
    """
    period_page_id = page_code_map.get(period)
    if not period_page_id:
        period_page_id = handle_missing_period_page(
            period, semester, notion_factory, page_code_map
        )
        if not period_page_id:
            return  # Skip further processing if page creation failed
    period_page_id = ensure_page_ids_is_list(period_page_id)[0]
    for _, row in group.iterrows():
        process_row(row, period_page_id, page_code_map, notion_factory)


def handle_missing_period_page(
    period: str,
    semester: int,
    notion_factory: NotionRequestFactory,
    page_code_map: dict[str, Union[str, list[str]]],
):
    """
    Handles the situation where a Notion page for a given period does not exist. Creates a new page and updates
    the page_code_map with the new page ID.

    Args:
        period (str): The period for which a new page needs to be created.
        semester (int): The semester number associated with the period.
        notion_factory (NotionRequestFactory): Instance of NotionRequestFactory used to interact with Notion API.
        page_code_map (dict[str, Union[str, list[str]]]): Dictionary mapping periods to Notion page IDs or lists of page IDs.

    Returns:
        str: The page ID of the newly created Notion page, or None if creation failed.
    """
    general_log.logger.info(f"Period page for '{period}' not found. Creating new page.")
    period_page_id = create_new_period_page(period, semester, notion_factory)
    if period_page_id:
        page_code_map[period] = period_page_id
        general_log.logger.info(
            f"Created new page for period '{period}' with page_id: {period_page_id}."
        )
    return period_page_id


def process_row(
    row: pd.Series,
    period_page_id: str,
    page_code_map: dict[str, Union[str, list[str]]],
    notion_factory: NotionRequestFactory,
):
    """
    Updates or creates a Notion page for a given row of data. The data includes code, subject, workload, and grade.

    Args:
        row (pd.Series): Row data containing 'CÓDIGO', 'MATÉRIA', 'CH', and 'NOTA'.
        period_page_id (str): The ID of the Notion page related to the period.
        page_code_map (dict[str, Union[str, list[str]]]): Dictionary mapping codes to Notion page IDs or lists of page IDs.
        notion_factory (NotionRequestFactory): Instance of NotionRequestFactory used to interact with Notion API.
    """
    code = row["CÓDIGO"]
    general_log.logger.info(f"Updating/Creating page for code: {code}.")
    data = build_notion_data(row, period_page_id)
    process_code_page(code, page_code_map, row, notion_factory, data)


def build_notion_data(row: pd.Series, period_page_id: str) -> dict:
    """
    Constructs the data payload for updating or creating a Notion page based on the provided row data.

    Args:
        row (pd.Series): Row data containing 'CÓDIGO', 'MATÉRIA', 'CH', and 'NOTA'.
        period_page_id (str): The ID of the Notion page related to the period.

    Returns:
        dict: The data payload for Notion API requests.
    """
    return {
        "item principal": {"relation": [{"id": period_page_id}]},
        "CÓDIGO": {"title": [{"text": {"content": row["CÓDIGO"]}}]},
        "MATÉRIA": {"rich_text": [{"text": {"content": row["MATÉRIA"]}}]},
        "CH": {"number": row["CH"]},
        "NOTA": {"number": row["NOTA"]},
    }


def process_code_page(
    code: str,
    page_code_map: dict[str, any],
    row: dict[str, any],
    notion_factory: NotionRequestFactory,
    data: dict[str, any],
) -> None:
    """
    Processes the given code to either update an existing page or create a new one in Notion.

    If the code is found in `page_code_map`, the function updates the corresponding pages.
    If the code is not found, a new page is created in Notion with the provided `data`.

    Parameters:
        code (str): The unique code representing the page.
        page_code_map (dict[str, Any]): A mapping of codes to Notion page IDs.
        row (dict[str, Any]): A dictionary containing row data with the 'NOTA' field.
        notion_factory (NotionRequestFactory): An instance of NotionRequestFactory to handle Notion API requests.
        data (dict[str, Any]): The data to be used when creating a new page in Notion.

    Returns:
        None
    """
    if code in page_code_map:
        for page_id in ensure_page_ids_is_list(page_code_map[code]):
            log_and_update_page(page_id, code, row, notion_factory)
            if page_id in page_code_map[code]:
                if isinstance(page_code_map[code], list):
                    page_code_map[code].remove(page_id)
                else:
                    page_code_map[code] = []
            if not page_code_map[code]:
                del page_code_map[code]
    else:
        general_log.logger.warning(f"No remaining page IDs for code {code}.")
        general_log.logger.info(
            f"Creating new page for code {code} with NOTA {row['NOTA']}."
        )

        response = notion_factory.create_page(data)
        if response.status_code == 200:
            general_log.logger.info(f"Successfully created new page for code {code}.")
        else:
            general_log.logger.error(
                f"Failed to create page for code {code}. Status code: {response.status_code}"
            )


def get_filtered_rows(df: pd.DataFrame, column_name: str, code: str) -> pd.DataFrame:
    """
    Filters the DataFrame for rows matching the given code in the specified column.

    Parameters:
        df (DataFrame): The DataFrame to filter.
        column_name (str): The name of the column to match the code.
        code (str): The code to match in the DataFrame.

    Returns:
        DataFrame: Filtered rows matching the code in the specified column.
    """
    return df[df[column_name] == code].copy()


def sort_rows_by_priority(
    filtered_rows: pd.DataFrame,
    res_priority: list[str] = ["AP", "DU", "DI", "RR"],
) -> pd.DataFrame:
    """
    Sorts the filtered rows by 'RES' priority and 'NOTA'.

    Parameters:
        filtered_rows (DataFrame): The filtered rows to be sorted.
        res_priority (list): A list defining the priority order for the 'RES' column. Default is ["AP", "DU", "DI", "RR"].

    Returns:
        DataFrame: Sorted rows based on 'RES' priority and 'NOTA'.
    """
    res_priority_map = {res: idx for idx, res in enumerate(res_priority)}
    filtered_rows["RES_PRIORITY"] = filtered_rows["RES"].map(res_priority_map)
    return filtered_rows.sort_values(
        by=["RES_PRIORITY", "NOTA"], ascending=[True, False]
    )


def ensure_page_ids_is_list(page_ids: Union[str, list[str]]) -> list[str]:
    """
    Ensures that page_ids is always a list.

    Parameters:
        page_ids: The page ID or list of page IDs.

    Returns:
        list: A list of page IDs.
    """
    if not isinstance(page_ids, list):
        return [page_ids]
    return page_ids


def update_pages_with_rows(
    sorted_rows: pd.DataFrame,
    page_ids: list[str],
    code: str,
    notion_factory: NotionRequestFactory,
):
    """
    Updates the Notion pages with the corresponding rows of data from the DataFrame.

    Parameters:
        sorted_rows (DataFrame): The sorted rows to update.
        page_ids (list): The list of page IDs to update.
        code (str): The code corresponding to the page and rows.
        notion_factory (NotionRequestFactory): An instance of the NotionRequestFactory.
    """
    for idx, page_id in enumerate(page_ids):
        if idx < len(sorted_rows):
            row = sorted_rows.iloc[idx]
            log_and_update_page(page_id, code, row, notion_factory)
        else:
            general_log.logger.warning(
                f"No more data available to update for code {code} (page_id: {page_id}). Skipping."
            )


def log_and_update_page(
    page_id: str, code: str, row: pd.Series, notion_factory: NotionRequestFactory
):
    """
    Logs the update and performs the actual update of the Notion page.

    Parameters:
        page_id (str): The Notion page ID to update.
        code (str): The code corresponding to the page and row.
        row (pd.Series): The row of data to update in the Notion page.
        notion_factory (NotionRequestFactory): An instance of the NotionRequestFactory.
    """
    general_log.logger.info(
        f"Updating Notion page (page_id: {page_id}) with {code} using row with RES='{row['RES']}' and NOTA={row['NOTA']}."
    )
    data = {"NOTA": {"number": row["NOTA"]}}
    response = notion_factory.update_page(page_id, data)

    if response.status_code == 200:
        general_log.logger.info(
            f"Successfully updated Notion page with {code} (page_id: {page_id}) with NOTA: {row['NOTA']}."
        )
    else:
        general_log.logger.error(
            f"Failed to update Notion page with {code} (page_id: {page_id}). Status code: {response.status_code}"
        )
