# Firebase/GCP Patch — What this adds

This patch modularizes Firebase Auth, rules, and GCP configs and wires a clean hexagonal layout.

## What’s included

- `apps/api/app/` — FastAPI with ports/adapters and Firebase auth middleware (bypass enabled by `BYPASS_AUTH=1` for dev)
- `apps/api/requirements.txt` + `requirements-dev.txt`
- `apps/admin_web/src/shared/` — Firebase init + token-aware fetch wrapper
- `apps/mobile/lib/services/` — Flutter auth + API client stubs
- `packages/gcp_firebase/` — API Gateway OpenAPI, Firestore/Storage rules, Terraform stub
- `tools/scripts/set_claims.py` — set custom claims (tenantId, role)

## Apply the patch

```bash
cd living_twin_monorepo
unzip -o living_twin_firebase_patch.zip
```

## Install backend deps

```bash
# Use your venv
make venv
./.venv/bin/pip install -r apps/api/requirements.txt
# Optional for local embeddings
./.venv/bin/pip install -r apps/api/requirements-dev.txt
```

## Run (dev with auth bypass)

```bash
export BYPASS_AUTH=1   # dev only
export LOCAL_EMBEDDINGS=1  # optional to avoid OpenAI spend
./.venv/bin/python -m uvicorn app.main:app --app-dir apps/api --reload --port 8080
```

## Run (with Firebase Auth)

- Set `.env` with `PROJECT_ID=your-project-id`
- Frontend obtains Firebase ID token and sends as `Authorization: Bearer <id token>`
- Unset `BYPASS_AUTH` to enforce tokens

## Set claims for a user

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
python tools/scripts/set_claims.py <uid> <tenantId> <role>
```

## Deploy rules (manual)

- Firestore rules: paste `packages/gcp_firebase/firestore_rules/firestore.rules` in console
- Storage rules: paste `packages/gcp_firebase/storage_rules/storage.rules` in console

## API Gateway

- Update `packages/gcp_firebase/api_gateway/openapi-gateway.yaml` with your project + Cloud Run URL
- Deploy with `gcloud api-gateway apis create ...` + `gcloud api-gateway gateways create ...`

## Notes

- All endpoints enforce `tenantId` through the auth middleware + adapters.
- Neo4j store uses `VECTOR_INDEX_NAME`; ensure it exists and matches your embedding dimension.
