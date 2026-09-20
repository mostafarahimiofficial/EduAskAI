"""A lightweight DuckDuckGo web-search tool."""

from duckduckgo_search import DDGS


def search_web(query, max_results=4):
    """Search the web and return concise source snippets.

    Args:
        query: Search phrase.
        max_results: Maximum results to include.

    Returns:
        Formatted search results, or an empty string when none are found.
    """
    try:
        results = DDGS().text(query, max_results=max_results)
        return "\n\n".join(
            f"Source: {item.get('title', 'Untitled')}\n{item.get('body', '')}\n{item.get('href', '')}"
            for item in results
        )
    except Exception as error:
        raise RuntimeError("Web search is unavailable. Check your Internet connection.") from error
