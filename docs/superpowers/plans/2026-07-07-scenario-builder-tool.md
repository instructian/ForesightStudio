# Scenario Builder Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A scenario-planning tool that turns the scanned signal/trend/shadow graph into 2×2 scenario sets: it ranks critical uncertainties, scaffolds four quadrant scenarios, links evidence and Shadow risks into each, wind-tunnels narratives against contradicting evidence, and compiles scenario reports.

**Architecture:** A new `ScenarioEngine` module (`src/scenario.py`) operating on the local SQLite `Database` (scenario tables from the Database Model Revision plan, Task 8), exposed through a `scenario` click sub-group in `src/cli.py`. Report generation follows the house pattern: deterministic Markdown template with optional Gemini enrichment. The Supabase scenario tables (`scenario_sets`/`scenarios`/`scenario_nodes`) mirror this model for the SaaS surface.

**Tech Stack:** Python 3.12, `sqlite3`, `click`, `unittest` (+ `click.testing.CliRunner`), optional `google.generativeai`.

## Global Constraints

- **DEPENDS ON:** `docs/superpowers/plans/2026-07-07-database-model-revision.md` Tasks 8–9 (SQLite scenario tables, `uncertainty_score`, `polarity`, `shadow_type` columns, and `Database` scenario methods). Do not start until those are merged.
- Test command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"` — full suite green after every task.
- Domain vocabulary: **Shadow** = weak signal of a declining system, obsolete behavior, or unwanted "worst-case"/disrupted future; the tool must surface Shadows in every scenario so worst cases are never blind spots. **Critical uncertainty** = a signal/trend that is simultaneously high-impact and high-uncertainty; the two chosen as axes define the 2×2.
- Quadrant convention (fixed): `High-High` = axis X high pole × axis Y high pole; `High-Low` = X high × Y low; `Low-High` = X low × Y high; `Low-Low` = X low × Y low.
- Engines never print; they return values. Only the CLI layer uses `click.echo` (matches existing `src/` style).
- All new Database access goes through the `Database` methods produced by the DB plan Task 8 — no raw SQL in `src/scenario.py` except read-only queries not covered by those methods.

## Feature Overview (what gets built)

| # | Feature | Foresight method it serves |
|---|---------|---------------------------|
| F1 | Critical Uncertainty Ranker — rank keeper signals by `impact_score × uncertainty_score`, flag axis candidates | Axis selection for 2×2 scenario matrices |
| F2 | Scenario Set Builder — create a set from two axis signals + pole labels; auto-scaffold the 4 quadrant scenarios | 2×2 (GBN-style) scenario construction |
| F3 | Evidence Linking — attach signals/trends/shadows to a scenario with roles: Driver, Evidence, Wildcard, Shadow-Risk, Implication | Grounding narratives in the scanning graph |
| F4 | Shadow Risk Register — per scenario (or whole set), all linked `polarity='Shadow'` signals ordered by impact, with shadow_type and mitigation notes | Blind-spot prevention, risk mitigation |
| F5 | Wind-Tunneling — surface Contradiction-linked evidence against a scenario's linked signals to stress-test the narrative | Scenario robustness testing |
| F6 | Scenario Report — Markdown report per set: axes rationale, quadrant narratives, evidence citations, risk register, early-warning indicators (optional Gemini polish) | Deliverable synthesis |
| F7 | CLI — `scenario axes / create-set / link / risks / windtunnel / report` | Operator workflow |

---

### Task 1: ScenarioEngine + Critical Uncertainty Ranker (F1)

**Files:**
- Create: `src/scenario.py`
- Test: `tests/test_scenario.py` (create)

**Interfaces:**
- Produces: `class ScenarioEngine` with `rank_critical_uncertainties(db, limit: int = 10) -> List[Dict[str, Any]]`. Each dict: `{"id", "title", "category", "polarity", "impact_score", "uncertainty_score", "criticality", "axis_candidate"}` sorted by `criticality` (impact × uncertainty) descending. Signals with `uncertainty_score IS NULL` are excluded (unassessed must not contaminate ranking). `axis_candidate` is True when both scores ≥ 7.

- [ ] **Step 1: Write the failing test.** Create `tests/test_scenario.py`:

```python
import unittest

from src.database import Database
from src.scenario import ScenarioEngine


def make_signal(db, sig_id, title, impact, uncertainty, polarity="Emergent", **kw):
    base = {
        "id": sig_id, "title": title, "description": f"{title} description",
        "category": "Technological", "time_horizon": "Mid-term",
        "impact_score": impact, "uncertainty_score": uncertainty,
        "polarity": polarity, "is_keeper": 1,
    }
    base.update(kw)
    return db.add_signal(base)


class TestCriticalUncertaintyRanker(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.engine = ScenarioEngine()

    def tearDown(self):
        self.db.close()

    def test_ranks_by_impact_times_uncertainty(self):
        make_signal(self.db, "low", "Low stakes", impact=3, uncertainty=3)
        make_signal(self.db, "crit", "Critical uncertainty", impact=9, uncertainty=8)
        make_signal(self.db, "mid", "Middling", impact=6, uncertainty=5)
        ranked = self.engine.rank_critical_uncertainties(self.db)
        self.assertEqual([r["id"] for r in ranked], ["crit", "mid", "low"])
        self.assertEqual(ranked[0]["criticality"], 72)
        self.assertTrue(ranked[0]["axis_candidate"])
        self.assertFalse(ranked[1]["axis_candidate"])

    def test_unassessed_signals_excluded(self):
        make_signal(self.db, "assessed", "Assessed", impact=5, uncertainty=5)
        self.db.add_signal({"id": "raw", "title": "No uncertainty yet",
                            "description": "d", "category": "Social",
                            "time_horizon": "Near-term", "is_keeper": 1})
        ranked = self.engine.rank_critical_uncertainties(self.db)
        self.assertEqual([r["id"] for r in ranked], ["assessed"])

    def test_non_keepers_excluded(self):
        make_signal(self.db, "dup", "Duplicate", impact=9, uncertainty=9, is_keeper=0)
        self.assertEqual(self.engine.rank_critical_uncertainties(self.db), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify FAIL.** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest tests.test_scenario -v` → ModuleNotFoundError: src.scenario.

