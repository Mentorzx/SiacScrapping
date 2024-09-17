import os
from tkinter import messagebox

import yaml

from config import config
from logs import general_log
from utils.generic_window import GenericWindow


class NotionLoginWindow(GenericWindow):
    """
    A class to create a login window for Notion Token and Database ID input.
    """

    def __init__(self):
        """
        Initialize the NotionLoginWindow class and set up the UI.
        """
        super().__init__(
            title=config["notion"]["window_title"],
            fields=config["notion"]["config_fields"],
            button_text=config["notion"]["button_text"],
            button_action=self._login,
            width=config["notion"]["window_size"][0],
            height=config["notion"]["window_size"][1],
        )

    def _login(self):
        """
        Handle the login action and validate input before saving the Notion Token
        and Database ID to config.yaml.
        """
        notion_data = self._gather_login_data()

        if self._has_empty_fields(notion_data):
            messagebox.showerror(
                "Error", "Notion Token and Database ID cannot be empty"
            )
            return

        if self._save_login_data(notion_data):
            messagebox.showinfo(
                "Success", "Notion Token and Database ID updated successfully!"
            )
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Failed to save login information")

    def _gather_login_data(self):
        """
        Collect login information from input fields.

        Returns:
        dict: A dictionary containing Notion token and database IDs.
        """
        return {
            "token": self.entries["Notion Token"].get(),
            "main_database_id": self.entries["Main Database ID"].get(),
            "timeline_database_id": self.entries["Timeline Database ID"].get(),
            "rr_database_id": self.entries["Rejection Database ID"].get(),
        }

    def _has_empty_fields(self, data):
        """
        Check if any field in the provided data is empty.

        Parameters:
        data (dict): The login data to check.

        Returns:
        bool: True if any field is empty, False otherwise.
        """
        return any(not value for value in data.values())

    def _save_login_data(self, data):
        """
        Save Notion login data to the config.yaml file.

        Parameters:
        data (dict): The login data to be saved.

        Returns:
        bool: True if data is saved successfully, False otherwise.
        """
        try:
            config["notion"].update(data)
            config_path = self._get_config_path()
            self._write_to_yaml(config_path, config)
            return True
        except Exception as e:
            general_log.logger.info(f"Error saving config: {e}")
            return False

    def _get_config_path(self):
        """
        Get the path to the config.yaml file.

        Returns:
        str: The absolute path to the config.yaml file.
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        config_directory = os.path.join(project_root, "config")
        return os.path.join(config_directory, "config.yaml")

    def _write_to_yaml(self, file_path, data):
        """
        Write data to a YAML file.

        Parameters:
        file_path (str): The path to the YAML file.
        data (dict): The data to be written to the file.
        """
        with open(file_path, "w") as config_file:
            yaml.dump(data, config_file, default_flow_style=False)
            
    def run(self):
        """
        Start the Tkinter main loop.
        """
        self.window.mainloop()
