from typing import Callable, Dict, List

import customtkinter as ctk


class GenericWindow:
    """
    A class to create a customizable window with various fields and button actions using CustomTkinter.
    """

    def __init__(
        self,
        title: str,
        fields: List[str],
        button_texts: List[str],
        button_actions: List[Callable[[], None]],
        resizable: bool = True,
    ) -> None:
        """
        Initialize the GenericWindow instance and configure the UI.

        Parameters:
            title (str): The title of the window.
            fields (List[str]): Labels for input fields.
            button_texts (List[str]): Texts for the buttons.
            button_actions (List[Callable[[], None]]): Actions to be executed on button clicks.
            resizable (bool): Whether the window is resizable.
        """
        if len(button_texts) != len(button_actions):
            raise ValueError("Each button text must have a corresponding action.")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title(title)
        self.window.resizable(resizable, resizable)

        self.fields = fields
        self.entries: Dict[str, ctk.CTkEntry] = {}
        self.button_texts = button_texts
        self.button_actions = button_actions

        self._setup_window()

    def _setup_window(self) -> None:
        """
        Configure window layout and widgets.
        """
        self._center_window()
        self._create_widgets()
        self._center_frame_on_resize()

    def _center_window(self) -> None:
        """
        Center the window on the screen.
        """
        self.window.update_idletasks()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _center_frame_on_resize(self) -> None:
        """
        Ensure the frame remains centered during window resizing.
        """
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

    def _create_widgets(self) -> None:
        """
        Create and arrange widgets in the window.
        """
        frame = ctk.CTkFrame(self.window, fg_color="#121212")
        frame.grid(row=0, column=0, padx=10, pady=10)

        self._create_fields(frame)
        self._create_buttons(frame)

        self.window.bind("<Return>", self._on_enter_key)

        self.window.update_idletasks()
        frame_width = frame.winfo_reqwidth() + 40
        frame_height = frame.winfo_reqheight() + 40
        self.window.geometry(f"{frame_width}x{frame_height}")

    def _create_fields(self, frame: ctk.CTkFrame) -> None:
        """
        Create input fields in the given frame.

        Parameters:
            frame (ctk.CTkFrame): The frame to place input fields into.
        """
        for idx, field in enumerate(self.fields):
            label = ctk.CTkLabel(frame, text=field, text_color="#E5E5E5")
            label.grid(row=idx, column=0, padx=10, pady=10, sticky="e")

            entry = ctk.CTkEntry(
                frame,
                placeholder_text=field,
                placeholder_text_color="#B0B0B0",
                fg_color="#2C2C2C",
                border_color="#2C2C2C",
                border_width=2,
                show="*",
            )
            entry.grid(row=idx, column=1, padx=10, pady=10)
            self.entries[field] = entry
            self._bind_entry_events(entry)

    def _create_buttons(self, frame: ctk.CTkFrame) -> None:
        """
        Create buttons in the given frame.

        Parameters:
            frame (ctk.CTkFrame): The frame to place buttons into.
        """
        for idx, (text, action) in enumerate(
            zip(self.button_texts, self.button_actions)
        ):
            button = ctk.CTkButton(
                frame,
                text=text,
                command=action,
                fg_color="#1A73E8",
                hover_color="#3367D6",
                text_color="#E5E5E5",
            )
            button.grid(row=len(self.fields) + idx, column=0, columnspan=2, pady=10)

    def _bind_entry_events(self, entry: ctk.CTkEntry) -> None:
        """
        Bind events to a given entry widget to handle focus and hover changes.

        Parameters:
            entry (ctk.CTkEntry): The entry widget to bind events to.
        """
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color="#3367D6"))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color="#2C2C2C"))
        entry.bind("<Enter>", lambda e: entry.configure(fg_color="#3A3A3A"))
        entry.bind("<Leave>", lambda e: entry.configure(fg_color="#2C2C2C"))

    def _on_enter_key(self, event) -> None:
        """
        Handle the Enter key press event to trigger the first button's action.

        Parameters:
            event (ctk.Event): The event object.
        """
        if self.button_actions:
            self.button_actions[0]()

    def run(self) -> None:
        """
        Start the CustomTkinter main loop.
        """
        self.window.mainloop()
