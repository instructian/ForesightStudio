# Foresight Studio: Core Architecture, Conventions & Project Memory

Welcome to **Foresight Studio**. This document serves as the canonical guidelines, architecture manual, and developer memory file for this repository. It must be read and adhered to by all developers and AI models working on this project.

---

## 1. Directory Structure

*   **`src/`**: Python source code.
    *   `src/cli.py`: Click-based terminal entrypoint exposing the full pipeline.
    *   `src/database.py`: Client for SQLite Knowledge Graph operations.
    *   `src/assessment.py`: Signal grading engine (Gemini API with heuristic fallbacks).
    *   `src/deduplication.py`: Cluster matching and medoid identification engine (SentenceTransformers with a pure-Python TF-IDF fallback).
    *   `src/synthesis.py`: Mathematical coordinate calculators and Strategic Report narrative compilers.
*   **`tests/`**: Test suite with unit and End-to-End integration coverage.
    *   `tests/test_database.py`: Database client unit tests.
    *   `tests/test_assessment.py`: Signal assessment and heuristic fallback unit tests.
    *   `tests/test_deduplication.py`: TF-IDF matrix math and cluster medoid tests.
    *   `tests/test_synthesis.py`: Polar math and report layout tests.
    *   `tests/test_cli.py`: Automated Click CliRunner shell tests.
    *   `tests/test_pipeline_e2e.py`: Full programmatic End-to-End pipeline integration test.
*   **`sources/`**: Clean-sequestered historical archives, chat transcripts, PDF briefs, and legacy functional schemas.
*   **`docs/`**: Active blueprints, implementation plans, and milestones.

---

## 2. Coding Conventions

*   **Python Version:** Optimized for **Python 3.12+**.
*   **Database Engine:** Standard **SQLite 3**.
    *   Always enforce foreign keys programmatically on connection: `PRAGMA foreign_keys = ON;`.
    *   Utilize row factory `sqlite3.Row` to allow clean dictionary mappings.
*   **Error Boundaries & Robustness (Technical Mandates):**
    *   The pipeline must maintain high-signal fallbacks for heavy ML systems. 
    *   If `sentence-transformers` is absent or throws loading errors, the engine must fall back to the built-in, pure-Python **`FallbackTFIDF`** similarity algorithm.
    *   If `google-generativeai` is absent or its API key is unset, the engine must fall back to the deterministic, keyword-driven **Heuristics Assessment** model.
*   **Design Justice Integration:**
    *   Original authors, source URLs, and descriptions of deduplicated and merged signals must **NEVER** be deleted or extracted out of the system.
    *   Duplicates must be aggregated inside the Keeper's `source_metadata` column as a JSON array, maintaining clean provenance and auditable attribution histories.

---

## 3. Test & Verification Guidelines

Every codebase change requires corresponding unit or integration tests:
*   Use Python's built-in `unittest` framework.
*   Isolate tests by using temporary files (`tempfile.mkstemp` or `tempfile.TemporaryDirectory`) for file systems and database schemas, cleaning them up in `tearDown`.
*   To run the complete test suite together:
    ```bash
    PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"
    ```
