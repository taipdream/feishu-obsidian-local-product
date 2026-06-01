# Core Backend

Packaged local backend for Feishu transport, routing, and vault writes.

## Test

```bash
python3 -m pytest -q
```

## Build local backend bundle

```bash
./scripts/build_backend_bundle.sh
```

This creates:

- `dist/backend-bundle/runtime`
- `dist/backend-bundle/app`
- `dist/backend-bundle/run_backend`

## Smoke check the bundle

```bash
./scripts/run_backend_bundle_smoke.sh
```

The first productized runtime target is a local bundle that can be launched by the future macOS shell without requiring the end user to run backend setup commands manually.
