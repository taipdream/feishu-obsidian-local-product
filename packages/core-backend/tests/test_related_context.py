import httpx

import feishu_obsidian_local_backend.related_context as related_context
from feishu_obsidian_local_backend.related_context import build_related_context_section, maybe_collect_related_context, tavily_search


def test_maybe_collect_related_context_gracefully_skips_without_key():
    result = maybe_collect_related_context(
        query="女性成长轻陪伴",
        tavily_api_key="",
        search_fn=lambda query, key: [{"title": "x"}],
    )
    assert result == []


def test_build_related_context_section_formats_results():
    items = [
        {
            "title": "Example 1",
            "url": "https://example.com/1",
            "snippet": "First snippet",
        },
        {
            "title": "Example 2",
            "url": "https://example.com/2",
            "snippet": "Second snippet",
        },
    ]
    section = build_related_context_section(items)
    assert "## Related Web Context" in section
    assert "Example 1" in section
    assert "https://example.com/2" in section


def test_build_related_context_section_returns_empty_string_for_no_results():
    assert build_related_context_section([]) == ""


def test_maybe_collect_related_context_gracefully_skips_on_http_error():
    def raise_error(query, key):
        raise httpx.ConnectError("boom")

    result = maybe_collect_related_context(
        query="女性成长轻陪伴",
        tavily_api_key="tvly-test",
        search_fn=raise_error,
    )
    assert result == []


def test_tavily_search_normalizes_response(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": [
                    {
                        "title": "Example Result",
                        "url": "https://example.com/item",
                        "content": "Useful summary",
                    }
                ]
            }

    monkeypatch.setattr(related_context.httpx, "post", lambda *args, **kwargs: DummyResponse())

    results = tavily_search("test query", "tvly-test")

    assert results == [
        {
            "title": "Example Result",
            "url": "https://example.com/item",
            "snippet": "Useful summary",
        }
    ]
