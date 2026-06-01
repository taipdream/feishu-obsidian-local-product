from pathlib import Path

import feishu_obsidian_local_backend.generate_weekly_review as generate_weekly_review
def test_main_generates_review_and_promotes_patterns(monkeypatch, tmp_path, capsys):
    sources_dir = tmp_path / "sources"
    ideas_dir = tmp_path / "ideas"
    reviews_dir = tmp_path / "reviews"
    themes_dir = tmp_path / "themes"
    playbooks_dir = tmp_path / "playbooks"
    for directory in [sources_dir, ideas_dir, reviews_dir, themes_dir, playbooks_dir]:
        directory.mkdir()

    review_path = reviews_dir / "review-2026-05-30.md"
    promoted_theme = themes_dir / "女性成长.md"
    promoted_playbook = playbooks_dir / "轻量陪伴.md"

    def fake_create_weekly_review(sources_dir_arg, ideas_dir_arg, reviews_dir_arg, days):
        assert sources_dir_arg == sources_dir.resolve()
        assert ideas_dir_arg == ideas_dir.resolve()
        assert reviews_dir_arg == reviews_dir.resolve()
        assert days == 14
        review_path.write_text("# Review", encoding="utf-8")
        return review_path

    def fake_create_pattern_notes(sources_dir, ideas_dir, themes_dir, playbooks_dir, days, min_count):
        assert sources_dir == (tmp_path / "sources").resolve()
        assert ideas_dir == (tmp_path / "ideas").resolve()
        assert themes_dir == (tmp_path / "themes").resolve()
        assert playbooks_dir == (tmp_path / "playbooks").resolve()
        assert days == 14
        assert min_count == 2
        promoted_theme.write_text("# Theme", encoding="utf-8")
        promoted_playbook.write_text("# Playbook", encoding="utf-8")
        return {"themes": [promoted_theme], "playbooks": [promoted_playbook]}

    monkeypatch.setattr(generate_weekly_review, "create_weekly_review", fake_create_weekly_review)
    monkeypatch.setattr(generate_weekly_review, "create_pattern_notes", fake_create_pattern_notes)
    monkeypatch.setattr(
        "sys.argv",
        [
            "generate_weekly_review.py",
            "--days",
            "14",
            "--sources-dir",
            str(sources_dir),
            "--ideas-dir",
            str(ideas_dir),
            "--reviews-dir",
            str(reviews_dir),
            "--themes-dir",
            str(themes_dir),
            "--playbooks-dir",
            str(playbooks_dir),
            "--min-count",
            "2",
        ],
    )

    result = generate_weekly_review.main()

    assert result == 0
    output = capsys.readouterr().out
    assert str(review_path) in output
    assert str(promoted_theme) in output
    assert str(promoted_playbook) in output
