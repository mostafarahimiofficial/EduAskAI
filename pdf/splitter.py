"""Simple text chunking for PDF retrieval."""


def split_text(text, chunk_size=900, overlap=150):
    """Split text into overlapping chunks at readable boundaries.

    Args:
        text: Text to split.
        chunk_size: Approximate maximum characters per chunk.
        overlap: Characters retained between neighboring chunks.

    Returns:
        A list of non-empty text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return [chunk for chunk in chunks if chunk]
