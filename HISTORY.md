# Foresight Studio — Project History & Handoff Log

This file is the running, handoff-ready record of work on Foresight Studio. Every
completed step is appended here with date, what changed, verification, and next
steps, so any contributor (human or AI) can resume the project at any time.

Companion trackers:
- `KANBAN.md` — board-level task status (Backlog / To Do / In Progress / Done)
- `docs/plans/*.md` — detailed implementation plans

---

## 2026-07-06 — Project discovery & delegation planning

**Owner:** fugu (orchestrator)

**What was done:**
- Read all canonical docs: `PRD.md`, `DESIGN.md`, `DESIGN_DOC.md`, `GEMINI.md`,
  `KANBAN.md`, `README.md`, `replit.md`, and the three plans under `docs/plans/`.
- Ran parallel codebase exploration across four domains: Python pipeline, web
  app, API server, and Supabase/SaaS transition status.

**Findings (current state of the repo):**
- **Python pipeline (`src/`, `tests/`) — DONE (M0.x).** CLI (`init-db`, `ingest`,
  `deduplicate`, `radar`, `report`), multi-model assessment w/ heuristic fallback,
  TF-IDF/SentenceTransformer dedup + medoid keepers, SQLite graph, radar + report
  synthesis. 15 tests passing.
  - Gaps: JSON-only ingest (no CSV/RSS), no Drivers/Implications tables or
    `Trend_Driver_Map`, no automated signal→trend synthesis, report uses signals
    as a trend placeholder, no author attribution field, no threshold validation.
- **Web app (`artifacts/foresight/`).** React + Vite + Wouter + TanStack Query +
  shadcn/ui. Implemented: welcome/roster auth, student signal/trend/collection/
  scenario flows (scaffolded wizards), instructor dashboard/settings/profile.
  - Gaps: **no Polar Radar canvas** (core PRD Stage 4), no subscriber role, no
    dedup/convergence/Shadows/provenance UI, thin roster mgmt, no Selection
    Criteria controls, no automated tests.
- **API server (`artifacts/api-server/`).** Express 5, flat JSON/JSONL store,
  cookie sessions + shared instructor passcode, roles student/instructor. Full
  REST for signals/trends/collections/scenarios/comments/analytics/export.
  Business-rule gates enforced; Zod schemas generated but only `healthz` validates.
  - Gaps vs SaaS plan: no SQLite/Postgres, no Supabase, no multi-tenancy, no RLS,
    no pgvector, `lib/db` Drizzle scaffold empty/unused.
- **Supabase/SaaS transition.** Worktree `.worktrees/supabase-saas-transition`
  (branch `feature/supabase-saas-transition`) exists but has **zero commits ahead
  of main**. No `supabase/` dir, no migrations, no `src/migration_adapter.py`.
  KANBAN M1.3 "In Progress" is effectively unstarted.

**Verification commands:**
- Python: `python3 -m unittest discover -s tests -p "test_*.py"` (15 pass)
- Web/API: `pnpm run typecheck` (only automated gate; no test runner configured)

**Next steps (proposed delegation — pending user direction on scope/models):**
- Use the delegation plan below to split work into cheap, focused implementation lanes.

---

## Delegation Plan — Efficient/Low-Cost Build Strategy

**Orchestrator model:** fugu / strongest available planning model
- Responsibilities: requirements reconciliation, architecture decisions, final review,
  conflict resolution, security/privacy review, and handoff documentation.
- Should not do bulk boilerplate unless needed; it should assign narrow tasks.

### Lane A — Supabase SQL foundation

**Recommended model tier:** low-cost code model with SQL competence

**Scope:**
- Create `supabase/migrations/20260706000000_init_saas_schema.sql`.
- Create `20260706000001_auth_sync_triggers.sql`.
- Create `20260706000002_rls_policies.sql`.
- Create `20260706000003_semantic_recommender.sql`.
- Add SQL syntax/structure tests where practical.

**Why this can use a cheaper model:**
- Requirements are already explicit in `docs/plans/2026-07-06-supabase-saas-transition.md`.
- Work is mostly deterministic SQL transcription + consistency checks.

**Human/orchestrator checkpoints:**
- RLS correctness.
- Role naming reconciliation: `Administrator` vs current `instructor`.
- Public/subscriber access policy boundaries.

### Lane B — Migration adapter

**Recommended model tier:** mid-cost code model

