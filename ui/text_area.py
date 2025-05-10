"""
Module containing the TextArea UI component for the Tkinter application.
This component provides a scrollable text area with an optional label.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any


class TextArea(ttk.Frame):
    """A scrollable text area component."""

    def __init__(
        self, 
        master: Any, 
        label_text: str = "", 
        height: int = 10,
        **kwargs
    ):
        """
        Initialize a text area with scrollbar.

        Args:
            master: The parent widget
            label_text: Text for the label (optional)
            height: Height of the text area in lines
            **kwargs: Additional arguments for the Frame
        """
        super().__init__(master, **kwargs)

        # Create and place the label if provided
        if label_text:
            self.label = ttk.Label(self, text=label_text)
            self.label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
            text_row = 1
        else:
            text_row = 0

        # Create and place the text widget
        self.text = tk.Text(self, height=height, wrap=tk.WORD)
        self.text.grid(row=text_row, column=0, sticky="nsew", padx=5, pady=5)

        # Create and place the scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.scrollbar.grid(row=text_row, column=1, sticky="ns", pady=5)
        self.text.configure(yscrollcommand=self.scrollbar.set)

        # Configure grid to expand text area
        self.columnconfigure(0, weight=1)
        self.rowconfigure(text_row, weight=1)

    def get(self) -> str:
        """Get the current text content."""
        return self.text.get("1.0", tk.END)

    def set(self, value: str) -> None:
        """Set the text content."""
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", value)

    def append(self, value: str, tag: str = None) -> None:
        """
        Append text to the current content.

        Args:
            value: The text to append
            tag: Optional tag to apply to the text
        """
        self.text.insert(tk.END, value, tag if tag else "")

    def configure_tag(self, tag_name: str, **kwargs) -> None:
        """
        Configure a tag with specified attributes.

        Args:
            tag_name: The name of the tag
            **kwargs: Attributes for the tag (foreground, background, etc.)
        """
        self.text.tag_configure(tag_name, **kwargs)
