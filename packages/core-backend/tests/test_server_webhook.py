import base64
import hashlib
import json
import subprocess

from fastapi.testclient import TestClient

import feishu_obsidian_local_backend.server as server
from feishu_obsidian_local_backend.server import app


def test_healthcheck():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_creates_markdown_note(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    inbox_dir.mkdir()
    source_dir.mkdir()
    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    sent = []
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: sent.append(text))
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "Example Domain", "resolved_author": "", "resolved_summary": ""},
    )
    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_1",
                    "message_type": "text",
                    "content": "{\"text\":\"https://example.com 一个新灵感\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    inbox_files = list(inbox_dir.glob("*.md"))
    source_files = list(source_dir.glob("*.md"))
    assert len(inbox_files) == 1
    assert len(source_files) == 1
    inbox_content = inbox_files[0].read_text(encoding="utf-8")
    source_content = source_files[0].read_text(encoding="utf-8")
    assert "https://example.com" in inbox_content
    assert "- Platform: generic-web" in inbox_content
    assert "- Resolved title: Example Domain" in inbox_content
    assert "type: source" in source_content
    assert sent[0] == server.RECEIVED_ACK_TEXT
    assert "已归档" in sent[1]
    assert "Example Domain" in sent[1]


def test_webhook_distill_creates_inbox_and_source_notes(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    inbox_dir.mkdir()
    source_dir.mkdir()
    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "Example Domain", "resolved_author": "", "resolved_summary": ""},
    )
    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_2",
                    "message_type": "text",
                    "content": "{\"text\":\"#distill\\nhttps://example.com 一个新灵感\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    inbox_files = list(inbox_dir.glob("*.md"))
    source_files = list(source_dir.glob("*.md"))
    assert len(inbox_files) == 1
    assert len(source_files) == 1
    inbox_content = inbox_files[0].read_text(encoding="utf-8")
    source_content = source_files[0].read_text(encoding="utf-8")
    assert "#distill" not in inbox_content
    assert "#distill" not in source_content
    assert "type: source" in source_content
    assert "status: Reviewed" in source_content


def test_webhook_idea_creates_inbox_source_and_idea_notes(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    inbox_dir.mkdir()
    source_dir.mkdir()
    ideas_dir.mkdir()
    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "IDEAS_DIR", str(ideas_dir))
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "", "resolved_author": "", "resolved_summary": ""},
    )
    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_3",
                    "message_type": "text",
                    "content": "{\"text\":\"#idea\\n做一个女性成长轻陪伴产品\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    inbox_files = list(inbox_dir.glob("*.md"))
    source_files = list(source_dir.glob("*.md"))
    idea_files = list(ideas_dir.glob("*.md"))
    assert len(inbox_files) == 1
    assert len(source_files) == 1
    assert len(idea_files) == 1
    idea_content = idea_files[0].read_text(encoding="utf-8")
    assert "type: idea" in idea_content
    assert "stage: exploring" in idea_content
    assert "做一个女性成长轻陪伴产品" in idea_content
    assert "[[01 Sources/" in idea_content


