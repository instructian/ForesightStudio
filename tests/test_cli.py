import unittest
import os
import tempfile
import json
from click.testing import CliRunner
from src.cli import cli

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        # Create a temporary directory for safe database and JSON setups
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_cli.db")
        self.json_path = os.path.join(self.temp_dir.name, "signals.json")

        # Set up a mock signals JSON file for ingestion
        self.mock_signals = [
            {
                "title": "Geriatric helper drones Hayward",
                "description": "Prototype drones assisting elders in California with hydration.",
                "category": "Technological",
                "source_url": "https://example.com/drones1",
                "source_type": "Observation",
                "date_observed": "2026-07-06"
            },
            {
                "title": "Geriatric helper drones Hayward",
                "description": "Prototype drones assisting elders in California with hydration and water services.",
                "category": "Technological",
                "source_url": "https://example.com/drones2",
                "source_type": "Observation",
                "date_observed": "2026-07-06"
            }
        ]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.mock_signals, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_e2e_cli_flow(self):
        # 1. Test init-db
        result = self.runner.invoke(cli, ["init-db", "--db-path", self.db_path])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Database successfully initialized", result.output)
        self.assertTrue(os.path.exists(self.db_path))

        # 2. Test ingest
        result = self.runner.invoke(cli, ["ingest", self.json_path, "--db-path", self.db_path])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Ingestion complete", result.output)
        self.assertIn("Successfully processed and saved 2 signals", result.output)

        # 3. Test deduplicate
        result = self.runner.invoke(cli, ["deduplicate", "--threshold", "0.45", "--db-path", self.db_path])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Deduplication finished", result.output)
        # 2 overlapping signals should cluster into 1 keeper and 1 duplicate
        self.assertIn("Active Keepers isolated (verified Signals): 1", result.output)
        self.assertIn("Redundant duplicates nested (Shadow research): 1", result.output)

        # 4. Test radar export
        radar_path = os.path.join(self.temp_dir.name, "radar.json")
        result = self.runner.invoke(cli, ["radar", "--format", "json", "--output", radar_path, "--db-path", self.db_path])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Successfully exported polar radar data", result.output)
        self.assertTrue(os.path.exists(radar_path))
        
        # Verify JSON content
        with open(radar_path, "r") as f:
            nodes = json.load(f)
            self.assertEqual(len(nodes), 1) # Only 1 keeper
            self.assertEqual(nodes[0]["theta_degrees"], 90.0) # Technological -> 90 degrees
            self.assertEqual(nodes[0]["radius"], 1.0) # Heuristics fallback Near-term -> r=1.0

        # 5. Test report compilation
        report_path = os.path.join(self.temp_dir.name, "report.md")
        result = self.runner.invoke(cli, ["report", "--output", report_path, "--db-path", self.db_path])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Strategic report successfully written", result.output)
        self.assertTrue(os.path.exists(report_path))

        with open(report_path, "r") as f:
            report_content = f.read()
            self.assertIn("# Foresight Studio: Strategic Synthesis Report", report_content)
            self.assertIn("Geriatric helper drones Hayward", report_content)

if __name__ == '__main__':
    unittest.main()
