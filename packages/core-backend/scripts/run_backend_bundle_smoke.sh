#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUNDLE="$ROOT/dist/backend-bundle"

if [ ! -x "$BUNDLE/run_backend" ]; then
  echo "Bundle entrypoint missing: $BUNDLE/run_backend"
  exit 1
fi

echo "Backend bundle smoke check OK: $BUNDLE/run_backend"
