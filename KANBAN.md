# Foresight Studio: Project Kanban Board

This Kanban board tracks the status of all current and future pieces of the Foresight Studio system.

| Backlog | To Do | In Progress | Done |
| :--- | :--- | :--- | :--- |
| [ ] **M1.5: Client Auth Web Gateway** <br> *Build login/signup screens linking to Supabase auth in frontend.* | [ ] **M4.1: Public Anonymized view API** <br> *Create `public_radar_view` SQL structure for headless Replit embeds.* | | [x] **M0.1: SQLite Graph Storage Schema** <br> *Created database schema for Signals, Trends, and Mappings.* |
| [ ] **M2.2: Gradings Analytics Board** <br> *Dashboard detailing total submissions, keepers, and consequence ratios.* | | | [x] **M0.2: Multi-Model Assessment** <br> *Signal scanning via Gemini SDK with heuristic backup paths.* |
| [ ] **M2.3: Lifecycle Term Toggles** <br> *Administrative dials to lock rosters, change invite codes, or disable logins.* | | | [x] **M0.3: Semantic Deduplication Engine** <br> *Sentence-similarity medoid clustering with pure Python TF-IDF fallbacks.* |
| [ ] **M3.1: Futures-Wheel Step Wizard** <br> *Form prompt-guiding 1st, 2nd, and 3rd order relational consequences.* | | | [x] **M0.4: Radar Coordinate Translators** <br> *Convert STEEP category and horizon terms to visual Polar coordinates.* |
| [ ] **M3.3: Interactive Polar Radar Canvas** <br> *Click-to-expand progressively disclosing nodes on HTML/JS polar grids.* | | | [x] **M0.5: Command Line CLICK Shell** <br> *Wiring ingestion, reports, and radars into terminal CLI execution commands.* |
| | | | [x] **M0.6: Integration Validation Suite** <br> *15 programmatic tests covering all CLI processes with 100% success rate.* |
| | | | [x] **M0.7: Project Discovery & Handoff Tracking** <br> *Created `HISTORY.md`; documented repo status, gaps, verification commands, and delegation plan.* |
| | | | [x] **M1.1: Supabase Database Sync** <br> *Added hosted schema migrations, profile tables, terms roster, pgvector node embeddings, and SQL tests.* |
| | | | [x] **M1.2: Database Migration Adapter** <br> *Added SQLite signal-to-Supabase node adapter with deterministic 384-dim embeddings and mocked-client tests.* |
| | | | [x] **M1.3: Git Feature Isolation** <br> *Implemented work in `.worktrees/supabase-saas-transition` on `feature/supabase-saas-transition`.* |
| | | | [x] **M2.1: Multi-Tenant RLS Policies** <br> *Added RLS rules for Administrator, Student, and Subscriber access boundaries.* |
| | | | [x] **M3.2: pgvector Related Node Bar** <br> *Added `surface_related_nodes` pgvector cosine similarity procedure.* |
| | | | [x] **M2.1a: Schema/RLS Hardening Audit** <br> *Added guard triggers for profiles/nodes, signup role hardening, RLS-safe recommender, and schema tests.* |
| | | | [x] **M2.1c: Provenance & Edge Integrity Fixes** <br> *Added first-class node provenance metadata and edge same-term consistency guards.* |
| | | | [x] **M2.1b: Live RLS Policy Tests** <br> *Started local Supabase via Path A, applied migrations, added authenticated grants, and verified role-isolated behavior with live SQL assertions.* |
| [ ] **M2.4: Invite-Code Isolation** <br> *Students can read `terms.invite_code` via `terms_approved_read_own`; move code to admin-only table or student-safe view.* | | | [x] **F1: Quick-Fix Batch (delegated)** <br> *Dynamic report date, removed unused `trends` var, Gemini model → 2.0-flash, `__pycache__` untracked + ignored, hardened `handle_new_user` in migration 000001, new `20260707000006_score_constraints.sql`. Verified: 48/48 tests OK.* |
| | | | [x] **P1: Database Model Revision Plan** <br> *11-task TDD plan: uncertainty/horizon_year, Shadow polarity affordances, verification decoupling, node_events history, edge multiplicity, HNSW, scenario scaffolding + RLS, SQLite parity, dedup rework. `docs/superpowers/plans/2026-07-07-database-model-revision.md`.* |
| [ ] **M2.6: Student Edge Update/Delete Policies** <br> *Students can insert edges but never correct or remove them; add scoped UPDATE/DELETE policies.* | | | [x] **P2: Scenario Builder Tool Plan** <br> *7-feature TDD plan: uncertainty ranker, 2x2 set builder, evidence linking, Shadow Risk Register, wind-tunneling, reports, CLI. `docs/superpowers/plans/2026-07-07-scenario-builder-tool.md`.* |
| [ ] **M1.4: Migration Adapter Integrity (remaining)** <br> *Adapter now maps all new fields, retires node_type='Shadow', and documents the admin-auth requirement — still open: real embeddings (hash vectors poison pgvector), idempotent upsert on source_signal_id, keeper_id remapping to new UUIDs, trends + signal_trend_map migration.* | [ ] **M5.1: Scenario Builder Implementation** <br> *Build the scenario planning tool per P2 plan: scenarios, critical-uncertainty axes, wind-tunneling, shadow risk registers. DB scaffolding is merged-ready on `feature/db-model-revision`.* | | [x] **P1-impl: Database Model Revision (11 tasks)** <br> *Branch `feature/db-model-revision` (1d680f6..0a15cd3): migrations 20260707100000–100007 — uncertainty/horizon_year/assessment provenance, Shadow polarity + shadow_type + mitigation affordances, verification status (retires node_type='Shadow' overload, locks Verified content), edge multiplicity PK, HNSW index, node_events history, scenario scaffolding + split per-role RLS, authenticated grants; SQLite parity + scenario CRUD; uncertainty assessment; adapter mapping; non-destructive idempotent dedup. Per-task reviews + Opus whole-branch review. Verified: 94/94 tests OK + live RLS assertions.* |
| [ ] **M4.3: Controlled Vocabularies** <br> *`geography`/`sector` free-text fragments aggregation; add lookup tables or ISO codes plus GIN index on tags.* | [ ] **M1.5a: Frontend Pilot (staged, handoff-ready)** <br> *Branch `feature/frontend-pilot` created, zero commits. Execute `docs/superpowers/plans/2026-07-08-frontend-pilot.md` (7 tasks: peer-validation migration, supabase-js foundations, session/roles, auth+waiting UI, shell, Signal Entry, live E2E). Cheap subagents for Tasks 1–2 per user directive.* | | [x] **M2.5: Lock Verified Signal Content** <br> *Done in migration 20260707100002: student UPDATE policy requires `verification <> 'Verified'` in USING and WITH CHECK.* |
| | [ ] **M1.5b/c: Frontend Phases 2–3 (planned)** <br> *Phase 2: browser+detail+validation UI, shadow lens (spec §5.3–5.4). Phase 3: admin roster/terms/audit/analytics (§5.5–5.8). Spec: `docs/superpowers/specs/2026-07-08-frontend-v1-design.md`; each phase gets its own plan.* | | [x] **P3: Frontend v1 Design (PRODUCT.md + spec + pilot plan)** <br> *Peer-only validation model (students verify, admins audit), Notion+Observable anchors on DESIGN.md paper palette, 7 surfaces specced, pilot plan with full SQL/zod/test code. Committed 0d23259 + 84f2b57.* |
| [ ] **M1.6: Pipeline Admin Auth for Migration** <br> *`guard_node_write` rejects service-role inserts with verification='Verified' (is_administrator() is auth.uid()-based); run the adapter as an approved Administrator or add a controlled bypass for the migration window.* | | | [x] **M2.7: Score Provenance & Trust** <br> *Done in migrations 100000/100002: `assessed_at`/`assessed_by` columns, guard trigger blocks non-admin changes to verification and assessment provenance.* |
| | | | [x] **M0.8: Non-Destructive Dedup** <br> *Done in Task 11: singletons stay Shadow status with metadata untouched, keeper provenance merged idempotently (stable across repeated runs), duplicates keep their own metadata. Term scoping deferred to SaaS pipeline work.* |
| | | | [x] **M4.2: HNSW Embedding Index** <br> *Done in migration 20260707100003: ivfflat dropped, HNSW cosine index created; edges PK widened to (source, target, relationship_type).* |

