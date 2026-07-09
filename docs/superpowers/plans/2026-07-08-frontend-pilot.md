# Frontend Pilot Implementation Plan (Peer Validation + App Shell + Auth + Signal Entry)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. UI tasks (4–6) additionally follow the impeccable craft production bar (`.claude` plugin impeccable, product register) — build, then inspect in-browser, then fix, per task.

**Goal:** Ship the pilot slice of the frontend v1 spec (`docs/superpowers/specs/2026-07-08-frontend-v1-design.md`): peer-validation database layer, Supabase session wiring, auth + approval flow, app shell, and the Signal Entry form — working end-to-end against the live local Supabase stack.

**Architecture:** One new Supabase migration (peer validation). Frontend work in `artifacts/foresight` (React 19 + Vite + Tailwind 4 + shadcn/Radix + wouter + react-query), adding `@supabase/supabase-js` and vitest. RLS is the authorization layer.

**Tech Stack:** PostgreSQL/Supabase, supabase-js v2, react-hook-form + zod (already deps), vitest + @testing-library/react (new dev deps).

## Global Constraints

- Python schema tests: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"` must stay green.
- Frontend: `pnpm --filter @workspace/foresight typecheck` and `pnpm --filter @workspace/foresight test` must pass after every task.
- Migrations idempotent, matching existing style. Policies `TO authenticated`.
- **Peer-only:** students can never validate their own signal; students can never write `nodes.verification` directly (only the validations trigger path).
- Design spec §4–§5.2 governs all UI: DESIGN.md palette, Restrained color, status vocabulary never hue-only, WCAG 2.2 AA, `prefers-reduced-motion` alternatives, no modals where inline works.
- Env: `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` via `artifacts/foresight/.env.local` (gitignored); a committed `.env.example` documents them.

---

### Task 1: Peer-validation migration

**Files:**
- Create: `supabase/migrations/20260708000000_peer_validation.sql`
- Modify: `tests/test_saas_schema.py` (append), `tests/sql/live_rls_assertions.sql` (append)

**Interfaces produced:** `validations` table (PK `(node_id, validator)`, `checklist JSONB`, `confidence 1–10`, `note`), trigger `apply_validation` → sets node `verification='Verified'`; `nodes.instructor_note TEXT` (admin-only writes, guarded).

- [ ] **Step 1: Failing tests.** Append to `tests/test_saas_schema.py`:

```python
PEER_VALIDATION = "20260708000000_peer_validation.sql"


class TestPeerValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = read_migration(PEER_VALIDATION)

    def test_validations_table(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS validations", self.sql)
        self.assertIn("PRIMARY KEY (node_id, validator)", self.sql)
        self.assertIn("confidence BETWEEN 1 AND 10", self.sql)

    def test_peer_only_insert_policy(self):
        self.assertIn("validations_student_insert_peer", self.sql)
        self.assertIn("created_by <> auth.uid()", self.sql)
        self.assertIn("verification = 'Raw'", self.sql)

    def test_trigger_flips_verification(self):
        self.assertIn("FUNCTION public.apply_validation()", self.sql)
        self.assertIn("SECURITY DEFINER", self.sql)
        self.assertIn("SET verification = 'Verified'", self.sql)

    def test_instructor_note_guarded(self):
        self.assertIn("ADD COLUMN IF NOT EXISTS instructor_note TEXT", self.sql)
        self.assertIn("NEW.instructor_note IS DISTINCT FROM OLD.instructor_note", self.sql)

    def test_checklist_keys_required(self):
        for key in ("source_checked", "not_duplicate", "signal_logic", "classification_justified"):
            self.assertIn(key, self.sql)
```

Add `PEER_VALIDATION` to `test_all_migration_files_present`.

- [ ] **Step 2: Run to verify FAIL** (missing file).

- [ ] **Step 3: Write the migration:**

