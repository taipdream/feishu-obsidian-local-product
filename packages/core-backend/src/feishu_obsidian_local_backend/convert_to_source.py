from pathlib import Path
import argparse

from feishu_obsidian_local_backend.source_converter import convert_inbox_note


DEFAULT_VAULT_ROOT = Path.home() / "Documents" / "InsightVault"
DEFAULT_SOURCE_DIR = DEFAULT_VAULT_ROOT / "01 Sources"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert an Inbox note into a Source note.")
    parser.add_argument("inbox_note", help="Path to the Inbox markdown note")
    parser.add_argument(
        "--source-dir",
        default=str(DEFAULT_SOURCE_DIR),
        help="Destination directory for the generated Source note",
    )
    args = parser.parse_args()

    inbox_path = Path(args.inbox_note).expanduser().resolve()
    source_dir = Path(args.source_dir).expanduser().resolve()
    source_dir.mkdir(parents=True, exist_ok=True)

    source_path = convert_inbox_note(inbox_path, source_dir)
    print(source_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
