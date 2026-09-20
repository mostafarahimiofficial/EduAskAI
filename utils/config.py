"""Simple application configuration."""

import os

from dotenv import load_dotenv

APP_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(APP_FOLDER, ".env"))

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PDF_FOLDER = os.path.join(APP_FOLDER, "data", "pdfs")
CHROMA_FOLDER = os.path.join(APP_FOLDER, "database", "chroma")


def ensure_data_folders():
    """Create local PDF and vector-database folders when needed."""
    os.makedirs(PDF_FOLDER, exist_ok=True)
    os.makedirs(CHROMA_FOLDER, exist_ok=True)
