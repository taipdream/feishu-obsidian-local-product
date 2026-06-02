#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist/backend-bundle"

rm -rf "$DIST"
mkdir -p "$DIST"
python3 -m venv "$DIST/runtime"
cp -R "$ROOT/src" "$DIST/app"

cat > "$DIST/run_backend" <<'EOF'
#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT/app"
PORT="${INGEST_PORT:-8787}"
"$ROOT/runtime/bin/python" -m uvicorn feishu_obsidian_local_backend.control_api:app --host 127.0.0.1 --port "$PORT" &
STATUS_PID=$!

cleanup() {
  kill "$STATUS_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM
"$ROOT/runtime/bin/python" -m feishu_obsidian_local_backend.ws_client
EOF

chmod +x "$DIST/run_backend"
echo "Backend bundle ready at $DIST"
