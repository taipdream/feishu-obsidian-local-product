import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_VAULT_ROOT = str(Path.home() / "Documents" / "InsightVault")
DEFAULT_INBOX_DIR = f"{DEFAULT_VAULT_ROOT}/00 Inbox"
DEFAULT_SOURCE_DIR = f"{DEFAULT_VAULT_ROOT}/01 Sources"
DEFAULT_IDEAS_DIR = f"{DEFAULT_VAULT_ROOT}/03 Ideas"
DEFAULT_ANSWERS_DIR = f"{DEFAULT_VAULT_ROOT}/06 Answers"
DEFAULT_ASSETS_DIR = f"{DEFAULT_VAULT_ROOT}/Assets"
ENV_PATH = Path(__file__).resolve().parent / ".env"

load_dotenv(ENV_PATH)


@dataclass(frozen=True)
class Settings:
    feishu_app_id: str
    feishu_app_secret: str
    feishu_encrypt_key: str
    tavily_api_key: str
    vault_root: str
    inbox_dir: str
    source_dir: str
    ideas_dir: str
    answers_dir: str
    assets_dir: str
    ingest_port: int
    feishu_verification_token: str


def load_settings() -> Settings:
    return Settings(
        feishu_app_id=os.environ.get("FEISHU_APP_ID", ""),
        feishu_app_secret=os.environ.get("FEISHU_APP_SECRET", ""),
        feishu_encrypt_key=os.environ.get("FEISHU_ENCRYPT_KEY", ""),
        tavily_api_key=os.environ.get("TAVILY_API_KEY", ""),
        vault_root=os.environ.get("VAULT_ROOT", DEFAULT_VAULT_ROOT),
        inbox_dir=os.environ.get("INBOX_DIR", DEFAULT_INBOX_DIR),
        source_dir=os.environ.get("SOURCE_DIR", DEFAULT_SOURCE_DIR),
        ideas_dir=os.environ.get("IDEAS_DIR", DEFAULT_IDEAS_DIR),
        answers_dir=os.environ.get("ANSWERS_DIR", DEFAULT_ANSWERS_DIR),
        assets_dir=os.environ.get("ASSETS_DIR", DEFAULT_ASSETS_DIR),
        ingest_port=int(os.environ.get("INGEST_PORT", "8787")),
        feishu_verification_token=os.environ.get("FEISHU_VERIFICATION_TOKEN", ""),
    )
