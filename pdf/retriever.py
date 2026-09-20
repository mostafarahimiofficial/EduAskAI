"""ChromaDB storage and retrieval for uploaded PDF chunks."""

import os
import shutil

import chromadb

from pdf.loader import extract_pages_from_pdf
from pdf.splitter import split_text
from utils.config import CHROMA_FOLDER, PDF_FOLDER, ensure_data_folders


class PDFRetriever:
    """Index PDFs locally and retrieve their most relevant passages."""

    def __init__(self):
        """Open the persistent Chroma collection used by the application."""
        ensure_data_folders()
        self.client = chromadb.PersistentClient(path=CHROMA_FOLDER)
        self.collection = self.client.get_or_create_collection("eduaskai_pdfs")

    def add_pdf(self, file_path):
        """Extract, chunk, and store a PDF with source and page metadata.

        Args:
            file_path: Local PDF path.

        Returns:
            The uploaded file's name.
        """
        filename = os.path.basename(file_path)
        stored_path = os.path.join(PDF_FOLDER, filename)

        documents, metadatas, ids = [], [], []
        for page_data in extract_pages_from_pdf(file_path):
            for index, chunk in enumerate(split_text(page_data["text"])):
                documents.append(chunk)
                metadatas.append({"source": filename, "page": page_data["page"]})
                ids.append(f"{filename}-{page_data['page']}-{index}")
        if not documents:
            raise ValueError("No usable text was found in this PDF.")
        if os.path.abspath(file_path) != os.path.abspath(stored_path):
            shutil.copy2(file_path, stored_path)
        self.remove_pdf(filename)
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        return filename

    def retrieve(self, question, count=4):
        """Find relevant chunks for a student question.

        Args:
            question: Student's question.
            count: Maximum number of chunks to return.

        Returns:
            A list of dictionaries with text and metadata.
        """
        if self.collection.count() == 0:
            return []
        result = self.collection.query(query_texts=[question], n_results=min(count, self.collection.count()))
        return [
            {"text": text, "source": metadata["source"], "page": metadata["page"]}
            for text, metadata in zip(result["documents"][0], result["metadatas"][0])
        ]

    def list_pdfs(self):
        """Return unique PDF source names currently stored in the collection."""
        data = self.collection.get(include=["metadatas"])
        return sorted({item["source"] for item in data.get("metadatas", [])})

    def remove_pdf(self, filename, delete_file=False):
        """Remove a PDF's indexed chunks and, optionally, its managed local copy."""
        data = self.collection.get(where={"source": filename})
        if data.get("ids"):
            self.collection.delete(ids=data["ids"])
        if delete_file:
            stored_path = os.path.join(PDF_FOLDER, os.path.basename(filename))
            if os.path.isfile(stored_path):
                os.remove(stored_path)
