"""Application entry point for EduAskAI."""

from app.ui import EduAskAIApp


def main():
    """Create and start the EduAskAI desktop application."""
    app = EduAskAIApp()
    app.mainloop()


if __name__ == "__main__":
    main()
