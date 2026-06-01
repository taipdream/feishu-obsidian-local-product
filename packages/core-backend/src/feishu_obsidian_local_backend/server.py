from datetime import datetime
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from feishu_obsidian_local_backend.answer_generator import create_answer_note, build_answer_result
from feishu_obsidian_local_backend.config import load_settings
from feishu_obsidian_local_backend.crypto_utils import decrypt_feishu_payload
from feishu_obsidian_local_backend.feishu_client import download_message_image, send_reply_text
from feishu_obsidian_local_backend.idea_converter import create_idea_note
from feishu_obsidian_local_backend.logging_utils import get_logger
from feishu_obsidian_local_backend.message_parser import parse_message_event
from feishu_obsidian_local_backend.source_converter import convert_inbox_note
from feishu_obsidian_local_backend.vault_writer import build_note_filename, render_markdown, write_asset, write_note
from feishu_obsidian_local_backend.web_metadata import resolve_link_metadata
from feishu_obsidian_local_backend.answer_generator import build_answer_chat_reply


logger = get_logger(__name__)
app = FastAPI()
SETTINGS = load_settings()
INBOX_DIR = SETTINGS.inbox_dir
SOURCE_DIR = SETTINGS.source_dir
IDEAS_DIR = SETTINGS.ideas_dir
ANSWERS_DIR = SETTINGS.answers_dir
ASSETS_DIR = SETTINGS.assets_dir
THEMES_DIR = f"{SETTINGS.vault_root}/02 Themes"
PLAYBOOKS_DIR = f"{SETTINGS.vault_root}/04 Playbooks"
REVIEWS_DIR = f"{SETTINGS.vault_root}/05 Reviews"
DEBUG_EVENT_PATH = str(Path(__file__).resolve().parent / "last_event.json")
FOLLOW_UP_RE = ("这个", "那个", "这条", "那条", "这篇", "那篇", "这个团队", "那个团队", "这个方向", "那个方向")
RECEIVED_ACK_TEXT = "已收到，处理中。"


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def normalize_payload(payload: dict) -> dict:
    if "encrypt" in payload:
        if not SETTINGS.feishu_encrypt_key:
            raise ValueError("encrypt payload received but FEISHU_ENCRYPT_KEY is empty")
        return decrypt_feishu_payload(SETTINGS.feishu_encrypt_key, payload["encrypt"])
    return payload


def process_normalized_event(normalized: dict) -> dict:
    with open(DEBUG_EVENT_PATH, "w", encoding="utf-8") as fh:
        json.dump(normalized, fh, ensure_ascii=False, indent=2)

    parsed = parse_message_event(normalized)
    if parsed["content_type"] == "ignored":
        logger.info("ignored non-message event")
        return {"ok": True, "ignored": True}

    if parsed["message_id"]:
        _safe_send_reply_text(parsed["message_id"], RECEIVED_ACK_TEXT)

    inbox_path = None
    metadata = {"resolved_title": "", "resolved_author": "", "resolved_summary": ""}
    title = parsed["title_hint"] or parsed["raw_text"][:24] or parsed["content_type"]
    if parsed["should_distill"] or parsed["should_create_idea"]:
        timestamp = datetime.now().replace(microsecond=0).isoformat()
        raw_content = parsed["raw_text"]

        if parsed["content_type"] == "image" and parsed["image_key"] and parsed["message_id"]:
            asset_filename = build_note_filename(timestamp, "image").replace(".md", ".png")
            image_bytes = download_message_image(
                SETTINGS.feishu_app_id,
                SETTINGS.feishu_app_secret,
                parsed["message_id"],
                parsed["image_key"],
            )
            write_asset(ASSETS_DIR, asset_filename, image_bytes)
            raw_content = f"![feishu image](../Assets/{asset_filename})"
            title = "image"
        elif parsed["original_link"]:
            metadata = resolve_link_metadata(parsed["original_link"], parsed["platform"])

        if metadata["resolved_summary"] and not parsed["body_hint"]:
            raw_content = metadata["resolved_summary"]
        if parsed["body_hint"]:
            raw_content = parsed["body_hint"]
        if not parsed["title_hint"] and metadata["resolved_title"]:
            title = metadata["resolved_title"]
        author = parsed["author_hint"] or metadata["resolved_author"]

        filename = build_note_filename(timestamp, title)
        markdown = render_markdown(
            title=title,
            timestamp=timestamp,
            content_type=parsed["content_type"],
            platform=parsed["platform"],
            original_link=parsed["original_link"],
            resolved_title=metadata["resolved_title"],
            author=author,
            sender=parsed["sender"],
            message_id=parsed["message_id"],
            parent_id=parsed["parent_id"],
            root_id=parsed["root_id"],
            raw_content=raw_content,
        )
        inbox_path = write_note(INBOX_DIR, filename, markdown)
    source_path = None
    reply_text = ""
    if parsed["should_distill"] and inbox_path is not None:
        source_path = convert_inbox_note(
            inbox_path,
            Path(SOURCE_DIR),
            tavily_api_key=SETTINGS.tavily_api_key,
        )
        platform_label = parsed["platform"] or "unknown"
        title_label = title or metadata["resolved_title"] or "未命名内容"
        if parsed["should_create_idea"]:
            reply_text = f"已归档并创建想法卡。\n平台：{platform_label}\n标题：{title_label}"
        else:
            reply_text = f"已归档。\n平台：{platform_label}\n标题：{title_label}"
    if parsed["should_create_idea"]:
        if source_path is not None:
            create_idea_note(parsed["raw_text"], source_path, Path(IDEAS_DIR))
        else:
            reply_text = "想法已收到，但当前没有可关联的资料卡。请用 #save 或附链接后再创建。"
    if parsed["should_answer"]:
        analysis_question, context_summary = _build_follow_up_context(parsed)
        answer_result = build_answer_result(
            parsed["raw_text"],
            Path(REVIEWS_DIR),
            sources_dir=Path(SOURCE_DIR),
            ideas_dir=Path(IDEAS_DIR),
            themes_dir=Path(THEMES_DIR),
            playbooks_dir=Path(PLAYBOOKS_DIR),
            tavily_api_key=SETTINGS.tavily_api_key,
            analysis_question=analysis_question or None,
            context_summary=context_summary,
        )
        if parsed["should_save_answer"]:
            create_answer_note(
                parsed["raw_text"],
                Path(REVIEWS_DIR),
                Path(ANSWERS_DIR),
                sources_dir=Path(SOURCE_DIR),
                ideas_dir=Path(IDEAS_DIR),
                themes_dir=Path(THEMES_DIR),
                playbooks_dir=Path(PLAYBOOKS_DIR),
                tavily_api_key=SETTINGS.tavily_api_key,
                analysis_question=analysis_question or None,
                context_summary=context_summary,
            )
        reply_text = build_answer_chat_reply(
            answer_result["direct_notes"],
            answer_result["signal_notes"],
            answer_result["web_fallback_items"],
        )
    elif parsed["content_type"] == "image":
        reply_text = "已保存图片并归档。"
    elif not parsed["should_distill"] and not parsed["should_create_idea"]:
        reply_text = "已收到。"
    if reply_text and parsed["message_id"]:
        _safe_send_reply_text(parsed["message_id"], reply_text)
    if inbox_path is not None:
        logger.info("archived %s", inbox_path.name)
    return {"ok": True}