- [ ] **Step 3: Implement.** Create `src/scenario.py`:

```python
import json
import os
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

QUADRANTS = ("High-High", "High-Low", "Low-High", "Low-Low")
ROLES = ("Driver", "Evidence", "Wildcard", "Shadow-Risk", "Implication")
AXIS_CANDIDATE_FLOOR = 7


class ScenarioEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.use_gemini = HAS_GEMINI_SDK and self.api_key is not None
        if self.use_gemini:
            genai.configure(api_key=self.api_key)

    def rank_critical_uncertainties(self, db, limit: int = 10) -> List[Dict[str, Any]]:
        """Rank keeper signals by impact x uncertainty for 2x2 axis selection.

        Unassessed signals (uncertainty NULL) are excluded so defaults cannot
        contaminate axis choice.
        """
        keepers = db.get_all_signals(filter_keeper=True)
        ranked = []
        for s in keepers:
            uncertainty = s.get("uncertainty_score")
            if uncertainty is None:
                continue
            impact = s.get("impact_score") or 0
            criticality = impact * uncertainty
            ranked.append({
                "id": s["id"],
                "title": s["title"],
                "category": s["category"],
                "polarity": s.get("polarity") or "Emergent",
                "impact_score": impact,
                "uncertainty_score": uncertainty,
                "criticality": criticality,
                "axis_candidate": impact >= AXIS_CANDIDATE_FLOOR and uncertainty >= AXIS_CANDIDATE_FLOOR,
            })
        ranked.sort(key=lambda r: r["criticality"], reverse=True)
        return ranked[:limit]
```

- [ ] **Step 4: Run tests → pass; full suite.**

- [ ] **Step 5: Commit.** `git add src/scenario.py tests/test_scenario.py && git commit -m "feat(scenario): critical uncertainty ranker"`

---

### Task 2: Scenario Set Builder (F2)

**Files:**
- Modify: `src/scenario.py`
- Test: `tests/test_scenario.py` (append)

**Interfaces:**
- Consumes: `Database.add_scenario_set`, `Database.add_scenario`, `Database.get_signal` (existing), `Database.get_scenarios_for_set`.
- Produces: `ScenarioEngine.create_scenario_set(db, title, axis_x_signal_id, axis_y_signal_id, axis_x_low_label, axis_x_high_label, axis_y_low_label, axis_y_high_label, description=None, horizon_year=None) -> Dict[str, Any]` returning `{"scenario_set_id": str, "scenarios": [{"id", "quadrant", "title"}, ...4 items]}`. Auto-generated quadrant titles combine pole labels, e.g. `"Distributed / Expensive"`. Raises `ValueError` if either axis signal is missing or if the two axes are the same signal.

- [ ] **Step 1: Write the failing test.** Append to `tests/test_scenario.py`:

```python
class TestScenarioSetBuilder(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.engine = ScenarioEngine()
        make_signal(self.db, "ax", "Energy decentralization", impact=8, uncertainty=8)
        make_signal(self.db, "ay", "Energy cost", impact=9, uncertainty=7)

    def tearDown(self):
        self.db.close()

    def _create(self):
        return self.engine.create_scenario_set(
            self.db, title="Energy 2040",
            axis_x_signal_id="ax", axis_y_signal_id="ay",
            axis_x_low_label="Centralized", axis_x_high_label="Distributed",
            axis_y_low_label="Cheap", axis_y_high_label="Expensive",
            horizon_year=2040,
        )

    def test_creates_set_and_four_quadrants(self):
        result = self._create()
        scenarios = self.db.get_scenarios_for_set(result["scenario_set_id"])
        self.assertEqual(len(scenarios), 4)
        self.assertEqual({s["quadrant"] for s in scenarios},
                         {"High-High", "High-Low", "Low-High", "Low-Low"})

    def test_quadrant_titles_combine_pole_labels(self):
        result = self._create()
        by_quadrant = {s["quadrant"]: s for s in
                       self.db.get_scenarios_for_set(result["scenario_set_id"])}
        self.assertEqual(by_quadrant["High-High"]["title"], "Distributed / Expensive")
        self.assertEqual(by_quadrant["Low-Low"]["title"], "Centralized / Cheap")

    def test_rejects_unknown_axis_signal(self):
        with self.assertRaises(ValueError):
            self.engine.create_scenario_set(
                self.db, title="Bad", axis_x_signal_id="missing", axis_y_signal_id="ay",
                axis_x_low_label="a", axis_x_high_label="b",
                axis_y_low_label="c", axis_y_high_label="d")

    def test_rejects_identical_axes(self):
        with self.assertRaises(ValueError):
            self.engine.create_scenario_set(
                self.db, title="Bad", axis_x_signal_id="ax", axis_y_signal_id="ax",
                axis_x_low_label="a", axis_x_high_label="b",
                axis_y_low_label="c", axis_y_high_label="d")
```

