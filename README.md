# Feishu Obsidian Local Product

Local macOS product workspace for:

- a packaged backend
- a menu bar app
- an Obsidian status plugin

## Build distributables

```bash
./scripts/package_all.sh
```

Outputs:

- `dist/app/FeishuObsidianLocal.app`
- `dist/releases/FeishuObsidianLocal-macos.zip`
- `dist/releases/FeishuObsidianLocal-macos.dmg`

## Install notes

See `docs/installing-unsigned-builds.md`.

## Smoke test the packaged app

```bash
chmod +x ./scripts/smoke_test_packaged_app.sh
./scripts/smoke_test_packaged_app.sh
```

Expected result:

- the command prints the packaged app's local `/status` JSON
- `backend_running`, `vault_ready`, and `feishu_connected` should all be `true` in the smoke environment
