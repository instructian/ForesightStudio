# Foresight Studio: Project Kanban Board

This Kanban board tracks the status of all current and future pieces of the Foresight Studio system.

| Backlog | To Do | In Progress | Done |
| :--- | :--- | :--- | :--- |
| [ ] **M1.5: Client Auth Web Gateway** <br> *Build login/signup screens linking to Supabase auth in frontend.* | [ ] **M4.1: Public Anonymized view API** <br> *Create `public_radar_view` SQL structure for headless Replit embeds.* | | [x] **M0.1: SQLite Graph Storage Schema** <br> *Created database schema for Signals, Trends, and Mappings.* |
| [ ] **M2.2: Gradings Analytics Board** <br> *Dashboard detailing total submissions, keepers, and consequence ratios.* | | | [x] **M0.2: Multi-Model Assessment** <br> *Signal scanning via Gemini SDK with heuristic backup paths.* |
| [ ] **M2.3: Lifecycle Term Toggles** <br> *Administrative dials to lock rosters, change invite codes, or disable logins.* | | | [x] **M0.3: Semantic Deduplication Engine** <br> *Sentence-similarity medoid clustering with pure Python TF-IDF fallbacks.* |
| [ ] **M3.1: Futures-Wheel Step Wizard** <br> *Form prompt-guiding 1st, 2nd, and 3rd order relational consequences.* | | | [x] **M0.4: Radar Coordinate Translators** <br> *Convert STEEP category and horizon terms to visual Polar coordinates.* |
| [ ] **M3.3: Interactive Polar Radar Canvas** <br> *Click-to-expand progressively disclosing nodes on HTML/JS polar grids.* | [ ] **M2.1b: Live RLS Policy Tests** <br> *Apply migrations to local Supabase/Postgres and verify role-isolated behavior with real users.* | | [x] **M0.5: Command Line CLICK Shell** <br> *Wiring ingestion, reports, and radars into terminal CLI execution commands.* |
| | | | [x] **M0.6: Integration Validation Suite** <br> *15 programmatic tests covering all CLI processes with 100% success rate.* |
| | | | [x] **M0.7: Project Discovery & Handoff Tracking** <br> *Created `HISTORY.md`; documented repo status, gaps, verification commands, and delegation plan.* |
| | | | [x] **M1.1: Supabase Database Sync** <br> *Added hosted schema migrations, profile tables, terms roster, pgvector node embeddings, and SQL tests.* |
| | | | [x] **M1.2: Database Migration Adapter** <br> *Added SQLite signal-to-Supabase node adapter with deterministic 384-dim embeddings and mocked-client tests.* |
| | | | [x] **M1.3: Git Feature Isolation** <br> *Implemented work in `.worktrees/supabase-saas-transition` on `feature/supabase-saas-transition`.* |
| | | | [x] **M2.1: Multi-Tenant RLS Policies** <br> *Added RLS rules for Administrator, Student, and Subscriber access boundaries.* |
| | | | [x] **M3.2: pgvector Related Node Bar** <br> *Added `surface_related_nodes` pgvector cosine similarity procedure.* |
| | | | [x] **M2.1a: Schema/RLS Hardening Audit** <br> *Added guard triggers for profiles/nodes, signup role hardening, RLS-safe recommender, and schema tests.* |
| | | | [x] **M2.1c: Provenance & Edge Integrity Fixes** <br> *Added first-class node provenance metadata and edge same-term consistency guards.* |
| [ ] **M2.4: Invite-Code Isolation** <br> *Students can read `terms.invite_code` via `terms_approved_read_own`; move code to admin-only table or student-safe view.* | | | [x] **F1: Quick-Fix Batch (delegated)** <br> *Dynamic report date, removed unused `trends` var, Gemini model → 2.0-flash, `__pycache__` untracked + ignored, hardened `handle_new_user` in migration 000001, new `20260707000006_score_constraints.sql`. Verified: 48/48 tests OK.* |
| [ ] **M2.5: Lock Verified Signal Content** <br> *Superseded by DB Revision Plan Task 3 (`verification <> 'Verified'` in student UPDATE policy).* | | | [x] **P1: Database Model Revision Plan** <br> *11-task TDD plan: uncertainty/horizon_year, Shadow polarity affordances, verification decoupling, node_events history, edge multiplicity, HNSW, scenario scaffolding + RLS, SQLite parity, dedup rework. `docs/superpowers/plans/2026-07-07-database-model-revision.md`.* |
| [ ] **M2.6: Student Edge Update/Delete Policies** <br> *Students can insert edges but never correct or remove them; add scoped UPDATE/DELETE policies.* | | | [x] **P2: Scenario Builder Tool Plan** <br> *7-feature TDD plan: uncertainty ranker, 2x2 set builder, evidence linking, Shadow Risk Register, wind-tunneling, reports, CLI. `docs/superpowers/plans/2026-07-07-scenario-builder-tool.md`.* |
| [ ] **M2.7: Score Provenance & Trust** <br> *Client-supplied impact/confidence/novelty scores are indistinguishable from pipeline-assessed ones; add `assessed_by`/`assessed_at` or service-role-only scoring.* | | | |
| [ ] **M1.4: Migration Adapter Integrity** <br> *Replace SHA-256 hash pseudo-embeddings (poison pgvector space), make migration idempotent (upsert on source_signal_id), remap keeper_id to new UUIDs, migrate trends + signal_trend_map.* | | | |
| [ ] **M0.8: Non-Destructive Term-Scoped Dedup** <br> *Dedup overwrites source_metadata, resets convergence, auto-elevates uncorroborated singletons to Signal, and clusters across terms; rework as append-only Aggregates edges with term scoping.* | | | |
| [ ] **M4.2: HNSW Embedding Index** <br> *Replace premature `ivfflat lists=100` with HNSW cosine index.* | | | |
| [ ] **M4.3: Controlled Vocabularies** <br> *`geography`/`sector` free-text fragments aggregation; add lookup tables or ISO codes plus GIN index on tags.* | | | |
| [ ] **M5.1: Scenario Builder Implementation** <br> *Build the scenario planning tool per P2 plan: scenarios, critical-uncertainty axes, wind-tunneling, shadow risk registers.* | | | |

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

### [To Do] M2.1b: Live RLS Policy Tests
*   **Status:** To Do 📋
*   **Description:** Apply migrations `00000` through `00005` to local Supabase/Postgres and verify actual role-isolated behavior for Administrator, Student, Subscriber, and unapproved users.

### [Done] M2.1c: Provenance & Edge Integrity Fixes
*   **Status:** Done ✅
*   **Verification:** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests/test_saas_schema.py tests/test_migration_adapter.py` → 33 tests OK; full Python suite → 48 tests OK.
*   **Description:** Added `20260706000005_provenance_and_edge_integrity.sql`, default migration-adapter `source_metadata` payloads, provenance schema tests, and edge same-term consistency tests.
