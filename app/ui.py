"""Dark-themed desktop interface for EduAskAI."""

import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from agent.agent import EduAskAgent
from app.widgets import ChatMessage
from pdf.retriever import PDFRetriever


class EduAskAIApp(ctk.CTk):
    """Main window that connects the student interface to the simple agent."""

    def __init__(self):
        """Build the interface and initialise local PDF storage."""
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("EduAskAI")
        self.geometry("1050x700")
        self.minsize(800, 550)
        self.configure(fg_color="#111827")
        self.retriever = PDFRetriever()
        self.agent = None
        self.startup_error = None
        try:
            self.agent = EduAskAgent(self.retriever)
        except ValueError as error:
            self.startup_error = str(error)
        self._build_layout()
        self.refresh_documents()
        if self.startup_error:
            self.add_message("EduAskAI", f"Setup needed: {self.startup_error}", True)
        else:
            self.add_message("EduAskAI", "Hello! Upload a PDF or ask me a question.", True)

    def _build_layout(self):
        """Create the sidebar, scrollable chat area, and message controls."""
        sidebar = ctk.CTkFrame(self, width=230, fg_color="#1F2937", corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="EduAskAI", font=ctk.CTkFont(size=26, weight="bold")).pack(padx=20, pady=(24, 6))
        ctk.CTkLabel(sidebar, text="Your educational AI assistant", text_color="#9CA3AF").pack(padx=14, pady=(0, 25))
        ctk.CTkButton(sidebar, text="+ New Chat", command=self.new_chat).pack(fill="x", padx=18, pady=6)
        ctk.CTkButton(sidebar, text="Add PDF", command=self.add_pdf).pack(fill="x", padx=18, pady=6)
        ctk.CTkLabel(sidebar, text="Difficulty", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=18, pady=(24, 5))
        self.difficulty = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(sidebar, values=["Easy", "Medium", "Hard"], variable=self.difficulty).pack(fill="x", padx=18)
        ctk.CTkLabel(sidebar, text="Documents", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=18, pady=(24, 5))
        self.selected_pdf = ctk.StringVar(value="No PDFs uploaded yet.")
        self.document_picker = ctk.CTkOptionMenu(
            sidebar,
            values=["No PDFs uploaded yet."],
            variable=self.selected_pdf,
            state="disabled",
        )
        self.document_picker.pack(fill="x", padx=18, pady=(0, 8))
        self.remove_pdf_button = ctk.CTkButton(
            sidebar,
            text="Remove Selected PDF",
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            command=self.remove_pdf,
            state="disabled",
        )
        self.remove_pdf_button.pack(fill="x", padx=18, pady=(0, 18))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True, padx=18, pady=18)
        self.chat = ctk.CTkScrollableFrame(main, fg_color="#0F172A")
        self.chat.pack(fill="both", expand=True)
        compose = ctk.CTkFrame(main, fg_color="transparent")
        compose.pack(fill="x", pady=(12, 0))
        self.input = ctk.CTkTextbox(compose, height=64, fg_color="#1F2937")
        self.input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input.bind("<Control-Return>", lambda event: self.send_message())
        self.send_button = ctk.CTkButton(compose, text="Send", width=100, command=self.send_message)
        self.send_button.pack(side="right", fill="y")
        ctk.CTkLabel(main, text="Tip: Ctrl+Enter sends a message. Ask for “5 easy questions” after uploading a PDF.", text_color="#9CA3AF").pack(anchor="w", pady=(6, 0))

    def add_message(self, sender, text, is_assistant=False):
        """Add a single message bubble to the bottom of the chat view."""
        message = ChatMessage(self.chat, sender, text, is_assistant)
        message.pack(fill="x", padx=10, pady=7, anchor="w")
        self.after(50, lambda: self.chat._parent_canvas.yview_moveto(1.0))

    def send_message(self):
        """Read student input and process it without freezing the interface."""
        message = self.input.get("1.0", "end").strip()
        if not message:
            messagebox.showinfo("EduAskAI", "Please type a message first.")
            return
        if not self.agent:
            messagebox.showerror("EduAskAI", self.startup_error or "AI service is not configured.")
            return
        self.input.delete("1.0", "end")
        self.add_message("You", message)
        self.send_button.configure(state="disabled", text="Thinking...")
        threading.Thread(target=self._answer_in_background, args=(message,), daemon=True).start()

    def _answer_in_background(self, message):
        """Run a potentially slow agent request in a worker thread."""
        try:
            response = self.agent.answer(message, self.difficulty.get())
        except Exception as error:
            response = f"Sorry, I could not complete that request. {error}"
        self.after(0, lambda: self._show_response(response))

    def _show_response(self, response):
        """Display a completed response and re-enable input controls."""
        self.add_message("EduAskAI", response, True)
        self.send_button.configure(state="normal", text="Send")

    def new_chat(self):
        """Clear the visible chat and history while keeping indexed PDFs available."""
        for child in self.chat.winfo_children():
            child.destroy()
        if self.agent:
            self.agent.new_chat()
        self.add_message("EduAskAI", "New chat started. Your uploaded PDFs are still available.", True)
        self.after(100, lambda: self.chat._parent_canvas.yview_moveto(0.0))

    def add_pdf(self):
        """Choose and index a PDF, reporting friendly success or error feedback."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF documents", "*.pdf")])
        if not file_path:
            return
        try:
            name = self.retriever.add_pdf(file_path)
            self.refresh_documents()
            self.add_message("EduAskAI", f"'{name}' is ready. You can now ask questions about it.", True)
        except ValueError as error:
            messagebox.showerror("PDF error", str(error))
        except Exception:
            messagebox.showerror("PDF error", "Unable to index this PDF. Please try another readable document.")

    def refresh_documents(self):
        """Refresh the selectable PDF list from ChromaDB's current sources."""
        files = self.retriever.list_pdfs()
        if files:
            current = self.selected_pdf.get()
            self.document_picker.configure(values=files, state="normal")
            self.selected_pdf.set(current if current in files else files[0])
            self.remove_pdf_button.configure(state="normal")
        else:
            self.selected_pdf.set("No PDFs uploaded yet.")
            self.document_picker.configure(values=["No PDFs uploaded yet."], state="disabled")
            self.remove_pdf_button.configure(state="disabled")

    def remove_pdf(self):
        """Remove the selected PDF's index and app-managed local copy."""
        selected = self.selected_pdf.get()
        if not selected or selected == "No PDFs uploaded yet.":
            messagebox.showinfo("EduAskAI", "Select a PDF name in the document list first.")
            return
        if not messagebox.askyesno("Remove PDF", f"Remove '{selected}' from EduAskAI?"):
            return
        try:
            self.retriever.remove_pdf(selected, delete_file=True)
            self.refresh_documents()
            self.add_message("EduAskAI", f"Removed '{selected}'.", True)
        except Exception as error:
            messagebox.showerror("PDF error", f"Unable to remove '{selected}'. {error}")
