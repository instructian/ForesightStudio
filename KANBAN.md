# Foresight Studio: Project Kanban Board

This Kanban board tracks the status of all current and future pieces of the Foresight Studio system.

| Backlog | To Do | In Progress | Done |
| :--- | :--- | :--- | :--- |
| [ ] **M1.5: Client Auth Web Gateway** <br> *Build login/signup screens linking to Supabase auth in frontend.* | [ ] **M1.1: Supabase Database Sync** <br> *Add hosted schema migrations, profile tables, and terms roster.* | [ ] **M1.3: Git Feature Isolation** <br> *Set up an isolated git worktree branch for SaaS transition.* | [x] **M0.1: SQLite Graph Storage Schema** <br> *Created database schema for Signals, Trends, and Mappings.* |
| [ ] **M2.2: Gradings Analytics Board** <br> *Dashboard detailing total submissions, keepers, and consequence ratios.* | [ ] **M1.2: Database Migration Adapter** <br> *Write a script in `/src/` to adapters and sync current SQLite items.* | | [x] **M0.2: Multi-Model Assessment** <br> *Signal scanning via Gemini SDK with heuristic backup paths.* |
| [ ] **M2.3: Lifecycle Term Toggles** <br> *Administrative dials to lock rosters, change invite codes, or disable logins.* | [ ] **M2.1: Multi-Tenant RLS Policies** <br> *Implement Row-Level Security rule-sets to secure student/subscriber roles.* | | [x] **M0.3: Semantic Deduplication Engine** <br> *Sentence-similarity medoid clustering with pure Python TF-IDF fallbacks.* |
| [ ] **M3.1: Futures-Wheel Step Wizard** <br> *Form prompt-guiding 1st, 2nd, and 3rd order relational consequences.* | [ ] **M4.1: Public Anonymized view API** <br> *Create `public_radar_view` SQL structure for headless Replit embeds.* | | [x] **M0.4: Radar Coordinate Translators** <br> *Convert STEEP category and horizon terms to visual Polar coordinates.* |
| [ ] **M3.2: pgvector Related Node Bar** <br> *Instant semantic recommendations overlay using PostgreSQL vector distances.* | | | [x] **M0.5: Command Line CLICK Shell** <br> *Wiring ingestion, reports, and radars into terminal CLI execution commands.* |
| [ ] **M3.3: Interactive Polar Radar Canvas** <br> *Click-to-expand progressively disclosing nodes on HTML/JS polar grids.* | | | [x] **M0.6: Integration Validation Suite** <br> *15 programmatic tests covering all CLI processes with 100% success rate.* |

---

## Task Details & Description Cards

### [Done] M0.1 - M0.6: Local Core CLI Engine
*   **Status:** Done ✅
*   **Verification:** All 15 tests passing natively on discovery run.
*   **Description:** Implements database schemas, vector-fallbacks, heuristics scoring, click decorators, and polar projection calculators inside `/src/` and verify E2E programmatic pathways.

### [In Progress] M1.3: Git Feature Isolation (using-git-worktrees)
*   **Status:** In Progress 🚧
*   **Description:** Use standard git-worktrees commands to create an isolated local feature workspace `.worktrees/supabase-saas-transition` on a new branch `feature/supabase-saas-transition`.

### [To Do] M1.1: Hosted PostgreSQL Schema Migrations
*   **Status:** To Do 📋
*   **Description:** Build the SQL migration files configuring terms, profiles, user role enums, and tables matching the SaaS specification. Set up `pgvector(384)` index mappings.

### [To Do] M1.2: Database Migration Script
*   **Status:** To Do 📋
*   **Description:** Program a Python migration pipeline matching our local SQLite schemas to remote Postgres APIs.

### [To Do] M2.1: Supabase Row-Level Security Policies
*   **Status:** To Do 📋
*   **Description:** Configure SQL rules ensuring students can edit only appropriate documents under active rosters while locking public enterprise views to verified nodes.
