import feishu_obsidian_local_backend.web_metadata as web_metadata
from feishu_obsidian_local_backend.web_metadata import extract_title_from_html, resolve_link_metadata


def test_extract_title_from_html_decodes_entities():
    html = "<html><head><title>Women &amp; Growth</title></head></html>"
    assert extract_title_from_html(html) == "Women & Growth"


def test_resolve_link_metadata_ignores_unsupported_platforms():
    assert resolve_link_metadata("https://v.douyin.com/abc123/", "douyin") == {
        "resolved_title": "",
        "resolved_author": "",
        "resolved_summary": "",
    }


def test_resolve_link_metadata_supports_xiaohongshu(monkeypatch):
    class DummyResponse:
        text = "<html><head><title>小红书标题示例</title></head></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(web_metadata.httpx, "get", lambda *args, **kwargs: DummyResponse())
    metadata = resolve_link_metadata("https://www.xiaohongshu.com/explore/abc", "xiaohongshu")
    assert metadata == {
        "resolved_title": "小红书标题示例",
        "resolved_author": "",
        "resolved_summary": "",
    }


def test_resolve_link_metadata_fetches_title(monkeypatch):
    class DummyResponse:
        text = "<html><head><title>Example Domain</title></head></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(web_metadata.httpx, "get", lambda *args, **kwargs: DummyResponse())
    metadata = resolve_link_metadata("https://example.com", "generic-web")
    assert metadata == {
        "resolved_title": "Example Domain",
        "resolved_author": "",
        "resolved_summary": "",
    }


def test_resolve_link_metadata_extracts_wechat_article_fields(monkeypatch):
    class DummyResponse:
        text = """
        <html>
          <head>
            <title>微信文章标题</title>
            <meta property="og:title" content="真正的微信文章标题" />
            <meta name="author" content="示例公众号" />
            <meta property="og:description" content="文章摘要示例" />
          </head>
          <body></body>
        </html>
        """

        def raise_for_status(self):
            return None

    monkeypatch.setattr(web_metadata.httpx, "get", lambda *args, **kwargs: DummyResponse())
    metadata = resolve_link_metadata("https://mp.weixin.qq.com/s/example", "wechat-official-account")
    assert metadata["resolved_title"] == "真正的微信文章标题"
    assert metadata["resolved_author"] == "示例公众号"
    assert metadata["resolved_summary"] == "文章摘要示例"


def test_resolve_link_metadata_handles_fetch_failure(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(web_metadata.httpx, "get", raise_error)
    metadata = resolve_link_metadata("https://example.com", "generic-web")
    assert metadata == {
        "resolved_title": "",
        "resolved_author": "",
        "resolved_summary": "",
    }
