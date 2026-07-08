# Database Model Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Revise the Foresight Studio data model to support scenario planning: add the uncertainty dimension, first-class Shadow (decline/risk) affordances, verification status decoupled from node type, signal history, edge multiplicity, and scenario scaffolding tables — in both the Supabase (SaaS) and SQLite (local pipeline) layers.

**Architecture:** Seven new idempotent Supabase migrations (numbered `20260707100000`–`20260707100006`) extend the existing `nodes`/`edges` schema and add `scenario_sets`/`scenarios`/`scenario_nodes` and `node_events`. The local SQLite layer (`src/database.py`) gains parity columns and scenario tables so the CLI pipeline keeps working offline. Schema correctness is verified with the repo's established text-parsing tests (`tests/test_saas_schema.py`) plus behavioral SQLite tests (`tests/test_database.py`).

**Tech Stack:** PostgreSQL 16 / Supabase (RLS, pgvector, plpgsql triggers), SQLite 3 via Python `sqlite3`, Python 3.12 `unittest`.

## Global Constraints

- All Supabase migrations must be idempotent (re-runnable): `IF NOT EXISTS`, `DROP ... IF EXISTS` before `CREATE`, and `DO $$ ... EXCEPTION WHEN duplicate_object THEN NULL; END $$` for enums — matching the style of `20260706000000_init_saas_schema.sql`.
- Every new table with user data MUST have RLS enabled in the same migration series that creates it. Policies are `TO authenticated`; anon gets nothing.
- Helper functions `public.is_administrator()`, `public.is_student()`, `public.is_subscriber()`, `public.current_user_term_id()` already exist (migration `20260706000002`) — reuse them, do not redefine.
- Test command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"` from repo root. The full suite must pass after every task.
- Score columns use INTEGER 1–10 with CHECK constraints; new assessment columns are NULLable (NULL = "not yet assessed") — do NOT default them to 5, that is the defect this plan removes.
- Domain vocabulary (use exactly): **Shadow** = a weak signal of a declining system, obsolete behavior, or unwanted "worst-case"/disrupted future (captured to prevent strategic blind spots). **Emergent** = a weak signal of a growing/appearing phenomenon. **Verification** = whether the pipeline/instructor has validated a node (`Raw`/`Verified`/`Archived`) — this is now independent of node type and polarity.

### Background: the "Shadow" naming collision (read before Task 2)

The current schema overloads `node_type = 'Shadow'` to mean "raw, unverified, or demoted-duplicate scanning point." The product definition of Shadow (above) is about *decline polarity*, not verification state. This plan resolves the collision:

- `polarity` column (`Emergent` | `Shadow`) carries the futures meaning.
- `verification` column (`Raw` | `Verified` | `Archived`) carries the pipeline meaning.
- `node_type = 'Shadow'` enum value is retired (rows backfilled to `Signal`); Postgres cannot drop enum values, so the value remains in the type but must never be written again.

---

### Task 1: Assessment dimensions migration (uncertainty, horizon year, assessment provenance)

**Files:**
- Create: `supabase/migrations/20260707100000_assessment_dimensions.sql`
- Modify: `tests/test_saas_schema.py` (append new test class + filename constant)

**Interfaces:**
- Produces: `nodes.uncertainty_score` (INTEGER NULL, CHECK 1–10), `nodes.horizon_year` (INTEGER NULL, CHECK 2020–2200), `nodes.assessed_at` (TIMESTAMPTZ NULL), `nodes.assessed_by` (VARCHAR(100) NULL — model name or 'human:<uuid>'). Tasks 8–10 and the Scenario Builder plan depend on `uncertainty_score` and `horizon_year` by these exact names.

- [x] **Step 1: Write the failing test.** Append to `tests/test_saas_schema.py` (add constant near the other filename constants):

```python
ASSESSMENT_DIMENSIONS = "20260707100000_assessment_dimensions.sql"


class TestAssessmentDimensions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(ASSESSMENT_DIMENSIONS)

    def test_uncertainty_score_column(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS uncertainty_score INTEGER", self.sql)
        self.assertIn("uncertainty_score BETWEEN 1 AND 10", self.sql)

    def test_horizon_year_column(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS horizon_year INTEGER", self.sql)
        self.assertIn("horizon_year BETWEEN 2020 AND 2200", self.sql)

    def test_assessment_provenance_columns(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS assessed_at TIMESTAMP WITH TIME ZONE", self.sql)
        self.assertIn("ADD COLUMN IF NOT EXISTS assessed_by VARCHAR(100)", self.sql)

    def test_no_default_five(self):
        self.assertNotIn("uncertainty_score INTEGER DEFAULT", self.sql)
```

Also add `ASSESSMENT_DIMENSIONS` to the tuple in `test_all_migration_files_present`.

- [x] **Step 2: Run to verify it fails.** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests.test_saas_schema -v` — expect FAIL (missing migration file).

- [x] **Step 3: Write the migration** `supabase/migrations/20260707100000_assessment_dimensions.sql`:

```sql
-- Scenario planning needs impact x uncertainty; the schema previously had no
-- uncertainty dimension on nodes (it was lost when SQLite trends were folded
-- into the unified nodes table). NULL means "not yet assessed" — deliberately
-- no DEFAULT so unassessed nodes cannot contaminate analytics.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS uncertainty_score INTEGER;
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS nodes_uncertainty_score_range;
ALTER TABLE nodes ADD CONSTRAINT nodes_uncertainty_score_range
    CHECK (uncertainty_score IS NULL OR uncertainty_score BETWEEN 1 AND 10);

-- Relative horizons (Near/Mid/Long) decay in meaning over time; anchor with
-- an estimated calendar year.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS horizon_year INTEGER;
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS nodes_horizon_year_range;
ALTER TABLE nodes ADD CONSTRAINT nodes_horizon_year_range
    CHECK (horizon_year IS NULL OR horizon_year BETWEEN 2020 AND 2200);

-- Assessment provenance: distinguishes pipeline-scored from self-scored nodes.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS assessed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS assessed_by VARCHAR(100);
```

- [x] **Step 4: Run tests to verify pass.** Same command as Step 2 → all pass; then run the full suite.

- [x] **Step 5: Commit.** `git add supabase/migrations/20260707100000_assessment_dimensions.sql tests/test_saas_schema.py && git commit -m "feat(db): add uncertainty, horizon_year, and assessment provenance to nodes"`

---

### Task 2: Shadow affordances migration (polarity, shadow_type, mitigation)

**Files:**
- Create: `supabase/migrations/20260707100001_shadow_affordances.sql`
- Modify: `tests/test_saas_schema.py`

**Interfaces:**
- Produces: `nodes.polarity` (`signal_polarity` enum `'Emergent'|'Shadow'`, NOT NULL DEFAULT `'Emergent'`), `nodes.shadow_type` (`shadow_type` enum `'Declining-System'|'Obsolete-Behavior'|'Worst-Case-Future'|'Disruption'`, NULL), `nodes.mitigation_notes` (TEXT NULL). Constraint `shadow_fields_require_shadow_polarity` guarantees shadow-only fields are NULL on Emergent nodes. The Scenario Builder's Shadow Risk Register queries `polarity = 'Shadow'`.

- [x] **Step 1: Write the failing test.** Append to `tests/test_saas_schema.py`:

```python
SHADOW_AFFORDANCES = "20260707100001_shadow_affordances.sql"