- [ ] **Step 2: Run to verify FAIL.**

- [ ] **Step 3: Implement.** Add to `ScenarioEngine`:

```python
    def create_scenario_set(
        self, db, title: str,
        axis_x_signal_id: str, axis_y_signal_id: str,
        axis_x_low_label: str, axis_x_high_label: str,
        axis_y_low_label: str, axis_y_high_label: str,
        description: Optional[str] = None,
        horizon_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a 2x2 scenario set and scaffold its four quadrant scenarios."""
        if axis_x_signal_id == axis_y_signal_id:
            raise ValueError("Axis X and Axis Y must be two different signals")
        for sig_id in (axis_x_signal_id, axis_y_signal_id):
            if db.get_signal(sig_id) is None:
                raise ValueError(f"Axis signal not found: {sig_id}")

        set_id = db.add_scenario_set({
            "title": title,
            "description": description,
            "axis_x_signal_id": axis_x_signal_id,
            "axis_y_signal_id": axis_y_signal_id,
            "axis_x_low_label": axis_x_low_label,
            "axis_x_high_label": axis_x_high_label,
            "axis_y_low_label": axis_y_low_label,
            "axis_y_high_label": axis_y_high_label,
            "horizon_year": horizon_year,
        })

        pole = {
            "High-High": (axis_x_high_label, axis_y_high_label),
            "High-Low": (axis_x_high_label, axis_y_low_label),
            "Low-High": (axis_x_low_label, axis_y_high_label),
            "Low-Low": (axis_x_low_label, axis_y_low_label),
        }
        scenarios = []
        for quadrant in QUADRANTS:
            x_label, y_label = pole[quadrant]
            scn_id = db.add_scenario({
                "scenario_set_id": set_id,
                "quadrant": quadrant,
                "title": f"{x_label} / {y_label}",
            })
            scenarios.append({"id": scn_id, "quadrant": quadrant,
                              "title": f"{x_label} / {y_label}"})
        return {"scenario_set_id": set_id, "scenarios": scenarios}
```

- [ ] **Step 4: Run tests → pass; full suite.**

- [ ] **Step 5: Commit.** `git commit -m "feat(scenario): 2x2 scenario set builder with quadrant scaffolding"`

---

### Task 3: Evidence Linking (F3)

**Files:**
- Modify: `src/scenario.py`
- Test: `tests/test_scenario.py` (append)

**Interfaces:**
- Consumes: `Database.map_signal_to_scenario`, `Database.get_scenario_signals`.
- Produces: `ScenarioEngine.link_signal(db, scenario_id, signal_id, role="Evidence", notes="") -> None` (raises `ValueError` for unknown role or missing signal) and `ScenarioEngine.get_linked(db, scenario_id, role: Optional[str] = None) -> List[Dict]`.

- [ ] **Step 1: Write the failing test.** Append:

```python
class TestEvidenceLinking(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.engine = ScenarioEngine()
        make_signal(self.db, "ax", "Axis X", impact=8, uncertainty=8)
        make_signal(self.db, "ay", "Axis Y", impact=8, uncertainty=8)
        result = self.engine.create_scenario_set(
            self.db, title="T", axis_x_signal_id="ax", axis_y_signal_id="ay",
            axis_x_low_label="lo", axis_x_high_label="hi",
            axis_y_low_label="lo2", axis_y_high_label="hi2")
        self.scenario_id = result["scenarios"][0]["id"]

    def tearDown(self):
        self.db.close()

    def test_link_and_filter_by_role(self):
        make_signal(self.db, "ev", "Evidence sig", impact=5, uncertainty=4)
        make_signal(self.db, "sh", "Decaying infra", impact=8, uncertainty=6,
                    polarity="Shadow", shadow_type="Declining-System")
        self.engine.link_signal(self.db, self.scenario_id, "ev", role="Evidence")
        self.engine.link_signal(self.db, self.scenario_id, "sh", role="Shadow-Risk")
        all_links = self.engine.get_linked(self.db, self.scenario_id)
        self.assertEqual(len(all_links), 2)
        risks = self.engine.get_linked(self.db, self.scenario_id, role="Shadow-Risk")
        self.assertEqual([r["id"] for r in risks], ["sh"])

    def test_rejects_unknown_role(self):
        make_signal(self.db, "ev", "Evidence sig", impact=5, uncertainty=4)
        with self.assertRaises(ValueError):
            self.engine.link_signal(self.db, self.scenario_id, "ev", role="Vibes")

    def test_rejects_missing_signal(self):
        with self.assertRaises(ValueError):
            self.engine.link_signal(self.db, self.scenario_id, "nope")
```

- [ ] **Step 2: Run to verify FAIL.**

