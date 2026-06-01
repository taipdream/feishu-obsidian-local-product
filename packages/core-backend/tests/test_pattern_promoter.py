from datetime import datetime
from pathlib import Path

from feishu_obsidian_local_backend.pattern_promoter import create_pattern_notes


def _write_source(
    path: Path,
    title: str,
    themes: str,
    problems: str,
    mechanisms: str,
    why_saved: str = "",
    my_judgment: str = "",
    related_context: str = "",
) -> None:
    body = f"""---
type: source
themes: [{themes}]
problems: [{problems}]
mechanisms: [{mechanisms}]
---

# {title}

## Why I Saved This

{why_saved or "- "}

## My Judgment

{my_judgment or "- "}
"""
    if related_context:
        body += f"""

## Related Web Context

{related_context}
"""
    path.write_text(body, encoding="utf-8")


def _write_idea(path: Path, title: str, related_source_stem: str) -> None:
    path.write_text(
        f"""---
type: idea
stage: exploring
related_sources:
  - "[[01 Sources/{related_source_stem}]]"
---

# {title}
""",
        encoding="utf-8",
    )


def test_create_pattern_notes_generates_theme_and_playbook_pages(tmp_path):
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    themes_dir = tmp_path / "themes"
    playbooks_dir = tmp_path / "playbooks"
    for directory in [sources_dir, ideas_dir, themes_dir, playbooks_dir]:
        directory.mkdir()

    source_a = sources_dir / "source-a.md"
    source_b = sources_dir / "source-b.md"
    _write_source(
        source_a,
        title="Source A",
        themes="女性成长",
        problems="身份焦虑",
        mechanisms="轻量陪伴",
        why_saved="- 适合用在女性成长场景里的低压力陪伴产品。",
        my_judgment="- 可以先用轻量入口承接焦虑，再逐步引导到更深互动。",
        related_context="""- 外部案例 A
  - https://example.com/a
  - 与女性成长社群有关
""",
    )
    _write_source(
        source_b,
        title="Source B",
        themes="女性成长",
        problems="身份焦虑",
        mechanisms="轻量陪伴",
        why_saved="- 用户不一定准备好为重服务付费，更适合先给低承诺入口。",
        my_judgment="- 避免只做安慰内容，最好配一个明确下一步动作。",
        related_context="""- 外部案例 B
  - https://example.com/b
  - 与低压力切入有关
""",
    )
    _write_idea(ideas_dir / "idea-a.md", "女性成长轻陪伴产品", "source-a")

    now = datetime(2026, 5, 30, 18, 0, 0)
    ts = now.timestamp()
    import os

    os.utime(source_a, (ts, ts))
    os.utime(source_b, (ts, ts))
    os.utime(ideas_dir / "idea-a.md", (ts, ts))

    result = create_pattern_notes(
        sources_dir=sources_dir,
        ideas_dir=ideas_dir,
        themes_dir=themes_dir,
        playbooks_dir=playbooks_dir,
        now=now,
        days=7,
        min_count=2,
    )

    assert len(result["themes"]) == 1
    assert len(result["playbooks"]) == 1

    theme_content = result["themes"][0].read_text(encoding="utf-8")
    playbook_content = result["playbooks"][0].read_text(encoding="utf-8")

    assert "type: theme" in theme_content
    assert "# 女性成长" in theme_content
    assert '[[01 Sources/source-a]]' in theme_content
    assert '[[03 Ideas/idea-a]]' in theme_content
    assert "女性成长场景里的低压力陪伴产品" in theme_content
    assert "可以先用轻量入口承接焦虑" in theme_content
    assert "可以继续观察这个主题是否适合沉淀成内容、社群或服务切入点。" not in theme_content
    assert "女性成长轻陪伴产品" in theme_content
    assert "外部案例 A" in theme_content

    assert "type: playbook" in playbook_content
    assert "# 轻量陪伴" in playbook_content
    assert "## Best-Fit Situations" in playbook_content
    assert "女性成长场景里的低压力陪伴产品" in playbook_content
    assert "女性成长" in playbook_content
    assert "身份焦虑" in playbook_content
    assert "## Validation Moves" in playbook_content
    assert "外部案例 A" in playbook_content
    assert "避免只做安慰内容" in playbook_content
    assert "https://example.com/b" in playbook_content


def test_create_pattern_notes_respects_min_count_threshold(tmp_path):
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    themes_dir = tmp_path / "themes"
    playbooks_dir = tmp_path / "playbooks"
    for directory in [sources_dir, ideas_dir, themes_dir, playbooks_dir]:
        directory.mkdir()

    source_a = sources_dir / "source-a.md"
    _write_source(
        source_a,
        title="Source A",
        themes="情绪价值",
        problems="",
        mechanisms="情绪安慰",
    )

    now = datetime(2026, 5, 30, 18, 0, 0)
    ts = now.timestamp()
    import os

    os.utime(source_a, (ts, ts))

    result = create_pattern_notes(
        sources_dir=sources_dir,
        ideas_dir=ideas_dir,
        themes_dir=themes_dir,
        playbooks_dir=playbooks_dir,
        now=now,
        days=7,
        min_count=2,
    )

    assert result["themes"] == []
    assert result["playbooks"] == []


def test_create_pattern_notes_ignores_example_notes(tmp_path):
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    themes_dir = tmp_path / "themes"
    playbooks_dir = tmp_path / "playbooks"
    for directory in [sources_dir, ideas_dir, themes_dir, playbooks_dir]:
        directory.mkdir()

    source_a = sources_dir / "example-source-a.md"
    source_b = sources_dir / "example-source-b.md"
    _write_source(
        source_a,
        title="Example A",
        themes="女性成长",
        problems="身份焦虑",
        mechanisms="轻量陪伴",
    )
    _write_source(
        source_b,
        title="Example B",
        themes="女性成长",
        problems="身份焦虑",
        mechanisms="轻量陪伴",
    )

    now = datetime(2026, 5, 30, 18, 0, 0)
    ts = now.timestamp()
    import os

    os.utime(source_a, (ts, ts))
    os.utime(source_b, (ts, ts))

    result = create_pattern_notes(
        sources_dir=sources_dir,
        ideas_dir=ideas_dir,
        themes_dir=themes_dir,
        playbooks_dir=playbooks_dir,
        now=now,
        days=7,
        min_count=2,
    )

    assert result["themes"] == []
    assert result["playbooks"] == []
