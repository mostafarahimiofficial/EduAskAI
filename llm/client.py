"""A small OpenAI-compatible client configured for Groq."""

from openai import APIConnectionError, APIStatusError, OpenAI

from utils.config import BASE_URL, GROQ_API_KEY, MODEL_NAME


class LLMClient:
    """Send chat requests to Groq through its OpenAI-compatible endpoint."""

    def __init__(self):
        """Create the API client without exposing an API key in source code.

        Raises:
            ValueError: If GROQ_API_KEY is missing from the environment.
        """
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")
        self.client = OpenAI(api_key=GROQ_API_KEY, base_url=BASE_URL)

    def ask(self, messages, temperature=0.3):
        """Generate a response for OpenAI-style chat messages.

        Args:
            messages: List of dictionaries with role and content keys.
            temperature: Creativity setting for the model.

        Returns:
            The response text.

        Raises:
            RuntimeError: If the AI service cannot complete the request.
        """
        try:
            result = self.client.chat.completions.create(
                model=MODEL_NAME, messages=messages, temperature=temperature
            )
            return result.choices[0].message.content.strip()
        except APIConnectionError as error:
            raise RuntimeError("Unable to reach Groq. Check your Internet connection and try again.") from error
        except APIStatusError as error:
            message = error.message or "Groq rejected the request."
            raise RuntimeError(f"Groq API error ({error.status_code}): {message}") from error
        except Exception as error:
            raise RuntimeError(f"Unable to complete the AI request: {error}") from error
