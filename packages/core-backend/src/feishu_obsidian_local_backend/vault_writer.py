from datetime import datetime
from pathlib import Path

from feishu_obsidian_local_backend.slugify import slugify_filename


def build_note_filename(timestamp: str, title: str) -> str:
    dt = datetime.fromisoformat(timestamp)
    slug = slugify_filename(title)
    return f"feishu-{dt.strftime('%Y-%m-%d-%H%M%S')}-{slug}.md"


def render_markdown(
    title: str,
    timestamp: str,
    content_type: str,
    platform: str,
    original_link: str,
    resolved_title: str,
    author: str,
    sender: str,
    message_id: str,
    parent_id: str,
    root_id: str,
    raw_content: str,
) -> str:
    return f"""# Inbox Capture - {title}

- Source: feishu-bot
- Captured at: {timestamp}
- Content type: {content_type}
- Platform: {platform}
- Original link: {original_link}
- Resolved title: {resolved_title}
- Author: {author}
- Sender: {sender}
- Message ID: {message_id}
- Parent ID: {parent_id}
- Root ID: {root_id}
- Why it looked useful:

## Raw Content

{raw_content}

## Immediate Notes
"""


def write_note(inbox_dir: str, filename: str, markdown: str) -> Path:
    path = Path(inbox_dir) / filename
    path.write_text(markdown, encoding="utf-8")
    return path


def write_asset(assets_dir: str, filename: str, data: bytes) -> Path:
    path = Path(assets_dir) / filename
    path.write_bytes(data)
    return path
