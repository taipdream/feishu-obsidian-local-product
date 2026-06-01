import json
from typing import Optional

import httpx


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    response = httpx.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 0:
        raise RuntimeError(payload.get("msg", "failed to get tenant_access_token"))
    return payload["tenant_access_token"]


def download_message_image(
    app_id: str,
    app_secret: str,
    message_id: str,
    image_key: str,
) -> bytes:
    token = get_tenant_access_token(app_id, app_secret)
    response = httpx.get(
        f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/resources/{image_key}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        params={"type": "image"},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.content


def send_reply_text(
    app_id: str,
    app_secret: str,
    message_id: str,
    text: str,
) -> None:
    token = get_tenant_access_token(app_id, app_secret)
    response = httpx.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        },
        timeout=30.0,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise httpx.HTTPStatusError(
            f"{exc}. response={response.text}",
            request=exc.request,
            response=exc.response,
        ) from exc
