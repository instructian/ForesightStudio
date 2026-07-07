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

if __name__ == '__main__':
    unittest.main()
