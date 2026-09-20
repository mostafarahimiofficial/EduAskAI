"""Functions for extracting readable text from PDF files."""

from pypdf import PdfReader

from utils.helpers import clean_text


def extract_pages_from_pdf(file_path):
    """Extract readable text from each page in a PDF.

    Args:
        file_path: Path to a PDF document.

    Returns:
        A list of dictionaries containing page number and text.

    Raises:
        ValueError: If the PDF has no readable text.
    """
    try:
        reader = PdfReader(file_path)
        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "")
            if text:
                pages.append({"page": page_number, "text": text})
    except Exception as error:
        raise ValueError("This file could not be read as a PDF.") from error
    if not pages:
        raise ValueError("This PDF does not contain readable text.")
    return pages