- [ ] **Step 3: Implement.** Add to `ScenarioEngine`:

```python
    def link_signal(self, db, scenario_id: str, signal_id: str,
                    role: str = "Evidence", notes: str = "") -> None:
        if role not in ROLES:
            raise ValueError(f"Unknown role '{role}'. Valid roles: {', '.join(ROLES)}")
        if db.get_signal(signal_id) is None:
            raise ValueError(f"Signal not found: {signal_id}")
        db.map_signal_to_scenario(scenario_id, signal_id, role=role, notes=notes)

    def get_linked(self, db, scenario_id: str,
                   role: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = db.get_scenario_signals(scenario_id)
        if role is not None:
            rows = [r for r in rows if r["role"] == role]
        return rows
```

- [ ] **Step 4: Run tests → pass; full suite.**

- [ ] **Step 5: Commit.** `git commit -m "feat(scenario): role-based evidence linking"`

---

### Task 4: Shadow Risk Register (F4)

**Files:**
- Modify: `src/scenario.py`
- Test: `tests/test_scenario.py` (append)

**Interfaces:**
- Produces: `ScenarioEngine.shadow_risk_register(db, scenario_id) -> List[Dict]`. Includes every linked signal that is a Shadow **by polarity or by role**: `polarity == 'Shadow'` OR `role == 'Shadow-Risk'`. Sorted by `impact_score` descending. Each entry: `{"id", "title", "shadow_type", "impact_score", "uncertainty_score", "mitigation_notes", "role", "link_notes"}`.

- [ ] **Step 1: Write the failing test.** Append:

```python
class TestShadowRiskRegister(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.engine = ScenarioEngine()
        make_signal(self.db, "ax", "Axis X", impact=8, uncertainty=8)
        make_signal(self.db, "ay", "Axis Y", impact=8, uncertainty=8)
        result = self.engine.create_scenario_set(
            self.db, title="T", axis_x_signal_id="ax", axis_y_signal_id="ay",
            axis_x_low_label="lo", axis_x_high_label="hi",
            axis_y_low_label="lo2", axis_y_high_label="hi2")
        self.scenario_id = result["scenarios"][0]["id"]

    def tearDown(self):
        self.db.close()

    def test_register_orders_shadows_by_impact(self):
        make_signal(self.db, "s1", "Pension system erosion", impact=6, uncertainty=5,
                    polarity="Shadow", shadow_type="Declining-System",
                    mitigation_notes="reform funding")
        make_signal(self.db, "s2", "Grid collapse cascade", impact=9, uncertainty=7,
                    polarity="Shadow", shadow_type="Worst-Case-Future")
        make_signal(self.db, "em", "Emergent positive", impact=10, uncertainty=5)
        self.engine.link_signal(self.db, self.scenario_id, "s1", role="Shadow-Risk")
        self.engine.link_signal(self.db, self.scenario_id, "s2", role="Shadow-Risk")
        self.engine.link_signal(self.db, self.scenario_id, "em", role="Evidence")
        register = self.engine.shadow_risk_register(self.db, self.scenario_id)
        self.assertEqual([r["id"] for r in register], ["s2", "s1"])
        self.assertEqual(register[0]["shadow_type"], "Worst-Case-Future")
        self.assertEqual(register[1]["mitigation_notes"], "reform funding")

    def test_shadow_polarity_counts_even_with_evidence_role(self):
        make_signal(self.db, "s3", "Obsolete workflow persists", impact=4, uncertainty=4,
                    polarity="Shadow", shadow_type="Obsolete-Behavior")
        self.engine.link_signal(self.db, self.scenario_id, "s3", role="Evidence")
        register = self.engine.shadow_risk_register(self.db, self.scenario_id)
        self.assertEqual([r["id"] for r in register], ["s3"])
```

- [ ] **Step 2: Run to verify FAIL.**

- [ ] **Step 3: Implement.** Add to `ScenarioEngine`:

```python
    def shadow_risk_register(self, db, scenario_id: str) -> List[Dict[str, Any]]:
        """All Shadows touching a scenario, highest impact first.

        A signal belongs on the register if it is a Shadow by polarity
        (declining system, obsolete behavior, worst-case future, disruption)
        or was explicitly linked with the Shadow-Risk role.
        """
        register = []
        for row in db.get_scenario_signals(scenario_id):
            if row.get("polarity") == "Shadow" or row["role"] == "Shadow-Risk":
                register.append({
                    "id": row["id"],
                    "title": row["title"],
                    "shadow_type": row.get("shadow_type"),
                    "impact_score": row.get("impact_score") or 0,
                    "uncertainty_score": row.get("uncertainty_score"),
                    "mitigation_notes": row.get("mitigation_notes"),
                    "role": row["role"],
                    "link_notes": row.get("link_notes"),
                })
        register.sort(key=lambda r: r["impact_score"], reverse=True)
        return register
```

- [ ] **Step 4: Run tests → pass; full suite.**

- [ ] **Step 5: Commit.** `git commit -m "feat(scenario): shadow risk register per scenario"`

---

### Task 5: Wind-Tunneling (F5)

**Files:**
- Modify: `src/scenario.py`
- Test: `tests/test_scenario.py` (append)

