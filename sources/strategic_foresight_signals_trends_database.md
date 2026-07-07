# Strategic Foresight Signals and Trends Database Design

## Overview

This document outlines a database design for collecting, organizing, analyzing, and synthesizing signals and trends in strategic foresight. The purpose of the system is to support signal capture, pattern recognition, trend synthesis, impact assessment, uncertainty tracking, and strategic implication development.

A good foresight database should help answer:

- What are we seeing?
- What signals cluster together?
- What larger shifts may be forming?
- Who or what is affected?
- What uncertainties could change the interpretation?
- What should decision-makers do differently?

---

## Core Database Structure

### 1. Signals

Stores weak signals, observations, anomalies, articles, field notes, emerging events, or early indicators of possible change.

Suggested fields:

| Field | Description |
|---|---|
| `signal_id` | Unique identifier for the signal |
| `title` | Short name or headline for the signal |
| `description` | Summary of the observed signal |
| `source_url` | Link to the original source, if available |
| `source_type` | Article, report, interview, observation, social media, academic source, etc. |
| `date_observed` | Date the signal was captured |
| `geography` | Relevant location or region |
| `sector` | Relevant industry, discipline, or domain |
| `tags` | Keywords for search and clustering |
| `confidence_score` | How reliable or credible the signal appears to be |
| `novelty_score` | How new, surprising, or unusual the signal is |
| `impact_score` | Estimated potential impact if the signal scales |
| `created_by` | Person or system that added the signal |

---

### 2. Trends

Stores synthesized patterns formed from multiple signals.

Suggested fields:

| Field | Description |
|---|---|
| `trend_id` | Unique identifier for the trend |
| `name` | Name of the trend |
| `summary` | Concise description of the trend |
| `trend_stage` | Weak signal, emerging, growing, mainstream, declining |
| `time_horizon` | Near-term, mid-term, or long-term |
| `impact_level` | Estimated level of possible impact |
| `uncertainty_level` | Degree of uncertainty surrounding the trend |
| `related_domains` | Related fields, disciplines, sectors, or systems |
| `created_at` | Date the trend was created |
| `updated_at` | Date the trend was last revised |

---

### 3. Signal_Trend_Map

A many-to-many bridge table connecting signals to trends.

Suggested fields:

| Field | Description |
|---|---|
| `signal_id` | Linked signal |
| `trend_id` | Linked trend |
| `relationship_type` | Evidence, contradiction, precursor, amplification, adjacent development |
| `strength_score` | Estimated strength of the relationship |
| `notes` | Explanation of why the signal relates to the trend |

---

### 4. Drivers_of_Change

Stores broader forces shaping the future.

Suggested fields:

| Field | Description |
|---|---|
| `driver_id` | Unique identifier for the driver |
| `name` | Name of the driver of change |
| `category` | STEEP category: social, technological, economic, environmental, political |
| `description` | Explanation of the driver |
| `relevance_score` | Estimated relevance to the foresight domain |

---

### 5. Trend_Driver_Map

Connects trends to broader drivers of change.

Suggested fields:

| Field | Description |
|---|---|
| `trend_id` | Linked trend |
| `driver_id` | Linked driver of change |
| `influence_level` | Estimated strength of influence |
| `notes` | Explanation of the relationship |

---

### 6. Implications

Stores strategic meaning for organizations, programs, policies, curricula, products, services, or communities.

Suggested fields:

| Field | Description |
|---|---|
| `implication_id` | Unique identifier for the implication |
| `trend_id` | Linked trend |
| `audience` | Relevant stakeholder group or decision-maker |
| `opportunity` | Potential opportunity created by the trend |
| `risk` | Potential risk or threat created by the trend |
| `strategic_question` | Question leaders should consider |
| `recommended_action` | Possible action, experiment, policy, or strategic move |

---

### 7. Scenarios

Stores future scenarios built from trends and uncertainties.

Suggested fields:

| Field | Description |
|---|---|
| `scenario_id` | Unique identifier for the scenario |
| `title` | Scenario title |
| `description` | Narrative description of the scenario |
| `time_horizon` | Future time frame represented by the scenario |
| `primary_uncertainties` | Key uncertainties shaping the scenario |
| `scenario_type` | Exploratory, normative, baseline, wildcard, preferred future, etc. |
| `strategic_relevance` | Why the scenario matters |

---

### 8. Scenario_Trend_Map

Connects scenarios to trends.

Suggested fields:

| Field | Description |
|---|---|
| `scenario_id` | Linked scenario |
| `trend_id` | Linked trend |
| `role_in_scenario` | How the trend functions in the scenario |

---

## Practical Lightweight Version

For a lightweight implementation, start with five core tables:

1. `signals`
2. `trends`
3. `signal_trend_map`
4. `drivers`
5. `implications`

This structure is enough to collect observations, synthesize them into patterns, connect them to STEEP drivers, and translate them into actionable strategic insight.

There is no need to build the Death Star before validating the radar.

---

## Suggested System Capabilities

The database should support the following capabilities:

### Signal Capture

Capture weak signals, observations, field notes, news items, anomalies, cultural shifts, emerging technologies, policy changes, research findings, and other early indicators of change.

### Pattern Recognition

Cluster related signals to detect emerging patterns, contradictions, and recurring developments across domains.

### Trend Synthesis

Translate clusters of signals into named trends with descriptions, time horizons, maturity stages, and uncertainty levels.

### Impact Assessment

Evaluate potential consequences for stakeholders, systems, institutions, communities, industries, curricula, products, and policies.

### Uncertainty Tracking

Identify assumptions, competing interpretations, unresolved questions, and possible disruptors that could alter the trajectory of a trend.

### Strategic Implications

Turn trends into strategic questions, opportunities, risks, and recommended actions.

---

## Suggested Implementation Options

This design can be implemented in several formats:

- Airtable
- Notion
- Google Sheets
- PostgreSQL
- MySQL
- SQLite
- Microsoft Dataverse
- A custom web application

For early-stage foresight work, Airtable or Notion may be sufficient. For larger-scale institutional use, PostgreSQL or another relational database would provide better structure, query power, and long-term maintainability.

---

## Recommended Next Step

Begin with a small working prototype using the five-table lightweight model. Collect 25 to 50 signals, cluster them into 5 to 10 emerging trends, and test whether the schema supports useful strategic interpretation.

After testing, expand the system to include scenarios, uncertainty tracking, stakeholder-specific implications, and dashboard views.