def test_webhook_question_creates_inbox_and_answer_note(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    answers_dir = tmp_path / "answers"
    reviews_dir = tmp_path / "reviews"
    inbox_dir.mkdir()
    source_dir.mkdir()
    ideas_dir.mkdir()
    answers_dir.mkdir()
    reviews_dir.mkdir()

    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "IDEAS_DIR", str(ideas_dir))
    monkeypatch.setattr(server, "ANSWERS_DIR", str(answers_dir))
    monkeypatch.setattr(server, "REVIEWS_DIR", str(reviews_dir))
    monkeypatch.setattr(server, "THEMES_DIR", str(tmp_path / "themes"))
    monkeypatch.setattr(server, "PLAYBOOKS_DIR", str(tmp_path / "playbooks"))
    (tmp_path / "themes").mkdir()
    (tmp_path / "playbooks").mkdir()
    sent = []
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: sent.append(text))
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "", "resolved_author": "", "resolved_summary": ""},
    )

    (reviews_dir / "review-2026-05-30.md").write_text(
        """# Weekly Review - 2026-05-30

## Pattern Signals

- Themes: 女性成长 (2), 情绪价值 (2)
- Problems: 身份焦虑 (2)
- Mechanisms: 轻量陪伴 (1)
""",
        encoding="utf-8",
    )
    (reviews_dir / "opportunities-2026-05-30.md").write_text(
        """# Opportunity Brief - 2026-05-30

## Direction 1

- Focus: 女性成长 x 身份焦虑
- Thesis: 围绕 女性成长 场景下的 身份焦虑，用 轻量陪伴 做更低门槛的切入。
- Next step: 访谈 3 位目标用户。
""",
        encoding="utf-8",
    )

    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_4",
                    "message_type": "text",
                    "content": "{\"text\":\"我该不该先做女性成长轻陪伴产品？\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    assert len(list(inbox_dir.glob("*.md"))) == 0
    assert len(list(source_dir.glob("*.md"))) == 0
    assert sent[0] == server.RECEIVED_ACK_TEXT
    assert "当前判断" in sent[1]


def test_webhook_asksave_question_creates_answer_note_without_inbox(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    answers_dir = tmp_path / "answers"
    reviews_dir = tmp_path / "reviews"
    inbox_dir.mkdir()
    source_dir.mkdir()
    ideas_dir.mkdir()
    answers_dir.mkdir()
    reviews_dir.mkdir()

    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "IDEAS_DIR", str(ideas_dir))
    monkeypatch.setattr(server, "ANSWERS_DIR", str(answers_dir))
    monkeypatch.setattr(server, "REVIEWS_DIR", str(reviews_dir))
    monkeypatch.setattr(server, "THEMES_DIR", str(tmp_path / "themes"))
    monkeypatch.setattr(server, "PLAYBOOKS_DIR", str(tmp_path / "playbooks"))
    (tmp_path / "themes").mkdir()
    (tmp_path / "playbooks").mkdir()
    sent = []
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: sent.append(text))
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "", "resolved_author": "", "resolved_summary": ""},
    )
    (reviews_dir / "review-2026-05-30.md").write_text(
        """# Weekly Review - 2026-05-30

## Pattern Signals

- Themes: 女性成长 (2)
- Problems: 身份焦虑 (2)
- Mechanisms: 轻量陪伴 (1)
""",
        encoding="utf-8",
    )
    (reviews_dir / "opportunities-2026-05-30.md").write_text(
        """# Opportunity Brief - 2026-05-30

## Direction 1

- Focus: 女性成长 x 身份焦虑
- Thesis: 围绕 女性成长 场景下的 身份焦虑，用 轻量陪伴 做更低门槛的切入。
- Next step: 访谈 3 位目标用户。
""",
        encoding="utf-8",
    )

    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_4b",
                    "message_type": "text",
                    "content": "{\"text\":\"#asksave\\n我该不该先做女性成长轻陪伴产品？\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    assert len(list(inbox_dir.glob("*.md"))) == 0
    assert len(list(source_dir.glob("*.md"))) == 0
    answer_files = list(answers_dir.glob("*.md"))
    assert len(answer_files) == 1
    answer_content = answer_files[0].read_text(encoding="utf-8")
    assert "我该不该先做女性成长轻陪伴产品？" in answer_content
    assert sent[0] == server.RECEIVED_ACK_TEXT
    assert "当前判断" in sent[1]


def test_webhook_creates_image_note_and_asset(tmp_path, monkeypatch):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    inbox_dir.mkdir()
    source_dir.mkdir()
    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "ASSETS_DIR", str(assets_dir))
    monkeypatch.setattr(server, "download_message_image", lambda app_id, app_secret, message_id, image_key: b"pngdata")
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "", "resolved_author": "", "resolved_summary": ""},
    )
    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_123",
                    "message_type": "image",
                    "content": "{\"image_key\":\"img_123\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    note_files = list(inbox_dir.glob("*.md"))
    source_files = list(source_dir.glob("*.md"))
    asset_files = list(assets_dir.glob("*.png"))
    assert len(note_files) == 1
    assert len(source_files) == 1
    assert len(asset_files) == 1
    assert "![feishu image]" in note_files[0].read_text(encoding="utf-8")