**Interfaces:**
- Consumes: `signal_trend_map` contradiction rows via a read-only query (the SQLite graph stores signal↔trend relations; `relationship_type='Contradiction'`), plus `get_scenario_signals`.
- Produces: `ScenarioEngine.wind_tunnel(db, scenario_id) -> Dict[str, Any]`: `{"stressors": [{"scenario_signal_id", "scenario_signal_title", "contradicting_trend_id", "contradicting_trend_name", "strength_score"}], "shadow_pressure": int, "robustness": str}` where `shadow_pressure` is the count of register entries with impact ≥ 7 and `robustness` is `"Fragile"` if there are any stressors with strength ≥ 7 or shadow_pressure ≥ 2, `"Contested"` if any stressors at all, else `"Unchallenged"`.

- [ ] **Step 1: Write the failing test.** Append:

```python
class TestWindTunnel(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.engine = ScenarioEngine()
        make_signal(self.db, "ax", "Axis X", impact=8, uncertainty=8)
        make_signal(self.db, "ay", "Axis Y", impact=8, uncertainty=8)
        result = self.engine.create_scenario_set(
            self.db, title="T", axis_x_signal_id="ax", axis_y_signal_id="ay",
            axis_x_low_label="lo", axis_x_high_label="hi",
            axis_y_low_label="lo2", axis_y_high_label="hi2")
        self.scenario_id = result["scenarios"][0]["id"]

    def tearDown(self):
        self.db.close()

    def test_contradicting_trend_becomes_stressor(self):
        make_signal(self.db, "ev", "Remote work grows", impact=7, uncertainty=5)
        self.engine.link_signal(self.db, self.scenario_id, "ev", role="Driver")
        self.db.add_trend({"id": "tr1", "name": "Office mandates return",
                           "summary": "s", "category": "Economic",
                           "time_horizon": "Near-term", "impact_level": "High",
                           "uncertainty_level": "Medium"})
        self.db.map_signal_to_trend("ev", "tr1", relationship_type="Contradiction",
                                    strength_score=8)
        result = self.engine.wind_tunnel(self.db, self.scenario_id)
        self.assertEqual(len(result["stressors"]), 1)
        self.assertEqual(result["stressors"][0]["contradicting_trend_id"], "tr1")
        self.assertEqual(result["robustness"], "Fragile")

    def test_unchallenged_when_no_contradictions(self):
        make_signal(self.db, "ev", "Quiet signal", impact=3, uncertainty=3)
        self.engine.link_signal(self.db, self.scenario_id, "ev")
        result = self.engine.wind_tunnel(self.db, self.scenario_id)
        self.assertEqual(result["stressors"], [])
        self.assertEqual(result["robustness"], "Unchallenged")

    def test_heavy_shadow_pressure_is_fragile(self):
        make_signal(self.db, "s1", "Collapse risk one", impact=8, uncertainty=6,
                    polarity="Shadow", shadow_type="Worst-Case-Future")
        make_signal(self.db, "s2", "Collapse risk two", impact=9, uncertainty=6,
                    polarity="Shadow", shadow_type="Disruption")
        self.engine.link_signal(self.db, self.scenario_id, "s1", role="Shadow-Risk")
        self.engine.link_signal(self.db, self.scenario_id, "s2", role="Shadow-Risk")
        result = self.engine.wind_tunnel(self.db, self.scenario_id)
        self.assertEqual(result["shadow_pressure"], 2)
        self.assertEqual(result["robustness"], "Fragile")
```

- [ ] **Step 2: Run to verify FAIL.**

- [ ] **Step 3: Implement.** Add to `ScenarioEngine`:

```python
    def wind_tunnel(self, db, scenario_id: str) -> Dict[str, Any]:
        """Stress-test a scenario against contradicting trends and Shadow load."""
        linked = db.get_scenario_signals(scenario_id)
        stressors = []
        cursor = db.conn.cursor()
        for sig in linked:
            cursor.execute("""
            SELECT t.id, t.name, m.strength_score
            FROM trends t
            JOIN signal_trend_map m ON t.id = m.trend_id
            WHERE m.signal_id = ? AND m.relationship_type = 'Contradiction'
            """, (sig["id"],))
            for trend_id, trend_name, strength in cursor.fetchall():
                stressors.append({
                    "scenario_signal_id": sig["id"],
                    "scenario_signal_title": sig["title"],
                    "contradicting_trend_id": trend_id,
                    "contradicting_trend_name": trend_name,
                    "strength_score": strength,
                })

        shadow_pressure = sum(
            1 for r in self.shadow_risk_register(db, scenario_id)
            if r["impact_score"] >= 7
        )

        if any((s["strength_score"] or 0) >= 7 for s in stressors) or shadow_pressure >= 2:
            robustness = "Fragile"
        elif stressors:
            robustness = "Contested"
        else:
            robustness = "Unchallenged"

        return {"stressors": stressors, "shadow_pressure": shadow_pressure,
                "robustness": robustness}
```

- [ ] **Step 4: Run tests → pass; full suite.**

- [ ] **Step 5: Commit.** `git commit -m "feat(scenario): wind-tunneling with contradiction stressors and shadow pressure"`

---

### Task 6: Scenario Report (F6)

**Files:**
- Modify: `src/scenario.py`
- Test: `tests/test_scenario.py` (append)

