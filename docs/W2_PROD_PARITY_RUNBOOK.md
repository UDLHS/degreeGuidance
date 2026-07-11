# W2 Runbook — Production parity (do this before the next real handbook)

**Goal:** the yearly PDF pipeline currently runs only on the dev laptop. After
this runbook, the deployed admin panel can do the whole yearly update: upload →
extract (worker) → gates → promote → students see the new year.

**Roles:** *You* click the dashboards (Render / Upstash / Supabase / Vercel).
*Claude* runs the scripts and verifies each step. Nothing here is destructive;
the migration step is guarded and reviewed (scripts/prod_sql/*.sql).

---

## 0. Prerequisites
- [ ] Merge `Admin-Panel` → `main` and push (Render/Vercel deploy from main).
- [ ] Have the Supabase connection string at hand (Settings → Database).

## 1. Apply schema migrations 36→41 to Supabase  *(Claude runs, you watch)*
```bash
PROD_DATABASE_URL='postgresql://…supabase…' \
  python -m scripts.apply_prod_migrations --dry-run   # shows pending steps
PROD_DATABASE_URL='postgresql://…supabase…' \
  python -m scripts.apply_prod_migrations             # applies + verifies
```
What it adds: extraction_columns (+staged run statuses), stream-override and
codeless-cutoff tables, conversation flag, agent_configs, factsheets (seeded
with the 129 markdown files). Each step only applies on top of the exact
expected version; the version row is UPDATEd, never INSERTed.

## 2. Upstash Redis  *(you)*
- [ ] Create a Redis database (region closest to Render).
- [ ] Copy the **redis://** connection URL (TLS variant `rediss://` if offered — Arq supports it).

## 3. Render — background worker  *(you, ~5 clicks)*
- [ ] New → **Background Worker**, same repo/branch as the API service.
- [ ] Build: same as API (installs Python deps).
- [ ] Start command: `arq apps.worker.settings.WorkerSettings`
- [ ] Environment variables (copy from the API service, then add/adjust):
      `DATABASE_URL` (Supabase), `REDIS_URL` (Upstash), `GEMINI_API_KEY`,
      `JWT_SECRET_KEY` (same as API), `INGESTION_WORK_DIR=/tmp/ingestion_work`,
      `ARCHIVE_DIR=/tmp/archive` *(see the disk note below)*.

### ✅ Disk note (RESOLVED — migration 42, 2026-07-11)
Render instances have **ephemeral disks**, and the API and worker are
**separate machines** — a file saved by one is not visible to the other.
Resolved with the **DB artifact store** (`ingestion_artifacts` table +
`core/ingestion/artifact_store.py`): every pipeline file (pdf, grid.json,
presence.json, csv, overrides.json, unmapped.json, pre-promote snapshots)
is written through to Postgres and rematerialized from it on whatever
instance needs it next. No bucket, no persistent disk, no extra service —
and it doubles as the permanent per-year retention of the raw handbook and
promoted CSV. Verified by tests that wipe the local work dir between every
pipeline stage (tests/integration/test_ingestion_artifacts.py).

## 4. API service env additions  *(you)*
- [ ] `REDIS_URL` (Upstash) — the API enqueues jobs.
- [ ] Optional W1 tuning: `RATE_LIMIT_CHAT_PER_MINUTE`, `RATE_LIMIT_PUBLIC_PER_MINUTE`,
      `GEMINI_DAILY_CALL_BUDGET` (defaults 8 / 120 / 1500).

## 5. Error tracking + uptime  *(you create accounts, Claude wires)*
- [ ] Sentry (or similar): create a project, hand Claude the DSN → one-line SDK
      init in the API + worker (new dependency, added at that point).
- [ ] Uptime check (e.g. UptimeRobot, free): monitor `https://<api>/health`.

## 6. Verification pass  *(Claude drives)*
- [ ] `GET /health` 200 on prod.
- [ ] Public smoke: `/api/v1/years` shows prod years; recommendations round-trip.
- [ ] Rate limit: burst > limit from one IP → 429 with Retry-After.
- [ ] Upload a small PDF on the deployed admin panel → worker log shows the job
      → run reaches `needs_mapping`. (This proves the whole loop.)
- [ ] Load test `/recommendations` (~200 requests, rotating X-Forwarded-For) —
      latency snapshot recorded in this doc.

## 7. Aftercare
- [ ] Record the date + versions here.
- [ ] Delete/rotate any connection strings pasted into chats or shells.
