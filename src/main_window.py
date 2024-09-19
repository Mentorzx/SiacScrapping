import os
import sys
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import config, save_data
from utils.generic_window import GenericWindow


class MainWindow(GenericWindow):
    """
    A class to create a combined window with two tabs: one for login functionality and one for Notion login.
    """

    def __init__(self) -> None:
        """
        Initialize the CombinedWindow class and set up the UI.
        """
        super().__init__(
            title=config["title"],
            tab_titles=["SIAC", "NOTION"],
            fields={
                "Login": ["CPF", "Password"],
                "Notion Login": config["notion"].get("config_fields", []),
            },
            button_texts={
                "Login": ["Login"],
                "Notion Login": ["Update Notion Credentials"],
            },
            button_actions={
                "Login": [self._handle_login],
                "Notion Login": [self._login],
            },
            toggle_window=-1,
        )
        self.driver: Optional[webdriver.Chrome] = None
        self.remember_login_checkbox = None
        self.remember_password_checkbox = None
        self.checkbox_frame: ctk.CTkFrame = None
        self._initialize_checkboxes()
        self._populate_fields_from_config()

    def _initialize_checkboxes(self) -> None:
        """
        Initialize the checkboxes for remembering login and password.
        """
        self.remember_login_var = ctk.IntVar()
        self.remember_password_var = ctk.IntVar()

        self.checkbox_frame = ctk.CTkFrame(
            self.window,
            fg_color="#02111B",
            corner_radius=15,
        )
        self.checkbox_frame.grid(
            row=len(self.fields["Login"]) + 1,
            column=0,
            columnspan=2,
            pady=(10, 20),
        )
        self.remember_login_checkbox = self._create_checkbox(
            frame=self.checkbox_frame,
            text="Remember Login",
            variable=self.remember_login_var,
            command=self._toggle_password_checkbox,
            column=0,
        )
        self.remember_password_checkbox = self._create_checkbox(
            frame=self.checkbox_frame,
            text="Remember Password",
            variable=self.remember_password_var,
            state="disabled",
            column=1,
        )

    def _create_checkbox(
        self, frame: ctk.CTkFrame, text: str, variable: ctk.IntVar, **kwargs
    ) -> ctk.CTkCheckBox:
        """
        Create a checkbox and add it to the specified frame.

        Parameters:
            frame (ctk.CTkFrame): The parent frame to place the checkbox in.
            text (str): The text to display on the checkbox.
            variable (ctk.IntVar): The variable to associate with the checkbox.
            **kwargs: Additional arguments for ctk.CTkCheckBox.
        """
        column = kwargs.pop("column", None)
        checkbox = ctk.CTkCheckBox(
            frame,
            text=text,
            variable=variable,
            fg_color="#1A73E8",
            hover_color="#ABDAE1",
            text_color="#ABDAE1",
            corner_radius=32,
            font=("Segoe UI", 12),
            **kwargs,
        )
        checkbox.grid(row=0, column=column, padx=20, pady=10, sticky="w")

        return checkbox

    def _toggle_password_checkbox(self, *args) -> None:
        """
        Enable or disable the 'Remember Password' checkbox based on the state of the 'Remember Login' checkbox.
        """
        is_login_remembered = self.remember_login_var.get()
        if not is_login_remembered:
            self.remember_password_var.set(0)
            self.remember_password_checkbox.configure(state="disabled")
            return
        self.remember_password_checkbox.configure(state="normal")

    def _populate_fields_from_config(self) -> None:
        """
        Populate the fields with saved values from the configuration file.
        """
        login_info = config.get("siac", {})
        notion_info = config.get("notion_login", {})
        cpf, password = login_info.get("login", ""), login_info.get("password", "")
        token, main_db_id = notion_info.get("token", ""), notion_info.get(
            "main_db_id", ""
        )
        timeline_db_id, rr_db_id = notion_info.get(
            "timeline_db_id", ""
        ), notion_info.get("rr_db_id", "")
        if cpf:
            self.entries["CPF"].insert(0, cpf)
            self.remember_login_var.set(1)
            self._toggle_password_checkbox()
            if password:
                self.entries["Password"].insert(0, password)
                self.remember_password_var.set(1)
        if all((token, main_db_id, timeline_db_id, rr_db_id)):
            for field, value in {
                "Notion Token": token,
                "Main Database ID": main_db_id,
                "Timeline Database ID": timeline_db_id,
                "Rejection Database ID": rr_db_id,
            }.items():
                self.entries[field].insert(0, value)
        else:
            self.remember_login_var.set(0)
            self.remember_password_var.set(0)

    def _handle_login(self) -> None:
        """
        Handle the login action by validating inputs, performing login, and saving credentials based on checkbox states.
        """
        cpf = self.entries["CPF"].get()
        password = self.entries["Password"].get()
        notion_data = self._gather_login_data()
        errors = [
            (
                "Notion IDs cannot be empty. Try putting them and Clicking Update."
                if self._has_empty_fields(notion_data["notion_login"])
                else None
            ),
            "CPF and Password cannot be empty. Auth only work with them." if not cpf or not password else None,
        ]
        if errors := [error for error in errors if error]:
            messagebox.showerror("Error", "\n".join(errors))
            return

        try:
            self._perform_login(cpf, password)
            messagebox.showinfo("Success", "Login successful")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")

    def _update_config(self, cpf: str, password: str) -> None:
        """
        Update the configuration file based on the 'Remember Login' and 'Remember Password' checkboxes.

        Parameters:
            cpf (str): CPF of the user.
            password (str): Password of the user.
        """
        config["siac"] = {
            "login": cpf if self.remember_login_var.get() else None,
            "password": password if self.remember_password_var.get() else None,
            "login_url": config["siac"].get("login_url", ""),
        }
        save_data(config)

    def _perform_login(self, cpf: str, password: str) -> None:
        """
        Perform login action using Selenium WebDriver.

        Parameters:
            cpf (str): CPF of the user.
            password (str): Password of the user.
        """
        service = Service(ChromeDriverManager().install())
        options = self._configure_browser_options()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(config["siac"]["login_url"])
        self._input_credentials(cpf, password)
        self._submit_login_form()
        self.driver.implicitly_wait(1)
        if not self._is_login_successful():
            self.driver.quit()
            raise ValueError("Wrong CPF or Password.")

    def _configure_browser_options(self) -> Options:
        """
        Configure and return the Chrome browser options.

        Returns:
            Options: Configured Chrome browser options.
        """
        options = Options()
        if config.get("webdriver", {}).get("headless", False):
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
        return options

    def _input_credentials(self, cpf: str, password: str) -> None:
        """
        Input credentials into the login form.

        Parameters:
            cpf (str): CPF of the user.
            password (str): Password of the user.
        """
        self.driver.find_element(By.NAME, "cpf").send_keys(cpf)
        self.driver.find_element(By.NAME, "senha").send_keys(password)

    def _submit_login_form(self) -> None:
        """
        Submit the login form.
        """
        self.driver.find_element(
            By.CSS_SELECTOR, 'input[type="image"][src="imagens/botoes/entrar.jpg"]'
        ).click()

    def _is_login_successful(self) -> bool:
        """
        Check if the login was successful by verifying the presence of an element.

        Returns:
            bool: True if login is successful, otherwise False.
        """
        try:
            self.driver.find_element(
                By.XPATH, '//tr[@onclick="changeDisplayS(17,18);"]'
            )
            return True
        except Exception:
            return False

    def _login(self) -> None:
        """
        Handle the login action and validate input before saving the Notion Token
        and Database ID to config.yaml.
        """
        notion_data = self._gather_login_data()
        if save_data(notion_data):
            messagebox.showinfo(
                "Success", "Notion Token and Database ID updated successfully!"
            )
        else:
            messagebox.showerror("Error", "Failed to save login information")

    def _gather_login_data(self) -> dict[str, str]:
        """
        Collect login information from input fields.

        Returns:
            dict: A dictionary containing Notion token and database IDs.
        """
        config["notion_login"] = {
            "token": self.entries["Notion Token"].get(),
            "main_db_id": self.entries["Main Database ID"].get(),
            "timeline_db_id": self.entries["Timeline Database ID"].get(),
            "rr_db_id": self.entries["Rejection Database ID"].get(),
        }
        return config

    def _has_empty_fields(self, data: dict[str, str]) -> bool:
        """
        Check if any field in the provided data dictionary is empty.

        Parameters:
            data (dict): Dictionary containing login information.

        Returns:
            bool: True if any field is empty, otherwise False.
        """
        return any(value.strip() == "" for value in data.values())

    def get_driver(self) -> Optional[webdriver.Chrome]:
        """
        Return the Selenium WebDriver instance.

        Returns:
            Optional[webdriver.Chrome]: An instance of Selenium WebDriver.
        """
        return self.driver

    def _on_tab_change(self):
        """
        Handle tab change.
        """
        if self.toggle_window == 0:
            self.checkbox_frame.grid(
                row=len(self.fields["Login"]) + 1,
                column=0,
                columnspan=2,
                pady=(10, 20),
            )
        elif self.toggle_window == 1:
            self.checkbox_frame.grid_forget()
        self._center_window()

    def _on_close(self) -> None:
        """
        Handle the window close event. Terminate the program gracefully.
        """
        try:
            login = self.entries["CPF"].get()
            password = self.entries["Password"].get()
            notion_data = self._gather_login_data()
            save_data(notion_data)
            self._update_config(login, password)
            if self.window:
                self.window.destroy()
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Error during window close: {e}")
        finally:
            sys.exit()
