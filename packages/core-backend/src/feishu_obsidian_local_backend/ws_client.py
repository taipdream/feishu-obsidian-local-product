import threading
from typing import Any, Dict

import lark_oapi as lark

from feishu_obsidian_local_backend.config import load_settings
from feishu_obsidian_local_backend.logging_utils import get_logger
from feishu_obsidian_local_backend.server import process_normalized_event


logger = get_logger(__name__)
SETTINGS = load_settings()


def build_webhook_like_payload_from_ws_event(data: Any) -> Dict[str, Any]:
    header = getattr(data, "header", None)
    event = getattr(data, "event", None)
    sender = getattr(event, "sender", None) if event else None
    sender_id = getattr(sender, "sender_id", None) if sender else None
    message = getattr(event, "message", None) if event else None

    return {
        "schema": getattr(data, "schema", ""),
        "header": {
            "event_id": getattr(header, "event_id", ""),
            "token": getattr(header, "token", ""),
            "create_time": getattr(header, "create_time", ""),
            "event_type": getattr(header, "event_type", ""),
            "tenant_key": getattr(header, "tenant_key", ""),
            "app_id": getattr(header, "app_id", ""),
        },
        "event": {
            "sender": {
                "sender_id": {
                    "open_id": getattr(sender_id, "open_id", ""),
                }
            },
            "message": {
                "message_id": getattr(message, "message_id", ""),
                "root_id": getattr(message, "root_id", ""),
                "parent_id": getattr(message, "parent_id", ""),
                "message_type": getattr(message, "message_type", ""),
                "content": getattr(message, "content", ""),
            },
        },
    }


def _process_ws_event_async(payload: Dict[str, Any]) -> None:
    try:
        process_normalized_event(payload)
    except Exception:
        logger.exception("failed to process websocket event")


def handle_message_event(data: Any) -> None:
    payload = build_webhook_like_payload_from_ws_event(data)
    threading.Thread(
        target=_process_ws_event_async,
        args=(payload,),
        daemon=True,
    ).start()


def create_ws_client() -> lark.ws.Client:
    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(handle_message_event)
        .build()
    )
    return lark.ws.Client(
        SETTINGS.feishu_app_id,
        SETTINGS.feishu_app_secret,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )


def main() -> None:
    client = create_ws_client()
    logger.info("starting feishu websocket client")
    client.start()


if __name__ == "__main__":
    main()
