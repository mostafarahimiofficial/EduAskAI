"""Small reusable text helpers."""

import re


def clean_text(text):
    """Return text with repeated whitespace replaced by single spaces.

    Args:
        text: Raw extracted text.

    Returns:
        A cleaner, readable string.
    """
    return re.sub(r"\s+", " ", text).strip()
