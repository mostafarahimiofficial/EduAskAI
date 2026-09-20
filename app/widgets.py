"""Reusable CustomTkinter widgets for chat messages."""

import customtkinter as ctk


class ChatMessage(ctk.CTkFrame):
    """A readable chat bubble with a copy button for assistant responses."""

    def __init__(self, master, sender, text, is_assistant=False):
        """Create a message bubble.

        Args:
            master: Parent widget.
            sender: Display name of message author.
            text: Message body.
            is_assistant: Whether to show a Copy button.
        """
        color = "#273449" if is_assistant else "#164E63"
        super().__init__(master, fg_color=color, corner_radius=10)
        self.text = text
        ctk.CTkLabel(self, text=sender, font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkLabel(self, text=text, justify="left", anchor="w", wraplength=620).pack(fill="x", padx=12, pady=8)
        if is_assistant:
            self.copy_button = ctk.CTkButton(self, text="Copy", width=70, height=26, command=self.copy_text)
            self.copy_button.pack(anchor="e", padx=10, pady=(0, 8))

    def copy_text(self):
        """Copy this assistant response to the system clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.text)
        self.copy_button.configure(text="Copied!")
        self.after(1400, lambda: self.copy_button.configure(text="Copy"))
