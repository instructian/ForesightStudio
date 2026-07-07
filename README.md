# Foresight Studio: Strategic Foresight CLI Engine

Foresight Studio is a collaborative strategic foresight pipeline designed to bridge speculative design pedagogy and enterprise strategic consulting. The tool ingests raw weak signals, automatically grades them along strategic dimensions, clusters them semantically to reduce cognitive overload, maintains their historical provenance in a sqlite-based knowledge graph, and outputs structured polar radar parameters and synthesized markdown reports.

---

## 1. System Requirements & Installation

Foresight Studio is built using **Python 3.12+** and is designed to operate on a zero-config, portable SQLite database.

### Installation Steps
1. Clone or navigate to this directory.
2. Setup a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install core dependencies:
   ```bash
   pip install -r requirements.txt
   ```

*Note: Optional heavy machine learning packages (`sentence-transformers`, `numpy`) and the `google-generativeai` SDK are supported with fallback pathways. If not present, the tool automatically executes an optimized pure-Python TF-IDF cosine-similarity engine and deterministic heuristic grading.*

---

## 2. CLI Usage Guide

Expose all pipeline stages using the Click-powered CLI shell:

```bash
# Set PYTHONPATH so the shell can locate src/
export PYTHONPATH=.
```

### Initialize Database Schema
Create the SQLite Knowledge Graph schema:
```bash
python3 src/cli.py init-db
```
*Creates the database file at `data/foresight_studio.db` by default.*

### Ingest Signal Scans
Ingest signals from a structured JSON dataset and run Multi-Model Assessment:
```bash
python3 src/cli.py ingest tests/signals.json
```
*This command runs Multi-Model Assessment (Gemini API or local heuristics fallback) to analyze and insert the signals.*

### Semantic Deduplication & Medoid Clustering
Group highly overlapping weak signals into clusters, isolate central Keepers, and link duplicates behind them as provenance metadata:
```bash
python3 src/cli.py deduplicate --threshold 0.75
```
*Reduces noise while preserving individual student/contributor attribution (Design Justice).*

### Export Spatial Polar Radar Mapping
Output polar coordinate positions ($\theta$ representing STEEP category, $r$ representing Time Horizon) for rendering on canvas components:
```bash
python3 src/cli.py radar --format json --output data/radar.json
```
*Outputs visual parameters including angular coordinates, diameters mapped to impact, and glow intensities mapped to convergence.*

### Compile Synthesized Strategic Reports
Generate board-ready executive summaries and category foresight reports:
```bash
python3 src/cli.py report --output data/strategic_report.md
```
*Optionally calls the Gemini API to write a cohesive strategic brief blending the top signals.*

---

## 3. Core Database Tables (Knowledge Graph)

* **`signals` / `shadows`:** Stores raw observation records. Stands as a "Shadow" until verified and elevated to a primary "Signal" node during deduplication. Includes JSON metadata to nesting duplicates.
* **`trends`:** Overarching synthesized macro patterns mapping multiple signal nodes.
* **`signal_trend_map`:** Relational join bridge mapping signals to trends with specific relation strengths and notes.

---

## 4. Execution Tests

Run the comprehensive unit and integration test suite with 100% passing coverage:

```bash
# Execute Database tests
PYTHONPATH=. python3 -m unittest tests/test_database.py

# Execute Assessment tests
PYTHONPATH=. python3 -m unittest tests/test_assessment.py

# Execute Semantic Deduplication tests
PYTHONPATH=. python3 -m unittest tests/test_deduplication.py

# Execute Radar Synthesis tests
PYTHONPATH=. python3 -m unittest tests/test_synthesis.py

# Execute CLI Shell tests
PYTHONPATH=. python3 -m unittest tests/test_cli.py

# Execute End-to-End Pipeline integration tests
PYTHONPATH=. python3 -m unittest tests/test_pipeline_e2e.py

# Run all tests together
PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"
```
