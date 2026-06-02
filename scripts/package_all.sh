#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

"$ROOT/scripts/build_app_bundle.sh"
"$ROOT/scripts/package_zip.sh"
"$ROOT/scripts/package_dmg.sh"
