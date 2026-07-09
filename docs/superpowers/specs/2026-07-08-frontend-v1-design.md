# Foresight Studio Frontend v1 — Design Specification

**Date:** 2026-07-08 · **Status:** Awaiting review · **Register:** product (PRODUCT.md) · **Visual system:** DESIGN.md (root)
**Origin:** brainstorm + impeccable shape interview (this session). Pilot surface: Signal Entry form.

---

## 1. Summary

The first human-usable web surface for Foresight Studio. Students sign up, get approved, submit Emergent/Shadow signals through a scaffolded form, browse the class signal graph, and **validate each other's signals** (peer-only) to produce Verified signals. Instructors run the term: approve the roster, manage terms, **audit student validations** (correct/demote where needed), and watch class analytics.

**Primary user actions.** Student: *submit a well-formed signal AND validate a classmate's signal with confidence.* Admin: *audit validations and correct where needed.*

## 2. Architecture

- **App:** extend the existing `artifacts/foresight` app (React 19, Vite, Tailwind 4, shadcn/Radix, wouter, react-query). Existing mockup pages (`collections-*`, `instructor-*`, `home`) are replaced.
- **Data:** `@supabase/supabase-js` direct to the local Supabase stack (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`). **RLS is the authorization layer** — no Express BFF for these flows. `artifacts/api-server` is untouched.
- ⚠️ **Recorded constraint:** re-evaluate Supabase-direct (rate limiting, abuse surface, key rotation) **before any production deployment**.
- **Auth:** Supabase email/password. Signup carries `full_name` metadata → hardened `handle_new_user` trigger creates an unapproved Student profile. No invite-code self-join in v1: **admin assigns term at approval** (also neutralizes the KANBAN M2.4 invite-code exposure path).
- **Session/roles:** a `SessionProvider` loads `profiles` row after login; routing branches on `role` + `is_approved`.

## 3. Verification model (peer validation)

Students generate everything, including validation. Admin audits.

- Any approved student may validate a **classmate's** Raw signal in their own term. **Peer-only: validator ≠ author** (DB-enforced). Instructors may validate anything (small-class fallback).
- Validation is a structured checklist, not a button:
  1. Source checked — URL reachable, source named
  2. Not a duplicate — searched the browser for similar signals
  3. Signal logic — description explains *why this is a signal* (what changed, what it points to)
  4. Classification justified — category, polarity, horizon defensible
  plus a **confidence score (1–10)** and an optional note.
- Completing the checklist inserts a `validations` row; a SECURITY DEFINER trigger flips the node to `Verified` and `node_events` records actor + transition (audit trail already exists).
- **Validate-then-freeze:** content stays locked for non-admins once Verified (existing policy). You can't validate a moving target.
- **Admin audit:** table of recent verifications with validator, checklist snapshot, confidence. Admin can correct fields, demote to Raw, and leave an `instructor_note` visible to the class — a teaching moment, not a punishment.

### 3.1 Required DB migration (`20260708…_peer_validation.sql`) — built in pilot phase

```
validations (
  node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
  validator UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  checklist JSONB NOT NULL,             -- the four booleans + freeform per-item notes
  confidence INTEGER NOT NULL CHECK (confidence BETWEEN 1 AND 10),
  note TEXT,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  PRIMARY KEY (node_id, validator)
)
```

- RLS: admin all; students SELECT validations for own-term nodes; students INSERT only with `validator = auth.uid()`, node in own term, node `verification = 'Raw'`, and **node.created_by <> auth.uid()** (peer-only).
- AFTER INSERT trigger (SECURITY DEFINER): set node `verification = 'Verified'`. Direct `verification` writes by students stay blocked by `guard_node_write` — the validations table is the only student path to Verified. Admin retains all transitions.
- `nodes.instructor_note TEXT` — admin-writable only (added to guard trigger protected fields), term-visible. Carries demotion/correction rationale.
- Checklist JSONB shape: `{"source_checked": bool, "not_duplicate": bool, "signal_logic": bool, "classification_justified": bool, "item_notes": {…}}` — all four must be true client-side to submit; DB requires the keys present.

## 4. Design direction

- **Color strategy: Restrained.** Warm-paper light theme per DESIGN.md's committed OKLCH palette (identity preservation). Six STEEP category colors appear **only as data** (tags, chart marks). Accent = primary actions + selection only.
- **Scene:** a student in a daylit studio classroom, laptop at 80% brightness, focused between conversations → light theme, calm surfaces, high-contrast ink.
- **Anchors:** **Notion** (calm document-like entry, progressive disclosure, inline flows over modals) + **Observable** (rigorous readable data display).
- **Status vocabulary** (never hue-only; always label or icon + color):
  - Verification: `Raw` (hollow dot) · `Verified` (filled check-dot) · `Archived` (struck dot)
  - Polarity: `Emergent` (sunrise glyph, brand accent tint) · `Shadow` (eclipse glyph, deep charcoal tint — weighty, not alarming; Shadows get equal light)
  - Roster: `Pending` · `Approved`
- **Component vocabulary:** one button shape, one form-control set (shadcn), lucide icons only, semantic z-index scale, skeletons not spinners, no nested cards, no side-stripe accents, no modals where inline disclosure works.
- **Motion:** 150–250ms state transitions, ease-out; checklist items confirm with a subtle settle; full `prefers-reduced-motion` alternatives. No page-load choreography.

## 5. Surfaces

### 5.0 App shell
Left rail: **Scan** (entry form), **Browse**, **Shadows**; admins additionally **Roster**, **Terms**, **Audit**, **Analytics**. User block (name, role, term, sign out) bottom of rail. Content column: forms capped at readable measure (~68ch), tables full-width. Rail collapses to icon rail <900px, bottom tab bar <600px.

### 5.1 Auth & approval
- Login / signup (email, password, full name). Errors mapped to human copy ("That email already has an account — sign in instead?").
- **Awaiting-approval holding screen** — calm first-run teaching moment: explains what happens next ("Your instructor approves new researchers and assigns you to a class term"), what Foresight Studio is, one illustration-free paragraph on signals vs shadows. Signed-in-but-unapproved users always land here.

### 5.2 Signal entry (— PILOT SURFACE)
A single-column "notebook page" with generous rhythm. Progressive disclosure order:
1. **Observation:** title, description (with inline hint: "what did you see, where, and why does it matter?")
2. **Classification:** STEEP category (6 segmented options w/ category color chips), **polarity** — two-option segmented control with plain-language descriptions: *"Emergent — something new appearing"* / *"Shadow — a system declining, a behavior going obsolete, a worst-case forming."* Choosing Shadow unfolds `shadow_type` (four options, one-line definitions each) + `mitigation_notes` ("how could an organization soften this if it lands?")
3. **Timing:** time_horizon (Near/Mid/Long with year-range hints) + optional `horizon_year`
4. **Source:** source_url, source_type, date_observed, geography, sector, tags
5. **Assessment (collapsed):** optional self-scores confidence/novelty/impact/uncertainty (1–10 sliders, unset by default — NULL means "not yet assessed", never silently 5)
Zod schema mirrors DB constraints exactly (scores 1–10, horizon_year 2020–2200, shadow fields require Shadow polarity). Submit → toast + "Add another" fast path or "View signal". States: default / validating / submitting / success / mapped-error.

### 5.3 Signal browser + detail
- Browser: dense table (product density) — title, category chip, polarity glyph, verification dot, horizon, author, date. Filter chips (category, polarity, verification, horizon) + text search, **URL-persisted**. Loading skeletons; "no results for these filters" ≠ "your class hasn't captured signals yet" (empty-state teaches the form).
- Detail: structured dossier — fields → scores → provenance (`source_metadata` merge history) → edges in/out → `node_events` timeline. If Verified: validation record (who, when, confidence, checklist). If demoted: `instructor_note` displayed prominently but kindly.
- **Validate this signal** (peer-only, Raw only, not own): checklist unfolds inline on the detail page, Notion-style. Own signals show "a classmate needs to validate this one" instead.

### 5.4 Shadow risk lens
Filtered view of `polarity = 'Shadow'` grouped by `shadow_type` (four plain-language group headers), ordered by impact within groups, `mitigation_notes` surfaced on each row. Empty state: "No shadows captured yet — worst-case futures are blind spots until someone writes them down."

### 5.5 Admin: Roster
Pending signups table → approve + assign term (inline select, no modal); approved roster below with term reassignment. Empty: "No pending researchers."

### 5.6 Admin: Terms
Create term (name; invite code generated), toggle active, rotate code. Codes visible to admins only.

### 5.7 Admin: Audit (replaces "verify queue")
Recent verifications: signal, validator, confidence, checklist snapshot (expandable), verified-at. Actions: open detail, **demote to Raw + instructor_note** (inline form), correct fields (admin edit). Optimistic updates with undo toast. Empty: "All caught up — no new validations to review."

### 5.8 Admin: Analytics
Per-term: submissions over time, Raw/Verified ratio, category breakdown, polarity split, validations per student (recharts, category colors as data). Under 5 signals: show counts, suppress charts (no fake precision).

## 6. States (cross-cutting checklist)

Every interactive component ships default/hover/focus-visible/active/disabled/loading. Surface-level: unauthenticated · awaiting-approval · approved-empty · form (5 states) · browser (skeleton, filtered-empty, true-empty, overflow text) · detail (not-found ≡ RLS-hidden) · already-validated · validation-draft-in-progress · demoted-with-note · roster-empty · audit-empty · analytics-sparse.

## 7. Content rules

Jargon-free per PRD; every foresight term gets a one-line plain definition at point of use. Error copy = what happened + what to do. No placeholder content at ship; seed via migration adapter from the cleaned 129-signal CSV. Microcopy inventory (holding screen, polarity descriptions, shadow_type definitions, empty states, error map) is part of the build, written per clarify.md.

## 8. Testing & verification

- `pnpm typecheck` gate; vitest for zod schemas, data mappers, and the validation-checklist gating logic.
- New migration tested in `tests/test_saas_schema.py` (text assertions) **and** appended to `tests/sql/live_rls_assertions.sql` (peer-only insert rejected for own signal; student direct `verification` update still rejected; trigger flips to Verified).
- E2E: manual scripted pass against live local stack — signup → approve → submit → peer validate → audit → demote — before pilot sign-off.

## 9. Sequencing

1. **Pilot:** peer-validation migration + app shell + auth/approval + Signal entry form (5.0–5.2), verified live.
2. Browser + detail + validation flow (5.3), Shadow lens (5.4).
3. Admin surfaces (5.5–5.8).
Each phase gets its own implementation plan (superpowers writing-plans) executed with subagent-driven development.

## 10. Decisions log

- Supabase-direct now; re-evaluate before production (user, 2026-07-08)
- All four admin features in v1 scope (user)
- Display: list+detail + shadow lens; polar radar deferred (user)
- **Students generate verification via peer-only validation; admin audits/corrects** (user)
- Validator ≠ author enforced at DB level; instructors exempt (user: "peer only validation is right")
- Admin assigns terms; no invite-code self-join in v1 (design decision, closes M2.4 path)
- Keep DESIGN.md light-paper identity; Notion + Observable anchors; Restrained color (user)
- Docs first, then pilot = Signal entry form (user)
