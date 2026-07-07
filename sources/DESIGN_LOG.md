# Design Log — CCSD Foresight Studio

A chronological record of the design and engineering decisions behind the CCSD Foresight Studio. Each entry is one shipped task. Read this alongside [`PRD.md`](./PRD.md), which tracks completion status, and the original [PRD source](../attached_assets/steep-pestle-collaborative-foresight-tool-prd_1777778985591.md), which is the long-form spec.

Entries are newest-first.

---

## 2026-05-03 · Task #13 — Scenario builder: carry-forward, scaffolded prompts, Markdown export

**Problem.** The 9-step scenario wizard treated each step as an island. By the time a student wrote the vignette they could no longer see which signals or archetype they had picked. Each input was a bare textarea with a one-line placeholder, so students with no foresight background had nowhere to push off from.

**Decision.**
- Render a compact, read-only **"What you've decided so far"** panel above the input on every step from #1 onward. Sections appear progressively as they become populated (signals + role badges → time horizon → archetype → environment excerpt → vignette excerpt → problems → personas).
- For steps 3–7 (Environment, Vignette, Problem statements, Personas, Journeys) add a 1–3 sentence helper paragraph in plain CCSD voice and a richer multi-line placeholder with concrete prompt cues (STEEP/PESTLE prompts for the environment, "show, don't summarize" for the vignette, "who / what / why" for problems, morning/mid-day/friction/evening for journeys, etc.).
- On step 9 add an **Export as Markdown** button that downloads `scenario-<slug>.md`. The file contains metadata, archetype framing, signals with role labels, environment, vignette, problems, personas, journeys, and the same traceability map shown on screen. It works for drafts and submitted scenarios. Pure client-side; no backend changes.

**Tradeoffs / what we did not do.** The carry-forward summary is read-only — students still go back via the step chips. No PDF export and no auto-save on every keystroke. No API or OpenAPI changes; this is entirely a frontend-side improvement.

**Files.** `artifacts/foresight/src/pages/scenarios-detail.tsx`.

---

## 2026-05-03 · Task #12 — Push to GitHub (initial CI scaffolding)

**Problem.** No remote on GitHub, no CI on `main`.

**Decision.** Add workflow templates under `docs/github-workflows/` (typecheck + build + Prettier on push and PR). Templates are committed under `docs/` rather than `.github/workflows/` because the Replit GitHub OAuth app does not have the `workflow` scope; the README in that folder explains how an instructor copies them into place.

**Tradeoffs.** Manual one-time copy step is friction, but it keeps the OAuth scope minimal.

---

## 2026-05-02 · Task #10 — Add to collection from signal & trend detail

**Problem.** Adding a signal or trend to a collection required navigating away to the collection page. Students lost their place mid-research.

**Decision.** Inline "Add to collection" affordance on signal and trend detail pages. Opens a popover with the user's accessible collections (private + class + explicitly-shared) and adds the item with one click. Reuses the existing collection-items endpoint.

**Files.** `artifacts/foresight/src/components/add-to-collection.tsx`, signal/trend detail pages.

---

## 2026-05-01 · Task #9 — Per-student and per-team collection sharing

**Problem.** A collection was either private or fully visible to the class. There was no middle ground for group projects.

**Decision.** Collections gained:
- A `visibility` field: `private`, `class`, or `shared`.
- `sharedWithStudentIds: string[]` for direct shares with named classmates.
- `sharedWithTeamIds: string[]` for shares with instructor-defined teams.

A new lightweight teams resource (instructor-managed) was added so groups can be referenced by name. Access is enforced on every collection read/write on the server, not just hidden in the UI.

**Tradeoffs.** Teams have no roles or hierarchy — flat membership is enough for a classroom.

**Files.** `artifacts/api-server/src/routes/collections.ts`, `routes/teams.ts`, `lib/api-spec/openapi.yaml`, multiple foresight UI components.

---

## 2026-04-30 · Task #8 — Trend creation with a real signal picker

**Problem.** The original trend form took supporting signals as free text, which broke server-side validation (`trendMinSignals`) and let students invent IDs.

**Decision.** Replace the textarea with a search-and-select picker that pulls from the live signals API and adds chips. Re-uses the same picker pattern that the scenario builder evidence board already used.

**Files.** `artifacts/foresight/src/pages/trends-*.tsx`.

