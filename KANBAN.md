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
