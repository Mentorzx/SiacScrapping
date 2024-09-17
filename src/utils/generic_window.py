import tkinter as tk
from tkinter import messagebox
from typing import Callable, List


class GenericWindow:
    """
    A class to create a generic window with customizable fields and button actions.
    """

    def __init__(
        self,
        title: str,
        fields: List[str],
        button_text: str,
        button_action: Callable,
        width: int = 300,
        height: int = 150,
        resizable: bool = False,
    ):
        """
        Initialize the GenericWindow class and set up the UI.

        Parameters:
            title (str): Title of the window.
            fields (List[str]): List of field labels to be displayed.
            button_text (str): Text to display on the button.
            button_action (Callable): Function to execute when the button is clicked.
            width (int): Width of the window.
            height (int): Height of the window.
            resizable (bool): Whether the window is resizable.
        """
        self.window = tk.Tk()
        self.window.title(title)
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(resizable, resizable)
        self.fields = fields
        self.entries = {}
        self.button_text = button_text
        self.button_action = button_action
        self._setup_window()

    def _setup_window(self):
        """
        Set up and centralize the window and create the widgets.
        """
        self._center_window()
        self._create_widgets()

    def _center_window(self):
        """
        Centralize the window on the screen.
        """
        self.window.update_idletasks()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _create_widgets(self):
        """
        Create and place widgets on the window.
        """
        frame = tk.Frame(self.window)
        frame.grid(row=0, column=0, padx=20, pady=20)

        for idx, field in enumerate(self.fields):
            tk.Label(frame, text=field).grid(
                row=idx, column=0, padx=10, pady=10, sticky="e"
            )
            entry = tk.Entry(frame, show="*")
            entry.grid(row=idx, column=1, padx=10, pady=10)
            self.entries[field] = entry

        self.window.bind("<Return>", self._on_enter_key)
        tk.Button(frame, text=self.button_text, command=self.button_action).grid(
            row=len(self.fields), column=0, columnspan=2, pady=5
        )

    def _on_enter_key(self, event):
        """
        Handle Enter key press event to trigger button action.
        """
        self.button_action()
    
    def run(self):
        """
        Start the Tkinter main loop.
        """
        self.window.mainloop()
