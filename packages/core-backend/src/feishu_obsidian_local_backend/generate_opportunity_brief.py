from pathlib import Path
import argparse

from feishu_obsidian_local_backend.opportunity_generator import create_opportunity_brief


DEFAULT_VAULT_ROOT = Path.home() / "Documents" / "InsightVault"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an opportunity brief from the latest review and current ideas.")
    parser.add_argument("--reviews-dir", default=str(DEFAULT_VAULT_ROOT / "05 Reviews"))
    parser.add_argument("--ideas-dir", default=str(DEFAULT_VAULT_ROOT / "03 Ideas"))
    parser.add_argument("--output-dir", default=str(DEFAULT_VAULT_ROOT / "05 Reviews"))
    args = parser.parse_args()

    output_path = create_opportunity_brief(
        Path(args.reviews_dir).expanduser().resolve(),
        Path(args.ideas_dir).expanduser().resolve(),
        Path(args.output_dir).expanduser().resolve(),
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
