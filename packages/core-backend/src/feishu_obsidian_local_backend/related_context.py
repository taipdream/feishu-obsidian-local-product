from typing import Callable, List

import httpx


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def tavily_search(query: str, api_key: str) -> List[dict]:
    response = httpx.post(
        TAVILY_SEARCH_URL,
        json={
            "api_key": api_key,
            "query": query,
            "max_results": 3,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
        },
        timeout=12.0,
    )
    response.raise_for_status()
    payload = response.json()
    results = payload.get("results", [])
    normalized = []
    for item in results:
        normalized.append(
            {
                "title": item.get("title", "").strip(),
                "url": item.get("url", "").strip(),
                "snippet": item.get("content", "").strip(),
            }
        )
    return normalized


def maybe_collect_related_context(
    query: str,
    tavily_api_key: str,
    search_fn: Callable[[str, str], List[dict]],
) -> List[dict]:
    if not tavily_api_key.strip() or not query.strip():
        return []
    try:
        return search_fn(query, tavily_api_key)
    except httpx.HTTPError:
        return []
    except ValueError:
        return []


def build_related_context_section(items: List[dict]) -> str:
    if not items:
        return ""
    lines = ["## Related Web Context", ""]
    for item in items:
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        snippet = item.get("snippet", "").strip()
        lines.append(f"- {title}")
        if url:
            lines.append(f"  - {url}")
        if snippet:
            lines.append(f"  - {snippet}")
    return "\n".join(lines)
