"""
Module containing the InputField UI component for the Tkinter application.
This component provides a text input field with an optional browse button.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Any


class InputField(ttk.Frame):
    """A text input field component."""

    def __init__(
        self, 
        master: Any, 
        label_text: str, 
        with_browse_button: bool = False,
        filetypes = None,
        dialog_title: str = "Select a file",
        **kwargs
    ):
        """
        Initialize an input field.

        Args:
            master: The parent widget
            label_text: Text for the label
            with_browse_button: Whether to include a browse button
            filetypes: List of tuples for file dialog (e.g., [("PDF files", "*.pdf")])
            dialog_title: Title for the file dialog
            **kwargs: Additional arguments for the Frame
        """
        self.filetypes = filetypes or [
            ("Document files", "*.pdf;*.txt"),
            ("PDF files", "*.pdf"),
            ("Text files", "*.txt")
        ]
        self.dialog_title = dialog_title
        super().__init__(master, **kwargs)

        # Create and place the label
        self.label = ttk.Label(self, text=label_text)
        self.label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Create and place the entry field
        self.entry = ttk.Entry(self)
        self.entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Add browse button if requested
        if with_browse_button:
            self.browse_button = ttk.Button(
                self, 
                text="Browse", 
                command=self._browse_file
            )
            self.browse_button.grid(row=0, column=2, padx=5, pady=5)

            # Create a description of supported file types
            file_types_desc = "Supported file types: "
            file_types = [ft[0].split()[0] for ft in self.filetypes if not ft[0].startswith("All")]
            file_types_desc += ", ".join(file_types)

            self.file_type_label = ttk.Label(
                self, 
                text=file_types_desc,
                font=("Arial", 8),
                foreground="gray"
            )
            self.file_type_label.grid(row=1, column=1, sticky="w", padx=5)

        # Configure grid to expand entry field
        self.columnconfigure(1, weight=1)

    def _browse_file(self) -> None:
        """Open file dialog and set the selected file path to the entry."""
        file_path = filedialog.askopenfilename(
            filetypes=self.filetypes,
            title=self.dialog_title
        )
        if file_path:
            self.set(file_path)

    def get(self) -> str:
        """Get the current text value."""
        return self.entry.get()

    def set(self, value: str) -> None:
        """Set the entry text value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
