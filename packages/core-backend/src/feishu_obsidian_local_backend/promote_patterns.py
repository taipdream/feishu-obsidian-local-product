from pathlib import Path
import argparse

from feishu_obsidian_local_backend.pattern_promoter import create_pattern_notes


DEFAULT_VAULT_ROOT = Path.home() / "Documents" / "InsightVault"


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote repeated Source patterns into Theme and Playbook notes.")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days")
    parser.add_argument("--min-count", type=int, default=2, help="Minimum repeated count required for promotion")
    parser.add_argument("--sources-dir", default=str(DEFAULT_VAULT_ROOT / "01 Sources"))
    parser.add_argument("--ideas-dir", default=str(DEFAULT_VAULT_ROOT / "03 Ideas"))
    parser.add_argument("--themes-dir", default=str(DEFAULT_VAULT_ROOT / "02 Themes"))
    parser.add_argument("--playbooks-dir", default=str(DEFAULT_VAULT_ROOT / "04 Playbooks"))
    args = parser.parse_args()

    result = create_pattern_notes(
        sources_dir=Path(args.sources_dir).expanduser().resolve(),
        ideas_dir=Path(args.ideas_dir).expanduser().resolve(),
        themes_dir=Path(args.themes_dir).expanduser().resolve(),
        playbooks_dir=Path(args.playbooks_dir).expanduser().resolve(),
        days=args.days,
        min_count=args.min_count,
    )
    for path in result["themes"] + result["playbooks"]:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
