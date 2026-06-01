from datetime import datetime, timedelta
from pathlib import Path

from feishu_obsidian_local_backend.review_generator import collect_recent_notes, create_weekly_review


def _write_note(path: Path, title: str, body: str = "") -> None:
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")


def test_collect_recent_notes_filters_by_mtime(tmp_path):
    recent = tmp_path / "recent.md"
    old = tmp_path / "old.md"
    _write_note(recent, "Recent Note")
    _write_note(old, "Old Note")

    now = datetime(2026, 5, 30, 10, 0, 0)
    recent_ts = now.timestamp()
    old_ts = (now - timedelta(days=10)).timestamp()

    recent.touch()
    old.touch()
    import os

    os.utime(recent, (recent_ts, recent_ts))
    os.utime(old, (old_ts, old_ts))

    notes = collect_recent_notes(tmp_path, days=7, now=now)
    assert [note["title"] for note in notes] == ["Recent Note"]


def test_create_weekly_review_writes_summary(tmp_path):
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    reviews_dir = tmp_path / "reviews"
    sources_dir.mkdir()
    ideas_dir.mkdir()
    reviews_dir.mkdir()

    source = sources_dir / "source-a.md"
    idea = ideas_dir / "idea-a.md"
    source.write_text(
        """---
themes: [情绪价值, 女性成长]
problems: [身份焦虑]
mechanisms: [轻量陪伴]
---

# Source A
""",
        encoding="utf-8",
    )
    _write_note(idea, "Idea A")

    now = datetime(2026, 5, 30, 10, 0, 0)
    ts = now.timestamp()
    import os

    os.utime(source, (ts, ts))
    os.utime(idea, (ts, ts))

    review_path = create_weekly_review(sources_dir, ideas_dir, reviews_dir, now=now, days=7)

    assert review_path.exists()
    content = review_path.read_text(encoding="utf-8")
    assert "# Weekly Review - 2026-05-30" in content
    assert "- New sources: 1" in content
    assert "- New ideas: 1" in content
    assert "## Pattern Signals" in content
    assert "- Themes: 情绪价值 (1), 女性成长 (1)" in content
    assert "- Problems: 身份焦虑 (1)" in content
    assert "- Mechanisms: 轻量陪伴 (1)" in content
    assert "[[01 Sources/source-a]]" in content
    assert "[[03 Ideas/idea-a]]" in content


def test_create_weekly_review_reads_multiline_frontmatter_lists(tmp_path):
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    reviews_dir = tmp_path / "reviews"
    sources_dir.mkdir()
    ideas_dir.mkdir()
    reviews_dir.mkdir()

    source = sources_dir / "source-b.md"
    source.write_text(
        """---
themes:
  - 情绪价值
  - 女性成长
problems:
  - 身份焦虑
mechanisms:
  - 轻量陪伴
---

# Source B
""",
        encoding="utf-8",
    )

    now = datetime(2026, 5, 30, 10, 0, 0)
    ts = now.timestamp()
    import os

    os.utime(source, (ts, ts))

    review_path = create_weekly_review(sources_dir, ideas_dir, reviews_dir, now=now, days=7)
    content = review_path.read_text(encoding="utf-8")
    assert "- Themes: 情绪价值 (1), 女性成长 (1)" in content
    assert "- Problems: 身份焦虑 (1)" in content
    assert "- Mechanisms: 轻量陪伴 (1)" in content


def test_create_weekly_review_counts_sources_with_related_context(tmp_path):
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    reviews_dir = tmp_path / "reviews"
    sources_dir.mkdir()
    ideas_dir.mkdir()
    reviews_dir.mkdir()

    source = sources_dir / "source-c.md"
    source.write_text(
        """---
themes: [情绪价值]
problems: []
mechanisms: []
---

# Source C

## Related Web Context

- Example
  - https://example.com
""",
        encoding="utf-8",
    )

    now = datetime(2026, 5, 30, 10, 0, 0)
    ts = now.timestamp()
    import os

    os.utime(source, (ts, ts))

    review_path = create_weekly_review(sources_dir, ideas_dir, reviews_dir, now=now, days=7)
    content = review_path.read_text(encoding="utf-8")
    assert "- Sources with web context: 1" in content
