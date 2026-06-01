from pathlib import Path

from feishu_obsidian_local_backend.config import Settings
from feishu_obsidian_local_backend.startup_guard import format_startup_error, gather_startup_issues


def make_settings(vault_root: Path) -> Settings:
    vault_root_str = str(vault_root)
    return Settings(
        feishu_app_id="cli_x",
        feishu_app_secret="secret",
        feishu_encrypt_key="encrypt",
        tavily_api_key="tvly_x",
        vault_root=vault_root_str,
        inbox_dir=str(vault_root / "00 Inbox"),
        source_dir=str(vault_root / "01 Sources"),
        ideas_dir=str(vault_root / "03 Ideas"),
        answers_dir=str(vault_root / "06 Answers"),
        assets_dir=str(vault_root / "Assets"),
        ingest_port=8787,
        feishu_verification_token="token",
    )


def test_gather_startup_issues_returns_empty_when_ready(tmp_path):
    vault_root = tmp_path / "vault"
    for rel in [
        "00 Inbox",
        "01 Sources",
        "02 Themes",
        "03 Ideas",
        "04 Playbooks",
        "05 Reviews",
        "06 Answers",
        "99 System",
        "Assets",
    ]:
        (vault_root / rel).mkdir(parents=True, exist_ok=True)

    issues = gather_startup_issues(make_settings(vault_root), env_exists=True)

    assert issues == []


def test_gather_startup_issues_reports_missing_env_keys_and_vault_dirs(tmp_path):
    vault_root = tmp_path / "vault"
    (vault_root / "00 Inbox").mkdir(parents=True, exist_ok=True)
    settings = make_settings(vault_root)
    settings = Settings(
        feishu_app_id="",
        feishu_app_secret=settings.feishu_app_secret,
        feishu_encrypt_key=settings.feishu_encrypt_key,
        tavily_api_key="",
        vault_root=settings.vault_root,
        inbox_dir=settings.inbox_dir,
        source_dir=settings.source_dir,
        ideas_dir=settings.ideas_dir,
        answers_dir=settings.answers_dir,
        assets_dir=settings.assets_dir,
        ingest_port=settings.ingest_port,
        feishu_verification_token="",
    )

    issues = gather_startup_issues(settings, env_exists=False)

    assert "backend/.env is missing" in issues
    assert "FEISHU_APP_ID is empty" in issues
    assert "FEISHU_VERIFICATION_TOKEN is empty" in issues
    assert "TAVILY_API_KEY is empty" in issues
    assert "01 Sources folder is missing from the vault" in issues


def test_format_startup_error_includes_clear_next_steps(tmp_path):
    message = format_startup_error(
        mode="ws",
        issues=[
            "backend/.env is missing",
            "FEISHU_APP_ID is empty",
            "01 Sources folder is missing from the vault",
        ],
    )

    assert "Cannot start Feishu long connection." in message
    assert "backend/.env is missing" in message
    assert "python3 scripts/doctor.py" in message
    assert "python3 scripts/bootstrap_local.py --wizard" in message
