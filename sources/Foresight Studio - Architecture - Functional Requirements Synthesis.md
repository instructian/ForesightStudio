Foresight Studio: Architecture & Functional Requirements Synthesis

# Foresight Studio: Architecture & Functional Requirements Synthesis

## 1. Core System Architecture Pipeline
The technical engine of Foresight Studio operates as a four-stage sequential pipeline to manage data ingestion, filter out noise, build relationships, and deliver highly visual, actionable strategic insight.

1. **Multi-Model Assessment:** Ingests raw data points and parallel-queries specialized reasoning models to evaluate each input across four primary dimensions (Impact Potential 1-10, Strategic Relevance, Time Horizon, and Actionability).
2. **Semantic Deduplication:** Converts raw signals into 384-dimensional vectors using the `all-MiniLM-L6-v2` transformer model. It runs a multi-stage cosine similarity matrix matching, isolates the central "medoid" signal as the clean keeper node, and calculates a **Convergence Score** based on duplicate density.
3. **Knowledge Graph Storage:** Upgrades flat-file structures to a relational graph schema where nodes (Signals, Trends, Shadows) are mapped by weighted structural edges, preserving original source attributions as hidden metadata.
4. **Interactive Radar Synthesis & Reports:** Translates node weights into visual parameters on a polar canvas. A final ensemble reasoning pass compiles these nodes into targeted executive summaries and category breakdown reports.

---

## 2. Functional Requirements Document (FRD)

### 2.1 Product Vision & Strategy
Foresight Studio is a collaborative STEEP/PESTLE foresight platform designed to serve a dual mandate. It provides an accessible, low-barrier entry point for students in speculative-design environments while possessing the analytical rigor required for enterprise strategic consulting. 

The platform transforms disparate, raw intelligence into actionable strategic narratives through automated assessment, intelligent deduplication, and spatial visualization. At its core, the platform is anchored in **Design Justice** and inclusive design, ensuring that complex strategic data—including marginalized and under-reported societal shifts—is digestible and navigable without overwhelming cognitive load.

---

### 2.2 Core Functional Pillars

#### A. Source Ingestion & Categorization
The system must actively ingest, parse, and categorize external data (e.g., via RSS feeds) and user-submitted content into a structured taxonomy. 
* **Macro Trends:** Standard STEEP/PESTLE horizon scanning.
* **Weak Signals & Tech Edge-Cases:** Niche industry monitors, academic pre-prints, and patent filings.
* **Shadow Research:** Alternative data sources specifically focused on tracking black swans, systemic risks, and marginalized or under-reported societal shifts.
* **Selection Criteria:** Scans and ingestions can be filtered by specific operational requirements, including regional focus needs, industry specialization, and verification requirements.

#### B. Multi-Dimensional Signal Assessment
The system must evaluate every ingested data point across multiple strategic dimensions to determine its true value and filter out noise.
* **Impact Potential:** An assigned score (1-10) determining how significantly the signal could affect an organization, industry, or strategic objective.
* **Strategic Relevance (Context):** Evaluation of how directly the signal relates to specific configured goals, regional focuses, or STEEP categories.
* **Time Horizon (Timing):** Classification of the signal's relevance timeline, distinguishing between short-term urgency and long-term macro strategy.
* **Actionability (Response):** Extraction of concrete next steps or specific responses an organization could take based on the signal.

#### C. Semantic Deduplication & Metadata Preservation
To prevent information overload and fatigue, the system must intelligently reduce redundant noise while preserving the integrity of the data's origins.
* **Similarity Matching:** The platform will analyze all signals to identify conceptual overlaps, recognizing identical trends expressed in different terminology.
* **Centrality Selection:** When duplicate signals are found, the system isolates the single most representative and articulate version (the "keeper") for the primary display.
* **Convergence Scoring:** The system calculates a score based on how many redundant signals were consolidated into the keeper, ranking the momentum and reliability of the trend.
* **Metadata Preservation & Attribution:** The system must strictly preserve the original clustered sources (the "dropped" duplicates) as hidden metadata behind the keeper signal, ensuring full provider attribution and allowing users to audit the raw data.

#### D. Interactive Radar & Knowledge Graph UI
Traditional static charts will be replaced by an interactive, node-based spatial mapping interface, allowing users to visually explore the strategic landscape.
* **Spatial Mapping:** Signals and trends are positioned on a polar/radar canvas based on their STEEP category (angle) and Time Horizon (distance from center).
* **Visual Encoding:** 
    * **Size:** Represents the Impact Potential of the node.
    * **Color/Intensity:** Represents the Convergence Score (highly corroborated trends glow brighter).
* **Progressive Disclosure:** The interface offers a clean macro-view by default. Users can interact (hover, click) to reveal the underlying Knowledge Graph, exposing deeper edge connections, provider attribution, and the clustered metadata.

#### E. Strategic Synthesis & Report Generation
The platform bridges the gap between raw data visualization and actionable business intelligence by synthesizing narratives.
* **Executive Summaries:** Aggregation of high-impact, highly convergent signals to identify cross-cutting themes and synthesize board-ready strategic implications.
* **Category Analysis:** Grouping data by specific STEEP domains to generate targeted insights and identify inter-category connections.
* **Actionable Intelligence Delivery:** Output reports that translate the visual radar data into clear, narrative-driven recommendations tailored for stakeholders.

---

### 2.3 User Roles & Experience

#### A. The Contributor (Student / Team Member)
* **Actions:** Can easily submit new signals, links, and observations into the ecosystem.
* **Experience:** Requires a clear, intuitive dashboard to view how their individual contributions connect to broader class or team trends.
* **Focus:** Needs an interface free from excessive enterprise jargon, prioritizing collaborative sensemaking and accessible design.

#### B. The Facilitator (Instructor / Consultant)
* **Actions:** Sets the "Selection Criteria" (e.g., configuring the regional focus or industry specialization for the current project). Configures validation thresholds (e.g., minimum convergence required to form a Trend).
* **Experience:** Requires overarching visibility into the entire dataset, including un-merged "Shadows" and weak signals. Can trigger the generation of Executive Summaries and export data.
* **Focus:** Acts as the gatekeeper, managing the pedagogical flow for Contributors and determining what synthesized data is elevated to Subscribers.

#### C. The Subscriber (Enterprise Client / Viewer)
* **Actions:** Operates in a strict "Read-Only" capacity. Cannot submit raw signals, alter configuration thresholds, or manipulate the Knowledge Graph.
* **Experience:** Seamless access to the Interactive Radar for exploring synthesized, high-convergence trends without being exposed to raw, un-deduplicated noise. Can interact with the visualization (zoom, filter, hover) and download AI-generated reports.
* **Focus:** Rapid insight extraction and clear strategic narratives, delivering immediate return-on-investment from the curated intelligence.