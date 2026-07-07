# Product Requirements Document (PRD): Foresight Studio

**Date:** July 6, 2026  
**Status:** Canonical  
**Version:** 1.0  
**Primary Audience:** Engineering Team, Instructors/Facilitators, Speculative Designers, Enterprise Partners  

---

## 1. Executive Summary & Vision

### 1.1 Product Vision
**Foresight Studio** is a collaborative strategic foresight platform designed to bridge the gap between speculative design pedagogy and enterprise-grade strategic consulting. The platform acts as a structured learning and analytical workspace where users move from raw horizon scanning to rigorous, defensible, and actionable strategic narratives. 

By automating multi-dimensional analysis, reducing cognitive noise through semantic deduplication, and organizing raw data into a relational knowledge graph, Foresight Studio enables users to trace, test, and contest assumptions about the future.

### 1.2 The Dual Mandate
Foresight Studio solves two distinct but complementary problems:
1. **The Pedagogical Path (Speculative Design Students):** Traditional classrooms struggle with spreadsheet-heavy signal tracking where student submissions lack standardization, dates are lost, and teamwork is disconnected. Foresight Studio provides an intuitive, highly scaffolded, jargon-free UI that guides students to capture, explain, and connect "weak signals."
2. **The Enterprise Path (Strategic Consultants & Executives):** Modern enterprise strategy is often overwhelmed by information fatigue, redundant signals, and lack of traceability. Foresight Studio utilizes semantic deduplication to synthesize noisy data into clear "Trends," mapping them on a spatial Polar Radar Canvas while preserving raw source provenance as auditable metadata.

### 1.3 Design Justice Integration
In accordance with **Design Justice** frameworks, the system is engineered to counter the extraction of marginalized lived experiences. It enforces **Provenance & Attribution Gating**, ensuring that under-reported societal shifts (Shadow Research) are not erased. When signals are merged, original authors and localized standpoints are preserved as active metadata behind the main visual nodes, creating a "designed contact zone" rather than a sterilized consensus.

---

## 2. Core Functional Pillars (The 4-Stage Pipeline)

Foresight Studio operates on a sequential 4-stage architecture to transition raw foresight data into visual, board-ready strategic summaries.

```
[ Ingestion ] ➔ [ Stage 1: Assessment ] ➔ [ Stage 2: Deduplication ] ➔ [ Stage 3: Knowledge Graph ] ➔ [ Stage 4: Radar & Reports ]
```

### 2.1 Stage 1: Multi-Model Assessment
Every ingested signal must be automatically evaluated across four primary dimensions to filter noise and standardize unstructured text:
* **Impact Potential (1-10):** Estimating the scope of disruption should the signal scale.
* **Strategic Relevance:** Scoring the conceptual distance between the signal and configured strategic domains (STEEP/PESTLE categories).
* **Time Horizon:** Categorizing timing into Near-Term (0-3 years), Mid-Term (3-10 years), or Long-Term (10-50 years).
* **Actionability:** Extracting concrete, immediate responses or specific organizational experiments triggered by the signal.

### 2.2 Stage 2: Semantic Deduplication & Metadata Preservation
To solve information overload:
* **Vector Transformation:** Text is converted to dense vector embeddings using the `all-MiniLM-L6-v2` transformer (384 dimensions).
* **Cosine Similarity Clustering:** Signals with similarity coefficients exceeding a threshold (default: 0.75) are grouped into single clusters.
* **Medoid Selection ("The Keeper"):** For each cluster, the central "medoid" node—the signal closest to all others in vector space—is selected as the primary visible signal (the "Keeper"). All other signals in the cluster are marked as "Duplicates."
* **Convergence Score Calculation:** The Keeper gains a dynamic Convergence Score representing the cluster's duplicate density (frequency/corroboration of the trend).
* **Provenance Retention:** Duplicates are not deleted; they are nested behind the Keeper. The platform preserves the names, source URLs, dates, and localized descriptions of all duplicates.

