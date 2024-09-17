import os
import sys
from tkinter import messagebox
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logs import general_log, return_log
from utils.generic_window import GenericWindow
from config import config


class LoginWindow(GenericWindow):
    """
    A class to create a login window for CPF and password input.
    """

    def __init__(self):
        """
        Initialize the LoginWindow class and set up the UI.
        """
        super().__init__(
            title="SIAC - UFBA - v1.0.0-beta1",
            fields=["CPF", "Password"],
            button_text="Login",
            button_action=self._login,
            width=250,
            height=150,
        )
        self.driver: Optional[webdriver.Chrome] = None

    def _login(self):
        """
        Handle the login action.
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

    def _perform_login(self, cpf: str, password: str):
        """
        Perform login action using Selenium WebDriver.

        Parameters:
            cpf (str): CPF of the user.
            password (str): Password of the user.
        """
        service = Service(ChromeDriverManager().install())
        options = Options()
        if config["webdriver"]["headless"]:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(config["login_url"])
        general_log.logger.info("Navigating to login page.")
        self._input_credentials(cpf, password)
        self._submit_login_form()
        self.driver.implicitly_wait(1)
        current_url = self.driver.current_url
        return_log.logger.info(f"Current URL after login attempt: {current_url}")
        try:
            self.driver.find_element(
                By.XPATH, '//tr[@onclick="changeDisplayS(17,18);"]'
            )
        except:
            general_log.logger.error("Wrong CPF or Password. Please Try again.")
            self.driver.quit()
            raise Exception("Wrong CPF or Password.")

    def _input_credentials(self, cpf: str, password: str):
        """
        Input credentials into the login form.

        Parameters:
            cpf (str): CPF of the user.
            password (str): Password of the user.
        """
        self.driver.find_element(By.NAME, "cpf").send_keys(cpf)
        self.driver.find_element(By.NAME, "senha").send_keys(password)
        general_log.logger.info("Credentials entered.")

    def _submit_login_form(self):
        """
        Submit the login form.
        """
        self.driver.find_element(
            By.CSS_SELECTOR, 'input[type="image"][src="imagens/botoes/entrar.jpg"]'
        ).click()
        general_log.logger.info("Login form submitted.")

    def get_driver(self) -> Optional[webdriver.Chrome]:
        """
        Return the Selenium WebDriver instance.

        Returns:
            Optional[webdriver.Chrome]: An instance of Selenium WebDriver.
        """
        return self.driver