**Interfaces:**
- Produces: `ScenarioEngine.compile_scenario_report(db, scenario_set_id) -> str` (Markdown). Template path is deterministic; if `self.use_gemini`, the template output is sent to Gemini for narrative polish with template fallback on any exception (mirrors `SynthesisEngine.compile_markdown_report`). Raises `ValueError` for an unknown set id.

- [ ] **Step 1: Write the failing test.** Append:

```python
class TestScenarioReport(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.engine = ScenarioEngine(api_key=None)  # deterministic template path
        make_signal(self.db, "ax", "Decentralization", impact=8, uncertainty=8)
        make_signal(self.db, "ay", "Energy cost", impact=9, uncertainty=7)
        result = self.engine.create_scenario_set(
            self.db, title="Energy 2040",
            axis_x_signal_id="ax", axis_y_signal_id="ay",
            axis_x_low_label="Centralized", axis_x_high_label="Distributed",
            axis_y_low_label="Cheap", axis_y_high_label="Expensive",
            horizon_year=2040)
        self.set_id = result["scenario_set_id"]
        self.hh = result["scenarios"][0]["id"]
        make_signal(self.db, "risk", "Transmission grid decay", impact=8, uncertainty=6,
                    polarity="Shadow", shadow_type="Declining-System",
                    mitigation_notes="invest in maintenance")
        self.engine.link_signal(self.db, self.hh, "risk", role="Shadow-Risk")

    def tearDown(self):
        self.db.close()

    def test_report_contains_axes_quadrants_and_risk_register(self):
        report = self.engine.compile_scenario_report(self.db, self.set_id)
        self.assertIn("# Scenario Set: Energy 2040", report)
        self.assertIn("Centralized", report)
        self.assertIn("Distributed / Expensive", report)
        self.assertIn("Shadow Risk Register", report)
        self.assertIn("Transmission grid decay", report)
        self.assertIn("invest in maintenance", report)

    def test_unknown_set_raises(self):
        with self.assertRaises(ValueError):
            self.engine.compile_scenario_report(self.db, "nope")
```

- [ ] **Step 2: Run to verify FAIL.**

- [ ] **Step 3: Implement.** Add to `ScenarioEngine`:

```python
    def compile_scenario_report(self, db, scenario_set_id: str) -> str:
        scenario_set = db.get_scenario_set(scenario_set_id)
        if scenario_set is None:
            raise ValueError(f"Scenario set not found: {scenario_set_id}")
        scenarios = db.get_scenarios_for_set(scenario_set_id)

        template = self._report_template(db, scenario_set, scenarios)
        if self.use_gemini:
            try:
                return self._polish_with_gemini(template)
            except Exception as e:
                print(f"Gemini report polish failed: {e}. Returning template report.")
        return template

    def _report_template(self, db, scenario_set: Dict[str, Any],
                         scenarios: List[Dict[str, Any]]) -> str:
        md = [f"# Scenario Set: {scenario_set['title']}"]
        if scenario_set.get("horizon_year"):
            md.append(f"\n**Horizon:** {scenario_set['horizon_year']}")

        axis_x = db.get_signal(scenario_set["axis_x_signal_id"]) if scenario_set.get("axis_x_signal_id") else None
        axis_y = db.get_signal(scenario_set["axis_y_signal_id"]) if scenario_set.get("axis_y_signal_id") else None
        md.append("\n## Critical Uncertainty Axes")
        if axis_x:
            md.append(f"- **Axis X — {axis_x['title']}:** "
                      f"{scenario_set.get('axis_x_low_label')} ↔ {scenario_set.get('axis_x_high_label')} "
                      f"(impact {axis_x.get('impact_score')}, uncertainty {axis_x.get('uncertainty_score')})")
        if axis_y:
            md.append(f"- **Axis Y — {axis_y['title']}:** "
                      f"{scenario_set.get('axis_y_low_label')} ↔ {scenario_set.get('axis_y_high_label')} "
                      f"(impact {axis_y.get('impact_score')}, uncertainty {axis_y.get('uncertainty_score')})")

        for scn in scenarios:
            md.append(f"\n## Quadrant {scn['quadrant']}: {scn['title']}")
            md.append(scn.get("narrative") or "*Narrative not yet written.*")
            if scn.get("early_warning_indicators"):
                md.append(f"\n**Early-warning indicators:** {scn['early_warning_indicators']}")

            linked = self.get_linked(db, scn["id"])
            evidence = [r for r in linked if r["role"] in ("Driver", "Evidence", "Wildcard", "Implication")]
            if evidence:
                md.append("\n**Evidence base:**")
                for r in evidence:
                    md.append(f"- [{r['role']}] {r['title']} "
                              f"(impact {r.get('impact_score')}, {r.get('category')})")

            register = self.shadow_risk_register(db, scn["id"])
            md.append("\n### Shadow Risk Register")
            if not register:
                md.append("*No shadow risks linked — verify this is not a blind spot.*")
            for r in register:
                md.append(f"- **{r['title']}** ({r.get('shadow_type') or 'Unclassified'}, "
                          f"impact {r['impact_score']})")
                if r.get("mitigation_notes"):
                    md.append(f"  - Mitigation: {r['mitigation_notes']}")

            tunnel = self.wind_tunnel(db, scn["id"])
            md.append(f"\n**Wind-tunnel robustness:** {tunnel['robustness']} "
                      f"({len(tunnel['stressors'])} contradiction stressor(s), "
                      f"shadow pressure {tunnel['shadow_pressure']})")

        return "\n".join(md)

    def _polish_with_gemini(self, template: str) -> str:
        prompt = (
            "You are a principal strategic foresight director. Rewrite the following "
            "2x2 scenario report into polished executive prose. Preserve every heading, "
            "every signal title, all scores, the Shadow Risk Register entries, and the "
            "wind-tunnel verdicts exactly — enrich only the narrative text.\n\n" + template
        )
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
```