class TestShadowAffordances(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(SHADOW_AFFORDANCES)

    def test_polarity_enum(self):
        self.assertIn("CREATE TYPE signal_polarity AS ENUM ('Emergent', 'Shadow')", self.sql)

    def test_shadow_type_enum(self):
        self.assertIn(
            "CREATE TYPE shadow_type AS ENUM ('Declining-System', 'Obsolete-Behavior', 'Worst-Case-Future', 'Disruption')",
            self.sql,
        )

    def test_polarity_column_not_null_default_emergent(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS polarity signal_polarity", self.sql)
        self.assertIn("'Emergent'::signal_polarity NOT NULL", self.sql)

    def test_shadow_fields_constraint(self):
        self.assertIn("shadow_fields_require_shadow_polarity", self.sql)
        self.assertIn("polarity = 'Shadow'", self.sql)

    def test_shadow_partial_index(self):
        self.assertIn("nodes_shadow_polarity_idx", self.sql)
```

Add `SHADOW_AFFORDANCES` to `test_all_migration_files_present`.

- [x] **Step 2: Run to verify FAIL** (missing file).

- [x] **Step 3: Write the migration** `supabase/migrations/20260707100001_shadow_affordances.sql`:

```sql
-- Shadows are weak signals of declining systems, obsolete behaviors, and
-- unwanted "worst-case" or disrupted futures. Capturing them prevents
-- strategic blind spots and lets organizations mitigate risks early.
-- Polarity is orthogonal to verification: a Shadow can be Raw or Verified.
DO $$
BEGIN
    CREATE TYPE signal_polarity AS ENUM ('Emergent', 'Shadow');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE shadow_type AS ENUM ('Declining-System', 'Obsolete-Behavior', 'Worst-Case-Future', 'Disruption');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE nodes ADD COLUMN IF NOT EXISTS polarity signal_polarity
    DEFAULT 'Emergent'::signal_polarity NOT NULL;
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS shadow_type shadow_type;
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS mitigation_notes TEXT;

ALTER TABLE nodes DROP CONSTRAINT IF EXISTS shadow_fields_require_shadow_polarity;
ALTER TABLE nodes ADD CONSTRAINT shadow_fields_require_shadow_polarity
    CHECK (polarity = 'Shadow' OR (shadow_type IS NULL AND mitigation_notes IS NULL));

CREATE INDEX IF NOT EXISTS nodes_shadow_polarity_idx ON nodes(polarity)
    WHERE polarity = 'Shadow';
```

- [x] **Step 4: Run tests → pass; run full suite.**

- [x] **Step 5: Commit.** `git commit -m "feat(db): first-class Shadow polarity, shadow_type, and mitigation affordances"`

---

### Task 3: Verification status migration (resolve node_type='Shadow' overload, lock verified content)

**Files:**
- Create: `supabase/migrations/20260707100002_verification_status.sql`
- Modify: `tests/test_saas_schema.py`

**Interfaces:**
- Produces: `nodes.verification` (`verification_status` enum `'Raw'|'Verified'|'Archived'`, NOT NULL DEFAULT `'Raw'`). Recreated RLS policies gate subscriber/student reads on `verification = 'Verified'` instead of `node_type = 'Signal'`. Student UPDATE policy now excludes Verified nodes (closes the "author edits verified content" hole). `public.guard_node_write()` additionally protects `verification` and `assessed_at`/`assessed_by`.
- Consumes: `polarity` from Task 2 (backfill maps old `node_type='Shadow'` rows).

- [x] **Step 1: Write the failing test.** Append to `tests/test_saas_schema.py`:

```python
VERIFICATION_STATUS = "20260707100002_verification_status.sql"


class TestVerificationStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(VERIFICATION_STATUS)

    def test_verification_enum(self):
        self.assertIn("CREATE TYPE verification_status AS ENUM ('Raw', 'Verified', 'Archived')", self.sql)

    def test_backfill_from_node_type(self):
        self.assertIn("UPDATE nodes SET verification", self.sql)
        self.assertIn("node_type = 'Signal'", self.sql)

    def test_retires_shadow_node_type(self):
        self.assertIn("SET node_type = 'Signal'", self.sql)
        self.assertIn("WHERE node_type = 'Shadow'", self.sql)

    def test_policies_use_verification(self):
        self.assertIn("nodes_subscriber_read_verified_signals", self.sql)
        self.assertIn("verification = 'Verified'", self.sql)

    def test_student_update_excludes_verified(self):
        self.assertIn("nodes_student_update_own_term", self.sql)
        self.assertIn("verification <> 'Verified'", self.sql)

    def test_guard_protects_verification(self):
        self.assertIn("NEW.verification IS DISTINCT FROM OLD.verification", self.sql)
```

Add `VERIFICATION_STATUS` to `test_all_migration_files_present`.

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Write the migration** `supabase/migrations/20260707100002_verification_status.sql`:

```sql
-- Decouple verification state from node structure. Historically
-- node_type='Shadow' meant "raw/unverified", colliding with the product
-- meaning of Shadow (decline-polarity signal, see 20260707100001).
-- After this migration node_type='Shadow' is retired (enum value remains,
-- Postgres cannot drop it — never write it again).
DO $$
BEGIN
    CREATE TYPE verification_status AS ENUM ('Raw', 'Verified', 'Archived');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE nodes ADD COLUMN IF NOT EXISTS verification verification_status;

UPDATE nodes SET verification =
    CASE WHEN node_type = 'Signal' AND is_keeper THEN 'Verified'::verification_status
         ELSE 'Raw'::verification_status END
WHERE verification IS NULL;

-- Old-world "Shadow" rows were raw scanning points, not decline signals:
-- restore their structural type and leave polarity as-is (default Emergent;
-- curators reclassify true decline signals via polarity).
UPDATE nodes SET node_type = 'Signal' WHERE node_type = 'Shadow';

ALTER TABLE nodes ALTER COLUMN verification SET DEFAULT 'Raw'::verification_status;
ALTER TABLE nodes ALTER COLUMN verification SET NOT NULL;

CREATE INDEX IF NOT EXISTS nodes_verification_idx ON nodes(verification, is_keeper);

-- Recreate read policies on verification instead of node_type.
DROP POLICY IF EXISTS nodes_subscriber_read_verified_signals ON nodes;
CREATE POLICY nodes_subscriber_read_verified_signals ON nodes
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND is_keeper = true
        AND verification = 'Verified'
    );

DROP POLICY IF EXISTS nodes_student_read_term_or_verified_signals ON nodes;
CREATE POLICY nodes_student_read_term_or_verified_signals ON nodes
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND (
            (is_keeper = true AND verification = 'Verified')
            OR term_id = public.current_user_term_id()
        )
    );