def _safe_send_reply_text(message_id: str, text: str) -> None:
    try:
        send_reply_text(
            SETTINGS.feishu_app_id,
            SETTINGS.feishu_app_secret,
            message_id,
            text,
        )
    except Exception:
        logger.exception("failed to send feishu reply")


def _extract_inbox_bullet(markdown: str, label: str) -> str:
    prefix = f"- {label}:"
    for line in markdown.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def _extract_inbox_section(markdown: str, heading: str) -> str:
    marker = f"## {heading}"
    lines = markdown.splitlines()
    collected = []
    capture = False
    for line in lines:
        if line.strip() == marker:
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture:
            collected.append(line)
    return "\n".join(collected).strip()


def _find_inbox_note_by_message_id(message_id: str) -> Optional[Path]:
    if not message_id:
        return None
    for path in sorted(Path(INBOX_DIR).glob("*.md"), reverse=True):
        markdown = path.read_text(encoding="utf-8")
        if _extract_inbox_bullet(markdown, "Message ID") == message_id:
            return path
    return None


def _build_follow_up_context(parsed: dict) -> tuple[str, str]:
    if not parsed["should_answer"]:
        return "", ""
    raw_text = parsed["raw_text"].strip()
    if not raw_text or not any(token in raw_text for token in FOLLOW_UP_RE):
        return "", ""

    context_note = _find_inbox_note_by_message_id(parsed.get("parent_id", "")) or _find_inbox_note_by_message_id(parsed.get("root_id", ""))
    if context_note is None:
        return "", ""

    markdown = context_note.read_text(encoding="utf-8")
    title = context_note.stem
    for line in markdown.splitlines():
        if line.startswith("# Inbox Capture - "):
            title = line.replace("# Inbox Capture - ", "", 1).strip()
            break
    link = _extract_inbox_bullet(markdown, "Original link")
    platform = _extract_inbox_bullet(markdown, "Platform")
    raw_content = _extract_inbox_section(markdown, "Raw Content")
    context_parts = [
        f"上一条内容标题：{title}",
        f"平台：{platform}" if platform else "",
        f"链接：{link}" if link else "",
        f"内容：{raw_content}" if raw_content else "",
    ]
    context_summary = "\n".join(f"- {part}" for part in context_parts if part)
    analysis_question = f"{context_summary}\n- 当前追问：{raw_text}"
    return analysis_question, context_summary


@app.post("/feishu/events")
async def feishu_events(request: Request) -> dict:
    payload = await request.json()
    normalized = normalize_payload(payload)

    if normalized.get("type") == "url_verification":
        if SETTINGS.feishu_verification_token and normalized.get("token") != SETTINGS.feishu_verification_token:
            return JSONResponse(status_code=403, content={"ok": False, "reason": "invalid token"})
        return {"challenge": normalized["challenge"]}

    if SETTINGS.feishu_verification_token and normalized.get("token"):
        if normalized["token"] != SETTINGS.feishu_verification_token:
            return JSONResponse(status_code=403, content={"ok": False, "reason": "invalid token"})
    return process_normalized_event(normalized)
