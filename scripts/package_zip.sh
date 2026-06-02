#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_ROOT="$ROOT/dist/app/FeishuObsidianLocal.app"
RELEASES_DIR="$ROOT/dist/releases"
ZIP_PATH="$RELEASES_DIR/FeishuObsidianLocal-macos.zip"

mkdir -p "$RELEASES_DIR"
rm -f "$ZIP_PATH"

ditto -c -k --sequesterRsrc --keepParent "$APP_ROOT" "$ZIP_PATH"
