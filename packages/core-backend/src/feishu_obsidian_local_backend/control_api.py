from pathlib import Path

from fastapi import FastAPI

from feishu_obsidian_local_backend.config import load_settings
from feishu_obsidian_local_backend.startup_guard import REQUIRED_VAULT_DIRS

app = FastAPI()


@app.get("/status")
def get_status() -> dict:
    settings = load_settings()
    vault_root = Path(settings.vault_root).expanduser()
    vault_ready = vault_root.exists() and all((vault_root / rel).exists() for rel in REQUIRED_VAULT_DIRS)
    credentials_ready = all(
        [
            settings.feishu_app_id,
            settings.feishu_app_secret,
            settings.feishu_verification_token,
            settings.feishu_encrypt_key,
        ]
    )

    if not credentials_ready:
        action_needed = "Complete local configuration"
    elif not vault_ready:
        action_needed = "Initialize vault"
    else:
        action_needed = "Ready"

    return {
        "backend_running": True,
        "vault_ready": vault_ready,
        "feishu_connected": credentials_ready,
        "last_ingest_status": "",
        "last_reply_status": "",
        "action_needed": action_needed,
    }