- [ ] **Step 4: Run tests → pass; full suite.**

- [ ] **Step 5: Commit.** `git commit -m "feat(scenario): scenario set markdown report with risk register and wind-tunnel verdicts"`

---

### Task 7: CLI `scenario` command group (F7)

**Files:**
- Modify: `src/cli.py`
- Test: `tests/test_cli.py` (append)

**Interfaces:**
- Consumes: every `ScenarioEngine` method above.
- Produces click commands (all take `--db-path` defaulting to `DEFAULT_DB_PATH`):
  - `scenario axes [--limit 10]` — table of ranked critical uncertainties with a `*` marker on axis candidates.
  - `scenario create-set TITLE --axis-x ID --axis-y ID --x-low L --x-high L --y-low L --y-high L [--horizon-year N]` — prints the set id and 4 scenario ids.
  - `scenario link SCENARIO_ID SIGNAL_ID [--role Evidence] [--notes ""]`
  - `scenario risks SCENARIO_ID` — prints the shadow risk register.
  - `scenario windtunnel SCENARIO_ID` — prints robustness verdict and stressors.
  - `scenario report SET_ID [--output scenario_report.md]` — writes the Markdown report.

- [ ] **Step 1: Write the failing test.** Append to `tests/test_cli.py` (follow the file's existing `CliRunner` pattern; use a temp db path fixture consistent with existing tests):

```python
class TestScenarioCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "scenario_cli.db")
        db = Database(self.db_path)
        for sig_id, title in (("ax", "Decentralization"), ("ay", "Energy cost")):
            db.add_signal({"id": sig_id, "title": title, "description": "d",
                           "category": "Technological", "time_horizon": "Mid-term",
                           "impact_score": 8, "uncertainty_score": 8, "is_keeper": 1})
        db.close()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_axes_lists_candidates(self):
        result = self.runner.invoke(cli, ["scenario", "axes", "--db-path", self.db_path])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Decentralization", result.output)
        self.assertIn("*", result.output)

    def test_create_set_link_and_report_roundtrip(self):
        created = self.runner.invoke(cli, [
            "scenario", "create-set", "Energy 2040",
            "--axis-x", "ax", "--axis-y", "ay",
            "--x-low", "Centralized", "--x-high", "Distributed",
            "--y-low", "Cheap", "--y-high", "Expensive",
            "--db-path", self.db_path])
        self.assertEqual(created.exit_code, 0)
        set_id = re.search(r"Set ID: (\S+)", created.output).group(1)
        scn_id = re.search(r"High-High.*?ID: (\S+)", created.output).group(1)

        report_path = os.path.join(self.tmpdir, "out.md")
        report = self.runner.invoke(cli, [
            "scenario", "report", set_id, "--output", report_path,
            "--db-path", self.db_path])
        self.assertEqual(report.exit_code, 0)
        with open(report_path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("Scenario Set: Energy 2040", content)
        self.assertIsNotNone(scn_id)
```

(Ensure `tests/test_cli.py` imports `re`, `tempfile`, `shutil`, `Database` — add any missing imports at the top, matching existing style.)

- [ ] **Step 2: Run to verify FAIL.**

- [ ] **Step 3: Implement.** In `src/cli.py`, import the engine (`from src.scenario import ScenarioEngine`) and add:

```python
@cli.group()
def scenario():
    """Scenario Builder: 2x2 sets, evidence linking, risk registers, reports."""
    pass

@scenario.command()
@click.option('--limit', default=10, help='Max ranked uncertainties to show.')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def axes(limit, db_path):
    """Rank critical uncertainties (impact x uncertainty) for axis selection."""
    db = get_db(db_path)
    try:
        ranked = ScenarioEngine().rank_critical_uncertainties(db, limit=limit)
    finally:
        db.close()
    if not ranked:
        click.echo("No assessed keeper signals found. Run ingest + deduplicate first.")
        return
    click.echo(f"{'':<2}{'ID':<14} | {'Impact':<6} | {'Uncert':<6} | {'Crit':<5} | Title")
    click.echo("-" * 70)
    for r in ranked:
        marker = "*" if r["axis_candidate"] else " "
        click.echo(f"{marker:<2}{r['id']:<14} | {r['impact_score']:<6} | "
                   f"{r['uncertainty_score']:<6} | {r['criticality']:<5} | {r['title']}")
    click.echo("\n* = axis candidate (impact >= 7 and uncertainty >= 7)")

@scenario.command('create-set')
@click.argument('title')
@click.option('--axis-x', required=True, help='Signal ID for the X axis.')
@click.option('--axis-y', required=True, help='Signal ID for the Y axis.')
@click.option('--x-low', required=True, help='Label for the X-axis low pole.')
@click.option('--x-high', required=True, help='Label for the X-axis high pole.')
@click.option('--y-low', required=True, help='Label for the Y-axis low pole.')
@click.option('--y-high', required=True, help='Label for the Y-axis high pole.')
@click.option('--horizon-year', default=None, type=int, help='Scenario horizon year.')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def create_set(title, axis_x, axis_y, x_low, x_high, y_low, y_high, horizon_year, db_path):
    """Create a 2x2 scenario set and scaffold its four quadrant scenarios."""
    db = get_db(db_path)
    try:
        result = ScenarioEngine().create_scenario_set(
            db, title=title, axis_x_signal_id=axis_x, axis_y_signal_id=axis_y,
            axis_x_low_label=x_low, axis_x_high_label=x_high,
            axis_y_low_label=y_low, axis_y_high_label=y_high,
            horizon_year=horizon_year)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        db.close()
        sys.exit(1)
    db.close()
    click.echo(f"Set ID: {result['scenario_set_id']}")
    for scn in result["scenarios"]:
        click.echo(f"  {scn['quadrant']}: \"{scn['title']}\" ID: {scn['id']}")

@scenario.command()
@click.argument('scenario_id')
@click.argument('signal_id')
@click.option('--role', default='Evidence', help='Driver|Evidence|Wildcard|Shadow-Risk|Implication')
@click.option('--notes', default='', help='Why this signal belongs in the scenario.')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def link(scenario_id, signal_id, role, notes, db_path):
    """Link a signal/shadow into a scenario with a role."""
    db = get_db(db_path)
    try:
        ScenarioEngine().link_signal(db, scenario_id, signal_id, role=role, notes=notes)
        click.echo(f"Linked {signal_id} -> {scenario_id} as {role}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()

@scenario.command()
@click.argument('scenario_id')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def risks(scenario_id, db_path):
    """Print the Shadow Risk Register for a scenario."""
    db = get_db(db_path)
    try:
        register = ScenarioEngine().shadow_risk_register(db, scenario_id)
    finally:
        db.close()
    if not register:
        click.echo("No shadow risks linked. Verify this is not a blind spot.")
        return
    for r in register:
        click.echo(f"[impact {r['impact_score']}] {r['title']} "
                   f"({r.get('shadow_type') or 'Unclassified'})")
        if r.get("mitigation_notes"):
            click.echo(f"    Mitigation: {r['mitigation_notes']}")

@scenario.command()
@click.argument('scenario_id')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def windtunnel(scenario_id, db_path):
    """Stress-test a scenario against contradicting trends and shadow load."""
    db = get_db(db_path)
    try:
        result = ScenarioEngine().wind_tunnel(db, scenario_id)
    finally:
        db.close()
    click.echo(f"Robustness: {result['robustness']} "
               f"(shadow pressure: {result['shadow_pressure']})")
    for s in result["stressors"]:
        click.echo(f"  \"{s['scenario_signal_title']}\" contradicted by "
                   f"\"{s['contradicting_trend_name']}\" (strength {s['strength_score']})")

@scenario.command()
@click.argument('set_id')
@click.option('--output', default='scenario_report.md', help='Output filepath.')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def report(set_id, output, db_path):
    """Compile the scenario set Markdown report."""
    db = get_db(db_path)
    try:
        report_md = ScenarioEngine().compile_scenario_report(db, set_id)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        db.close()
        sys.exit(1)
    db.close()
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True) if os.path.dirname(output) else None
    with open(output, 'w', encoding='utf-8') as f:
        f.write(report_md)
    click.echo(f"Scenario report written to: {output}")
```

Note: the top-level `report` command already exists; the new one lives under the `scenario` group (`scenario report`), so there is no name collision in click.

- [ ] **Step 4: Run tests → pass; full suite.**

- [ ] **Step 5: Commit.** `git commit -m "feat(cli): scenario command group (axes, create-set, link, risks, windtunnel, report)"`

---

## Deferred (explicitly out of scope — YAGNI for v1)

- Radar overlay of scenario membership (extend `SynthesisEngine.generate_radar_json` with a `scenario_id` filter) — add once the web radar canvas (KANBAN M3.3) exists to consume it.
- Supabase-side ScenarioEngine (the SQL scaffolding + RLS ships in the DB plan; a SaaS API layer should reuse this engine against Postgres when the web gateway lands).
- Gemini-drafted quadrant narratives (auto-writing `scenarios.narrative` from linked evidence) — the report polish hook in Task 6 is the extension point.

## Self-Review Checklist

1. Feature coverage: F1→T1, F2→T2, F3→T3, F4→T4, F5→T5, F6→T6, F7→T7. ✓
2. No placeholders: every step carries runnable code. ✓
3. Type consistency: `ScenarioEngine` method names/signatures match between tasks and the CLI (T7 consumes exactly `rank_critical_uncertainties`, `create_scenario_set`, `link_signal`, `shadow_risk_register`, `wind_tunnel`, `compile_scenario_report`); role/quadrant string spellings match the DB plan's enums including `'Shadow-Risk'` and `'High-High'`. ✓
4. Dependency declared: DB plan Tasks 8–9 gate this plan. ✓
