import os
import sys
from tkinter import Checkbutton, Frame, IntVar, Tk, messagebox
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import config, save_data
from logs import general_log, return_log
from utils.generic_window import GenericWindow


class LoginWindow(GenericWindow):
    """
    A class to create a login window for CPF and password input with "Remember Login" and "Remember Password" functionality.
    """

    def __init__(self) -> None:
        """
        Initialize the LoginWindow class and set up the UI.
        """
        super().__init__(
            title="SIAC - UFBA - v1.0.0-beta1",
            fields=["CPF", "Password"],
            button_texts=["Login"],
            button_actions=[self._handle_login],
        )
        self.driver: Optional[webdriver.Chrome] = None
        self._initialize_checkboxes()
        self._populate_fields_from_config()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _initialize_checkboxes(self) -> None:
        """
        Initialize the checkboxes for remembering login and password.
        """
        self.remember_login_var = IntVar()
        self.remember_password_var = IntVar()

        checkbox_frame = Frame(self.window, bg=self.window.cget("bg"))
        checkbox_frame.grid(
            row=len(self.fields) + 1, column=0, columnspan=2, pady=(10, 20)
        )
        self._create_checkbox(
            frame=checkbox_frame,
            text="Remember Login",
            variable=self.remember_login_var,
            command=self._toggle_password_checkbox,
            column=0,
        )
        self._create_checkbox(
            frame=checkbox_frame,
            text="Remember Password",
            variable=self.remember_password_var,
            state="disabled",
            column=1,
        )

    def _create_checkbox(
        self, frame: Frame, text: str, variable: IntVar, **kwargs
    ) -> None:
        """
        Create a checkbox and add it to the specified frame.

        Parameters:
            frame (Frame): The parent frame to place the checkbox in.
            text (str): The text to display on the checkbox.
            variable (IntVar): The variable to associate with the checkbox.
            **kwargs: Additional arguments for Checkbutton.
        """
        column = kwargs.pop("column", None)
        Checkbutton(
            frame,
            activebackground=self.window.cget("bg"),
            activeforeground="#E5E5E5",
            bg=self.window.cget("bg"),
            fg="#E5E5E5",
            selectcolor=self.window.cget("bg"),
            text=text,
            variable=variable,
            **kwargs,
        ).grid(row=0, column=column, padx=10, pady=5, sticky="w")

    def _toggle_password_checkbox(self, *args) -> None:
        """
        Enable or disable the 'Remember Password' checkbox based on the state of the 'Remember Login' checkbox.
        """
        is_login_remembered = self.remember_login_var.get()
        self.remember_password_var.set(0)
        self.window.children["!frame"].children["!checkbutton2"].config(
            state="normal" if is_login_remembered else "disabled"
        )

    def _populate_fields_from_config(self) -> None:
        """
        Populate the CPF and Password fields with saved values from the configuration file.
        """
        login_info = config.get("siac", {})
        cpf = login_info.get("login", "")
        password = login_info.get("password", "")

        self.entries["CPF"].insert(0, cpf if cpf else "")
        self.entries["Password"].insert(0, password if password else "")
        if cpf:
            self.remember_login_var.set(1)
            if password:
                self.remember_password_var.set(1)
                self._toggle_password_checkbox()
        else:
            self.remember_login_var.set(0)
            self.remember_password_var.set(0)

    def _handle_login(self) -> None:
        """
        Handle the login action by validating inputs, performing login, and saving credentials based on checkbox states.
        """
        cpf = self.entries["CPF"].get()
        password = self.entries["Password"].get()

        if not cpf or not password:
            messagebox.showerror("Error", "CPF and Password cannot be empty")
            return

        try:
            self._perform_login(cpf, password)
            messagebox.showinfo("Success", "Login successful")
            self.window.destroy()
        except Exception as e:
            general_log.logger.error(f"Login failed: {e}")
            messagebox.showerror("Error", f"Login failed: {e}")

        self._update_config(cpf, password)

    def _update_config(self, cpf: str, password: str) -> None:
        """
        Update the configuration file based on the 'Remember Login' and 'Remember Password' checkboxes.

        Parameters:
            cpf (str): CPF of the user.
            password (str): Password of the user.
        """
        config["siac"] = {
            "login": cpf if self.remember_login_var.get() else "",
            "password": password if self.remember_password_var.get() else "",
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
        general_log.logger.info("Navigating to login page.")

        self._input_credentials(cpf, password)
        self._submit_login_form()

        self.driver.implicitly_wait(1)
        current_url = self.driver.current_url
        return_log.logger.info(f"Current URL after login attempt: {current_url}")

        if not self._is_login_successful():
            general_log.logger.error("Wrong CPF or Password. Please try again.")
            self.driver.quit()
            raise Exception("Wrong CPF or Password.")

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
        general_log.logger.info("Credentials entered.")

    def _submit_login_form(self) -> None:
        """
        Submit the login form.
        """
        self.driver.find_element(
            By.CSS_SELECTOR, 'input[type="image"][src="imagens/botoes/entrar.jpg"]'
        ).click()
        general_log.logger.info("Login form submitted.")

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
        except:
            return False

    def get_driver(self) -> Optional[webdriver.Chrome]:
        """
        Return the Selenium WebDriver instance.

        Returns:
            Optional[webdriver.Chrome]: An instance of Selenium WebDriver.
        """
        return self.driver

    def _on_close(self):
        """
        Handle the window close event. Terminate the program.
        """
        self.window.destroy()
        Tk().destroy()
        exit()
