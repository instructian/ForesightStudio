import unittest
import os
import tempfile
from src.database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary file-based database for tests
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)

    def tearDown(self):
        self.db.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_add_and_get_signal(self):
        signal_data = {
            "title": "Autonomous geriatric helper drones in CSU East Bay",
            "description": "Drones equipped with hydration and companion interfaces were observed assisting elders.",
            "category": "Technological",
            "time_horizon": "Near-term",
            "source_url": "https://example.com/drones",
            "source_type": "Observation",
            "impact_score": 8,
            "status": "Shadow"
        }
        sig_id = self.db.add_signal(signal_data)
        self.assertTrue(sig_id.startswith("sig_") or len(sig_id) > 0)

        stored = self.db.get_signal(sig_id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored["title"], signal_data["title"])
        self.assertEqual(stored["category"], "Technological")
        self.assertEqual(stored["time_horizon"], "Near-term")
        self.assertEqual(stored["impact_score"], 8)
        self.assertEqual(stored["status"], "Shadow")
        self.assertEqual(stored["is_keeper"], 1)

    def test_update_signal_deduplication(self):
        signal_data = {
            "title": "Autonomous geriatric helper drones",
            "description": "Drones helping elderly with tasks.",
            "category": "Technological",
            "time_horizon": "Near-term"
        }
        sig_id = self.db.add_signal(signal_data)

        # Update deduplication status (marking it as duplicate of itself as mock)
        meta = [{"author": "Ian Pollock", "source_url": "https://example.com"}]
        self.db.update_signal_deduplication_status(sig_id, is_keeper=False, keeper_id=None, convergence_score=1.5, status="Signal", source_metadata=meta)

        updated = self.db.get_signal(sig_id)
        self.assertEqual(updated["is_keeper"], 0)
        self.assertEqual(updated["convergence_score"], 1.5)
        self.assertEqual(updated["status"], "Signal")
        self.assertEqual(updated["source_metadata"], meta)

    def test_add_and_get_trend_and_map(self):
        trend_data = {
            "name": "Eldercare Automation",
            "summary": "The rapid growth of robotic support systems for senior demographics.",
            "category": "Technological",
            "time_horizon": "Mid-term",
            "impact_level": "High",
            "uncertainty_level": "Medium"
        }
        trend_id = self.db.add_trend(trend_data)

        stored_trend = self.db.get_trend(trend_id)
        self.assertIsNotNone(stored_trend)
        self.assertEqual(stored_trend["name"], trend_data["name"])

        signal_data = {
            "title": "Eldercare Robot Assist",
            "description": " Geriatric robot assisting with movement.",
            "category": "Technological",
            "time_horizon": "Near-term"
        }
        sig_id = self.db.add_signal(signal_data)

        self.db.map_signal_to_trend(sig_id, trend_id, relationship_type="Evidence", strength_score=9, notes="Strong correlation")

        mapped_signals = self.db.get_trend_signals(trend_id)
        self.assertEqual(len(mapped_signals), 1)
        self.assertEqual(mapped_signals[0]["id"], sig_id)
        self.assertEqual(mapped_signals[0]["relationship_type"], "Evidence")
        self.assertEqual(mapped_signals[0]["strength_score"], 9)

class TestScenarioTables(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def _signal(self, title="Solar microgrids", polarity="Emergent", **kw):
        base = {
            "title": title,
            "description": "desc",
            "category": "Technological",
            "time_horizon": "Mid-term",
            "polarity": polarity,
        }
        base.update(kw)
        return self.db.add_signal(base)

    def test_signal_shadow_fields_roundtrip(self):
        sig_id = self._signal(
            title="Mall retail collapse",
            polarity="Shadow",
            shadow_type="Declining-System",
            mitigation_notes="Diversify anchor tenants",
            uncertainty_score=8,
            horizon_year=2032,
        )
        sig = self.db.get_signal(sig_id)
        self.assertEqual(sig["polarity"], "Shadow")
        self.assertEqual(sig["shadow_type"], "Declining-System")
        self.assertEqual(sig["uncertainty_score"], 8)
        self.assertEqual(sig["horizon_year"], 2032)

    def test_scenario_set_roundtrip(self):
        x = self._signal("Axis X")
        y = self._signal("Axis Y")
        set_id = self.db.add_scenario_set({
            "title": "Energy 2040",
            "axis_x_signal_id": x,
            "axis_y_signal_id": y,
            "axis_x_low_label": "Centralized",
            "axis_x_high_label": "Distributed",
            "axis_y_low_label": "Cheap",
            "axis_y_high_label": "Expensive",
            "horizon_year": 2040,
        })
        stored = self.db.get_scenario_set(set_id)
        self.assertEqual(stored["title"], "Energy 2040")
        self.assertEqual(stored["axis_x_signal_id"], x)

    def test_scenarios_unique_quadrant_per_set(self):
        set_id = self.db.add_scenario_set({"title": "S"})
        self.db.add_scenario({"scenario_set_id": set_id, "quadrant": "High-High", "title": "A"})
        with self.assertRaises(Exception):
            self.db.add_scenario({"scenario_set_id": set_id, "quadrant": "High-High", "title": "B"})

    def test_scenario_signal_mapping(self):
        set_id = self.db.add_scenario_set({"title": "S"})
        scn_id = self.db.add_scenario({"scenario_set_id": set_id, "quadrant": "Low-Low", "title": "Collapse"})
        sig_id = self._signal("Grid failures", polarity="Shadow", shadow_type="Worst-Case-Future")
        self.db.map_signal_to_scenario(scn_id, sig_id, role="Shadow-Risk", notes="stress case")
        rows = self.db.get_scenario_signals(scn_id)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["role"], "Shadow-Risk")
        self.assertEqual(rows[0]["title"], "Grid failures")

if __name__ == '__main__':
    unittest.main()