def test_webhook_wechat_link_uses_resolved_author_and_summary(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    inbox_dir.mkdir()
    source_dir.mkdir()
    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {
            "resolved_title": "真正的微信文章标题",
            "resolved_author": "示例公众号",
            "resolved_summary": "这是文章摘要。",
        },
    )
    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_5",
                    "message_type": "text",
                    "content": "{\"text\":\"https://mp.weixin.qq.com/s/example\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    inbox_files = list(inbox_dir.glob("*.md"))
    source_files = list(source_dir.glob("*.md"))
    assert len(inbox_files) == 1
    assert len(source_files) == 1
    inbox_content = inbox_files[0].read_text(encoding="utf-8")
    source_content = source_files[0].read_text(encoding="utf-8")
    assert "# Inbox Capture - 真正的微信文章标题" in inbox_content
    assert "- Author: 示例公众号" in inbox_content
    assert "这是文章摘要。" in inbox_content
    assert "author: 示例公众号" in source_content
    assert "## Key Excerpts" in source_content
    assert "这是文章摘要。" in source_content


def test_webhook_follow_up_question_uses_parent_context(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    answers_dir = tmp_path / "answers"
    reviews_dir = tmp_path / "reviews"
    themes_dir = tmp_path / "themes"
    playbooks_dir = tmp_path / "playbooks"
    for path in [inbox_dir, source_dir, ideas_dir, answers_dir, reviews_dir, themes_dir, playbooks_dir]:
        path.mkdir()

    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "IDEAS_DIR", str(ideas_dir))
    monkeypatch.setattr(server, "ANSWERS_DIR", str(answers_dir))
    monkeypatch.setattr(server, "REVIEWS_DIR", str(reviews_dir))
    monkeypatch.setattr(server, "THEMES_DIR", str(themes_dir))
    monkeypatch.setattr(server, "PLAYBOOKS_DIR", str(playbooks_dir))
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: None)
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "成都CPI运营团队", "resolved_author": "", "resolved_summary": ""},
    )

    review_text = """# Weekly Review - 2026-05-30

## Pattern Signals

- Themes: 轻创业 (2)
- Problems: 身份焦虑 (2)
- Mechanisms: 轻量陪伴 (2)
"""
    (reviews_dir / "review-2026-05-30.md").write_text(review_text, encoding="utf-8")
    (reviews_dir / "opportunities-2026-05-30.md").write_text(
        """# Opportunity Brief - 2026-05-30

## Direction 1

- Focus: 轻创业 x 陪伴式运营
- Thesis: 先判断团队打法，再决定是否借鉴。
- Next step: 找到 3 条直接案例。
""",
        encoding="utf-8",
    )

    parent_markdown = server.render_markdown(
        title="成都CPI运营团队",
        timestamp="2026-05-30T22:20:00",
        content_type="text-link",
        platform="generic-web",
        original_link="https://example.com/cpi",
        resolved_title="成都CPI运营团队",
        author="",
        sender="ou_x",
        message_id="om_parent",
        parent_id="",
        root_id="om_parent",
        raw_content="成都CPI运营团队，主要在做内容运营和社群承接。",
    )
    server.write_note(str(inbox_dir), "feishu-parent.md", parent_markdown)

    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "parent_id": "om_parent",
                "root_id": "om_parent",
                "message": {
                    "message_id": "om_followup",
                    "message_type": "text",
                    "content": "{\"text\":\"你对这个怎么看？\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    assert list(answers_dir.glob("*.md")) == []


def _encrypt_payload(payload: dict, encrypt_key: str) -> str:
    raw = json.dumps(payload).encode("utf-8")
    iv = b"0123456789abcdef"
    key = hashlib.sha256(encrypt_key.encode("utf-8")).digest()
    result = subprocess.run(
        [
            "openssl",
            "enc",
            "-aes-256-cbc",
            "-K",
            key.hex(),
            "-iv",
            iv.hex(),
        ],
        input=raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    encrypted = result.stdout
    return base64.b64encode(iv + encrypted).decode("utf-8")


def test_url_verification_plaintext():
    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "type": "url_verification",
            "token": server.SETTINGS.feishu_verification_token,
            "challenge": "abc123",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"challenge": "abc123"}


def test_url_verification_encrypted():
    client = TestClient(server.app)
    original_settings = server.SETTINGS
    try:
        server.SETTINGS = server.SETTINGS.__class__(
            feishu_app_id=original_settings.feishu_app_id,
            feishu_app_secret=original_settings.feishu_app_secret,
            feishu_encrypt_key="test-encrypt-key",
            tavily_api_key=original_settings.tavily_api_key,
            vault_root=original_settings.vault_root,
            inbox_dir=original_settings.inbox_dir,
            source_dir=original_settings.source_dir,
            ideas_dir=original_settings.ideas_dir,
            answers_dir=original_settings.answers_dir,
            assets_dir=original_settings.assets_dir,
            ingest_port=original_settings.ingest_port,
            feishu_verification_token=original_settings.feishu_verification_token,
        )
        body = {
            "type": "url_verification",
            "token": server.SETTINGS.feishu_verification_token,
            "challenge": "enc123",
        }
        encrypted = _encrypt_payload(body, server.SETTINGS.feishu_encrypt_key)
        response = client.post("/feishu/events", json={"encrypt": encrypted})
        assert response.status_code == 200
        assert response.json() == {"challenge": "enc123"}
    finally:
        server.SETTINGS = original_settings


def test_webhook_ignores_non_message_events(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "INBOX_DIR", str(tmp_path))
    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "schema": "2.0",
            "header": {
                "event_type": "im.chat.access_event.bot_p2p_chat_entered_v1",
                "token": server.SETTINGS.feishu_verification_token,
            },
            "event": {
                "chat_id": "oc_x",
                "operator_id": {"open_id": "ou_x"},
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True, "ignored": True}
    files = list(tmp_path.glob("*.md"))
    assert files == []


def test_webhook_continues_when_ack_reply_fails(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    inbox_dir.mkdir()
    source_dir.mkdir()
    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))

    calls = {"count": 0}

    def flaky_send_reply(app_id, app_secret, message_id, text):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("ack failed")

    monkeypatch.setattr(server, "send_reply_text", flaky_send_reply)
    monkeypatch.setattr(
        server,
        "resolve_link_metadata",
        lambda link, platform: {"resolved_title": "Example Domain", "resolved_author": "", "resolved_summary": ""},
    )

    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_6",
                    "message_type": "text",
                    "content": "{\"text\":\"https://example.com 一个新灵感\"}",
                },
            }
        },
    )

    assert response.status_code == 200
    assert len(list(inbox_dir.glob("*.md"))) == 1
    assert len(list(source_dir.glob("*.md"))) == 1


def test_webhook_plain_text_chat_does_not_persist(tmp_path, monkeypatch):
    inbox_dir = tmp_path / "inbox"
    source_dir = tmp_path / "sources"
    inbox_dir.mkdir()
    source_dir.mkdir()
    sent = []
    monkeypatch.setattr(server, "INBOX_DIR", str(inbox_dir))
    monkeypatch.setattr(server, "SOURCE_DIR", str(source_dir))
    monkeypatch.setattr(server, "send_reply_text", lambda app_id, app_secret, message_id, text: sent.append(text))

    client = TestClient(server.app)
    response = client.post(
        "/feishu/events",
        json={
            "event": {
                "sender": {"sender_id": {"open_id": "ou_x"}},
                "message": {
                    "message_id": "om_text_chat",
                    "message_type": "text",
                    "content": "{\"text\":\"收到\"}",
                },
            }
        },
    )
    assert response.status_code == 200
    assert list(inbox_dir.glob("*.md")) == []
    assert list(source_dir.glob("*.md")) == []
    assert sent[0] == server.RECEIVED_ACK_TEXT
