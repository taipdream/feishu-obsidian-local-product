from pathlib import Path
import re

from feishu_obsidian_local_backend.related_context import build_related_context_section, maybe_collect_related_context, tavily_search
from feishu_obsidian_local_backend.slugify import slugify_filename
from feishu_obsidian_local_backend.tag_suggester import suggest_tags


SECTION_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def _extract_title(markdown: str) -> str:
    first_line = markdown.splitlines()[0].strip()
    if " - " in first_line:
        return first_line.split(" - ", 1)[1].strip()
    return first_line.lstrip("# ").strip()


def _extract_bullet_value(markdown: str, label: str) -> str:
    prefix = f"- {label}:"
    for line in markdown.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def _extract_section(markdown: str, name: str) -> str:
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group(1).strip() != name:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[start:end].strip()
    return ""


def parse_inbox_markdown(markdown: str) -> dict:
    platform = _extract_bullet_value(markdown, "Platform")
    author = _extract_bullet_value(markdown, "Public account") or _extract_bullet_value(markdown, "Author")
    return {
        "title": _extract_title(markdown),
        "platform": platform,
        "source_url": _extract_bullet_value(markdown, "Original link"),
        "author": author,
        "captured_at": _extract_bullet_value(markdown, "Captured at"),
        "why_saved": _extract_bullet_value(markdown, "Why it looked useful"),
        "body": _extract_section(markdown, "Pasted Summary or Body") or _extract_section(markdown, "Raw Content"),
        "notes": _extract_section(markdown, "Immediate Notes"),
    }


def build_related_context_query(parsed: dict) -> str:
    body_excerpt = " ".join(parsed["body"].split())[:280]
    query_parts = [
        parsed["title"].strip(),
        parsed["why_saved"].strip(),
        body_excerpt.strip(),
    ]
    return " ".join(part for part in query_parts if part)


def render_source_markdown(parsed: dict) -> str:
    suggestions = suggest_tags("\n".join([parsed["title"], parsed["why_saved"], parsed["body"], parsed["notes"]]))
    themes = ", ".join(suggestions["themes"])
    problems = ", ".join(suggestions["problems"])
    mechanisms = ", ".join(suggestions["mechanisms"])
    related_context_section = build_related_context_section(parsed.get("related_context", []))
    return f"""---
type: source
status: Reviewed
platform: {parsed["platform"]}
source_url: {parsed["source_url"]}
author: {parsed["author"]}
captured_at: {parsed["captured_at"]}
content_type: inbox-capture
themes: [{themes}]
audiences: []
problems: [{problems}]
mechanisms: [{mechanisms}]
business_models: []
linked_ideas: []
---

# {parsed["title"]}

## Why I Saved This

- {parsed["why_saved"]}

## Key Excerpts

{parsed["body"]}

## My Judgment

{parsed["notes"]}

## Reusable Angle

- 

{related_context_section}

## Related Notes

- Themes:
- Ideas:
"""


def build_source_filename(parsed: dict, source_dir: Path) -> str:
    slug = slugify_filename(parsed["title"])
    if slug == "capture":
        date_part = parsed["captured_at"] or "undated"
        base_name = f"source-{date_part}"
    else:
        base_name = slug

    candidate = source_dir / f"{base_name}.md"
    suffix = 2
    while candidate.exists():
        candidate = source_dir / f"{base_name}-{suffix}.md"
        suffix += 1
    return candidate.name


def convert_inbox_note(
    inbox_path: Path,
    source_dir: Path,
    tavily_api_key: str = "",
    search_fn=tavily_search,
) -> Path:
    parsed = parse_inbox_markdown(inbox_path.read_text(encoding="utf-8"))
    parsed["related_context"] = maybe_collect_related_context(
        query=build_related_context_query(parsed),
        tavily_api_key=tavily_api_key,
        search_fn=search_fn,
    )
    filename = build_source_filename(parsed, source_dir)
    destination = source_dir / filename
    destination.write_text(render_source_markdown(parsed), encoding="utf-8")
    return destination
