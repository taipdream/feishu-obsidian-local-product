from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from collections import Counter
import re


FRONTMATTER_LIST_RE = re.compile(r"^(themes|problems|mechanisms):\s*\[(.*?)\]\s*$", re.MULTILINE)
FRONTMATTER_KEY_RE = re.compile(r"^(themes|problems|mechanisms):\s*$")
FRONTMATTER_ITEM_RE = re.compile(r"^\s*-\s+(.*?)\s*$")


def extract_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def has_related_web_context(path: Path) -> bool:
    return "## Related Web Context" in path.read_text(encoding="utf-8")


def collect_recent_notes(directory: Path, days: int, now: datetime) -> list[dict]:
    cutoff = now - timedelta(days=days)
    notes = []
    for path in sorted(directory.glob("*.md")):
        modified = datetime.fromtimestamp(path.stat().st_mtime)
        if modified < cutoff:
            continue
        notes.append(
            {
                "path": path,
                "title": extract_title(path),
                "modified": modified,
            }
        )
    return notes


def extract_frontmatter_lists(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    result = {
        "themes": [],
        "problems": [],
        "mechanisms": [],
    }
    for match in FRONTMATTER_LIST_RE.finditer(text):
        key = match.group(1)
        raw_values = match.group(2).strip()
        if not raw_values:
            continue
        result[key] = [item.strip() for item in raw_values.split(",") if item.strip()]

    current_key = None
    for line in text.splitlines():
        inline_match = FRONTMATTER_LIST_RE.match(line)
        if inline_match:
            current_key = None
            continue

        key_match = FRONTMATTER_KEY_RE.match(line)
        if key_match:
            current_key = key_match.group(1)
            continue

        if current_key is not None:
            item_match = FRONTMATTER_ITEM_RE.match(line)
            if item_match:
                result[current_key].append(item_match.group(1).strip())
                continue
            if line.strip() and not line.startswith(" "):
                current_key = None
    return result


def summarize_source_patterns(sources: list[dict]) -> dict:
    counters = {
        "themes": Counter(),
        "problems": Counter(),
        "mechanisms": Counter(),
    }
    for note in sources:
        extracted = extract_frontmatter_lists(note["path"])
        for bucket, values in extracted.items():
            counters[bucket].update(values)
    return {bucket: list(counter.items()) for bucket, counter in counters.items()}


def render_weekly_review(now: datetime, sources: list[dict], ideas: list[dict], days: int) -> str:
    patterns = summarize_source_patterns(sources)
    enriched_source_count = sum(1 for note in sources if has_related_web_context(note["path"]))
    source_lines = "\n".join(f"- [[01 Sources/{note['path'].stem}]]" for note in sources) or "- None"
    idea_lines = "\n".join(f"- [[03 Ideas/{note['path'].stem}]]" for note in ideas) or "- None"
    theme_line = ", ".join(f"{name} ({count})" for name, count in patterns["themes"]) or "None"
    problem_line = ", ".join(f"{name} ({count})" for name, count in patterns["problems"]) or "None"
    mechanism_line = ", ".join(f"{name} ({count})" for name, count in patterns["mechanisms"]) or "None"
    return f"""# Weekly Review - {now.date().isoformat()}

- Window: last {days} days
- New sources: {len(sources)}
- New ideas: {len(ideas)}
- Sources with web context: {enriched_source_count}

## Pattern Signals

- Themes: {theme_line}
- Problems: {problem_line}
- Mechanisms: {mechanism_line}

## Sources

{source_lines}

## Ideas

{idea_lines}
"""


def create_weekly_review(
    sources_dir: Path,
    ideas_dir: Path,
    reviews_dir: Path,
    now: Optional[datetime] = None,
    days: int = 7,
) -> Path:
    now = now or datetime.now()
    sources = collect_recent_notes(sources_dir, days=days, now=now)
    ideas = collect_recent_notes(ideas_dir, days=days, now=now)
    reviews_dir.mkdir(parents=True, exist_ok=True)
    destination = reviews_dir / f"review-{now.date().isoformat()}.md"
    destination.write_text(render_weekly_review(now, sources, ideas, days), encoding="utf-8")
    return destination
