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
exec "$ROOT/runtime/bin/python" -m feishu_obsidian_local_backend.ws_client
EOF

chmod +x "$DIST/run_backend"
echo "Backend bundle ready at $DIST"
