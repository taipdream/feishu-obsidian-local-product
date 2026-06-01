from datetime import datetime
from pathlib import Path

from feishu_obsidian_local_backend.opportunity_generator import create_opportunity_brief, parse_review_signals


def test_parse_review_signals_reads_ranked_counts():
    review = """# Weekly Review - 2026-05-30

## Pattern Signals

- Themes: 女性成长 (2), 情绪价值 (2)
- Problems: 身份焦虑 (2), 行动力不足 (1)
- Mechanisms: 轻量陪伴 (1), 情绪承接 (1)
"""
    signals = parse_review_signals(review)
    assert signals["themes"] == [("女性成长", 2), ("情绪价值", 2)]
    assert signals["problems"] == [("身份焦虑", 2), ("行动力不足", 1)]
    assert signals["mechanisms"] == [("轻量陪伴", 1), ("情绪承接", 1)]


def test_create_opportunity_brief_writes_three_directions(tmp_path):
    reviews_dir = tmp_path / "reviews"
    ideas_dir = tmp_path / "ideas"
    output_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    ideas_dir.mkdir()

    review = reviews_dir / "review-2026-05-30.md"
    review.write_text(
        """# Weekly Review - 2026-05-30

## Pattern Signals

- Themes: 女性成长 (2), 情绪价值 (2)
- Problems: 身份焦虑 (2), 行动力不足 (1)
- Mechanisms: 轻量陪伴 (1), 情绪承接 (1), 降低启动成本 (1)

## Sources

- [[01 Sources/source-a]]
""",
        encoding="utf-8",
    )

    idea = ideas_dir / "example-idea-note.md"
    idea.write_text(
        """# 女性成长轻陪伴产品

## One-Sentence Idea

- 用低压力的陪伴感内容和轻互动机制，帮助用户管理日常焦虑。
""",
        encoding="utf-8",
    )

    result = create_opportunity_brief(reviews_dir, ideas_dir, output_dir, now=datetime(2026, 5, 30, 11, 0, 0))
    content = result.read_text(encoding="utf-8")

    assert result.exists()
    assert "# Opportunity Brief - 2026-05-30" in content
    assert "## Direction 1" in content
    assert "## Direction 2" in content
    assert "## Direction 3" in content
    assert "女性成长" in content
    assert "身份焦虑" in content
    assert "轻量陪伴" in content
    assert "[[03 Ideas/example-idea-note]]" in content
    assert "[[01 Sources/source-a]]" in content