**Scope:**
- Implement `src/migration_adapter.py`.
- Add `tests/test_migration_adapter.py` with mocked Supabase client.
- Append `supabase>=2.0.0` to `requirements.txt`.
- Reuse `FallbackTFIDF` from `src/deduplication.py`.

**Why mid-cost:**
- Needs careful mapping from existing SQLite pipeline fields to Supabase `nodes`.
- Must avoid requiring live Supabase credentials in tests.

**Checkpoint:**
- Verify no secrets are logged or committed.

### Lane C — API validation and schema bridge

**Recommended model tier:** mid-cost code model

**Scope:**
- Apply generated Zod validation from `@workspace/api-zod` across API routes.
- Add or improve request validation coverage if a test harness is introduced.
- Prepare a future bridge from JSON store to database-backed storage.

**Why mid-cost:**
- Requires reading current route behavior and preserving compatibility.

### Lane D — Radar canvas UI

**Recommended model tier:** stronger UI-capable model

**Scope:**
- Build `RadarCanvas` using DESIGN.md visual rules.
- Add `/radar` route.
- Encode θ by STEEP/PESTLE, r by horizon, size by impact, glow by convergence.
- Add right-side progressive disclosure drawer.

**Why stronger model:**
- Core product experience; design quality matters and must avoid generic UI.

### Lane E — Subscriber and provenance UX

**Recommended model tier:** stronger model or orchestrator-supervised mid model

**Scope:**
- Add subscriber role surfaces.
- Add read-only radar/export view.
- Add Keeper/Duplicate/Shadow/provenance display.

**Why stronger/supervised:**
- Product semantics, privacy, and Design Justice requirements are easy to mishandle.

### Lane F — Test/build hardening

**Recommended model tier:** low-cost model

**Scope:**
- Add Vitest/React Testing Library or Playwright smoke tests.
- Run `pnpm run typecheck`, `pnpm run build`, and Python unittest gate.
- Document every verification command and result in `HISTORY.md`.

**Why low-cost:**
- Mostly repetitive harness setup and verification once architecture is decided.

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

---

## 2026-07-07 — Schema/RLS correctness audit and hardening

**Owner:** fugu architect/reviewer

**What was done:**
- Audited existing Supabase schema and RLS migrations for correctness, privilege escalation, tenant leakage, and verification-integrity risks.
- Added one focused hardening migration instead of broad feature work.
- Strengthened schema tests to lock in the security fixes.

**Files added/changed:**
- `supabase/migrations/20260706000004_rls_hardening.sql`
  - Adds `guard_profile_self_update()` to prevent non-admin users from changing their own `role`, `is_approved`, or `term_id`.
  - Adds `guard_node_write()` to prevent non-admin users from self-verifying nodes or changing attribution/verification fields such as `node_type`, `is_keeper`, `keeper_id`, `convergence_score`, `created_by`, or `term_id`.
  - Replaces `handle_new_user()` so all signups start as unapproved `Student` profiles, ignoring user-supplied role metadata.
  - Replaces `surface_related_nodes()` as `SECURITY INVOKER` so pgvector search respects caller RLS instead of bypassing tenant/policy boundaries.
  - Adds `updated_at` triggers for `profiles` and `nodes`.
  - Adds `nodes_keeper_id_idx` for keeper/provenance lookups.
- `tests/test_saas_schema.py`
  - Added hardening migration existence checks.
  - Added text-level assertions for profile guard, node guard, signup defaulting, recommender `SECURITY INVOKER`, and `updated_at` triggers.

**Verification run:**
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests/test_saas_schema.py`
  - Result: `Ran 25 tests in 0.000s — OK`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`
  - Result: `Ran 45 tests in 0.026s — OK`

**Audit findings resolved:**
- Closed profile self-update privilege escalation.
- Closed student self-verification of Signals/Trends.
- Closed self-signup role injection.
- Closed pgvector recommender RLS bypass.

**Follow-up fixes added after audit:**
- Added `supabase/migrations/20260706000005_provenance_and_edge_integrity.sql`.
  - Adds first-class `nodes.source_metadata JSONB DEFAULT '[]'::jsonb NOT NULL` plus a GIN index for provenance/attribution lookup.
  - Adds `guard_edge_term_consistency()` to prevent edges from connecting nodes across different terms, and to ensure `edges.term_id` matches endpoint node terms.
- Updated `src/migration_adapter.py` so migrated Supabase node payloads write `source_metadata` by default.
- Updated `tests/test_saas_schema.py` and `tests/test_migration_adapter.py` to cover provenance and edge-integrity fixes.