-- Close the post-verification content-mutation hole: students may no longer
-- edit nodes once they are Verified.
DROP POLICY IF EXISTS nodes_student_update_own_term ON nodes;
CREATE POLICY nodes_student_update_own_term ON nodes
    FOR UPDATE TO authenticated
    USING (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND verification <> 'Verified'
    )
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND verification <> 'Verified'
    );

-- Extend the write guard: verification and assessment provenance are owned
-- by the pipeline/administrators.
CREATE OR REPLACE FUNCTION public.guard_node_write()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    IF public.is_administrator() THEN
        RETURN NEW;
    END IF;

    IF TG_OP = 'INSERT' THEN
        IF NEW.node_type = 'Trend' THEN
            RAISE EXCEPTION 'Not authorized to create Trend nodes';
        END IF;
        IF NEW.verification IS DISTINCT FROM 'Raw'::verification_status THEN
            RAISE EXCEPTION 'Not authorized to create pre-verified nodes';
        END IF;
        IF NEW.assessed_at IS NOT NULL OR NEW.assessed_by IS NOT NULL THEN
            RAISE EXCEPTION 'Not authorized to set assessment provenance';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.node_type IS DISTINCT FROM OLD.node_type
       OR NEW.verification IS DISTINCT FROM OLD.verification
       OR NEW.is_keeper IS DISTINCT FROM OLD.is_keeper
       OR NEW.convergence_score IS DISTINCT FROM OLD.convergence_score
       OR NEW.keeper_id IS DISTINCT FROM OLD.keeper_id
       OR NEW.created_by IS DISTINCT FROM OLD.created_by
       OR NEW.term_id IS DISTINCT FROM OLD.term_id
       OR NEW.assessed_at IS DISTINCT FROM OLD.assessed_at
       OR NEW.assessed_by IS DISTINCT FROM OLD.assessed_by THEN
        RAISE EXCEPTION 'Not authorized to modify verification or attribution fields';
    END IF;

    RETURN NEW;
END;
$$;
```

Note: the trigger `guard_nodes_write` already exists (migration `20260706000004`) and points at this function name — `CREATE OR REPLACE` is sufficient; do not recreate the trigger.

- [x] **Step 4: Run tests → pass; full suite.** If `tests/test_saas_schema.py` has existing assertions that `guard_node_write` blocks `node_type IN ('Signal', 'Trend')` on INSERT, update them to the new Trend-only + verification form.

- [x] **Step 5: Commit.** `git commit -m "feat(db): verification status column, retire node_type Shadow overload, lock verified content"`

---

### Task 4: Edge multiplicity + HNSW index migration

**Files:**
- Create: `supabase/migrations/20260707100003_edge_multiplicity_and_hnsw.sql`
- Modify: `tests/test_saas_schema.py`

**Interfaces:**
- Produces: edges PK `(source_node_id, target_node_id, relationship_type)` so a pair can be both `Cites` and `Contradicts`; HNSW cosine index `nodes_embedding_hnsw_idx` replacing the premature ivfflat index.

- [x] **Step 1: Write the failing test.** Append:

```python
EDGE_MULTIPLICITY = "20260707100003_edge_multiplicity_and_hnsw.sql"


class TestEdgeMultiplicityAndHnsw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(EDGE_MULTIPLICITY)

    def test_pk_includes_relationship_type(self):
        self.assertIn("DROP CONSTRAINT IF EXISTS edges_pkey", self.sql)
        self.assertIn("PRIMARY KEY (source_node_id, target_node_id, relationship_type)", self.sql)

    def test_hnsw_replaces_ivfflat(self):
        self.assertIn("DROP INDEX IF EXISTS nodes_embedding_idx", self.sql)
        self.assertIn("USING hnsw (embedding vector_cosine_ops)", self.sql)
```

Add `EDGE_MULTIPLICITY` to `test_all_migration_files_present`.

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Write the migration** `supabase/migrations/20260707100003_edge_multiplicity_and_hnsw.sql`:

```sql
-- A node pair can hold multiple relationship types simultaneously
-- (e.g. Cites AND Contradicts); the old two-column PK forbade that.
ALTER TABLE edges ALTER COLUMN source_node_id SET NOT NULL;
ALTER TABLE edges ALTER COLUMN target_node_id SET NOT NULL;
ALTER TABLE edges DROP CONSTRAINT IF EXISTS edges_pkey;
ALTER TABLE edges ADD PRIMARY KEY (source_node_id, target_node_id, relationship_type);

-- ivfflat with lists=100 on a near-empty table has poor recall and needs
-- retraining as data grows; HNSW needs no list tuning.
DROP INDEX IF EXISTS nodes_embedding_idx;
CREATE INDEX IF NOT EXISTS nodes_embedding_hnsw_idx
    ON nodes USING hnsw (embedding vector_cosine_ops);
```

- [x] **Step 4: Run tests → pass; full suite.**

- [x] **Step 5: Commit.** `git commit -m "feat(db): edge relationship multiplicity and HNSW embedding index"`

---

### Task 5: Node events history migration (append-only signal evolution)

**Files:**
- Create: `supabase/migrations/20260707100004_node_events.sql`
- Modify: `tests/test_saas_schema.py`

**Interfaces:**
- Produces: `node_events` table (`id BIGINT IDENTITY PK, node_id UUID FK, event_type VARCHAR(50), actor UUID, payload JSONB, created_at TIMESTAMPTZ`) and trigger `log_node_events` capturing INSERT plus any change to scores/verification/polarity. Read-only for clients (no INSERT/UPDATE/DELETE policies; the SECURITY DEFINER trigger writes). The Scenario Builder's signal-momentum queries read this table.

- [x] **Step 1: Write the failing test.** Append:

```python
NODE_EVENTS = "20260707100004_node_events.sql"


class TestNodeEvents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(NODE_EVENTS)

    def test_table_created(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS node_events", self.sql)
        self.assertIn("payload JSONB", self.sql)

    def test_rls_enabled_read_only(self):
        self.assertIn("ALTER TABLE node_events ENABLE ROW LEVEL SECURITY", self.sql)
        self.assertNotIn("FOR INSERT", self.sql)
        self.assertNotIn("FOR UPDATE", self.sql)
        self.assertNotIn("FOR DELETE", self.sql)

    def test_logging_trigger(self):
        self.assertIn("FUNCTION public.log_node_event()", self.sql)
        self.assertIn("AFTER INSERT OR UPDATE ON nodes", self.sql)
```

Add `NODE_EVENTS` to `test_all_migration_files_present`.

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Write the migration** `supabase/migrations/20260707100004_node_events.sql`:

```sql
-- Append-only history so signal evolution (strengthening, decay,
-- verification, reclassification) can be plotted over time.
CREATE TABLE IF NOT EXISTS node_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    actor UUID,
    payload JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS node_events_node_id_idx ON node_events(node_id, created_at);

ALTER TABLE node_events ENABLE ROW LEVEL SECURITY;

-- Clients may only read events for nodes they can already see; writes happen
-- exclusively via the SECURITY DEFINER trigger below (no write policies).
DROP POLICY IF EXISTS node_events_admin_read ON node_events;
CREATE POLICY node_events_admin_read ON node_events
    FOR SELECT TO authenticated
    USING (public.is_administrator());

DROP POLICY IF EXISTS node_events_student_read_term ON node_events;
CREATE POLICY node_events_student_read_term ON node_events
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM nodes
            WHERE nodes.id = node_events.node_id
              AND nodes.term_id = public.current_user_term_id()
        )
    );

