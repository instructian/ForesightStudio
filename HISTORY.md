# Foresight Studio — Project History & Handoff Log

This file is the running, handoff-ready record of work on Foresight Studio. Every
completed step is appended here with date, what changed, verification, and next
steps, so any contributor can resume the project at any time.

Companion trackers:
- `KANBAN.md` — board-level task status (Backlog / To Do / In Progress / Done)
- `docs/plans/*.md` — detailed implementation plans

---

## 2026-07-06 — Supabase SaaS Lane A/B implementation

**Owner:** fugu orchestrator with parallel implementation agents

**Branch/worktree:**
- Branch: `feature/supabase-saas-transition`
- Worktree: `.worktrees/supabase-saas-transition`

**What was done:**
- Implemented Lane A: Supabase SQL foundation.
- Implemented Lane B: SQLite-to-Supabase Python migration adapter.
- Updated `KANBAN.md` to mark M1.1, M1.2, M1.3, M2.1, and M3.2 as completed for this milestone.

**Files added/changed:**
- `supabase/migrations/20260706000000_init_saas_schema.sql`
  - Enables `pgvector`.
  - Defines enums: `user_role`, `node_type`, `steep_category`, `horizon_type`, `edge_type`.
  - Creates `terms`, `profiles`, `nodes`, and `edges` tables.
  - Adds indexes including `nodes_embedding_idx` using `ivfflat` + `vector_cosine_ops`.
- `supabase/migrations/20260706000001_auth_sync_triggers.sql`
  - Adds `public.handle_new_user()` and `on_auth_user_created` trigger for Supabase Auth profile creation.
- `supabase/migrations/20260706000002_rls_policies.sql`
  - Adds helper functions for role/approval checks.
  - Enables RLS on `terms`, `profiles`, `nodes`, and `edges`.
  - Adds administrator full-access policies.
  - Adds student term-scoped read/insert/update policies.
  - Adds subscriber read-only verified-signal policies.
- `supabase/migrations/20260706000003_semantic_recommender.sql`
  - Adds `surface_related_nodes(vector(384), float, int)` using pgvector cosine distance.
- `src/migration_adapter.py`
  - Reads current SQLite `signals` rows.
  - Builds Supabase `nodes` payloads.
  - Generates deterministic normalized 384-length embeddings without external ML services.
  - Supports injected Supabase client for testability.
- `tests/test_saas_schema.py`
  - Text-level migration tests with no live Postgres dependency.
- `tests/test_migration_adapter.py`
  - Adapter unit tests using mocked Supabase client and temporary SQLite DB.
- `requirements.txt`
  - Added `supabase>=2.0.0`.

**Verification run:**
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`
  - Result: `Ran 40 tests in 0.026s — OK`
- `pnpm run typecheck`
  - Result: blocked before typecheck by pnpm dependency approval gate:
    `ERR_PNPM_IGNORED_BUILDS Ignored build scripts: esbuild@0.27.3`.
  - This is unrelated to the Python/SQL changes; requires a user-approved `pnpm approve-builds` decision.

**Known limitations / next steps:**
- SQL migrations are verified by static tests only; they have not been applied to a live/local Supabase database yet.
- `src/migration_adapter.py` currently migrates SQLite signals only; trend and edge migration should be a later lane.
- Target `nodes` schema does not include a dedicated provenance JSON column. The adapter can include provenance only when initialized with `node_metadata_field`; consider adding a first-class metadata/provenance column before production migration.
- Next recommended lane: add `public_radar_view` SQL and/or wire Supabase Auth gateway in frontend.