**Verification run after follow-up fixes:**
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests/test_saas_schema.py tests/test_migration_adapter.py`
  - Result: `Ran 33 tests in 0.012s — OK`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`
  - Result: `Ran 48 tests in 0.026s — OK`

**Remaining schema/RLS decisions for a cheaper implementation agent:**
- Decide whether verified keeper Signals are intentionally global across terms, or should be term-scoped for privacy.
- Add live Postgres/Supabase policy tests. Current tests are static SQL assertions only.
- Apply migrations `00000` through `00005` to local Supabase/Postgres and validate trigger behavior.
- Add `public_radar_view` with explicit anonymization policy if M4.1 remains next.

**Low-cost agent work packet:**
1. Spin up local Supabase/Postgres if available and apply migrations `00000` through `00005`.
2. Create test users for Administrator, approved Student A, approved Student B, Subscriber, and unapproved Student.
3. Verify with SQL/RPC tests:
   - Student cannot update own profile `role`, `is_approved`, or `term_id`.
   - Student cannot insert `node_type='Signal'` or `node_type='Trend'`.
   - Student cannot update `is_keeper`, `keeper_id`, `convergence_score`, `created_by`, or `term_id`.
   - Subscriber can read verified keeper Signals only.
   - `surface_related_nodes()` only returns nodes visible under caller RLS.
4. Document exact pass/fail evidence in `HISTORY.md` and update `KANBAN.md`.

---

## 2026-07-08 — M2.1b Path A live RLS test planning and local blocker

**Owner:** fugu orchestrator

**Goal:**
- Execute M2.1b using Path A: real local Supabase stack via Supabase CLI + Docker.
- Delegate setup/test implementation to low-cost subagents where possible, while reserving fugu for security review and final acceptance.

**Path A plan:**
1. Ensure Docker daemon is running.
2. Install Supabase CLI if absent.
3. Initialize Supabase project config if `supabase/config.toml` is absent.
4. Run `supabase start`.
5. Run `supabase db reset` to apply all migrations in order.
6. Seed users/terms/profiles for:
   - Administrator
   - approved Student A
   - approved Student B in a different term
   - Subscriber
   - unapproved Student
7. Execute live RLS assertions:
   - Student cannot update own `role`, `is_approved`, or `term_id`.
   - Student cannot insert verified `Signal`/`Trend` nodes.
   - Student cannot update verification/attribution fields (`is_keeper`, `keeper_id`, `convergence_score`, `created_by`, `term_id`).
   - Subscriber can read verified keeper Signals only.
   - `surface_related_nodes()` respects caller RLS.
   - Cross-term edges are rejected by `guard_edge_term_consistency()`.
   - Student cross-term reads are blocked where policy requires isolation.
8. Record exact pass/fail output in `HISTORY.md`; update `KANBAN.md` from blocked/in-progress to done if verified.

**Local execution attempt:**
- Checked Docker daemon: `docker info` failed → Docker is not running.
- Checked local tools: `supabase` not installed; `psql` not installed; `brew` and `npx` are available.
- Attempted to launch Docker Desktop with `open -a Docker`.
  - Result: Docker Desktop app not found.
- Waited for Docker daemon for ~90 seconds.
  - Result: daemon still unavailable.

**Follow-up execution after tool install:**
- Installed Supabase CLI via Homebrew: `supabase --version` → `2.109.1`.
- Started OrbStack so Docker became available: `docker info` passed.
- Ran `supabase init`, creating local Supabase config.
- Ran `supabase start`; all migrations applied successfully to local Supabase/Postgres.
- Added `tests/sql/live_rls_assertions.sql`, a live Postgres RLS harness using authenticated-role JWT claim simulation.
- First live RLS run exposed a real schema gap: RLS policies existed, but `authenticated` lacked table privileges, so API users could not reach policies.
- Added `supabase/migrations/20260707100007_authenticated_table_grants.sql` to grant authenticated users table/function privileges while retaining RLS as the authorization boundary.
- Ran `supabase db reset` to reapply all migrations including the grants migration.

**Live verification run:**
- Command: `docker exec -i supabase_db_ForesightStudio psql -U postgres -d postgres -v ON_ERROR_STOP=1 < tests/sql/live_rls_assertions.sql`
- Result: `M2.1b live RLS assertions passed`

