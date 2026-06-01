from __future__ import annotations

from pathlib import Path

from feishu_obsidian_local_backend.config import ENV_PATH, Settings, load_settings


REQUIRED_VAULT_DIRS = [
    "00 Inbox",
    "01 Sources",
    "02 Themes",
    "03 Ideas",
    "04 Playbooks",
    "05 Reviews",
    "06 Answers",
    "99 System",
    "Assets",
]

REQUIRED_ENV_KEYS = [
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_VERIFICATION_TOKEN",
    "FEISHU_ENCRYPT_KEY",
    "TAVILY_API_KEY",
]


def gather_startup_issues(settings: Settings, env_exists: bool) -> list[str]:
    issues: list[str] = []
    if not env_exists:
        issues.append("backend/.env is missing")

    values = {
        "FEISHU_APP_ID": settings.feishu_app_id,
        "FEISHU_APP_SECRET": settings.feishu_app_secret,
        "FEISHU_VERIFICATION_TOKEN": settings.feishu_verification_token,
        "FEISHU_ENCRYPT_KEY": settings.feishu_encrypt_key,
        "TAVILY_API_KEY": settings.tavily_api_key,
    }
    for key in REQUIRED_ENV_KEYS:
        if not values[key]:
            issues.append(f"{key} is empty")

    vault_root = Path(settings.vault_root).expanduser()
    if not vault_root.exists():
        issues.append(f"Vault root does not exist: {vault_root}")
        return issues

    for rel in REQUIRED_VAULT_DIRS:
        if not (vault_root / rel).exists():
            issues.append(f"{rel} folder is missing from the vault")

    return issues


def format_startup_error(mode: str, issues: list[str]) -> str:
    mode_label = "Feishu long connection" if mode == "ws" else "backend server"
    lines = [f"Cannot start {mode_label}."]
    lines.append("")
    lines.append("Fix these items first:")
    for issue in issues:
        lines.append(f"- {issue}")
    lines.append("")
    lines.append("Recommended next steps:")
    lines.append("- Run: python3 scripts/doctor.py")
    lines.append("- If setup is incomplete, run: python3 scripts/bootstrap_local.py --wizard")
    lines.append("- Then try starting again.")
    return "\n".join(lines)


def assert_ready_or_exit(mode: str) -> None:
    settings = load_settings()
    issues = gather_startup_issues(settings, env_exists=ENV_PATH.exists())
    if issues:
        raise SystemExit(format_startup_error(mode, issues))


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Check startup prerequisites before running the backend.")
    parser.add_argument("--mode", choices=["ws", "server"], default="ws")
    args = parser.parse_args()

    assert_ready_or_exit(args.mode)
    print("Startup preflight OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