CREATE OR REPLACE FUNCTION public.log_node_event()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    changes JSONB := '{}'::jsonb;
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO public.node_events (node_id, event_type, actor, payload)
        VALUES (NEW.id, 'created', auth.uid(), jsonb_build_object(
            'node_type', NEW.node_type, 'polarity', NEW.polarity,
            'verification', NEW.verification));
        RETURN NEW;
    END IF;

    IF NEW.impact_score IS DISTINCT FROM OLD.impact_score THEN
        changes := changes || jsonb_build_object('impact_score',
            jsonb_build_object('old', OLD.impact_score, 'new', NEW.impact_score));
    END IF;
    IF NEW.uncertainty_score IS DISTINCT FROM OLD.uncertainty_score THEN
        changes := changes || jsonb_build_object('uncertainty_score',
            jsonb_build_object('old', OLD.uncertainty_score, 'new', NEW.uncertainty_score));
    END IF;
    IF NEW.convergence_score IS DISTINCT FROM OLD.convergence_score THEN
        changes := changes || jsonb_build_object('convergence_score',
            jsonb_build_object('old', OLD.convergence_score, 'new', NEW.convergence_score));
    END IF;
    IF NEW.verification IS DISTINCT FROM OLD.verification THEN
        changes := changes || jsonb_build_object('verification',
            jsonb_build_object('old', OLD.verification, 'new', NEW.verification));
    END IF;
    IF NEW.polarity IS DISTINCT FROM OLD.polarity THEN
        changes := changes || jsonb_build_object('polarity',
            jsonb_build_object('old', OLD.polarity, 'new', NEW.polarity));
    END IF;

    IF changes <> '{}'::jsonb THEN
        INSERT INTO public.node_events (node_id, event_type, actor, payload)
        VALUES (NEW.id, 'updated', auth.uid(), changes);
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS log_node_events ON nodes;
CREATE TRIGGER log_node_events
    AFTER INSERT OR UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION public.log_node_event();
```

- [x] **Step 4: Run tests → pass; full suite.**

- [x] **Step 5: Commit.** `git commit -m "feat(db): append-only node_events history with change-logging trigger"`

---

### Task 6: Scenario scaffolding migration (tables)

**Files:**
- Create: `supabase/migrations/20260707100005_scenario_scaffolding.sql`
- Modify: `tests/test_saas_schema.py`

**Interfaces:**
- Produces the tables the Scenario Builder plan consumes (exact names):
  - `scenario_sets(id, title, description, axis_x_node_id, axis_y_node_id, axis_x_low_label, axis_x_high_label, axis_y_low_label, axis_y_high_label, horizon_year, created_by, term_id, is_published, created_at, updated_at)`
  - `scenarios(id, scenario_set_id, quadrant, title, narrative, early_warning_indicators, created_at, updated_at)` with `UNIQUE (scenario_set_id, quadrant)`
  - `scenario_nodes(scenario_id, node_id, role, notes, created_by, created_at)` PK `(scenario_id, node_id, role)`
  - Enums: `scenario_quadrant ('High-High','High-Low','Low-High','Low-Low')`, `scenario_node_role ('Driver','Evidence','Wildcard','Shadow-Risk','Implication')`

- [x] **Step 1: Write the failing test.** Append:

```python
SCENARIO_SCAFFOLDING = "20260707100005_scenario_scaffolding.sql"


class TestScenarioScaffolding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(SCENARIO_SCAFFOLDING)

    def test_enums(self):
        self.assertIn("CREATE TYPE scenario_quadrant AS ENUM ('High-High', 'High-Low', 'Low-High', 'Low-Low')", self.sql)
        self.assertIn("CREATE TYPE scenario_node_role AS ENUM ('Driver', 'Evidence', 'Wildcard', 'Shadow-Risk', 'Implication')", self.sql)

    def test_tables(self):
        for table in ("scenario_sets", "scenarios", "scenario_nodes"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", self.sql)

    def test_axis_references(self):
        self.assertIn("axis_x_node_id UUID REFERENCES nodes(id)", self.sql)
        self.assertIn("axis_y_node_id UUID REFERENCES nodes(id)", self.sql)

    def test_quadrant_unique_per_set(self):
        self.assertIn("UNIQUE (scenario_set_id, quadrant)", self.sql)

    def test_scenario_nodes_pk(self):
        self.assertIn("PRIMARY KEY (scenario_id, node_id, role)", self.sql)
```

Add `SCENARIO_SCAFFOLDING` to `test_all_migration_files_present`.

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Write the migration** `supabase/migrations/20260707100005_scenario_scaffolding.sql`:

```sql
-- 2x2 scenario planning scaffolding: a scenario_set is one 2x2 matrix built
-- on two critical-uncertainty axes (trend/signal nodes); each set holds four
-- quadrant scenarios; scenario_nodes ties evidence, drivers, wildcards, and
-- Shadow risks into each scenario narrative.
DO $$
BEGIN
    CREATE TYPE scenario_quadrant AS ENUM ('High-High', 'High-Low', 'Low-High', 'Low-Low');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE scenario_node_role AS ENUM ('Driver', 'Evidence', 'Wildcard', 'Shadow-Risk', 'Implication');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS scenario_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    axis_x_node_id UUID REFERENCES nodes(id) ON DELETE SET NULL,
    axis_y_node_id UUID REFERENCES nodes(id) ON DELETE SET NULL,
    axis_x_low_label VARCHAR(255),
    axis_x_high_label VARCHAR(255),
    axis_y_low_label VARCHAR(255),
    axis_y_high_label VARCHAR(255),
    horizon_year INTEGER CHECK (horizon_year IS NULL OR horizon_year BETWEEN 2020 AND 2200),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    term_id UUID REFERENCES terms(id) ON DELETE SET NULL,
    is_published BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT distinct_axes CHECK (
        axis_x_node_id IS NULL OR axis_y_node_id IS NULL OR axis_x_node_id <> axis_y_node_id
    )
);

CREATE TABLE IF NOT EXISTS scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_set_id UUID REFERENCES scenario_sets(id) ON DELETE CASCADE NOT NULL,
    quadrant scenario_quadrant NOT NULL,
    title VARCHAR(255) NOT NULL,
    narrative TEXT,
    early_warning_indicators TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (scenario_set_id, quadrant)
);

CREATE TABLE IF NOT EXISTS scenario_nodes (
    scenario_id UUID REFERENCES scenarios(id) ON DELETE CASCADE,
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    role scenario_node_role DEFAULT 'Evidence'::scenario_node_role NOT NULL,
    notes TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (scenario_id, node_id, role)
);