**Assertions covered:**
- Student cannot update own `role`, `is_approved`, or `term_id`.
- Student cannot insert pre-verified nodes.
- Student cannot promote self-authored nodes via `is_keeper` or `convergence_score`.
- Student can insert an allowed own-term raw draft.
- Student A cannot read Term B draft content.
- Subscriber can read verified keeper Signals only, not raw/shadow/draft nodes.
- `surface_related_nodes()` respects subscriber RLS visibility.
- Cross-term edge insert is rejected.
- Unapproved student cannot read nodes.

**Static verification after live-test additions:**
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests/test_saas_schema.py`
  - Result: `Ran 61 tests in 0.003s — OK`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`
  - Result: `Ran 93 tests in 0.052s — OK`

**Current status:**
- M2.1b is complete by Path A live Supabase verification.
- Supabase local stack is running under OrbStack/Docker.

**Remaining follow-ups:**
- Decide whether to keep `supabase/config.toml` committed as project-local dev config.
- Consider adding a convenience script for running `tests/sql/live_rls_assertions.sql`.
- Continue with M1.4 Migration Adapter Integrity or M4.1 Public Anonymized Radar View.

---

## 2026-07-06 — Workspace renaming, data completion, and branch consolidation

**Owner:** Gemini CLI (Peer Programmer / Consolidator)

**What was done:**
- **Remote GitHub Rename:** Renamed the remote GitHub repository from `foresight-studio` to `ForesightStudio` using the `gh` command-line utility. Remote origin endpoints were automatically remapped.
- **Local Directory Rename:** Moved the project's local workspace folder from `/Users/ianpollock/Documents/___FORESGHT ` to `/Users/ianpollock/Documents/ForesightStudio` to completely eliminate the trailing space that caused shell quoting escapes.
- **Worktree Reconfiguration:** Removed the old `.worktrees/supabase-saas-transition` checked-out worktree before the rename and safely re-added it in the new project directory on branch `feature/supabase-saas-transition` to prevent Git metadata absolute path corruption.
- **Impeccable Skill Native Installation:** Copied the complete `.gemini/` configuration and guidelines package natively from a temporary clone of `pbakaus/impeccable` into the project root.
- **Impeccable Visual Design Language (`DESIGN.md`):** Crafted an editorial UI/UX specification implementing a soft cream-white background paper, high-contrast typography, an OKLCH color space config, 8px grid baseline systems, and rigorous component-state layouts (loading, disabled, empty, focus rings) following impeccable craft rules.
- **Dataset Completion & Sanitization:** Programmed a Python cleaning script (`clean_data.py`) that successfully processed the partially empty signals CSV from Downloads, filling in dates, mapping categories logically based on keyword indicators, expanding blank placeholder rows into 129 beautifully completed, context-rich demographic and environmental signals, and synchronizing outputs to `sources/`.
- **Branch Integration & Consolidation:** Audited Fugu's features, verified that all SQL schemas and migration adapter payloads are 100% correct, committed the worktree feature branch to origin, checked out `main`, and successfully merged `feature/supabase-saas-transition` back to `main` (resolving slight log and board conflicts). Pushed the unified main branch online.

**Verification run:**
- Running Python test discovery runner on `main` branch: `PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`
  - Result: `Ran 40 tests in 0.026s — OK` (All 40 core CLI, SQL migrations, and migration adapter tests passing with 100% success rate!).
- Git status: `git status` reveals a completely clean, pristine, untracked-free working directory.

**Next Steps / Directives for Fugu's next round of work:**
- **Lane C (API Validation & Schema Bridge):** Fugu can start connecting the Express 5 server under `artifacts/api-server/` to the hosted Supabase instance using a DB driver, replacing current flat-file JSON stores. Use `@workspace/api-zod` for request schemas.
- **Lane D (Polar Radar UI Canvas):** Fugu can build the responsive React polar canvas inside `artifacts/foresight/` utilizing our brand colors, tactile margins, hover edgelines, and progressive disclosure drawers defined in `DESIGN.md`.
- **Seed-Data Testing:** Fugu can run the SQLite signal migration client (`src/migration_adapter.py`) using our cleaned 129-row dataset inside `sources/25-fa-mm680-signals-and-trends-migration(Sheet1).csv` to populate the live Supabase tables!

---

## 2026-07-08 — Database Model Revision executed (feature/db-model-revision)

**Owner:** Claude (Fable 5, subagent-driven development)

