from datetime import datetime
from pathlib import Path

from feishu_obsidian_local_backend.answer_generator import build_web_fallback_query, create_answer_note


def test_create_answer_note_uses_relevant_local_evidence(tmp_path):
    reviews_dir = tmp_path / "reviews"
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    answers_dir = tmp_path / "answers"
    reviews_dir.mkdir()
    sources_dir.mkdir()
    ideas_dir.mkdir()
    answers_dir.mkdir()

    (reviews_dir / "review-2026-05-30.md").write_text(
        """# Weekly Review - 2026-05-30

## Pattern Signals

- Themes: 女性成长 (2)
""",
        encoding="utf-8",
    )
    (reviews_dir / "opportunities-2026-05-30.md").write_text(
        """# Opportunity Brief - 2026-05-30

## Direction 1

- Focus: 女性成长 x 身份焦虑
""",
        encoding="utf-8",
    )
    (sources_dir / "chengdu-cpi-source.md").write_text(
        """# 成都CPI运营观察

团队优势在于运营节奏快，擅长内容转化和本地资源整合。

## Why I Saved This

- 这条适合用来判断团队型服务能力和运营优势。

## My Judgment

- 这个团队更像强执行和资源整合型，而不是纯创意型。

## Related Web Context

- 成都CPI官网
  - https://example.com/cpi
  - 团队以本地资源整合见长
""",
        encoding="utf-8",
    )
    (ideas_dir / "chengdu-cpi-idea.md").write_text(
        """# 成都CPI运营团队机会

## One-Sentence Idea

- 围绕成都CPI运营团队的优势设计服务切入。
""",
        encoding="utf-8",
    )
    (tmp_path / "themes").mkdir()
    (tmp_path / "playbooks").mkdir()
    (tmp_path / "themes" / "chengdu-cpi-theme.md").write_text(
        """# 成都本地运营能力

## Definition

- 本地资源整合和运营执行可能是成都团队型服务的关键优势。
""",
        encoding="utf-8",
    )
    (tmp_path / "playbooks" / "local-ops.md").write_text(
        """# 本地资源整合

## Core Mechanism

- 用本地资源连接和执行效率形成服务壁垒。
""",
        encoding="utf-8",
    )

    answer = create_answer_note(
        "成都CPI的运营团队优势在哪里？",
        reviews_dir,
        answers_dir,
        now=datetime(2026, 5, 30, 14, 0, 0),
        sources_dir=sources_dir,
        ideas_dir=ideas_dir,
        themes_dir=tmp_path / "themes",
        playbooks_dir=tmp_path / "playbooks",
    )
    content = answer.read_text(encoding="utf-8")
    assert "## Direct Evidence" in content
    assert "[[01 Sources/chengdu-cpi-source]]" in content
    assert "[[03 Ideas/chengdu-cpi-idea]]" in content
    assert "[[02 Themes/chengdu-cpi-theme]]" in content
    assert "[[04 Playbooks/local-ops]]" in content
    assert "## Related Signals" in content
    assert "## Current Read" in content
    assert "## Inference" in content
    assert "成都CPI官网" in content
    assert "团队型服务能力" in content
    assert "库内证据不足" not in content


def test_create_answer_note_reports_insufficient_local_evidence(tmp_path):
    reviews_dir = tmp_path / "reviews"
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    answers_dir = tmp_path / "answers"
    reviews_dir.mkdir()
    sources_dir.mkdir()
    ideas_dir.mkdir()
    answers_dir.mkdir()

    (reviews_dir / "review-2026-05-30.md").write_text(
        """# Weekly Review - 2026-05-30

## Pattern Signals

- Themes: 女性成长 (2)
""",
        encoding="utf-8",
    )

    captured = {}

    def fake_search(query, key):
        captured["query"] = query
        return [
            {
                "title": "成都CPI官网",
                "url": "https://example.com/cpi",
                "snippet": "团队以本地资源整合和执行效率见长。",
            }
        ]

    answer = create_answer_note(
        "成都CPI的运营团队优势在哪里？",
        reviews_dir,
        answers_dir,
        now=datetime(2026, 5, 30, 14, 0, 0),
        sources_dir=sources_dir,
        ideas_dir=ideas_dir,
        themes_dir=tmp_path / "themes",
        playbooks_dir=tmp_path / "playbooks",
        tavily_api_key="tvly-test",
        web_search_fn=fake_search,
    )
    content = answer.read_text(encoding="utf-8")
    assert "库内证据不足" in content
    assert "## Web Fallback" in content
    assert "成都CPI官网" in content
    assert "## Suggested Collection Next" in content
    assert "补 1-3 条直接相关来源" in content
    assert "团队介绍" in content
    assert "成都CPI" in captured["query"]
    assert "官网" in captured["query"]
    assert "团队" in captured["query"]


def test_build_web_fallback_query_preserves_core_entity():
    query = build_web_fallback_query("成都CPI的运营团队优势在哪里？")
    assert "成都CPI" in query
    assert "官网" in query
    assert "团队" in query
    assert "运营" in query
