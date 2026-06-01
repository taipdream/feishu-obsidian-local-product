from pathlib import Path

from feishu_obsidian_local_backend.source_converter import build_related_context_query, convert_inbox_note, parse_inbox_markdown


SAMPLE_INBOX = """# WeChat Capture - 情绪价值不是安慰，而是让人敢继续往前走

- Platform: wechat-official-account
- Captured at: 2026-05-29
- Original link: https://mp.weixin.qq.com/example-article
- Public account: 示例公众号
- Why it looked useful: 它把“情绪价值”从泛安慰转成更可商业化的陪伴机制。

## Pasted Summary or Body

第一段内容。
第二段内容。

## Immediate Notes

- 这和“轻陪伴式焦虑管理”产品方向高度相关。
- 值得提炼成机制标签，而不只是主题标签。
"""


def test_parse_inbox_markdown_extracts_core_fields():
    parsed = parse_inbox_markdown(SAMPLE_INBOX)
    assert parsed["title"] == "情绪价值不是安慰，而是让人敢继续往前走"
    assert parsed["platform"] == "wechat-official-account"
    assert parsed["source_url"] == "https://mp.weixin.qq.com/example-article"
    assert parsed["author"] == "示例公众号"
    assert parsed["captured_at"] == "2026-05-29"
    assert "第一段内容" in parsed["body"]
    assert "轻陪伴式焦虑管理" in parsed["notes"]


def test_parse_inbox_markdown_reads_author_field():
    markdown = """# Inbox Capture - 一个小红书案例

- Platform: xiaohongshu
- Captured at: 2026-05-30
- Original link: https://www.xiaohongshu.com/explore/abc
- Author: 某某博主
- Why it looked useful: 标题结构很强。

## Raw Content

正文内容。

## Immediate Notes

- 适合研究评论区承接。
"""
    parsed = parse_inbox_markdown(markdown)
    assert parsed["author"] == "某某博主"


def test_convert_inbox_note_creates_source_markdown(tmp_path):
    inbox_path = tmp_path / "capture.md"
    source_dir = tmp_path / "sources"
    inbox_path.write_text(SAMPLE_INBOX, encoding="utf-8")
    source_dir.mkdir()

    source_path = convert_inbox_note(inbox_path, source_dir)

    assert source_path.exists()
    content = source_path.read_text(encoding="utf-8")
    assert "type: source" in content
    assert "status: Reviewed" in content
    assert "platform: wechat-official-account" in content
    assert "source_url: https://mp.weixin.qq.com/example-article" in content
    assert "author: 示例公众号" in content
    assert "themes: [情绪价值]" in content
    assert "problems: []" in content
    assert "mechanisms: [轻量陪伴]" in content
    assert "# 情绪价值不是安慰，而是让人敢继续往前走" in content
    assert "## Why I Saved This" in content
    assert "它把“情绪价值”从泛安慰转成更可商业化的陪伴机制。" in content
    assert "## Key Excerpts" in content
    assert "第一段内容。" in content
    assert "## My Judgment" in content
    assert "轻陪伴式焦虑管理" in content
    assert "## Related Web Context" not in content


def test_convert_inbox_note_uses_non_colliding_filename_for_non_ascii_title(tmp_path):
    inbox_path = tmp_path / "capture.md"
    source_dir = tmp_path / "sources"
    inbox_path.write_text(SAMPLE_INBOX, encoding="utf-8")
    source_dir.mkdir()

    first = convert_inbox_note(inbox_path, source_dir)
    second = convert_inbox_note(inbox_path, source_dir)

    assert first.name == "source-2026-05-29.md"
    assert second.name == "source-2026-05-29-2.md"


def test_build_related_context_query_uses_title_reason_and_body():
    parsed = parse_inbox_markdown(SAMPLE_INBOX)
    query = build_related_context_query(parsed)
    assert "情绪价值不是安慰" in query
    assert "更可商业化的陪伴机制" in query
    assert "第一段内容" in query


def test_convert_inbox_note_includes_related_context_when_search_returns_results(tmp_path):
    inbox_path = tmp_path / "capture.md"
    source_dir = tmp_path / "sources"
    inbox_path.write_text(SAMPLE_INBOX, encoding="utf-8")
    source_dir.mkdir()

    source_path = convert_inbox_note(
        inbox_path,
        source_dir,
        tavily_api_key="tvly-test",
        search_fn=lambda query, key: [
            {
                "title": "Related Example",
                "url": "https://example.com/related",
                "snippet": "A related context snippet.",
            }
        ],
    )

    content = source_path.read_text(encoding="utf-8")
    assert "## Related Web Context" in content
    assert "Related Example" in content
    assert "https://example.com/related" in content