```sql
-- Peer validation: students generate verification; admins audit.
-- A validation row is the ONLY student path to Verified (guard_node_write
-- still blocks direct verification writes by non-admins).
CREATE TABLE IF NOT EXISTS validations (
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    validator UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    checklist JSONB NOT NULL,
    confidence INTEGER NOT NULL CHECK (confidence BETWEEN 1 AND 10),
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (node_id, validator),
    CONSTRAINT checklist_keys_present CHECK (
        checklist ? 'source_checked'
        AND checklist ? 'not_duplicate'
        AND checklist ? 'signal_logic'
        AND checklist ? 'classification_justified'
    )
);

CREATE INDEX IF NOT EXISTS validations_validator_idx ON validations(validator, created_at);

ALTER TABLE validations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS validations_admin_all ON validations;
CREATE POLICY validations_admin_all ON validations
    FOR ALL TO authenticated
    USING (public.is_administrator())
    WITH CHECK (public.is_administrator());

DROP POLICY IF EXISTS validations_student_read_term ON validations;
CREATE POLICY validations_student_read_term ON validations
    FOR SELECT TO authenticated
    USING (
        public.is_student()
        AND EXISTS (
            SELECT 1 FROM nodes
            WHERE nodes.id = validations.node_id
              AND nodes.term_id = public.current_user_term_id()
        )
    );

-- Peer-only: validator is the caller, node is a classmate's Raw signal in-term.
DROP POLICY IF EXISTS validations_student_insert_peer ON validations;
CREATE POLICY validations_student_insert_peer ON validations
    FOR INSERT TO authenticated
    WITH CHECK (
        public.is_student()
        AND validator = auth.uid()
        AND EXISTS (
            SELECT 1 FROM nodes
            WHERE nodes.id = validations.node_id
              AND nodes.term_id = public.current_user_term_id()
              AND nodes.created_by <> auth.uid()
              AND nodes.verification = 'Raw'
        )
    );

CREATE OR REPLACE FUNCTION public.apply_validation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    UPDATE public.nodes
    SET verification = 'Verified'
    WHERE id = NEW.node_id AND verification = 'Raw';
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS apply_validation_on_insert ON validations;
CREATE TRIGGER apply_validation_on_insert
    AFTER INSERT ON validations
    FOR EACH ROW EXECUTE FUNCTION public.apply_validation();

-- Instructor correction note: admin-writable, term-visible.
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS instructor_note TEXT;

-- Extend the node write guard to protect instructor_note.
-- (CREATE OR REPLACE of guard_node_write: copy the existing function body from
-- 20260707100002_verification_status.sql and add to the UPDATE-branch check:
--    OR NEW.instructor_note IS DISTINCT FROM OLD.instructor_note
-- Keep every other clause identical.)

GRANT SELECT, INSERT ON validations TO authenticated;
```

(The guard function replacement is written out in full in the migration — the implementer copies the current body from `20260707100002` and adds the one clause.)

- [ ] **Step 4: Live assertions.** Append to `tests/sql/live_rls_assertions.sql`, following its existing structure: (a) student inserting a validation for their OWN node → rejected; (b) student inserting for a classmate's Raw node in-term → accepted AND node becomes Verified; (c) student direct `UPDATE nodes SET verification` → still rejected; (d) second validation for an already-Verified node → rejected by policy (verification no longer 'Raw'); (e) student `UPDATE nodes SET instructor_note` → rejected. Apply migrations to the local stack and run the file.

- [ ] **Step 5: Run Python suite → green. Commit** `feat(db): peer validation table, trigger, and instructor notes`.

---

### Task 2: Frontend foundations (supabase client, vitest, env)

