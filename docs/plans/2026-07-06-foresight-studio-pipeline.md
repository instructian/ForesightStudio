# Foresight Studio: Pipeline & CLI Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a robust, production-grade Python CLI tool implementing the four-stage sequential strategic foresight pipeline (Multi-Model Assessment, Semantic Deduplication, SQLite Knowledge Graph, and Radar Synthesis/Reports) as described in the Foresight Studio Architecture, while reorganizing and clean-sequestering the existing documents.

**Architecture:**
1. **Multi-Model Assessment:** Runs an assessment pipeline utilizing `google-generativeai` (Gemini API) to score and evaluate signal inputs. If no API key is set, it falls back gracefully to structured heuristic grading.
2. **Semantic Deduplication:** Uses sentence-transformers (`all-MiniLM-L6-v2`) to compute 384-dimensional dense vectors. Runs Cosine Similarity grouping, selects central medoids as "keepers" (Signals), and marks others as "duplicates" linked to their keepers. Fallback to TF-IDF token overlap if the library fails or isn't installed.
3. **SQLite Knowledge Graph:** Implements a schema for Signals, Trends, Shadows, and relationships, preserving the raw sources as JSON metadata behind keepers.
4. **Radar Synthesis & Reporting:** Outputs polar radar coordinate matrices (STEEP category as angle, Horizon as radius) and compiles executive-level markdown reports of high-convergence trends.

**Tech Stack:** Python 3.12, SQLite, NumPy, SciPy, SentenceTransformers (optional with fallback), Google Generative AI SDK, Click.

---

### Task 1: Sequester Existing Documents

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /sources/`
- Move: All original MD, PDF, and other files in `/Users/ianpollock/Documents/___FORESGHT /` into the `/Users/ianpollock/Documents/___FORESGHT /sources/` folder.

**Step 1: Write a python script to safely move files**
We will write a python script to sequester the files to prevent any manual errors or OS shell issues.

**Step 2: Run script to verify files are sequestered**
Expected: Root folder contains only `sources/` and any new PRD or design documents.

**Step 3: Commit**
```bash
git add sources/
git commit -m "chore: sequester legacy documents in sources folder"
```

---

### Task 2: Create Comprehensive PRD

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /PRD.md`

**Step 1: Write the PRD**
Compile a master PRD that integrates pedagogical, research, and enterprise goals, fully grounding the system in the `Foresight Studio: Architecture & Functional Requirements Synthesis`.

**Step 2: Verify PRD is written**
Ensure formatting is clean and covers all core pillars: source ingestion, multi-model assessment, semantic deduplication, knowledge graph mapping, interactive radar UI variables, and user roles (Student, Facilitator, Subscriber).

**Step 3: Commit**
```bash
git add PRD.md
git commit -m "docs: create comprehensive PRD at root"
```

---

### Task 3: Create Design Document

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /DESIGN_DOC.md`

**Step 1: Write the Design Document**
Specify system architecture, SQLite tables schema, vector clustering algorithm, polar radar coordinate mapping functions, and CLI design spec.

**Step 2: Verify Design Document is written**
Confirm mathematical formulations for deduplication convergence scores and polar conversions.

**Step 3: Commit**
```bash
git add DESIGN_DOC.md
git commit -m "docs: create technical design doc at root"
```

---

### Task 4: Implement SQLite Database Schema & Client

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /src/database.py`
- Test: `/Users/ianpollock/Documents/___FORESGHT /tests/test_database.py`

**Step 1: Write failing database test**
Define test cases verifying SQLite schema creation, CRUD operations for signals (including source JSON metadata), trends, and signal-trend mappings.

**Step 2: Run test to verify it fails**
Run: `python3 -m unittest tests/test_database.py`
Expected: FAIL (module not found)

**Step 3: Implement database.py**
Write the sqlite3 connections, schema execution (Signals, Trends, Signal_Trend_Map, Shadows), and insertion/query functions.

**Step 4: Verify test passes**
Run: `python3 -m unittest tests/test_database.py`
Expected: PASS

**Step 5: Commit**
```bash
git add src/database.py tests/test_database.py
git commit -m "feat: implement SQLite database and schema client"
```

---

### Task 5: Implement Multi-Model Assessment Engine

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /src/assessment.py`
- Test: `/Users/ianpollock/Documents/___FORESGHT /tests/test_assessment.py`

**Step 1: Write failing assessment test**
Test both the LLM API path (with mock response) and the heuristic fallback mode. Verify keys returned: `impact_score`, `strategic_relevance`, `time_horizon`, `actionability`.

**Step 2: Run test to verify it fails**
Expected: FAIL

**Step 3: Implement assessment.py**
Implement assessment scoring logic. If `GEMINI_API_KEY` is present in the environment or a fallback config, call the Gemini API (`gemini-2.5-flash` or `gemini-1.5-flash`) with a structured JSON schema. If not, parse keywords to generate a robust deterministic heuristic evaluation.

**Step 4: Verify test passes**
Expected: PASS

**Step 5: Commit**
```bash
git add src/assessment.py tests/test_assessment.py
git commit -m "feat: implement multi-model assessment engine with heuristic fallback"
```

---

### Task 6: Implement Semantic Deduplication Engine

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /src/deduplication.py`
- Test: `/Users/ianpollock/Documents/___FORESGHT /tests/test_deduplication.py`