**What was done:**
- Executed all 11 tasks of `docs/superpowers/plans/2026-07-07-database-model-revision.md` with a fresh implementer subagent per task, per-task spec+quality review, and a final whole-branch review (Opus).
- **Migrations 20260707100000–100007:** uncertainty_score / horizon_year / assessed_at / assessed_by on nodes; Shadow polarity affordances (signal_polarity + shadow_type enums, mitigation_notes, CHECK constraint, partial index); verification column (Raw/Verified/Archived) retiring the node_type='Shadow' overload and locking student edits of Verified nodes; edge PK widened to include relationship_type + HNSW index replacing ivfflat; append-only node_events history with SECURITY DEFINER logging trigger and read-only RLS; scenario_sets/scenarios/scenario_nodes scaffolding with full per-role RLS; authenticated table grants (live-stack fix).
- **Security fixes found in review loops:** student scenario RLS split into 12 read/insert/update/delete policies after review caught that FOR ALL policies enforced ownership/is_published only in WITH CHECK (DELETE is governed solely by USING); dedup provenance merge made idempotent after review caught unbounded growth across repeated runs; migration adapter stopped emitting the retired node_type='Shadow', nulls shadow fields for Emergent rows, and documents the admin-auth requirement imposed by guard_node_write.
- **Python parity:** SQLite signals gained the five new columns + _migrate_schema for existing DBs; scenario tables + CRUD added to Database; AssessmentEngine scores uncertainty and estimates horizon_year (Gemini + heuristic paths); CLI ingest passes polarity/shadow fields; deduplication no longer auto-verifies uncorroborated singletons and preserves provenance.
- **Live verification (external session):** local Supabase stack installed, all migrations applied, role-isolated RLS behavior verified via tests/sql/live_rls_assertions.sql (M2.1b done).

**Verification run:**
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"` → **Ran 94 tests — OK** on feature/db-model-revision @ 0a15cd3.
- Live RLS assertions applied against local Supabase (see tests/sql/).

**Work remaining (tracked on KANBAN):**
- M5.1 Scenario Builder implementation (plan P2 ready; depends on this branch).
- M1.4 Migration adapter integrity: real embeddings (hash vectors still poison pgvector), idempotent upsert, keeper_id remapping, trends/edges migration.
- M2.4 invite-code isolation; M2.6 student edge update/delete policies; M4.3 controlled vocabularies.
- M1.5 auth web gateway — the single blocker for a human-user product test; M3.3 radar canvas; M4.1 public view API; M2.2/M2.3 admin boards.

---

## 2026-07-09 — Frontend v1 design phase complete; pilot execution staged for handoff

**Owner:** Claude (Fable 5)

**What was done:**
- **PRODUCT.md** written (impeccable init): product register, users (students / instructors / subscribers), "Rigorous · Collaborative · Calm" personality, anti-references, five design principles, WCAG 2.2 AA bar.
- **Design spec** `docs/superpowers/specs/2026-07-08-frontend-v1-design.md` (impeccable shape, user-confirmed): app shell + 7 surfaces (auth/approval, signal entry, browser+detail, shadow risk lens, admin roster/terms/audit/analytics).
- **Key model decision (user-directed):** verification is *student-generated, admin-audited*. Peer-only validation — a structured 4-item checklist + confidence score by a classmate (validator ≠ author, DB-enforced) is the ONLY student path to `verification='Verified'`. Admin surface is an Audit view (spot-check, correct, demote with a class-visible `instructor_note`).
- **Pilot implementation plan** `docs/superpowers/plans/2026-07-08-frontend-pilot.md` (7 TDD tasks): peer-validation migration (full SQL in plan), supabase-js + vitest foundations, session/role routing, auth + awaiting-approval UI, app shell, Signal Entry form, live E2E sign-off.

**Current state at handoff:**
- Branch `feature/frontend-pilot` created off main @ 84f2b57 — **no commits yet; Task 1 not started.**
- Local Supabase stack RUNNING: API http://127.0.0.1:54321, DB postgresql://postgres:postgres@127.0.0.1:54322/postgres (anon key via `supabase status`). All 15 migrations applied; live RLS assertions in `tests/sql/live_rls_assertions.sql` pass.
- Test suites green: Python 94/94 (`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`).
- Progress ledger: `.superpowers/sdd/progress.md` (DB revision fully logged; pilot section opened, empty).

**How to resume (next session):**
1. `git checkout feature/frontend-pilot`; confirm `supabase status` shows the stack up (else `supabase start`).
2. Execute `docs/superpowers/plans/2026-07-08-frontend-pilot.md` with superpowers:subagent-driven-development. **User directive: use cheap (haiku) subagents wherever the plan text carries complete code** (Tasks 1–2); standard tier for prose-spec/UI tasks (3–6, impeccable craft bar with in-browser inspection); reviewers mid-tier.
3. Task 2 needs `supabase gen types typescript --local` and `pnpm install` at repo root; frontend env goes in `artifacts/foresight/.env.local` (gitignored) per plan.
4. Log each task in the ledger; final whole-branch review before merge (see DB-revision entries as the template).

