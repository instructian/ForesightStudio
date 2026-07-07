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

### Recommended execution order

1. Lane A + Lane B in parallel on `feature/supabase-saas-transition`.
2. Orchestrator reviews SQL/RLS + adapter mapping.
3. Lane C to strengthen API validation before storage migration.
4. Lane D to deliver visible product value: Polar Radar Canvas.
5. Lane E for subscriber/provenance workflows.
6. Lane F after each milestone and before handoff.

### Required documentation after each lane

For every completed lane or subtask:
- Append entry to `HISTORY.md` with date, owner/model tier, files changed,
  verification command/output summary, blockers, and next step.
- Move matching item in `KANBAN.md` to In Progress/Done.
- Never mark Done without verification evidence.