CREATE INDEX IF NOT EXISTS scenario_sets_term_id_idx ON scenario_sets(term_id);
CREATE INDEX IF NOT EXISTS scenarios_set_id_idx ON scenarios(scenario_set_id);
CREATE INDEX IF NOT EXISTS scenario_nodes_node_id_idx ON scenario_nodes(node_id);

DROP TRIGGER IF EXISTS set_scenario_sets_updated_at ON scenario_sets;
CREATE TRIGGER set_scenario_sets_updated_at
    BEFORE UPDATE ON scenario_sets
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_scenarios_updated_at ON scenarios;
CREATE TRIGGER set_scenarios_updated_at
    BEFORE UPDATE ON scenarios
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
```

- [x] **Step 4: Run tests → pass; full suite.**

- [x] **Step 5: Commit.** `git commit -m "feat(db): scenario_sets, scenarios, and scenario_nodes scaffolding"`

---

### Task 7: Scenario RLS migration

**Files:**
- Create: `supabase/migrations/20260707100006_scenario_rls.sql`
- Modify: `tests/test_saas_schema.py`

**Interfaces:**
- Produces: RLS on all three scenario tables. Admin full access; students full CRUD on their own term's sets (and child scenarios/links); subscribers read published sets only.

- [x] **Step 1: Write the failing test.** Append:

```python
SCENARIO_RLS = "20260707100006_scenario_rls.sql"


class TestScenarioRls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(SCENARIO_RLS)

    def test_rls_enabled_all_tables(self):
        for table in ("scenario_sets", "scenarios", "scenario_nodes"):
            self.assertIn(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY", self.sql)

    def test_admin_policies(self):
        for policy in ("scenario_sets_admin_all", "scenarios_admin_all", "scenario_nodes_admin_all"):
            self.assertIn(policy, self.sql)

    def test_student_term_scoped(self):
        self.assertIn("scenario_sets_student_term", self.sql)
        self.assertIn("public.current_user_term_id()", self.sql)

    def test_subscriber_published_only(self):
        self.assertIn("scenario_sets_subscriber_read_published", self.sql)
        self.assertIn("is_published = true", self.sql)
```

Add `SCENARIO_RLS` to `test_all_migration_files_present`.

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Write the migration** `supabase/migrations/20260707100006_scenario_rls.sql`:

```sql
ALTER TABLE scenario_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_nodes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS scenario_sets_admin_all ON scenario_sets;
CREATE POLICY scenario_sets_admin_all ON scenario_sets
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

DROP POLICY IF EXISTS scenario_sets_student_term ON scenario_sets;
CREATE POLICY scenario_sets_student_term ON scenario_sets
    FOR ALL TO authenticated
    USING (
        public.is_student()
        AND term_id = public.current_user_term_id()
    )
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND term_id = public.current_user_term_id()
        AND is_published = false
    );

DROP POLICY IF EXISTS scenario_sets_subscriber_read_published ON scenario_sets;
CREATE POLICY scenario_sets_subscriber_read_published ON scenario_sets
    FOR SELECT TO authenticated
    USING (public.is_subscriber() AND is_published = true);

-- Child tables inherit visibility through their parent set.
DROP POLICY IF EXISTS scenarios_admin_all ON scenarios;
CREATE POLICY scenarios_admin_all ON scenarios
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

DROP POLICY IF EXISTS scenarios_student_term ON scenarios;
CREATE POLICY scenarios_student_term ON scenarios
    FOR ALL TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.term_id = public.current_user_term_id()
        )
    )
    WITH CHECK (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenarios_subscriber_read_published ON scenarios;
CREATE POLICY scenarios_subscriber_read_published ON scenarios
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND EXISTS (
            SELECT 1 FROM scenario_sets ss
            WHERE ss.id = scenarios.scenario_set_id AND ss.is_published = true
        )
    );

DROP POLICY IF EXISTS scenario_nodes_admin_all ON scenario_nodes;
CREATE POLICY scenario_nodes_admin_all ON scenario_nodes
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

DROP POLICY IF EXISTS scenario_nodes_student_term ON scenario_nodes;
CREATE POLICY scenario_nodes_student_term ON scenario_nodes
    FOR ALL TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
        )
    )
    WITH CHECK (
        public.is_student()
        AND created_by = auth.uid()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id
              AND ss.term_id = public.current_user_term_id()
              AND ss.is_published = false
        )
    );

DROP POLICY IF EXISTS scenario_nodes_subscriber_read_published ON scenario_nodes;
CREATE POLICY scenario_nodes_subscriber_read_published ON scenario_nodes
    FOR SELECT TO authenticated
    USING (
        public.is_subscriber()
        AND EXISTS (
            SELECT 1 FROM scenarios s
            JOIN scenario_sets ss ON ss.id = s.scenario_set_id
            WHERE s.id = scenario_nodes.scenario_id AND ss.is_published = true
        )
    );
