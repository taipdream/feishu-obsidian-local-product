from feishu_obsidian_local_backend.vault_writer import build_note_filename, render_markdown, write_asset


def test_build_note_filename_for_text():
    name = build_note_filename("2026-05-29T12:00:00", "女性情绪价值产品")
    assert name.startswith("feishu-2026-05-29-120000-")
    assert name.endswith(".md")


def test_render_markdown_includes_required_sections():
    markdown = render_markdown(
        title="测试标题",
        timestamp="2026-05-29T12:00:00",
        content_type="text-link",
        platform="wechat",
        original_link="https://example.com",
        resolved_title="测试网页标题",
        author="示例作者",
        sender="ou_x",
        message_id="om_1",
        parent_id="om_0",
        root_id="om_root",
        raw_content="https://example.com 很适合研究标题套路",
    )
    assert "# Inbox Capture - 测试标题" in markdown
    assert "- Source: feishu-bot" in markdown
    assert "- Platform: wechat" in markdown
    assert "- Resolved title: 测试网页标题" in markdown
    assert "- Author: 示例作者" in markdown
    assert "- Message ID: om_1" in markdown
    assert "- Parent ID: om_0" in markdown
    assert "- Root ID: om_root" in markdown
    assert "## Raw Content" in markdown


def test_write_asset_creates_file(tmp_path):
    path = write_asset(str(tmp_path), "sample.png", b"abc")
    assert path.name == "sample.png"
    assert path.read_bytes() == b"abc"
