import os
import re
import sys

import customtkinter as ctk
from PIL import Image

from config import config
from utils.generic_window import GenericWindow


class LoadingWindow(GenericWindow):
    """
    A class to create a loading window with an animation and an info message area.
    """

    def __init__(self) -> None:
        """
        Initialize the LoadingWindow instance and configure the loading animation UI.
        """
        super().__init__(
            title=config["title"],
            tab_titles=["SIAC -> NOTION"],
            toggle_window=-1,
            resizable=False,
        )
        self.checking_logs = True
        self.loading_label = ctk.CTkLabel(
            self.frames[0],
            text="Loading...",
            text_color="#ABDAE1",
            fg_color="#1A73E8",
            corner_radius=15,
            font=("Segoe UI", 16, "bold"),
        )
        self.loading_label.grid(padx=20, pady=20)

        self.status_label = ctk.CTkLabel(
            self.frames[0],
            text="Initializing...",
            text_color="#ABDAE1",
            font=("Segoe UI", 12, "bold"),
            wraplength=280,
        )
        self.status_label.grid(padx=20, pady=10)

        if getattr(sys, "frozen", False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        image_path = os.path.join(self.base_path, "src/icons", "loading1.png")
        self.image = Image.open(image_path)
        self.ctk_image = ctk.CTkImage(self.image, size=(80, 80))
        self.loading_icon = ctk.CTkLabel(self.window, image=self.ctk_image, text="")
        self.loading_icon.grid(pady=30, sticky="s")

        self.animation_running = True
        self.animate_loading_icon()
        self.check_logs()

    def animate_loading_icon(self) -> None:
        """
        Animate the loading icon while the window is open.
        """
        angle = 0

        def update():
            nonlocal angle
            self.rotate_image(angle)
            angle = (angle + 2) % 360
            if self.animation_running:
                self.frames[0].after(1, update)

        update()

    def rotate_image(self, angle: int) -> None:
        """Rotates the loading icon image by the specified angle and updates the label.

        Args:
            angle (int): The angle to rotate the image.
        """
        rotated_image = self.image.rotate(-angle)
        self.ctk_image = ctk.CTkImage(rotated_image, size=(80, 80))
        self.loading_icon.configure(image=self.ctk_image)
        self.loading_icon.grid(pady=20, sticky="s")
        self.frames[0].update()

    def show_info(self, message: str) -> None:
        """
        Update the status message displayed in the loading window.

        Parameters:
            message (str): The message to display.
        """
        self.status_label.configure(text=message)
        self.frames[0].update()

    def get_last_log_message(self) -> str:
        """
        Retrieves the last line of the latest general log file from the logs directory.

        Returns:
            str: The last log message (without the log level), or an empty string if no logs are found.
        """
        log_dir = os.path.join(self.base_path, "logs", "logs")
        log_files = [
            f
            for f in os.listdir(log_dir)
            if f.startswith("general_log_") and f.endswith(".log")
        ]
        if not log_files:
            return ""
        log_files.sort(key=lambda f: int(f.split("_")[-1].split(".")[0]))
        latest_log_file = os.path.join(log_dir, log_files[-1])
        try:
            with open(latest_log_file, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(latest_log_file, "r", encoding="latin1") as file:
                lines = file.readlines()
        if lines:
            last_line = lines[-1].strip()
            return self.extract_message(last_line)

        return ""

    def extract_message(self, log_line: str) -> str:
        """
        Extracts the message part from a log line.

        Parameters:
            log_line (str): The log line to process.

        Returns:
            str: The extracted message.
        """
        match = re.search(r"-\s*[A-Z]+\s*-\s*(.*)", log_line)
        return match[1].strip() if match else log_line

    def check_logs(self):
        """
        Check the logs for the last message and update the loading UI accordingly.
        """
        if self.checking_logs:
            if current_log_message := self.get_last_log_message():
                self.show_info(f"{current_log_message}...")
                if "Program completed successfully" in current_log_message:
                    self.stop_loading()
                if "Application terminated" in current_log_message:
                    self.stop_loading(False)

            self.frames[0].after(1, self.check_logs)

    def stop_loading(self, success: bool = True) -> None:
        """
        Stop the loading animation and update the UI to show that synchronization is complete.
        """
        self.animation_running = False
        self.checking_logs = False
        self.loading_icon.destroy()
        self.loading_label.configure(text="Synced" if success else "Failure")
        self.show_static_icon(success)

    def show_static_icon(self, success: bool = True) -> None:
        """
        Show the static icon indicating completion.
        """
        if hasattr(self, "completed_icon"):
            return
        completed_image_path = os.path.join(
            self.base_path, "src/icons", "done.png" if success else "cancel.png"
        )
        completed_image = Image.open(completed_image_path)
        self.ctk_completed_image = ctk.CTkImage(completed_image, size=(80, 80))
        self.completed_icon = ctk.CTkLabel(
            self.window, image=self.ctk_completed_image, text=""
        )
        self.completed_icon.grid(pady=30, sticky="s")
        self.frames[0].update()