---

## Handoff Protocol

Every completed implementation or discovery step must be recorded in both:
1. `HISTORY.md` with date, owner, changes, verification, and next steps.
2. This `KANBAN.md` with the task moved to its current status and any status notes updated.

Never mark Done without verification evidence.

---

## Task Details & Description Cards

### [Done] M0.1 - M0.6: Local Core CLI Engine
*   **Status:** Done ✅
*   **Verification:** All 15 tests passing natively on discovery run.
*   **Description:** Implements database schemas, vector-fallbacks, heuristics scoring, click decorators, and polar projection calculators inside `/src/` and verify E2E programmatic pathways.

### [Done] M0.7: Project Discovery & Handoff Tracking
*   **Status:** Done ✅
*   **Verification:** Documented in `HISTORY.md` and structured running project log.
*   **Description:** Performed comprehensive codebase exploration mapping Python cli, API endpoints, web clients, and worktrees.

### [Done] M1.3: Git Feature Isolation (using-git-worktrees)
*   **Status:** Done ✅
*   **Verification:** Work completed inside `.worktrees/supabase-saas-transition` on branch `feature/supabase-saas-transition`.
*   **Description:** Uses an isolated local feature workspace for the SaaS transition.

### [Done] M1.1: Hosted PostgreSQL Schema Migrations
*   **Status:** Done ✅
*   **Verification:** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"` → 40 tests OK.
*   **Description:** Added Supabase migrations configuring terms, profiles, role enums, nodes, edges, pgvector embeddings, and schema-level indexes.

