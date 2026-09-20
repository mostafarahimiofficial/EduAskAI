"""Small decision helpers for the agent's available tools."""

CURRENT_INFORMATION_WORDS = (
    "latest", "today", "current", "news", "price", "weather", "recent",
    "find information", "search the internet", "online",
)


def needs_web_search(message):
    """Return whether a message likely requests current external information."""
    message = message.lower()
    return any(word in message for word in CURRENT_INFORMATION_WORDS)


def asks_for_questions(message):
    """Return whether a message asks to generate study questions."""
    message = message.lower()
    return "question" in message and any(word in message for word in ("generate", "create", "give me"))


def asks_for_explanation(message):
    """Return whether a message asks for a simple concept explanation."""
    message = message.lower()
    return "explain" in message or "simple explanation" in message