### 2.3 Stage 3: SQLite Knowledge Graph Storage
The system replaces flat lists with a relational knowledge graph using SQLite, schema-hardened for relational integrity:
* **Nodes:**
  * **Signals / Shadows:** Raw observations. Signals are verified; Shadows represent anomalous, un-deduplicated, or marginalized weak signals.
  * **Trends:** Synthesized macro patterns linked to multiple signals.
  * **Drivers of Change:** Overarching forces of change (STEEP/PESTLE categories).
  * **Implications:** Risks, opportunities, and strategic questions for audiences.
* **Edges:** Many-to-many associations (`Signal_Trend_Map`, `Trend_Driver_Map`) mapped with semantic attributes (`relationship_type`, `strength_score`) to ensure strict traceability from high-level scenario down to original raw source articles.

### 2.4 Stage 4: Interactive Radar & Narrative Synthesis
Visualizing complex foresight landscapes spatially on a Polar Canvas:
* **Spatial Radar Geometry:**
  * **Angle (θ):** Determined by the STEEP/PESTLE category.
    * *Social (S):* 30°
    * *Technological (T):* 90°
    * *Economic (Ec):* 150°
    * *Environmental (En):* 210°
    * *Political (P):* 270°
    * *Legal (L):* 330°
  * **Radius (r):** Derived from the Time Horizon (Near=1.0, Mid=2.0, Long=3.0).
* **Visual Attributes:**
  * **Node Size:** Encodes the *Impact Potential* (higher impact = larger dot).
  * **Node Glow/Intensity:** Encodes the *Convergence Score* (more duplicate density = brighter glow).
* **Executive Report Compiler:** Compiles a final markdown/JSON synthesis combining high-impact, highly convergent trends into board-ready executive summaries.

---

## 3. User Personas & Experience Requirements

### 3.1 The Contributor (Student / Team Member)
* **Goal:** Easily submit signals, see how individual scans connect to broader trends, and work without cognitive overload.
* **Dashboard Requirements:**
  * Low-barrier submission wizard (title, description, URL, date, category).
  * Context-aware, inline prompts explaining foresight terminology in a supportive, academic voice.
  * Real-time contribution view showing where their signals sit on the collective radar.

### 3.2 The Facilitator (Instructor / Consultant)
* **Goal:** Set project filters, establish verification rules, monitor participation, and compile synthesized portfolios.
* **Dashboard Requirements:**
  * "Selection Criteria" controls to configure specific regional constraints, industry filters, or PESTLE domains.
  * Database access to view "Shadows" and adjust deduplication similarity thresholds (0.50 - 0.95).
  * Prompt control panel to configure LLM reasoning parameters.

### 3.3 The Subscriber (Enterprise Client / Executive)
* **Goal:** Extract rapid strategic insights, read synthesized narratives, and explore the radar without dealing with un-deduplicated noise.
* **Dashboard Requirements:**
  * Read-only spatial Polar Radar canvas.
  * Progressive Disclosure: clicking a Node reveals the Keeper details, which can be expanded to show the underlying Knowledge Graph, original source URLs, and individual duplicates (provenance).
  * Export options for generated executive portfolios and visual radar configurations.

---

## 4. Technical Constraints & Out-of-Scope

### 4.1 Technical Constraints
* **Runtime:** Python 3.12+ for the core pipeline engine.
* **Storage:** SQLite 3 database for the relational schema, ensuring zero-configuration deployment and full portfolio portability.
* **Dependencies:** Optimized for high portability. Dynamic fallbacks are required for ML pipelines: if `sentence-transformers` is absent, the engine must gracefully fall back to optimized TF-IDF and keyword-overlap algorithms. If the `GEMINI_API_KEY` is not present, the assessment engine must execute deterministic heuristic analysis.

### 4.2 Out-of-Scope (Non-Goals)
* **SSO/Identity Server:** Simple passcode and secure cookied sessions are sufficient for pedagogical/consulting scopes.
* **Autonomous Scenario Writer:** The tool must not autonomously invent scenario text; it is an analytical assistant. Final scenario text must remain student-authored and grounded in verifiable signals.
* **Real-time Collaboration Socket Server:** Traditional polling is sufficient for dashboard refreshes.
