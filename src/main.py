import os
import sys
from typing import Union

import pandas as pd

sys.path.append("../../")
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main_window import MainWindow
from notion_update import update_notion
from scraper import Scraper
from services.notion_api import NotionRequestFactory
from logs import general_log, return_log
from config import config


def initialize_application() -> Scraper:
    """
    Initialize the application by setting up the login window and scraper.

    Returns:
        Scraper: An instance of the Scraper class with an initialized WebDriver.
    """
    general_log.logger.info("Starting the SIAC Scraping application.")
    login_window = MainWindow()
    login_window.run()
    driver = login_window.get_driver()
    if driver is None:
        general_log.logger.error("Failed to initialize the WebDriver.")
        raise RuntimeError("WebDriver initialization failed.")
    general_log.logger.info("WebDriver initialized successfully.")
    scraper = Scraper(driver)
    general_log.logger.info("Scraper instance created successfully.")

    return scraper


def execute_scraping(scraper: Scraper):
    """
    Execute the table scraping process and return the scraped DataFrame.

    Parameters:
        scraper (Scraper): An instance of the Scraper class.

    Returns:
        DataFrame: The DataFrame obtained from the scraping process.
    """
    general_log.logger.info("Starting the scraping process.")
    try:
        df = scraper.scrape_table()
        if not df.empty:
            return_log.logger.info(f"DataFrame obtained from scraping: {df.head()}")
            return df
        else:
            general_log.logger.warning("DataFrame is empty after scraping.")
    except Exception as e:
        general_log.logger.error(f"Scraping failed: {e}")
        raise


def get_page_id_from_code(df, notion_factory: NotionRequestFactory) -> dict:
    """
    Given a DataFrame with 'CÓDIGO' column, search for the corresponding page in Notion.

    Parameters:
        df (DataFrame): The DataFrame containing the 'CÓDIGO' column.
        notion_factory (NotionRequestFactory): An instance of the NotionRequestFactory.

    Returns:
        dict: A dictionary mapping each code from the DataFrame to its corresponding page IDs in Notion.
    """
    general_log.logger.info("Fetching pages from Notion to match codes.")
    page_code_map = {}
    try:
        pages = notion_factory.get_pages()
        for page in pages:
            props = page["properties"]
            if props["CÓDIGO"]["title"]:
                notion_code = props["CÓDIGO"]["title"][0]["text"]["content"]
                matching_row = df[df["CÓDIGO"] == notion_code]
            else:
                notion_code = []
                matching_row = pd.DataFrame()
            if not matching_row.empty:
                if notion_code not in page_code_map:
                    page_code_map[notion_code] = []
                page_id = page["id"]
                page_code_map[notion_code].append(page_id)
                general_log.logger.info(
                    f"Matched Notion page with code: {notion_code}, page_id: {page_id}"
                )
    except Exception as e:
        general_log.logger.error(f"Error while fetching pages or matching codes: {e}")
        raise

    return page_code_map


def create_notion_factories() -> dict[str, NotionRequestFactory]:
    """
    Creates and returns NotionRequestFactory instances for different Notion databases.

    Returns:
        dict[str, NotionRequestFactory]: A dictionary with NotionRequestFactory instances for each database type.
    """
    return {
        "main": NotionRequestFactory(config, config["notion_login"]["main_db_id"]),
        "rr": NotionRequestFactory(config, config["notion_login"]["rr_db_id"], "rr"),
    }


def generate_page_code_maps(
    df: pd.DataFrame, notion_factories: dict[str, NotionRequestFactory]
) -> dict[str, dict[str, Union[str, list[str]]]]:
    """
    Generates page code maps for each Notion database based on the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        notion_factories (dict[str, NotionRequestFactory]): A dictionary with NotionRequestFactory instances.

    Returns:
        dict[str, dict[str, Union[str, list[str]]]]: A dictionary with page code maps for each Notion database.
    """
    return {
        "main": get_page_id_from_code(df, notion_factories["main"]),
        "rr": get_page_id_from_code(df, notion_factories["rr"]),
    }


def update_all_notion_tables(
    df: pd.DataFrame,
    page_code_maps: dict[str, dict[str, Union[str, list[str]]]],
    notion_factories: dict[str, NotionRequestFactory],
):
    """
    Updates all Notion tables with data from the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        page_code_maps (dict[str, dict[str, Union[str, list[str]]]]): A dictionary with page code maps for each Notion database.
        notion_factories (dict[str, NotionRequestFactory]): A dictionary with NotionRequestFactory instances.
    """
    for table_type, page_code_map in page_code_maps.items():
        if notion_factory := notion_factories[table_type]:
            update_notion(df, page_code_map, notion_factory, table_type)


def main():
    """
    Main entry point for the SIAC Scraping project.
    Initializes the application, performs scraping, and updates Notion databases.
    """
    try:
        scraper = initialize_application()
        data_frame = execute_scraping(scraper)
        if data_frame.empty:
            general_log.logger.warning("No data was scraped. Exiting the application.")
            return
        notion_factories = create_notion_factories()
        page_code_maps = generate_page_code_maps(data_frame, notion_factories)
        update_all_notion_tables(data_frame, page_code_maps, notion_factories)
        general_log.logger.info(
            "Program completed successfully. All tasks were executed and results were processed as expected."
        )
        print(
            "Program completed successfully. All tasks were executed and results were processed as expected."
        )
    except Exception as error:
        general_log.logger.critical(f"Application terminated due to: {error}")


if __name__ == "__main__":
    main()
