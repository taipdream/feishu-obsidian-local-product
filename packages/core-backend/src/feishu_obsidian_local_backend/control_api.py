from fastapi import FastAPI

app = FastAPI()


@app.get("/status")
def get_status() -> dict:
    return {
        "backend_running": True,
        "vault_ready": False,
        "feishu_connected": False,
        "last_ingest_status": "",
        "last_reply_status": "",
        "action_needed": "Finish onboarding",
    }