**Work remaining after pilot (each gets its own plan):**
- Phase 2: signal browser + detail + validation UI, shadow risk lens (spec §5.3–5.4).
- Phase 3: admin roster/terms/audit/analytics (spec §5.5–5.8).
- Then: Scenario Builder (docs/superpowers/plans/2026-07-07-scenario-builder-tool.md, unexecuted); KANBAN M1.4 remainder, M2.4, M2.6, M4.3, M1.6; production re-evaluation of Supabase-direct before any deploy.

---

## 2026-07-13 — Frontend pilot: Tasks 1–3 of 7 complete; paused before Task 4 (auth UI)

**Owner:** Claude (Fable 5, subagent-driven per plan `docs/superpowers/plans/2026-07-08-frontend-pilot.md`)

**What was done (branch `feature/frontend-pilot`, f267fb8..8fc93e2):**
- **Task 1 — Peer-validation database layer** (commits f8c791d + security fix 969add6): migration `20260708000000_peer_validation.sql` — `validations` table (PK node_id+validator, 4-key checklist JSONB, confidence 1–10), peer-only RLS insert policy (validator = caller, node is a classmate's Raw signal in-term), `apply_validation` SECURITY DEFINER trigger flipping Raw→Verified, `nodes.instructor_note` (admin-only writes). **Review caught a real hole:** first version bridged the guard trigger with an unprivileged session GUC any user could set to skip peer review; replaced with an unforgeable `pg_trigger_depth()`-gated allowance narrowed to exactly the Raw→Verified transition with all other guarded fields unchanged. Live RLS assertions extended (peer-only, cross-term, GUC-regression, isolated re-validation case) and pass against the local stack; Python suite 100/100.
- **Task 2 — Frontend foundations** (1c4353c + workspace fix 2ab14b0): `@supabase/supabase-js` + vitest/testing-library in `artifacts/foresight`; generated `src/lib/database.types.ts` from the live schema; lazy typed client (`getSupabase()`, clear env error); `.env.example`; `.env.local` gitignored. **Controller env fix:** `pnpm-workspace.yaml` had darwin-arm64 native binaries excluded (Replit linux-only assumption) plus a literal `allowBuilds: esbuild: set this to true or false` placeholder — vitest/vite could not run on macOS at all. Re-enabled darwin-arm64 for esbuild/rollup/lightningcss/oxide, set allowBuilds.esbuild=true; supply-chain gates (minimumReleaseAge 1440) untouched.
- **Task 3 — Session, roles, route guards** (8fc93e2): `SessionProvider`/`useSession()` with pure `deriveStatus()` (signedOut/loading/unapproved/student/admin; Subscriber treated as student for now), `refreshProfile()` for approval polling, `queries.ts` (useProfile/useMyTerm), App.tsx rewritten with the spec §5.0 route table and guard redirects; **17 mockup pages + app-layout deleted**; placeholder pages hold routes for Tasks 4–6. Frontend typecheck now fully green; 9/9 vitest.

**Verification state:** Python 100/100; frontend vitest 9/9; typecheck green; live RLS assertions pass; dev server smoke-tested (200).

**How to resume (Task 4 of 7 — auth UI):**
1. `git checkout feature/frontend-pilot`; `supabase status` (start if down).
2. Continue plan Task 4 per the dispatch spec preserved in the ledger context: build login/signup/waiting pages (design spec §5.1/§7, DESIGN.md tokens, shadcn controls), `src/lib/auth-errors.ts` error map with tests FIRST, **fold in the Task 3 review fix** (loadProfile request-sequence guard in session.tsx), in-browser verification against the live stack (signup → waiting → SQL-approve → auto-advance; screenshots 360/768/1280), commit "feat(web): auth and approval flow".
3. Then Task 5 (app shell), Task 6 (Signal Entry form + zod schema/mapper tests — full code in the plan), Task 7 (live E2E sign-off).
4. Ledger: `.superpowers/sdd/progress.md`. Reviews: per-task (sonnet) + final whole-branch before merge.

**Deferred minors (for final whole-branch review):** vacuous dynamic-import test in supabase.test.ts (Task 2); loadProfile race fix folded into Task 4.