**Step 1: Write failing deduplication test**
Provide 5 sample signals, with 3 closely overlapping (e.g. "autonomous eldercare robots", "robotic geriatric assistance devices"). Test similarity grouping and medoid selection (finding the most central document in the cluster as the "keeper").

**Step 2: Run test to verify it fails**
Expected: FAIL

**Step 3: Implement deduplication.py**
Use `sentence-transformers` for dense embeddings, calculating a cosine similarity matrix. Cluster signals exceeding a threshold (e.g., 0.75). For each cluster, compute the pairwise average similarity to identify the medoid ("keeper") signal. Mark other clustered signals as duplicates, assign them a `keeper_id`, and calculate a `convergence_score` for the keeper based on duplicate density (e.g., $1.0 + 0.5 \times N_{duplicates}$). Provide a token/TF-IDF vector fallback if sentence-transformers is missing.

**Step 4: Verify test passes**
Expected: PASS

**Step 5: Commit**
```bash
git add src/deduplication.py tests/test_deduplication.py
git commit -m "feat: implement semantic deduplication and medoid clustering"
```

---

### Task 7: Implement Interactive Radar & Narrative Synthesis

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /src/synthesis.py`
- Test: `/Users/ianpollock/Documents/___FORESGHT /tests/test_synthesis.py`

**Step 1: Write failing synthesis test**
Verify translation of categories (Social, Tech, etc.) to angular polar coordinates and Horizons (Near, Mid, Long) to radial coordinates. Verify narrative synthesis compiling high-convergence keepers into markdown reports.

**Step 2: Run test to verify it fails**
Expected: FAIL

**Step 3: Implement synthesis.py**
Write the coordinate calculators and report templates.
- Angle mappings: Social=30°, Technological=90°, Economic=150°, Environmental=210°, Political=270°, Legal=330°.
- Radius mapping: Near-term=1.0, Mid-term=2.0, Long-term=3.0.
- Report compiler: Loops over the database and outputs structural summaries. Optionally prompts Gemini for a blended executive narrative.

**Step 4: Verify test passes**
Expected: PASS

**Step 5: Commit**
```bash
git add src/synthesis.py tests/test_synthesis.py
git commit -m "feat: implement radar coordinate translation and report synthesis"
```

---

### Task 8: Implement CLI Shell

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /src/cli.py`
- Create: `/Users/ianpollock/Documents/___FORESGHT /requirements.txt`
- Test: `/Users/ianpollock/Documents/___FORESGHT /tests/test_cli.py`

**Step 1: Write CLI command tests**
Verify commands exist: `init-db`, `ingest`, `deduplicate`, `report`, `radar`.

**Step 2: Run test to verify it fails**
Expected: FAIL

**Step 3: Implement src/cli.py**
Use the `click` library to wire commands to the engines in `src/`.
- `init-db`: initializes SQLite database.
- `ingest <path_or_url>`: ingests data, performs multi-model assessment, and stores in the DB as Shadows/Signals.
- `deduplicate`: runs semantic deduplication on database entries, clustering duplicates behind medoid keepers.
- `report`: generates markdown summary of all active trends and high-impact keepers.
- `radar`: exports a JSON structure representing visual parameters for polar canvas rendering (including nodes, angles, radii, glow intensity derived from convergence score, size from impact).

**Step 4: Verify tests pass**
Expected: PASS

**Step 5: Commit**
```bash
git add src/cli.py requirements.txt tests/test_cli.py
git commit -m "feat: implement Click CLI shell and requirements configuration"
```

---

### Task 9: End-to-End Pipeline Validation

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /tests/test_pipeline_e2e.py`

**Step 1: Write E2E pipeline test**
Run the complete flow programmatically: Ingest a set of 8 raw signals, execute deduplication, map them in the graph database, generate polar coordinates, and export a markdown synthesis report.

**Step 2: Run test and verify success**
Expected: PASS

**Step 3: Commit**
```bash
git add tests/test_pipeline_e2e.py
git commit -m "test: implement E2E pipeline integration test"
```

---

### Task 10: Run full test suite and build workspace instructions

**Files:**
- Create: `/Users/ianpollock/Documents/___FORESGHT /GEMINI.md`
- Create: `/Users/ianpollock/Documents/___FORESGHT /README.md`

**Step 1: Execute all workspace tests**
Ensure 100% test passing rate across all unit and E2E tests.

**Step 2: Create GEMINI.md & README.md**
Write clear instructions for running the CLI tool, setting up a python environment, and performing future work.

**Step 3: Commit**
```bash
git add GEMINI.md README.md
git commit -m "docs: finalize workspace documentation and instructions"
```
