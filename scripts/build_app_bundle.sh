#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_ROOT="$ROOT/dist/app/FeishuObsidianLocal.app"
CONTENTS="$APP_ROOT/Contents"
MACOS_DIR="$CONTENTS/MacOS"
RESOURCES_DIR="$CONTENTS/Resources"
BACKEND_DIR="$ROOT/packages/core-backend"
SHELL_DIR="$ROOT/apps/macos-shell"

rm -rf "$APP_ROOT"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

"$BACKEND_DIR/scripts/build_backend_bundle.sh"

cd "$SHELL_DIR"
HOME=/private/tmp/swiftpm-home CLANG_MODULE_CACHE_PATH=/private/tmp/swift-module-cache swift build -c release

cp ".build/release/FeishuObsidianLocal" "$MACOS_DIR/FeishuObsidianLocal"
cp -R "$BACKEND_DIR/dist/backend-bundle" "$RESOURCES_DIR/backend-bundle"

cat > "$CONTENTS/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>FeishuObsidianLocal</string>
    <key>CFBundleIdentifier</key>
    <string>local.feishu.obsidian.product</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>FeishuObsidianLocal</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.0</string>
</dict>
</plist>
PLIST