---

## 2026-04-29 · Task #7 — Archetype descriptions in the scenario builder

**Problem.** "Continuation / New Equilibrium / Collapse / Transformation" meant nothing to students who had never read Jim Dator. They picked one at random and the rest of the wizard fell apart.

**Decision.** Each archetype card now carries a Dator-style two-sentence description plus a **"Thing From The Future"** prompt that anchors an everyday object in that future. Picking an archetype is now a real choice, not a label selection.

**Files.** `artifacts/foresight/src/pages/scenarios-detail.tsx` (`ARCHETYPE_DESCRIPTIONS`).

---

## 2026-04-28 · Task #6 — Five illustrated landing-page variants

**Problem.** No one had visual agreement on what the front door of the tool should feel like.

**Decision.** Used the canvas mockup-sandbox to render five distinct landing-page directions in parallel for side-by-side comparison. The "academic notebook crossed with a modern research workspace" direction was selected and graduated into the main app.

---

## 2026-04-27 · Task #5 — Class join code authentication (no database)

**Problem.** The PRD called for authenticated identity, but a database was scope-creep for a classroom tool.

**Decision.** Build identity on a flat `roster.json` file:
- One **class join code** generated on first server boot, salted-hash persisted to disk, plaintext kept in-memory so the instructor can re-reveal it without rotating until restart.
- Students sign in with `(joinCode, fullName, optional displayName)`. A returning name (Unicode-normalized + case-insensitive + whitespace-folded) re-uses the same roster entry.
- Faculty sign in with a separate **instructor passcode** (default `foresight2026`, changeable from `/instructor/settings`).
- Sessions are signed cookies; every mutating route is CSRF-protected and same-origin-gated.

The instructor dashboard exposes a **Class access** panel with Show / Hide / Copy / Rotate.

**Tradeoffs.** No password reset, no email recovery, no SSO. Acceptable for a single course; flagged in the PRD roadmap as a blocker for institutional rollout.

**Files.** `artifacts/api-server/src/auth/*`, `artifacts/api-server/data/roster.json`, multiple UI pages.

---

## 2026-04-25 · Task #3 — 2×2 scenario matrix on the instructor dashboard

**Problem.** Instructors had no fast way to see how a class's scenarios were distributed across the foresight space.

**Decision.** Add a 2×2 matrix view on the instructor dashboard. Axes are configurable; each scenario is a dot positioned by its archetype + time horizon by default. Clicking a dot opens the scenario.

---

## 2026-04-22 · Task #1 — Foresight Studio MVP

**Problem.** Build the first end-to-end version: signals → trends → collections → scenarios, with classroom-grade auth, exports, and a participation dashboard, against the PRD attached on day one.

**Decision (architecture).**
- pnpm monorepo, Node 24, TypeScript 5.9.
- API: Express 5 with Zod validation and **flat JSON files** under `artifacts/api-server/data/` instead of a database — so a course is archivable and the deployment story is "a single Replit".
- Web: React + Vite + wouter + TanStack Query.
- Contract: OpenAPI 3 (`lib/api-spec/openapi.yaml`) → Orval-generated react-query hooks. Client and server share types end-to-end.
- File evidence (PDF / image uploads on signal sources) goes to a local upload directory served by the API.
- Server-side validation gates: a submitted signal needs a source, a trend needs ≥`config.trendMinSignals` signals, a submitted scenario needs ≥`config.scenarioMinSignals` signals.

**Decision (UX).** A persisted design system was generated for the project (`design-system/foresight-studio/MASTER.md`) and treated as canonical for every later UI change. The visual identity is "an academic notebook crossed with a modern research workspace" — light, calm, foresight-domain-anchored.

**Outcome.** Shipped the MVP with code-review revisions, including CSRF/cookie hardening (a follow-up commit explicitly addressed cross-origin abuse). All later tasks build on this base.

---

## Conventions for future entries

When adding a new entry, please use this shape:

```
## YYYY-MM-DD · Task #N — One-line title

**Problem.** What was wrong or missing.
**Decision.** What we built and why.
**Tradeoffs.** What we explicitly did not do.
**Files.** Anchor paths if non-obvious.
```

Keep entries short; deeper detail belongs in the per-task plan files under `.local/tasks/` and in the PRD.