```

- [x] **Step 4: Run tests → pass; full suite.**

- [x] **Step 5: Commit.** `git commit -m "feat(db): RLS policies for scenario scaffolding tables"`

---

### Task 8: SQLite parity — new signal columns and scenario tables

**Files:**
- Modify: `src/database.py`
- Test: `tests/test_database.py` (append)

**Interfaces:**
- Produces (exact signatures the Scenario Builder plan consumes):
  - `signals` gains columns: `uncertainty_score INTEGER`, `horizon_year INTEGER`, `polarity TEXT CHECK IN ('Emergent','Shadow') DEFAULT 'Emergent'`, `shadow_type TEXT`, `mitigation_notes TEXT` — and `add_signal` persists them.
  - `Database.add_scenario_set(s: dict) -> str`, `Database.get_scenario_set(set_id: str) -> Optional[dict]`
  - `Database.add_scenario(sc: dict) -> str`, `Database.get_scenarios_for_set(set_id: str) -> List[dict]`
  - `Database.map_signal_to_scenario(scenario_id, signal_id, role='Evidence', notes='')`, `Database.get_scenario_signals(scenario_id: str) -> List[dict]` (each row includes the joined signal columns plus `role` and `link_notes`).
  - `Database._migrate_schema()` adds missing columns to pre-existing DBs via `PRAGMA table_info(signals)` + `ALTER TABLE ADD COLUMN`.

- [x] **Step 1: Write the failing tests.** Append to `tests/test_database.py`:

```python
class TestScenarioTables(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def _signal(self, title="Solar microgrids", polarity="Emergent", **kw):
        base = {
            "title": title,
            "description": "desc",
            "category": "Technological",
            "time_horizon": "Mid-term",
            "polarity": polarity,
        }
        base.update(kw)
        return self.db.add_signal(base)

    def test_signal_shadow_fields_roundtrip(self):
        sig_id = self._signal(
            title="Mall retail collapse",
            polarity="Shadow",
            shadow_type="Declining-System",
            mitigation_notes="Diversify anchor tenants",
            uncertainty_score=8,
            horizon_year=2032,
        )
        sig = self.db.get_signal(sig_id)
        self.assertEqual(sig["polarity"], "Shadow")
        self.assertEqual(sig["shadow_type"], "Declining-System")
        self.assertEqual(sig["uncertainty_score"], 8)
        self.assertEqual(sig["horizon_year"], 2032)

    def test_scenario_set_roundtrip(self):
        x = self._signal("Axis X")
        y = self._signal("Axis Y")
        set_id = self.db.add_scenario_set({
            "title": "Energy 2040",
            "axis_x_signal_id": x,
            "axis_y_signal_id": y,
            "axis_x_low_label": "Centralized",
            "axis_x_high_label": "Distributed",
            "axis_y_low_label": "Cheap",
            "axis_y_high_label": "Expensive",
            "horizon_year": 2040,
        })
        stored = self.db.get_scenario_set(set_id)
        self.assertEqual(stored["title"], "Energy 2040")
        self.assertEqual(stored["axis_x_signal_id"], x)

    def test_scenarios_unique_quadrant_per_set(self):
        set_id = self.db.add_scenario_set({"title": "S"})
        self.db.add_scenario({"scenario_set_id": set_id, "quadrant": "High-High", "title": "A"})
        with self.assertRaises(Exception):
            self.db.add_scenario({"scenario_set_id": set_id, "quadrant": "High-High", "title": "B"})

    def test_scenario_signal_mapping(self):
        set_id = self.db.add_scenario_set({"title": "S"})
        scn_id = self.db.add_scenario({"scenario_set_id": set_id, "quadrant": "Low-Low", "title": "Collapse"})
        sig_id = self._signal("Grid failures", polarity="Shadow", shadow_type="Worst-Case-Future")
        self.db.map_signal_to_scenario(scn_id, sig_id, role="Shadow-Risk", notes="stress case")
        rows = self.db.get_scenario_signals(scn_id)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["role"], "Shadow-Risk")
        self.assertEqual(rows[0]["title"], "Grid failures")
```

- [x] **Step 2: Run to verify FAIL.** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests.test_database -v` → AttributeError / OperationalError.

- [x] **Step 3: Implement in `src/database.py`.**

3a. In `_init_schema`, extend the `signals` CREATE TABLE (after `source_metadata TEXT,`):

```sql
            uncertainty_score INTEGER CHECK(uncertainty_score BETWEEN 1 AND 10),
            horizon_year INTEGER CHECK(horizon_year BETWEEN 2020 AND 2200),
            polarity TEXT CHECK(polarity IN ('Emergent', 'Shadow')) DEFAULT 'Emergent',
            shadow_type TEXT CHECK(shadow_type IN ('Declining-System', 'Obsolete-Behavior', 'Worst-Case-Future', 'Disruption')),
            mitigation_notes TEXT,
```

3b. Still in `_init_schema`, add the three scenario tables after `signal_trend_map`:

```python
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenario_sets (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            axis_x_signal_id TEXT REFERENCES signals(id) ON DELETE SET NULL,
            axis_y_signal_id TEXT REFERENCES signals(id) ON DELETE SET NULL,
            axis_x_low_label TEXT,
            axis_x_high_label TEXT,
            axis_y_low_label TEXT,
            axis_y_high_label TEXT,
            horizon_year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id TEXT PRIMARY KEY,
            scenario_set_id TEXT NOT NULL REFERENCES scenario_sets(id) ON DELETE CASCADE,
            quadrant TEXT CHECK(quadrant IN ('High-High', 'High-Low', 'Low-High', 'Low-Low')) NOT NULL,
            title TEXT NOT NULL,
            narrative TEXT,
            early_warning_indicators TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (scenario_set_id, quadrant)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenario_signal_map (
            scenario_id TEXT REFERENCES scenarios(id) ON DELETE CASCADE,
            signal_id TEXT REFERENCES signals(id) ON DELETE CASCADE,
            role TEXT CHECK(role IN ('Driver', 'Evidence', 'Wildcard', 'Shadow-Risk', 'Implication')) DEFAULT 'Evidence',
            notes TEXT,
            PRIMARY KEY (scenario_id, signal_id, role)
        );
        """)
        self._migrate_schema(cursor)
```

3c. Add the lightweight column migration (new method on `Database`):

```python
    def _migrate_schema(self, cursor):
        cursor.execute("PRAGMA table_info(signals)")
        existing = {row[1] for row in cursor.fetchall()}
        additions = {
            "uncertainty_score": "INTEGER CHECK(uncertainty_score BETWEEN 1 AND 10)",
            "horizon_year": "INTEGER CHECK(horizon_year BETWEEN 2020 AND 2200)",
            "polarity": "TEXT CHECK(polarity IN ('Emergent', 'Shadow')) DEFAULT 'Emergent'",
            "shadow_type": "TEXT CHECK(shadow_type IN ('Declining-System', 'Obsolete-Behavior', 'Worst-Case-Future', 'Disruption'))",
            "mitigation_notes": "TEXT",
        }
        for column, ddl in additions.items():
            if column not in existing:
                cursor.execute(f"ALTER TABLE signals ADD COLUMN {column} {ddl}")
```

3d. Extend `add_signal`'s INSERT to include the five new columns (append to the column list, the `VALUES` placeholders, and the parameter tuple):

```python
            signal.get("uncertainty_score"),
            signal.get("horizon_year"),
            signal.get("polarity", "Emergent"),
            signal.get("shadow_type"),
            signal.get("mitigation_notes")
```

3e. Add the scenario CRUD methods:

```python
    def add_scenario_set(self, scenario_set: Dict[str, Any]) -> str:
        cursor = self.conn.cursor()
        set_id = scenario_set.get("id") or f"scnset_{os.urandom(4).hex()}"
        cursor.execute("""
        INSERT OR REPLACE INTO scenario_sets (
            id, title, description, axis_x_signal_id, axis_y_signal_id,
            axis_x_low_label, axis_x_high_label, axis_y_low_label, axis_y_high_label,
            horizon_year
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            set_id,
            scenario_set["title"],
            scenario_set.get("description"),
            scenario_set.get("axis_x_signal_id"),
            scenario_set.get("axis_y_signal_id"),
            scenario_set.get("axis_x_low_label"),
            scenario_set.get("axis_x_high_label"),
            scenario_set.get("axis_y_low_label"),
            scenario_set.get("axis_y_high_label"),
            scenario_set.get("horizon_year"),
        ))
        self.conn.commit()
        return set_id

    def get_scenario_set(self, set_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scenario_sets WHERE id = ?", (set_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_scenario(self, scenario: Dict[str, Any]) -> str:
        cursor = self.conn.cursor()
        scn_id = scenario.get("id") or f"scn_{os.urandom(4).hex()}"
        cursor.execute("""
        INSERT INTO scenarios (
            id, scenario_set_id, quadrant, title, narrative, early_warning_indicators
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            scn_id,
            scenario["scenario_set_id"],
            scenario["quadrant"],
            scenario["title"],
            scenario.get("narrative"),
            scenario.get("early_warning_indicators"),
        ))
        self.conn.commit()
        return scn_id

    def get_scenarios_for_set(self, set_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scenarios WHERE scenario_set_id = ? ORDER BY quadrant", (set_id,))
        return [dict(r) for r in cursor.fetchall()]

    def map_signal_to_scenario(self, scenario_id: str, signal_id: str, role: str = "Evidence", notes: str = ""):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO scenario_signal_map (scenario_id, signal_id, role, notes)
        VALUES (?, ?, ?, ?)
        """, (scenario_id, signal_id, role, notes))
        self.conn.commit()

    def get_scenario_signals(self, scenario_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT s.*, m.role, m.notes AS link_notes
        FROM signals s
        JOIN scenario_signal_map m ON s.id = m.signal_id
        WHERE m.scenario_id = ?
        """, (scenario_id,))
        res = []
        for r in cursor.fetchall():
            d = dict(r)
            d["source_metadata"] = json.loads(d["source_metadata"] or "[]")
            res.append(d)
        return res
```

