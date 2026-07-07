# System Design Document: Foresight Studio Pipeline Engine

**Date:** July 6, 2026  
**Status:** Approved  
**Version:** 1.0  
**Target Architecture:** Python 3.12, SQLite 3  

---

## 1. System Architecture Diagram

```
+-------------------------------------------------------------------------------------------------+
|                                     Foresight Studio Engine                                     |
|                                                                                                 |
|   +---------------------+        +-------------------------+        +-----------------------+   |
|   |   1. Ingestion CLI  | -----> | 2. Multi-Model Assess   | -----> | 3. Semantic Dedupl.   |   |
|   |  - JSON file reader |        |  - Gemini API (Model)   |        |  - SentenceTransformer|   |
|   |  - RSS Feed parser  |        |  - Heuristic (Fallback) |        |  - TF-IDF (Fallback)  |   |
|   +---------------------+        +-------------------------+        +-----------------------+   |
|                                                                                 |               |
|                                                                                 v               |
|   +---------------------+        +-------------------------+        +-----------------------+   |
|   |  5. Output / Radar  | <----- |   4. SQLite Graph DB    | <----- |   Medoid Clustering   |   |
|   |  - Markdown report  |        |  - Relational signals   |        |  - "Keeper" isolation |   |
|   |  - Polar JSON state |        |  - Source provenance    |        |  - Dup linking        |   |
|   +---------------------+        +-------------------------+        +-----------------------+   |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. SQLite Knowledge Graph Database Schema

We use SQLite 3 for localized, zero-config relational storage. Foreign key constraints are enforced on connection.

```sql
-- Enforce on connection: PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS signals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT CHECK(category IN ('Social', 'Technological', 'Economic', 'Environmental', 'Political', 'Legal')) NOT NULL,
    source_url TEXT,
    source_type TEXT,
    date_observed TEXT,
    geography TEXT,
    sector TEXT,
    tags TEXT, -- Comma-separated strings
    confidence_score INTEGER DEFAULT 5,
    novelty_score INTEGER DEFAULT 5,
    impact_score INTEGER DEFAULT 5,
    strategic_relevance TEXT,
    time_horizon TEXT CHECK(time_horizon IN ('Near-term', 'Mid-term', 'Long-term')) NOT NULL,
    actionability TEXT,
    status TEXT CHECK(status IN ('Signal', 'Shadow')) DEFAULT 'Shadow',
    convergence_score REAL DEFAULT 1.0,
    is_keeper INTEGER DEFAULT 1, -- 1 for True, 0 for False (duplicate)
    keeper_id TEXT, -- Pointer to parent keeper signal if this is a duplicate
    source_metadata TEXT, -- JSON dictionary of original authors/duplicates for provenance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(keeper_id) REFERENCES signals(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS trends (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    summary TEXT NOT NULL,
    category TEXT CHECK(category IN ('Social', 'Technological', 'Economic', 'Environmental', 'Political', 'Legal')) NOT NULL,
    time_horizon TEXT CHECK(time_horizon IN ('Near-term', 'Mid-term', 'Long-term')) NOT NULL,
    impact_level TEXT CHECK(impact_level IN ('Low', 'Medium', 'High')) NOT NULL,
    uncertainty_level TEXT CHECK(uncertainty_level IN ('Low', 'Medium', 'High')) NOT NULL,
    convergence_score REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS signal_trend_map (
    signal_id TEXT,
    trend_id TEXT,
    relationship_type TEXT CHECK(relationship_type IN ('Evidence', 'Contradiction', 'Precursor', 'Adjacent')) DEFAULT 'Evidence',
    strength_score INTEGER CHECK(strength_score BETWEEN 1 AND 10) DEFAULT 5,
    notes TEXT,
    PRIMARY KEY (signal_id, trend_id),
    FOREIGN KEY(signal_id) REFERENCES signals(id) ON DELETE CASCADE,
    FOREIGN KEY(trend_id) REFERENCES trends(id) ON DELETE CASCADE
);
```

---

## 3. Core Algorithms

### 3.1 Multi-Model Assessment Pipeline (Stage 1)
Upon signal ingestion, the text is evaluated by the assessment engine:
1. **Gemini API Execution:** If `GEMINI_API_KEY` is set, a structured prompt is dispatched using the JSON response schema. It requests:
   - `impact_score` (Integer 1-10)
   - `time_horizon` ('Near-term', 'Mid-term', 'Long-term')
   - `strategic_relevance` (Explanation text)
   - `actionability` (Direct organizational next-step)
2. **Heuristic Fallback Strategy:** If the Gemini API is inaccessible, the text is scanned against a localized taxonomy dictionary to calculate scores deterministically:
   - *Time Horizon:* Checked against keyword vectors (e.g. "immediate", "soon", "now" -> Near-term; "decade", "horizon", "2070" -> Long-term).
   - *Impact Score:* Scored by scanning intensity nouns (e.g. "disrupt", "collapse", "revolutionize" +2; "slight", "minor" -1).

### 3.2 Semantic Deduplication & Medoid Clustering (Stage 2)
The deduplication pipeline runs in a 3-step matrix operation:

#### Step 1: Embeddings Vectorization
Text elements (Title + Description) are compiled and mapped to vectors:
$$\mathbf{v}_i = \text{Embed}(t_i) \in \mathbb{R}^{384}$$
*Fallback:* If `sentence-transformers` is unavailable, TF-IDF is run on word tokens to generate high-dimensional sparse representations.

#### Step 2: Cosine Similarity Matching
A pair-wise cosine similarity matrix $\mathbf{S}$ is generated for active signals:
$$S_{i,j} = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \|\mathbf{v}_j\|}$$
Signals are grouped into clusters where $S_{i,j} \geq 0.75$.

#### Step 3: Central Medoid Selection ("Keeper")
Within each similarity cluster $C$, the central **Medoid** node is isolated. The medoid is the signal that maximizes average similarity to all other members in the cluster:
$$k = \arg\max_{i \in C} \frac{1}{|C|} \sum_{j \in C} S_{i,j}$$
* Signal $k$ is marked as the **Keeper** (`is_keeper = 1`).
* All other signals $j \in C \setminus \{k\}$ are marked as duplicates (`is_keeper = 0`), and mapped via `keeper_id = k`.
* The Keeper's **Convergence Score** is calculated based on duplicate frequency:
$$\text{Convergence Score} = 1.0 + \alpha \cdot (|C| - 1)$$
where scaling factor $\alpha = 0.5$.

#### Step 4: Metadata Aggregation
The `source_metadata` column of the Keeper is updated with a JSON list representing the full attribution history of the duplicates (author, original URL, observation date). This ensures zero information loss and satisfies Design Justice requirements.

### 3.3 Polar Radar Geometry Conversion (Stage 4)
Radar parameters translate high-dimensional signals into visual coordinates on a polar polar chart:

* **Category Angle Mapping ($\theta$):**
  $$\theta(\text{Social}) = 30^\circ, \quad \theta(\text{Technological}) = 90^\circ, \quad \theta(\text{Economic}) = 150^\circ$$
  $$\theta(\text{Environmental}) = 210^\circ, \quad \theta(\text{Political}) = 270^\circ, \quad \theta(\text{Legal}) = 330^\circ$$
* **Radius Mapping ($r$):**
  $$r(\text{Near-term}) = 1.0, \quad r(\text{Mid-term}) = 2.0, \quad r(\text{Long-term}) = 3.0$$
* **Visual Node Representation:**
  - **Dot Diameter ($D$):** Linearly mapped to the `impact_score` (1-10 range):
    $$D = d_{\min} + \beta \cdot \text{impact\_score}$$
  - **Glow Intensity ($G$):** Logarithmically scaled with the `convergence_score`:
    $$G = \log(1.0 + \text{convergence\_score})$$

---

## 4. CLI Spec & Interface Designs

The tool is accessible via the executable python shell:

```bash
# Initialize DB
python3 src/cli.py init-db

# Ingest signals
python3 src/cli.py ingest <path_to_json_or_csv>

# Deduplicate DB entries
python3 src/cli.py deduplicate --threshold 0.75

# Output spatial polar coordinate layout of the graph
python3 src/cli.py radar --format json

# Write synthesized report of high-convergence strategic issues
python3 src/cli.py report --output report.md
```
