"""
Module containing the LabeledCombobox UI component for the Tkinter application.
This component provides a combobox with a label.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Any, Optional


class LabeledCombobox(ttk.Frame):
    """A labeled combobox component."""
    
    def __init__(
        self, 
        master: Any, 
        label_text: str, 
        values: List[str], 
        on_select: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize a labeled combobox.
        
        Args:
            master: The parent widget
            label_text: Text for the label
            values: List of values for the combobox
            on_select: Callback function when selection changes
            **kwargs: Additional arguments for the Frame
        """
        super().__init__(master, **kwargs)
        
        # Create and place the label
        self.label = ttk.Label(self, text=label_text)
        self.label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Create and place the combobox
        self.combobox = ttk.Combobox(self, values=values, state="readonly")
        self.combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Set default selection to first item if available
        if values:
            self.combobox.current(0)
        
        # Configure grid to expand combobox
        self.columnconfigure(1, weight=1)
        
        # Bind selection event if callback provided
        if on_select:
            self.combobox.bind("<<ComboboxSelected>>", on_select)
    
    def get(self) -> str:
        """Get the current selected value."""
        return self.combobox.get()
    
    def set(self, value: str) -> None:
        """Set the combobox value."""
        self.combobox.set(value)