Note: `add_scenario` deliberately uses plain `INSERT` (not `INSERT OR REPLACE`) so the `UNIQUE (scenario_set_id, quadrant)` constraint raises on duplicates — the test in Step 1 depends on this.

- [x] **Step 4: Run tests → pass; full suite.**

- [x] **Step 5: Commit.** `git commit -m "feat(db): SQLite parity — shadow/uncertainty columns and scenario tables"`

---

### Task 9: Assessment engine — score uncertainty and horizon year

**Files:**
- Modify: `src/assessment.py`
- Test: `tests/test_assessment.py` (append)

**Interfaces:**
- Produces: `assess_signal(...)` return dict gains keys `uncertainty_score` (int 1–10) and `horizon_year` (int or None). Both the Gemini path and the heuristic path must return them.

- [x] **Step 1: Write the failing test.** Append to `tests/test_assessment.py`:

```python
class TestUncertaintyAssessment(unittest.TestCase):
    def setUp(self):
        self.engine = AssessmentEngine(api_key=None)  # forces heuristic path

    def test_heuristic_returns_uncertainty_and_horizon_year(self):
        result = self.engine.assess_signal(
            title="Speculative fusion breakthrough could transform energy by 2050",
            description="Unproven, contested experimental results.",
            category="Technological",
        )
        self.assertIn("uncertainty_score", result)
        self.assertTrue(1 <= result["uncertainty_score"] <= 10)
        self.assertIn("horizon_year", result)

    def test_contested_language_raises_uncertainty(self):
        contested = self.engine.assess_signal(
            title="Unproven speculative claim", description="might possibly happen, contested",
            category="Social")
        settled = self.engine.assess_signal(
            title="Documented measured adoption", description="confirmed by longitudinal data",
            category="Social")
        self.assertGreater(contested["uncertainty_score"], settled["uncertainty_score"])
```

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Implement.** In `_assess_with_heuristics`, after the impact block, add:

```python
        # 2b. Evaluate Uncertainty Score (1-10)
        high_uncertainty_keywords = ["might", "possibly", "speculative", "unproven", "contested", "unclear", "debate", "experimental", "rumor"]
        low_uncertainty_keywords = ["confirmed", "documented", "measured", "established", "regulation passed", "longitudinal", "official"]

        uncertainty = 5
        if any(w in text_to_scan for w in high_uncertainty_keywords):
            uncertainty = 8
        elif any(w in text_to_scan for w in low_uncertainty_keywords):
            uncertainty = 3

        # 2c. Estimate horizon year: explicit 4-digit year wins, else map horizon band
        year_match = re.search(r"\b(20[2-9][0-9]|21[0-9][0-9])\b", text_to_scan)
        if year_match:
            horizon_year = int(year_match.group(1))
        else:
            horizon_year = {"Near-term": 2028, "Mid-term": 2035, "Long-term": 2050}[horizon]
```

(`import re` is already available — confirm the module imports `re`; add it to the top imports if absent.)

Extend both return dicts (heuristic and Gemini) with:

```python
            "uncertainty_score": uncertainty,
            "horizon_year": horizon_year,
```

For the Gemini path: add dimensions 5 and 6 to the prompt —

```
        5. Uncertainty (An integer 1-10: how contested/unknowable the signal's trajectory is; 10 = deeply uncertain)
        6. Horizon Year (Your best single-year estimate, e.g. 2035, for when this signal reaches mainstream impact)
```

and to the example JSON structure `"uncertainty_score": 7, "horizon_year": 2035`, then clamp/validate after parsing:

```python
        uncertainty_score = max(1, min(10, int(data.get("uncertainty_score", 5))))
        horizon_year = data.get("horizon_year")
        horizon_year = int(horizon_year) if horizon_year and 2020 <= int(horizon_year) <= 2200 else None
```

- [x] **Step 4: Run tests → pass; full suite.** Also update `src/cli.py` `ingest` to pass the two new assessment keys into `signal_record`:

```python
                "uncertainty_score": assessment_results["uncertainty_score"],
                "horizon_year": assessment_results["horizon_year"],
                "polarity": raw_sig.get("polarity", "Emergent"),
                "shadow_type": raw_sig.get("shadow_type"),
                "mitigation_notes": raw_sig.get("mitigation_notes"),
```

- [x] **Step 5: Commit.** `git commit -m "feat(assessment): uncertainty score and horizon-year estimation"`

---

### Task 10: Migration adapter — map new fields

**Files:**
- Modify: `src/migration_adapter.py`
- Test: `tests/test_migration_adapter.py` (append)

**Interfaces:**
- Consumes: SQLite columns from Task 8; Supabase columns from Tasks 1–3.
- Produces: `build_node_payload` emits `uncertainty_score`, `horizon_year`, `polarity`, `shadow_type`, `mitigation_notes`, and `verification` (derived: keeper + status 'Signal' → 'Verified', else 'Raw').

