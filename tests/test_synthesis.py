import unittest
from unittest.mock import MagicMock
from src.synthesis import SynthesisEngine

class TestSynthesis(unittest.TestCase):
    def setUp(self):
        self.engine = SynthesisEngine(api_key=None)

    def test_polar_coordinates_mapping(self):
        # Social Near-term
        theta, r = self.engine.calculate_polar_coordinates("Social", "Near-term")
        self.assertEqual(theta, 30.0)
        self.assertEqual(r, 1.0)

        # Technological Long-term
        theta, r = self.engine.calculate_polar_coordinates("Technological", "Long-term")
        self.assertEqual(theta, 90.0)
        self.assertEqual(r, 3.0)

        # Legal Mid-term
        theta, r = self.engine.calculate_polar_coordinates("Legal", "Mid-term")
        self.assertEqual(theta, 330.0)
        self.assertEqual(r, 2.0)

    def test_visual_parameters(self):
        # Impact 5, Convergence 1.0 (standalone)
        size, glow = self.engine.calculate_visual_parameters(5, 1.0)
        self.assertEqual(size, 18.0) # 8.0 + 2.0 * 5 = 18.0
        self.assertAlmostEqual(glow, 0.693, places=3) # ln(1 + 1) = ln(2) = 0.6931...

        # Impact 9, Convergence 3.0 (high cluster density)
        size, glow = self.engine.calculate_visual_parameters(9, 3.0)
        self.assertEqual(size, 26.0) # 8.0 + 2.0 * 9 = 26.0
        self.assertAlmostEqual(glow, 1.386, places=3) # ln(1 + 3) = ln(4) = 1.3862...

    def test_generate_radar_json(self):
        mock_db = MagicMock()
        keepers = [
            {
                "id": "s1", "title": "Elderly Drones", "category": "Technological", "time_horizon": "Near-term",
                "impact_score": 7, "convergence_score": 1.5, "status": "Signal", "source_metadata": [{"id": "s2"}]
            }
        ]
        mock_db.get_all_signals.return_value = keepers

        nodes = self.engine.generate_radar_json(mock_db)
        self.assertEqual(len(nodes), 1)
        node = nodes[0]
        self.assertEqual(node["id"], "s1")
        self.assertEqual(node["theta_degrees"], 90.0)
        self.assertEqual(node["radius"], 1.0)
        self.assertEqual(node["visual_size"], 22.0) # 8.0 + 2*7
        self.assertEqual(node["duplicates_count"], 1)

    def test_compile_markdown_report_template(self):
        mock_db = MagicMock()
        keepers = [
            {
                "id": "s1", "title": "Geriatric companion drones", "category": "Technological", "time_horizon": "Near-term",
                "description": "Drones assisting elderly Hayward residents with hydration.",
                "impact_score": 8, "convergence_score": 1.5, "status": "Signal",
                "source_metadata": [{"title": "Drones in Hayward", "source_url": "https://hayward.org"}]
            }
        ]
        mock_db.get_all_signals.return_value = keepers

        # Force template compile by forcing use_gemini to False
        self.engine.use_gemini = False
        report = self.engine.compile_markdown_report(mock_db)

        self.assertIn("# Foresight Studio: Strategic Synthesis Report", report)
        self.assertIn("Geriatric companion drones", report)
        self.assertIn("Hayward residents", report)
        self.assertIn("Drones in Hayward", report)
        self.assertIn("https://hayward.org", report)

if __name__ == '__main__':
    unittest.main()
