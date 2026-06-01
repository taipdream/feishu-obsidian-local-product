import json

import httpx

import feishu_obsidian_local_backend.feishu_client as feishu_client
from feishu_obsidian_local_backend.feishu_client import send_reply_text


def test_send_reply_text_escapes_newlines(monkeypatch):
    calls = []

    def fake_post(url, json=None, headers=None, timeout=None):
        calls.append(
            {
                "url": url,
                "json": json,
                "headers": headers,
                "timeout": timeout,
            }
        )
        if "tenant_access_token" in url:
            return httpx.Response(
                200,
                json={"code": 0, "tenant_access_token": "token"},
                request=httpx.Request("POST", url),
            )
        return httpx.Response(200, json={"code": 0}, request=httpx.Request("POST", url))

    monkeypatch.setattr(feishu_client.httpx, "post", fake_post)

    send_reply_text("app-id", "app-secret", "om_123", "第一行\n第二行")

    reply_call = calls[-1]
    assert reply_call["url"].endswith("/im/v1/messages/om_123/reply")
    assert json.loads(reply_call["json"]["content"]) == {"text": "第一行\n第二行"}
