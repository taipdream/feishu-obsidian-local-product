from pathlib import Path
import argparse

from feishu_obsidian_local_backend.pattern_promoter import create_pattern_notes
from feishu_obsidian_local_backend.review_generator import create_weekly_review


DEFAULT_VAULT_ROOT = Path.home() / "Documents" / "InsightVault"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a weekly review from recent Sources and Ideas.")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days")
    parser.add_argument("--min-count", type=int, default=2, help="Minimum repeated count required for pattern promotion")
    parser.add_argument("--sources-dir", default=str(DEFAULT_VAULT_ROOT / "01 Sources"))
    parser.add_argument("--ideas-dir", default=str(DEFAULT_VAULT_ROOT / "03 Ideas"))
    parser.add_argument("--reviews-dir", default=str(DEFAULT_VAULT_ROOT / "05 Reviews"))
    parser.add_argument("--themes-dir", default=str(DEFAULT_VAULT_ROOT / "02 Themes"))
    parser.add_argument("--playbooks-dir", default=str(DEFAULT_VAULT_ROOT / "04 Playbooks"))
    args = parser.parse_args()

    sources_dir = Path(args.sources_dir).expanduser().resolve()
    ideas_dir = Path(args.ideas_dir).expanduser().resolve()
    reviews_dir = Path(args.reviews_dir).expanduser().resolve()
    themes_dir = Path(args.themes_dir).expanduser().resolve()
    playbooks_dir = Path(args.playbooks_dir).expanduser().resolve()

    review_path = create_weekly_review(
        sources_dir,
        ideas_dir,
        reviews_dir,
        days=args.days,
    )
    promoted = create_pattern_notes(
        sources_dir=sources_dir,
        ideas_dir=ideas_dir,
        themes_dir=themes_dir,
        playbooks_dir=playbooks_dir,
        days=args.days,
        min_count=args.min_count,
    )
    print(review_path)
    for path in promoted["themes"] + promoted["playbooks"]:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
