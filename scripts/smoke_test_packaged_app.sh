#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_RUNNER="$ROOT/dist/app/FeishuObsidianLocal.app/Contents/Resources/backend-bundle/run_backend"
TMP_VAULT="/private/tmp/feishu-product-smoke-vault"
LOG_FILE="/tmp/feishu_product_smoke.log"
PORT="${SMOKE_TEST_PORT:-8899}"

rm -rf "$TMP_VAULT"
mkdir -p \
  "$TMP_VAULT/00 Inbox" \
  "$TMP_VAULT/01 Sources" \
  "$TMP_VAULT/02 Themes" \
  "$TMP_VAULT/03 Ideas" \
  "$TMP_VAULT/04 Playbooks" \
  "$TMP_VAULT/05 Reviews" \
  "$TMP_VAULT/06 Answers" \
  "$TMP_VAULT/99 System" \
  "$TMP_VAULT/Assets"

cleanup() {
  if [ -n "${PID:-}" ]; then
    kill "$PID" >/dev/null 2>&1 || true
    wait "$PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

FEISHU_APP_ID='dummy' \
FEISHU_APP_SECRET='dummy' \
FEISHU_VERIFICATION_TOKEN='dummy' \
FEISHU_ENCRYPT_KEY='dummy' \
TAVILY_API_KEY='dummy' \
SKIP_FEISHU_WS='1' \
VAULT_ROOT="$TMP_VAULT" \
INBOX_DIR="$TMP_VAULT/00 Inbox" \
SOURCE_DIR="$TMP_VAULT/01 Sources" \
IDEAS_DIR="$TMP_VAULT/03 Ideas" \
ANSWERS_DIR="$TMP_VAULT/06 Answers" \
ASSETS_DIR="$TMP_VAULT/Assets" \
INGEST_PORT="$PORT" \
"$APP_RUNNER" >"$LOG_FILE" 2>&1 &
PID=$!

sleep 4
curl -sf "http://127.0.0.1:${PORT}/status"
