import json
import re
from urllib.parse import urlparse


LINK_RE = re.compile(r"https?://\S+")
DISTILL_RE = re.compile(r"(?m)^\s*#distill\s*$")
IDEA_RE = re.compile(r"(?m)^\s*#idea\s*$")
SAVE_RE = re.compile(r"(?m)^\s*#save\s*$")
ASKSAVE_RE = re.compile(r"(?m)^\s*#asksave\s*$")
QUESTION_PREFIXES = ("我该不该", "怎么", "如何", "为什么", "有没有", "帮我分析", "给我建议")
FIELD_PATTERNS = {
    "title_hint": re.compile(r"^(?:标题|题目|小红书标题)\s*[：:]\s*(.+?)\s*$", re.MULTILINE),
    "author_hint": re.compile(r"^(?:公众号|公众号名|作者|博主)\s*[：:]\s*(.+?)\s*$", re.MULTILINE),
    "original_link": re.compile(r"^(?:链接|原链接)\s*[：:]\s*(https?://\S+)\s*$", re.MULTILINE),
}


def detect_platform(link: str) -> str:
    if not link:
        return "plain-text"

    hostname = urlparse(link).netloc.lower()
    if "mp.weixin.qq.com" in hostname:
        return "wechat-official-account"
    if "xiaohongshu.com" in hostname or "xhslink.com" in hostname:
        return "xiaohongshu"
    if "douyin.com" in hostname:
        return "douyin"
    return "generic-web"


def detect_question(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.endswith(("？", "?")):
        return True
    return stripped.startswith(QUESTION_PREFIXES)


def extract_structured_fields(text: str) -> dict:
    result = {
        "title_hint": "",
        "author_hint": "",
        "original_link": "",
        "body_hint": text.strip(),
    }
    working = text
    for key, pattern in FIELD_PATTERNS.items():
        match = pattern.search(working)
        if match:
            result[key] = match.group(1).strip()
            working = pattern.sub("", working)

    if not result["original_link"]:
        match = LINK_RE.search(working)
        if match:
            result["original_link"] = match.group(0)

    if not result["title_hint"] and result["original_link"]:
        lines = [line.strip() for line in working.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("http://") or line.startswith("https://"):
                continue
            if len(line) <= 60:
                result["title_hint"] = line
                working = working.replace(line, "", 1)
                break

    body_hint = working.strip()
    if result["original_link"] and body_hint == result["original_link"]:
        body_hint = ""
    result["body_hint"] = body_hint
    return result


def parse_message_event(payload: dict) -> dict:
    event = payload["event"]
    message = event.get("message")
    sender = event.get("sender", {}).get("sender_id", {}).get("open_id", "")
    parent_id = event.get("parent_id", "")
    root_id = event.get("root_id", "")

    if not message:
        return {
            "content_type": "ignored",
            "raw_text": "",
            "original_link": "",
            "platform": "ignored",
            "should_distill": False,
            "should_create_idea": False,
            "should_answer": False,
            "should_save_answer": False,
            "sender": sender,
            "message_id": "",
            "parent_id": parent_id,
            "root_id": root_id,
            "image_key": "",
            "title_hint": "",
            "author_hint": "",
            "body_hint": "",
        }

    message_type = message["message_type"]
    message_id = message.get("message_id", "")
    content = json.loads(message["content"])

    if message_type == "text":
        raw_text = content.get("text", "").strip()
        has_distill_marker = bool(DISTILL_RE.search(raw_text))
        has_idea_marker = bool(IDEA_RE.search(raw_text))
        has_save_marker = bool(SAVE_RE.search(raw_text))
        has_asksave_marker = bool(ASKSAVE_RE.search(raw_text))
        if has_distill_marker:
            raw_text = DISTILL_RE.sub("", raw_text).strip()
        if has_idea_marker:
            raw_text = IDEA_RE.sub("", raw_text).strip()
        if has_save_marker:
            raw_text = SAVE_RE.sub("", raw_text).strip()
        if has_asksave_marker:
            raw_text = ASKSAVE_RE.sub("", raw_text).strip()
        should_answer = detect_question(raw_text) and not has_idea_marker
        structured = extract_structured_fields(raw_text)
        original_link = structured["original_link"]
        match = LINK_RE.search(raw_text)
        content_type = "text-link" if match else "text"
        should_save_answer = should_answer and has_asksave_marker
        should_distill = bool(match) or has_distill_marker or has_save_marker or has_idea_marker
        return {
            "content_type": content_type,
            "raw_text": raw_text,
            "original_link": original_link,
            "platform": detect_platform(original_link),
            "should_distill": should_distill and not should_answer,
            "should_create_idea": has_idea_marker,
            "should_answer": should_answer,
            "should_save_answer": should_save_answer,
            "sender": sender,
            "message_id": message_id,
            "parent_id": parent_id,
            "root_id": root_id,
            "image_key": "",
            "title_hint": structured["title_hint"],
            "author_hint": structured["author_hint"],
            "body_hint": structured["body_hint"],
        }

    if message_type == "image":
        image_key = content.get("image_key", "")
        return {
            "content_type": "image",
            "raw_text": "",
            "original_link": "",
            "platform": "image",
            "should_distill": True,
            "should_create_idea": False,
            "should_answer": False,
            "should_save_answer": False,
            "sender": sender,
            "message_id": message_id,
            "parent_id": parent_id,
            "root_id": root_id,
            "image_key": image_key,
            "title_hint": "",
            "author_hint": "",
            "body_hint": "",
        }

    return {
        "content_type": "unsupported",
        "raw_text": json.dumps(content, ensure_ascii=False),
        "original_link": "",
        "platform": "unsupported",
        "should_distill": False,
        "should_create_idea": False,
        "should_answer": False,
        "should_save_answer": False,
        "sender": sender,
        "message_id": message_id,
        "parent_id": parent_id,
        "root_id": root_id,
        "image_key": "",
        "title_hint": "",
        "author_hint": "",
        "body_hint": "",
    }
