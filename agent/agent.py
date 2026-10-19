"""Single-agent request routing for chat, PDFs, and web search."""

import re

from agent.prompts import GENERAL_SYSTEM_PROMPT, PDF_SYSTEM_PROMPT, WEB_SYSTEM_PROMPT, question_prompt
from agent.tools import asks_for_explanation, asks_for_questions, needs_web_search
from llm.client import LLMClient
from search.web_search import search_web


class EduAskAgent:
    """Choose a simple appropriate tool and ask the configured LLM for an answer."""

    def __init__(self, retriever):
        """Create the agent.

        Args:
            retriever: PDFRetriever used to find uploaded-document content.
        """
        self.retriever = retriever
        self.llm = LLMClient()
        self.history = []

    def new_chat(self):
        """Clear only in-memory conversation history; PDFs remain indexed."""
        self.history = []

    def answer(self, message, difficulty="Medium", question_count=5, document_name=None):
        """Route a student message and return an educational response.

        Args:
            message: Student's text.
            difficulty: Selected study-question difficulty.
            question_count: Default number of generated questions.

        Returns:
            Assistant response text.
        """
        if needs_web_search(message):
            return self._web_answer(message)
        if asks_for_questions(message) and document_name:
            chunks = self.retriever.get_pdf_chunks(document_name)
        else:
            chunks = self.retriever.retrieve(message, source=document_name)
        if asks_for_questions(message):
            count_match = re.search(r"\b(\d+)\b", message)
            count = int(count_match.group(1)) if count_match else question_count
            if not chunks:
                return "Please upload a readable PDF first so I can generate questions from it."
            context = self._study_context(chunks)
            response = self.llm.ask([
                {"role": "system", "content": PDF_SYSTEM_PROMPT},
                {"role": "user", "content": question_prompt(context, difficulty, count)},
            ], temperature=0.4)
        elif chunks:
            extra = " Explain it simply with an example when useful." if asks_for_explanation(message) else ""
            response = self.llm.ask([
                {"role": "system", "content": PDF_SYSTEM_PROMPT},
                {"role": "user", "content": f"PDF passages:\n{self._format_context(chunks)}\n\nStudent question: {message}{extra}"},
            ])
        else:
            messages = [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}]
            messages.extend(self.history[-8:])
            messages.append({"role": "user", "content": message})
            response = self.llm.ask(messages)
        self.history.extend([{"role": "user", "content": message}, {"role": "assistant", "content": response}])
        return response

    def _web_answer(self, message):
        """Search the web, then ask the LLM to summarize the results with links."""
        results = search_web(message)
        if not results:
            return "I could not find useful web results for that request."
        return self.llm.ask([
            {"role": "system", "content": WEB_SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {message}\n\nWeb results:\n{results}"},
        ])

    @staticmethod
    def _format_context(chunks):
        """Format retrieved chunks with source metadata for an LLM prompt."""
        return "\n\n".join(f"[{item['source']}, page {item['page']}]\n{item['text']}" for item in chunks)

    def _study_context(self, chunks):
        """Build document-wide study context while keeping long PDFs manageable."""
        if len(chunks) <= 12:
            return self._format_context(chunks)

        summaries = []
        for start in range(0, len(chunks), 10):
            batch = chunks[start:start + 10]
            material = self._format_context(batch)
            summary = self.llm.ask([
                {
                    "role": "system",
                    "content": (
                        "You are preparing study notes from a PDF. Extract only substantive, "
                        "explained concepts, processes, evidence, and conclusions. Ignore page "
                        "labels, titles, headings without explanation, and administrative details. "
                        "Keep the notes concise and retain the supplied page citations. Do not add facts."
                    ),
                },
                {
                    "role": "user",
                    "content": "Extract up to 5 important study ideas from these passages:\n\n" + material,
                },
            ], temperature=0.1)
            summaries.append(summary)
        return "\n\n".join(summaries)
