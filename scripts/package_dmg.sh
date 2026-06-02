#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_ROOT="$ROOT/dist/app/FeishuObsidianLocal.app"
RELEASES_DIR="$ROOT/dist/releases"
STAGE_DIR="$ROOT/dist/dmg-stage"
DMG_PATH="$RELEASES_DIR/FeishuObsidianLocal-macos.dmg"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR" "$RELEASES_DIR"
cp -R "$APP_ROOT" "$STAGE_DIR/FeishuObsidianLocal.app"
ln -s /Applications "$STAGE_DIR/Applications"
rm -f "$DMG_PATH"

hdiutil create \
  -volname "FeishuObsidianLocal" \
  -srcfolder "$STAGE_DIR" \
  -ov -format UDZO \
  "$DMG_PATH"
