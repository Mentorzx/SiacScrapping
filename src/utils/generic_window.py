import sys
from typing import Callable, Optional

import customtkinter as ctk
import pyautogui
from selenium import webdriver


class GenericWindow:
    """
    A class to create a customizable window with tabbed interface using CustomTkinter.

    Attributes:
        title (str): The title of the window.
        tab_titles (list[str]): Titles for each tab.
        fields (dict[str, list[str]]): A dictionary where keys are tab titles and values are lists of field labels for each tab.
        button_texts (dict[str, list[str]]): A dictionary where keys are tab titles and values are lists of button texts for each tab.
        button_actions (dict[str, list[Callable[[], None]]]): A dictionary where keys are tab titles and values are lists of button actions for each tab.
        resizable (bool): Whether the window is resizable.
    """

    def __init__(
        self,
        title: str,
        tab_titles: list[str],
        fields: dict[str, list[str]],
        button_texts: dict[str, list[str]],
        button_actions: dict[str, list[Callable[[], None]]],
        toggle_window: int,
        resizable: bool = True,
    ) -> None:
        """
        Initialize the GenericWindow instance and configure the UI with tab view.

        Parameters:
            title (str): The title of the window.
            tab_titles (list[str]): Titles for each tab.
            fields (dict[str, list[str]]): Field labels organized by tab title.
            button_texts (dict[str, list[str]]): Button texts organized by tab title.
            button_actions (dict[str, list[Callable[[], None]]]): Button actions organized by tab title.
            toggle_window(int): Trigger the window resize event.
            resizable (bool): Whether the window is resizable.
        """
        self.toggle_window = toggle_window
        self.driver: Optional[webdriver.Chrome] = None
        self._validate_inputs(button_texts, button_actions)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")

        self.window = ctk.CTk()
        self.window.title(title)
        self.window.resizable(resizable, resizable)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        self.fields = fields
        self.entries: dict[str, ctk.CTkEntry] = {}
        self.button_texts = button_texts
        self.button_actions = button_actions

        self.tab_view = ctk.CTkTabview(
            self.window,
            text_color="#02111B",
            segmented_button_selected_color="#1A73E8",
            segmented_button_unselected_color="#8C827D",
            command=self._on_tab_change,
        )
        self.tab_view.grid(row=0, column=0, padx=10, pady=10)
        self._setup_tabs(tab_titles)

    def _validate_inputs(
        self,
        button_texts: dict[str, list[str]],
        button_actions: dict[str, list[Callable[[], None]]],
    ) -> None:
        """
        Validate that each button text has a corresponding action.

        Parameters:
            button_texts (dict[str, list[str]]): Button texts organized by tab title.
            button_actions (dict[str, list[Callable[[], None]]]): Button actions organized by tab title.

        Raises:
            ValueError: If there is a mismatch between button texts and actions.
        """
        for tab in button_texts:
            if len(button_texts[tab]) != len(button_actions.get(tab, [])):
                raise ValueError(
                    f"Each button text must have a corresponding action for tab: {tab}"
                )

    def _setup_tabs(self, tab_titles: list[str]) -> None:
        """
        Configure the tabs and their content.

        Parameters:
            tab_titles (list[str]): Titles for each tab.
        """
        for idx, title in enumerate(tab_titles):
            self.tab_view.add(title)
            frame = ctk.CTkFrame(
                self.tab_view.tab(title),
                corner_radius=15,
                fg_color="#02111B",
            )
            self.tab_view._segmented_button.configure(
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
            )
            frame.grid(row=0, column=0, padx=30, pady=30)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            self._create_widgets(frame, idx)

    def _create_widgets(self, frame: ctk.CTkFrame, tab_index: int) -> None:
        """
        Create and arrange widgets in a specific tab.

        Parameters:
            frame (ctk.CTkFrame): The frame to place widgets into.
            tab_index (int): The index of the tab to match the order of fields.
        """
        self._create_fields(frame, tab_index)
        self._create_buttons(frame, tab_index)

        self.window.bind("<Return>", self._on_enter_key)
        self.window.update_idletasks()

        self._center_window()

    def _create_fields(self, frame: ctk.CTkFrame, tab_index: int) -> None:
        """
        Create input fields in the given frame for the specified tab.

        Parameters:
            frame (ctk.CTkFrame): The frame to place input fields into.
            tab_index (int): The index of the tab to match the order of fields.
        """
        field_keys = list(self.fields.keys())
        if tab_index < len(field_keys):
            fields_key = field_keys[tab_index]
            fields = self.fields.get(fields_key, [])
            for idx, field in enumerate(fields):
                label = ctk.CTkLabel(
                    frame,
                    text=field,
                    text_color="#ABDAE1",
                    font=("Segoe UI", 12, "bold"),
                )
                label.grid(row=idx, column=0, padx=10, pady=10, sticky="e")
                entry = ctk.CTkEntry(
                    frame,
                    placeholder_text=field,
                    placeholder_text_color="#B0B0B0",
                    fg_color="#8C827D",
                    border_color="#8C827D",
                    text_color="#02111B",
                    border_width=2,
                    show="*" if "Password" in field else "",
                    font=("Segoe UI", 12, "bold"),
                )
                entry.grid(row=idx, column=1, padx=10, pady=10)
                self.entries[field] = entry

    def _create_buttons(self, frame: ctk.CTkFrame, tab_index: int) -> None:
        """
        Create buttons in the given frame for the specified tab.

        Parameters:
            frame (ctk.CTkFrame): The frame to place buttons into.
            tab_index (int): The index of the tab to match the order of buttons.
        """
        button_keys = list(self.button_texts.keys())
        if tab_index < len(button_keys):
            button_key = button_keys[tab_index]
            button_texts = self.button_texts.get(button_key, [])
            button_actions = self.button_actions.get(button_key, [])
            for idx, (text, action) in enumerate(zip(button_texts, button_actions)):
                button = ctk.CTkButton(
                    frame,
                    text=text,
                    command=action,
                    fg_color="#1A73E8",
                    hover_color="#3367D6",
                    text_color="#E5E5E5",
                    corner_radius=32,
                    border_color="#1A5BC3",
                    font=("Segoe UI", 16, "bold"),
                )
                button.grid(
                    row=len(self.fields.get(button_key, [])),
                    column=idx,
                    columnspan=2,
                    pady=20,
                )

    def _on_enter_key(self, event) -> None:
        """
        Handle the Enter key press event to toggle_window the first button's action of the currently active tab.

        Parameters:
            event (ctk.Event): The event object.
        """
        if self.button_actions:
            active_tab = self.tab_view.get()
            if actions := self.button_actions.get(active_tab, []):
                actions[0]()

    def _center_window(self) -> None:
        """
        Center the window on the screen or toggle its size.
        """

        def calculate_center_position(width: int, height: int) -> tuple[int, int]:
            """Calculate the coordinates to center the window on the screen."""
            screen_width, screen_height = pyautogui.size()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            return x, y

        login_window_width, login_window_height = 400, 400
        window_width, window_height = (
            self.window.winfo_width(),
            self.window.winfo_height(),
        )
        if self.toggle_window < 0:
            x, y = calculate_center_position(login_window_width, login_window_height)
            self.window.geometry(f"{login_window_width}x{login_window_height}+{x}+{y}")
            self.toggle_window = 0
        elif self.toggle_window == 0:
            self.toggle_window = 1
            self.window.geometry(f"{login_window_width}x{login_window_height}")
        else:
            self.toggle_window = 0
            self.window.geometry(f"{window_width}x{window_height}")

    def _on_tab_change(self):
        """
        Handle tab change.
        """
        self._center_window

    def _on_close(self) -> None:
        """
        Handle the window close event. Terminate the program gracefully.
        """
        try:
            if self.window:
                self.window.destroy()
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Error during window close: {e}")
        finally:
            sys.exit()

    def run(self) -> None:
        """
        Start the CustomTkinter main loop.
        """
        self.window.mainloop()
