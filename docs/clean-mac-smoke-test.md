# Clean Mac Smoke Test

## Automated preflight

Before asking a real user to install the app, run:

```bash
./scripts/package_all.sh
./scripts/smoke_test_packaged_app.sh
```

This confirms the packaged `.app` can launch its embedded local status service without relying on the source tree.

## Manual friend-view validation

1. Install Obsidian manually
2. Open the macOS shell app
3. Accept or change the default vault path
4. Enter Feishu and provider credentials
5. Start backend
6. Confirm status shows:
   - Vault ready
   - Backend running
   - Feishu connected
7. Send a Feishu message
8. Confirm reply is delivered
9. Confirm forwarded content appears in the vault
