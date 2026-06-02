# Installing Unsigned Builds

This product currently ships as an unsigned local macOS build.

## What to download

- `FeishuObsidianLocal-macos.zip`
  - fastest way to share the app as a compressed file
  - unzip it, then move `FeishuObsidianLocal.app` into `Applications`
- `FeishuObsidianLocal-macos.dmg`
  - more standard Mac install flow
  - open the disk image, drag `FeishuObsidianLocal.app` into `Applications`

Both artifacts contain the same app and embedded backend bundle.

## First launch on macOS

Because the app is unsigned, macOS may block the first launch.

Use this sequence:

1. Move `FeishuObsidianLocal.app` into `Applications`
2. In Finder, right-click the app and choose `Open`
3. Confirm `Open` in the system prompt

If macOS still blocks it:

1. Open `System Settings`
2. Go to `Privacy & Security`
3. Scroll to the security section near the bottom
4. Approve the blocked app, then try `Open` again

## What the app stores locally

Machine-local configuration is stored on the Mac and is not written into the shared vault by default.

The user still needs to provide:

- their own Obsidian installation
- their own Feishu app credentials
- their own model API key
- their own search API key, if web enrichment is enabled

## Current release scope

This release is intended for local installs and friend testing.

It does not yet include:

- Apple code signing
- notarization
- automatic updates
