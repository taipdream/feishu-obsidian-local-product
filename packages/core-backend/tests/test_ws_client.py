from types import SimpleNamespace

from feishu_obsidian_local_backend.ws_client import build_webhook_like_payload_from_ws_event


def test_build_webhook_like_payload_from_ws_event_preserves_message_fields():
    data = SimpleNamespace(
        schema="2.0",
        header=SimpleNamespace(
            event_id="evt_1",
            token="token_1",
            create_time="1710000000",
            event_type="im.message.receive_v1",
            tenant_key="tenant_x",
            app_id="cli_x",
        ),
        event=SimpleNamespace(
            sender=SimpleNamespace(
                sender_id=SimpleNamespace(open_id="ou_x"),
            ),
            message=SimpleNamespace(
                message_id="om_1",
                root_id="om_root",
                parent_id="om_parent",
                message_type="text",
                content='{"text":"你对这个怎么看？"}',
            ),
        ),
    )

    payload = build_webhook_like_payload_from_ws_event(data)

    assert payload["schema"] == "2.0"
    assert payload["header"]["event_type"] == "im.message.receive_v1"
    assert payload["event"]["sender"]["sender_id"]["open_id"] == "ou_x"
    assert payload["event"]["message"]["message_id"] == "om_1"
    assert payload["event"]["message"]["root_id"] == "om_root"
    assert payload["event"]["message"]["parent_id"] == "om_parent"
    assert payload["event"]["message"]["content"] == '{"text":"你对这个怎么看？"}'
