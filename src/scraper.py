from typing import List

import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By

from config import config
from logs import general_log, return_log


class TableDataFilter:
    """
    A class to filter unwanted rows from table data.
    """

    def filter_rows(self, data: List[List[str]]) -> List[List[str]]:
        """
        Filter out unwanted rows from the table data.

        Parameters:
            data (List[List[str]]): The table data to be filtered.

        Returns:
            List[List[str]]: The filtered table data.
        """

        def is_unwanted_row(row: List[str]) -> bool:
            unwanted_patterns = [
                (" ", 1),
                ("Estudos Extracurriculares", 1),
                ("Total Geral", 1),
                ("Subtotal:", 4),
                ("Período", 6),
            ]
            for pattern, length in unwanted_patterns:
                if len(row) == length and row[0] == pattern:
                    return True
            if len(row) == 2 and row[0].startswith("CH - Carga Horária"):
                return True
            return False

        filtered_data = [row for row in data if not is_unwanted_row(row)]
        return_log.logger.info(f"Data filtered as: {filtered_data}")
        return filtered_data


class Scraper:
    """
    A class to handle scraping operations and convert table data to a Pandas DataFrame.
    """

    def __init__(self, driver):
        """
        Initialize the Scraper class with a Selenium WebDriver instance.

        Parameters:
            driver: Selenium WebDriver instance.
        """
        self.driver = driver
        self.config = config
        self.filter = TableDataFilter()

    def scrape_table(self) -> pd.DataFrame:
        """
        Perform scraping and convert the table data to a Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the scraped and filtered data.
        """
        self.driver.get(self.config["completed_courses_url"])
        general_log.logger.info("Navigating to completed courses page.")

        try:
            table_data = self._extract_table_data()
            general_log.logger.info(f"Extracted table data")
            if len(table_data) > 8:
                df = self._convert_table_to_dataframe(table_data)
                df = self._calculate_weighted_average(df)
                return df
            else:
                general_log.logger.warning("Not enough rows found in table.")
                return pd.DataFrame()
        except Exception as e:
            general_log.logger.error(
                f"Failed to scrape and convert table to DataFrame: {e}"
            )
            raise
        finally:
            self.driver.quit()

    def _convert_table_to_dataframe(self, table_data: list) -> pd.DataFrame:
        """
        Convert extracted table data into a DataFrame and process it.

        Parameters:
            table_data (list): The raw table data extracted from the scraping.

        Returns:
            pd.DataFrame: The processed DataFrame.
        """
        headers = [
            "PERÍODO",
            "CÓDIGO",
            "MATÉRIA",
            "CH",
            "CR",
            "NOTA",
            "PCH",
            "PCR",
            "RES",
        ]
        data = table_data[36:-14]
        filtered_data = self.filter.filter_rows(data)
        df = pd.DataFrame(filtered_data, columns=headers)

        df["PERÍODO"] = df["PERÍODO"].replace("", None)
        df["PERÍODO"] = df["PERÍODO"].ffill()
        df["NOTA"] = df["NOTA"].replace("--", None)
        df["NOTA"] = pd.to_numeric(df["NOTA"], errors="coerce")
        df["NOTA"] = df["NOTA"].replace(np.nan, None)
        df["CH"] = df["CH"].replace("--", None)
        df["CH"] = pd.to_numeric(df["CH"], errors="coerce")
        df["CH"] = df["CH"].replace(np.nan, None)

        return_log.logger.info(f"DataFrame created with shape: {df.shape}")
        general_log.logger.info("Table data successfully converted to DataFrame.")

        return df.dropna(subset=['CÓDIGO'])

    def _calculate_weighted_average(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the weighted average of the CH and Nota columns for specified codes and update the DataFrame.

        Parameters:
            df (pd.DataFrame): The DataFrame containing course data.

        Returns:
            pd.DataFrame: Updated DataFrame with calculated grades for FIS122, FIS123, and FIS121.
        """
        course_mappings = {
            "FIS122": ["FISD34", "FISD41"],
            "FIS123": ["FISD37", "FISD40"],
            "FIS121": ["FISD36", "FISD42"],
        }

        for target_code, source_codes in course_mappings.items():
            filtered_rows = df[df["CÓDIGO"].isin(source_codes)].copy()
            if self._validate_source_codes(filtered_rows, source_codes):
                df = self._update_course_grade(df, filtered_rows, target_code)

        return df

    def _validate_source_codes(
        self, filtered_rows: pd.DataFrame, source_codes: list
    ) -> bool:
        """
        Validate if there are valid notes and sufficient data for the given source codes.

        Parameters:
            filtered_rows (pd.DataFrame): The DataFrame containing the filtered rows.
            source_codes (list): List of course codes to validate.

        Returns:
            bool: True if there are valid notes and sufficient data, otherwise False.
        """
        if filtered_rows.empty:
            general_log.logger.warning(
                f"No data found for source codes: {source_codes}"
            )
            return False
        if filtered_rows["NOTA"].isna().all():
            general_log.logger.warning(
                f"All notes are missing for source codes: {source_codes}"
            )
            return False

        return True

    def _update_course_grade(
        self, df: pd.DataFrame, filtered_rows: pd.DataFrame, target_code: str
    ) -> pd.DataFrame:
        """
        Calculate the weighted average for a specific target course based on the source courses.

        Parameters:
            df (pd.DataFrame): The DataFrame containing course data.
            filtered_rows (pd.DataFrame): The DataFrame containing the filtered rows.
            target_code (str): The course code to update.

        Returns:
            pd.DataFrame: Updated DataFrame with the calculated grade for the target course.
        """
        total_ch = filtered_rows["CH"].sum()
        weighted_sum = (filtered_rows["CH"] * filtered_rows["NOTA"]).sum()
        weighted_avg = weighted_sum / total_ch if total_ch != 0 else 0

        target_rows = df[(df["CÓDIGO"] == target_code) & (df["RES"] == "DI")]
        if not target_rows.empty:
            df.loc[(df["CÓDIGO"] == target_code) & (df["RES"] == "DI"), "NOTA"] = (
                weighted_avg
            )
            df.loc[(df["CÓDIGO"] == target_code) & (df["RES"] == "DI"), "CH"] = (
                total_ch
            )
            df.loc[(df["CÓDIGO"] == target_code) & (df["RES"] == "DI"), "RES"] = (
                "AP" if weighted_avg >= 5 else "RR"
            )

            general_log.logger.info(
                f"Updated {target_code} with weighted average Nota: {weighted_avg} "
                f"and result: {'AP' if weighted_avg >= 5 else 'RR'}"
            )

        return df

    def _extract_table_data(self) -> List[List[str]]:
        """
        Extract table data from the web page.

        Returns:
            List[List[str]]: The extracted table data.
        """
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table tr")
        table_data = [
            [col.text for col in row.find_elements(By.TAG_NAME, "td")] for row in rows
        ]
        return_log.logger.info(f"Raw table data extracted: {table_data}")
        return table_data