- [x] **Step 1: Write the failing test.** Append to `tests/test_migration_adapter.py` (follow the file's existing fixture pattern for constructing an adapter without a client):

```python
class TestShadowAndUncertaintyMapping(unittest.TestCase):
    def setUp(self):
        self.adapter = MigrationAdapter(sqlite_path=":memory:", supabase_client=object())

    def test_payload_includes_new_dimensions(self):
        row = {
            "id": "sig_1", "title": "Mall decline", "description": "d",
            "category": "Economic", "time_horizon": "Mid-term",
            "is_keeper": 1, "status": "Signal",
            "uncertainty_score": 7, "horizon_year": 2033,
            "polarity": "Shadow", "shadow_type": "Declining-System",
            "mitigation_notes": "hedge",
        }
        payload = self.adapter.build_node_payload(row)
        self.assertEqual(payload["uncertainty_score"], 7)
        self.assertEqual(payload["horizon_year"], 2033)
        self.assertEqual(payload["polarity"], "Shadow")
        self.assertEqual(payload["shadow_type"], "Declining-System")
        self.assertEqual(payload["verification"], "Verified")

    def test_raw_row_maps_to_raw_verification(self):
        row = {"id": "sig_2", "title": "t", "description": "d",
               "category": "Social", "time_horizon": "Near-term",
               "is_keeper": 0, "status": "Shadow"}
        payload = self.adapter.build_node_payload(row)
        self.assertEqual(payload["verification"], "Raw")
        self.assertEqual(payload["polarity"], "Emergent")
```

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Implement.** In `build_node_payload`, add to the payload dict:

```python
            "uncertainty_score": row.get("uncertainty_score"),
            "horizon_year": row.get("horizon_year"),
            "polarity": row.get("polarity") or "Emergent",
            "shadow_type": row.get("shadow_type"),
            "mitigation_notes": row.get("mitigation_notes"),
            "verification": self._resolve_verification(row),
```

and add the helper next to `_resolve_node_type`:

```python
    def _resolve_verification(self, row: Dict[str, Any]) -> str:
        if int(row.get("is_keeper", 1) or 0) == 1 and row.get("status") == "Signal":
            return "Verified"
        return "Raw"
```

- [x] **Step 4: Run tests → pass; full suite.**

- [x] **Step 5: Commit.** `git commit -m "feat(migration): map uncertainty, shadow, and verification fields to Supabase payloads"`

---

### Task 11: Non-destructive deduplication (no singleton auto-elevation, provenance preserved)

**Files:**
- Modify: `src/deduplication.py:150-241` (`deduplicate_database`)
- Test: `tests/test_deduplication.py` (append + amend)

**Interfaces:**
- Consumes: `Database.update_signal_deduplication_status` (unchanged signature).
- Produces: behavior change — singletons stay `Shadow` status (Raw) with their existing `source_metadata` untouched; keepers are elevated to `Signal` only when the cluster has ≥ 2 members; a duplicate's prior `source_metadata` is merged into the keeper's provenance rather than discarded.

- [x] **Step 1: Write the failing tests.** Append to `tests/test_deduplication.py`:

```python
class TestNonDestructiveDedup(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.engine = DeduplicationEngine(threshold=0.75)

    def tearDown(self):
        self.db.close()

    def test_singleton_is_not_elevated(self):
        self.db.add_signal({
            "id": "solo", "title": "Unique lone observation about kelp",
            "description": "Nothing else is similar to this at all.",
            "category": "Environmental", "time_horizon": "Near-term",
        })
        self.engine.deduplicate_database(self.db)
        sig = self.db.get_signal("solo")
        self.assertEqual(sig["status"], "Shadow")
        self.assertTrue(sig["is_keeper"])

    def test_duplicate_provenance_is_merged_not_erased(self):
        base = {"category": "Technological", "time_horizon": "Mid-term"}
        self.db.add_signal({"id": "a", "title": "Robotic delivery drones expand",
                            "description": "Drones deliver parcels in cities.",
                            "source_metadata": [{"note": "original-a"}], **base})
        self.db.add_signal({"id": "b", "title": "Robotic delivery drones expanding",
                            "description": "Drones delivering parcels in cities.",
                            "source_metadata": [{"note": "original-b"}], **base})
        self.engine.deduplicate_database(self.db)
        keepers = self.db.get_all_signals(filter_keeper=True)
        self.assertEqual(len(keepers), 1)
        keeper = keepers[0]
        self.assertEqual(keeper["status"], "Signal")
        notes = {m.get("note") for m in keeper["source_metadata"] if "note" in m}
        self.assertIn("original-b" if keeper["id"] == "a" else "original-a", notes)
```

Amend any existing test that asserts singletons become `Signal` (search for `status.*Signal` in `tests/test_deduplication.py`) to expect `Shadow`.

- [x] **Step 2: Run to verify FAIL.**

- [x] **Step 3: Implement.** In `deduplicate_database`, replace the singleton branch (currently elevates to `Signal` and wipes metadata) with:

```python
            if len(cluster) == 1:
                # Singleton: keeper of itself, but an uncorroborated observation
                # is NOT verified — it stays a Shadow-status research point, and
                # its existing provenance is preserved untouched.
                idx = cluster[0]
                sig = signals[idx]
                db.update_signal_deduplication_status(
                    sig_id=sig["id"],
                    is_keeper=True,
                    keeper_id=None,
                    convergence_score=1.0,
                    status=sig.get("status") or "Shadow",
                    source_metadata=sig.get("source_metadata") or []
                )
                keepers_count += 1
                continue
```

In the multi-node branch, build provenance by merging instead of replacing — before the keeper update:

```python
            # Merge, never erase: keeper keeps its own prior provenance plus a
            # snapshot of each duplicate (including the duplicate's provenance).
            provenance_metadata = list(keeper_sig.get("source_metadata") or [])
            for d_idx in duplicate_indices:
                d_sig = signals[d_idx]
                provenance_metadata.append({
                    "id": d_sig["id"],
                    "title": d_sig["title"],
                    "description": d_sig["description"],
                    "source_url": d_sig.get("source_url"),
                    "date_observed": d_sig.get("date_observed"),
                    "geography": d_sig.get("geography"),
                    "sector": d_sig.get("sector"),
                    "prior_source_metadata": d_sig.get("source_metadata") or [],
                })
```

and in the duplicate-update loop keep each duplicate's own metadata:

```python
                db.update_signal_deduplication_status(
                    sig_id=d_sig["id"],
                    is_keeper=False,
                    keeper_id=keeper_sig["id"],
                    convergence_score=1.0,
                    status="Shadow",
                    source_metadata=d_sig.get("source_metadata") or []
                )
```

(SaaS note for future work, do not implement here: when this pipeline runs against Supabase it must be scoped `WHERE term_id = :term` so cohorts never cluster into each other.)

- [x] **Step 4: Run tests → pass; full suite** (dedup, pipeline e2e, cli tests may assert old singleton elevation — update expectations where they encode the old destructive behavior, keeping all other assertions).

- [x] **Step 5: Commit.** `git commit -m "fix(dedup): preserve provenance, stop auto-verifying uncorroborated singletons"`

---

## Self-Review Checklist (run after drafting)

1. Spec coverage: uncertainty ✓ (T1, T9), horizon anchoring ✓ (T1, T9), shadows affordance ✓ (T2), verification decoupling + verified-content lock ✓ (T3), edge multiplicity ✓ (T4), history ✓ (T5), scenario scaffolding + RLS ✓ (T6, T7), SQLite parity ✓ (T8), adapter mapping ✓ (T10), dedup integrity ✓ (T11).
2. Deliberately out of scope (tracked on KANBAN, not here): invite-code isolation (M2.4), student edge UPDATE/DELETE (M2.6), controlled vocabularies (M4.3), adapter idempotency/keeper remapping (M1.4).
3. Type consistency: `verification` column name (not `verification_status` — that's the enum type) used consistently in T3, T5, T10. `scenario_signal_map.role` values match Supabase `scenario_node_role` enum spelling exactly, including `'Shadow-Risk'`.