**Files:**
- Modify: `artifacts/foresight/package.json` (add `@supabase/supabase-js`; dev: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`; script `"test": "vitest run"`)
- Create: `artifacts/foresight/src/lib/supabase.ts`, `artifacts/foresight/src/lib/database.types.ts` (generated: `supabase gen types typescript --local`), `artifacts/foresight/.env.example`, `artifacts/foresight/vitest.config.ts`

**Interfaces produced:** `supabase` typed client singleton; `Database` types. Consumed by every later task.

- [ ] Steps: install deps (`pnpm install` at repo root) → generate types from the live local stack → client module reading `import.meta.env.VITE_SUPABASE_URL/ANON_KEY` (throws a clear error at startup if missing) → smoke vitest test asserting the client module exports and env validation logic → typecheck + test green → commit `feat(web): supabase client, generated types, vitest baseline`.

---

### Task 3: Session, roles, and route guards

**Files:**
- Create: `artifacts/foresight/src/lib/session.tsx` (SessionProvider + `useSession()`), `artifacts/foresight/src/lib/queries.ts` (react-query hooks: `useProfile`, `useMyTerm`)
- Modify: `artifacts/foresight/src/App.tsx` (route table per spec §5.0; delete mockup page routes)

**Interfaces produced:** `useSession(): { user, profile, status: 'loading'|'signedOut'|'unapproved'|'student'|'admin' }`. Routing: signedOut → `/login`; unapproved → `/waiting`; student → app; admin → app + admin routes.

- [ ] Steps: failing vitest tests for the status derivation (given mocked session/profile combinations → expected status) → implement provider (supabase `onAuthStateChange` + profile fetch) → tests + typecheck green → commit `feat(web): session provider and role-based routing`.

---

### Task 4: Auth pages + awaiting-approval screen (UI — craft bar)

**Files:**
- Create: `artifacts/foresight/src/pages/login.tsx`, `signup.tsx`, `waiting.tsx`
- Spec: design spec §5.1 + §7 microcopy rules; DESIGN.md tokens.

**Requirements:** email/password forms (react-hook-form + zod), `full_name` in signup metadata; Supabase auth errors mapped to human copy (error map module with unit tests); waiting screen per spec (calm teaching moment, sign-out link, auto-advances when approval lands via profile refetch). All form states; AA contrast; keyboard-complete.

- [ ] Steps: error-map unit tests first → build pages → **in-browser inspection** (dev server against live stack: signup → waiting → approve via SQL → auto-advance) with screenshots at 360px/768px/1280px → fix findings → typecheck + tests green → commit `feat(web): auth and approval flow`.

---

### Task 5: App shell (UI — craft bar)

**Files:**
- Create: `artifacts/foresight/src/components/shell.tsx`, nav config module
- Modify: `App.tsx` (wrap routed pages), `index.css` (tokens from DESIGN.md if not yet ported: OKLCH variables, z-index scale)

**Requirements:** left rail per spec §5.0 (Scan/Browse/Shadows + admin items by role), user block, active-route treatment, icon rail <900px, bottom tabs <600px; reduced-motion safe transitions; landmarks (`nav`, `main`) + skip link.

- [ ] Steps: build → in-browser inspection at three widths incl. keyboard walk → fix → typecheck green → commit `feat(web): app shell and navigation`.

---

### Task 6: Signal Entry form (UI — craft bar, the pilot's heart)

**Files:**
- Create: `artifacts/foresight/src/pages/scan.tsx`, `src/lib/signal-schema.ts`, `src/lib/signal-mapper.ts`
- Test: `src/lib/__tests__/signal-schema.test.ts`, `signal-mapper.test.ts`

**Interfaces produced:** `signalSchema` (zod) and `toNodeInsert(values, session): NodesInsert`.

- [ ] **Step 1: Failing schema/mapper tests** — the deterministic core:

```ts
import { describe, expect, it } from "vitest";
import { signalSchema } from "../signal-schema";

const base = {
  title: "Community solar co-ops spreading",
  description: "Three new co-ops formed this quarter in mid-size cities.",
  category: "Technological",
  polarity: "Emergent",
  time_horizon: "Mid-term",
};

describe("signalSchema", () => {
  it("accepts a minimal valid Emergent signal", () => {
    expect(signalSchema.safeParse(base).success).toBe(true);
  });
  it("rejects shadow_type on an Emergent signal", () => {
    const r = signalSchema.safeParse({ ...base, shadow_type: "Disruption" });
    expect(r.success).toBe(false);
  });
  it("requires shadow_type when polarity is Shadow", () => {
    const r = signalSchema.safeParse({ ...base, polarity: "Shadow" });
    expect(r.success).toBe(false);
  });
  it("bounds horizon_year to 2020-2200 and scores to 1-10", () => {
    expect(signalSchema.safeParse({ ...base, horizon_year: 2019 }).success).toBe(false);
    expect(signalSchema.safeParse({ ...base, impact_score: 11 }).success).toBe(false);
  });
  it("leaves unset scores undefined, never defaulting to 5", () => {
    const r = signalSchema.parse(base);
    expect(r.impact_score).toBeUndefined();
  });
});
```

Mapper tests: `toNodeInsert` emits `polarity`, nulls shadow fields for Emergent, splits tags, omits score keys when undefined (so DB stores NULL), never sets `verification`/`node_type`/`term_id`/`created_by` (RLS/trigger territory — insert relies on policy defaults: `created_by`/`term_id` are supplied explicitly from session per the insert policy; verify against `nodes_student_insert_own_term` which requires both).

- [ ] **Step 2–3:** implement schema (discriminated union on polarity) + mapper → tests green.
- [ ] **Step 4:** build the page per spec §5.2 (five disclosure sections, segmented polarity control with plain-language descriptions, Shadow unfold, collapsed Assessment sliders, submit → toast + "Add another"/"View signal"). Supabase insert via react-query mutation; error map reused from Task 4.
- [ ] **Step 5:** in-browser inspection against live stack — submit an Emergent and a Shadow signal as an approved student; verify rows in DB carry correct polarity/shadow fields and NULL unset scores; screenshots at three widths; keyboard-only submission pass; reduced-motion check.
- [ ] **Step 6:** typecheck + full frontend tests + full Python suite green → commit `feat(web): signal entry form (pilot surface)`.

---

### Task 7: Pilot E2E sign-off

- [ ] Scripted manual pass on the live stack: fresh signup → waiting screen → admin approves + assigns term (SQL) → student submits Emergent + Shadow signals → second student account validates one (direct SQL insert into `validations` until the UI flow ships in phase 2) → node flips Verified → student cannot edit it → suite + live assertions green.
- [ ] Record results in HISTORY.md; move pilot card on KANBAN; note phase-2 scope (browser/detail/validation UI, shadow lens).

## Self-Review

- Spec §3.1 ↔ Task 1: table, peer-only policy, trigger, instructor_note, checklist keys — covered. Spec §5.1–5.2 ↔ Tasks 4–6 — covered. §8 testing ↔ Tasks 1/6/7 — covered.
- Deliberate deviation from writing-plans' complete-code rule: UI tasks 4–6 specify contracts, states, and verification steps but not full JSX — the impeccable craft loop (build → inspect → fix) owns visual implementation; pre-transcribed JSX would be dead on arrival after the first in-browser iteration. Deterministic logic (SQL, zod, mappers, error map) carries full code + tests.
- Type consistency: `signalSchema`/`toNodeInsert` names used in Tasks 6; `useSession` statuses in Tasks 3–5.