### [Done] M1.2: Database Migration Script
*   **Status:** Done ✅
*   **Verification:** `tests/test_migration_adapter.py` included in full Python test run → 40 tests OK.
*   **Description:** Added `src/migration_adapter.py` to map local SQLite signals to Supabase node payloads with deterministic 384-length embeddings and mocked-client tests.

### [Done] M2.1: Supabase Row-Level Security Policies
*   **Status:** Done ✅
*   **Verification:** `tests/test_saas_schema.py` validates RLS migration contains helper functions and Administrator/Student/Subscriber policies.
*   **Description:** Configured SQL rules ensuring approved students are term-scoped and subscribers are read-only against verified keeper signals.

### [Done] M3.2: pgvector Related Node Procedure
*   **Status:** Done ✅
*   **Verification:** `tests/test_saas_schema.py` validates `surface_related_nodes(vector(384), float, int)` and pgvector cosine operator usage.
*   **Description:** Added a PostgreSQL function for semantic related-node lookup using pgvector cosine distance.

### [Done] M2.1a: Schema/RLS Hardening Audit
*   **Status:** Done ✅
*   **Verification:** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests/test_saas_schema.py` → 25 tests OK; full Python suite → 45 tests OK.
*   **Description:** Added `20260706000004_rls_hardening.sql` to prevent profile privilege escalation, student self-verification, signup role injection, and pgvector RLS bypass.

### [Done] M2.1b: Live RLS Policy Tests
*   **Status:** Done ✅
*   **Path:** Path A — local Supabase CLI stack.
*   **Verification:** `docker exec -i supabase_db_ForesightStudio psql -U postgres -d postgres -v ON_ERROR_STOP=1 < tests/sql/live_rls_assertions.sql` → `M2.1b live RLS assertions passed`; `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"` → 93 tests OK.
*   **Description:** Installed Supabase CLI, started OrbStack Docker daemon, initialized local Supabase config, applied all migrations, added authenticated table grants, and verified role-isolated behavior for Administrator, Student, Subscriber, and unapproved users.

### [Done] M2.1c: Provenance & Edge Integrity Fixes
*   **Status:** Done ✅
*   **Verification:** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests/test_saas_schema.py tests/test_migration_adapter.py` → 33 tests OK; full Python suite → 48 tests OK.
*   **Description:** Added `20260706000005_provenance_and_edge_integrity.sql`, default migration-adapter `source_metadata` payloads, provenance schema tests, and edge same-term consistency tests.
