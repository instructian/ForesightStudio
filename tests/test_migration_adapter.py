import os
import tempfile
import unittest

from src.database import Database
from src.migration_adapter import MigrationAdapter


class MockInsert:
    def __init__(self):
        self.payloads = []

    def insert(self, payload):
        self.payloads.append(payload)
        return self

    def execute(self):
        return {"data": self.payloads[-1]}


class MockSupabase:
    def __init__(self):
        self.tables = {}

    def table(self, name):
        self.tables.setdefault(name, MockInsert())
        return self.tables[name]


class TestMigrationAdapter(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)
        self.db.add_signal({
            "id": "sig_keeper",
            "title": "Autonomous geriatric helper drones",
            "description": "Drones equipped with hydration and companion interfaces assist elders.",
            "category": "Technological",
            "source_url": "https://example.com/drones",
            "source_type": "Observation",
            "date_observed": "2026-07-06",
            "geography": "Hayward, CA",
            "sector": "Healthcare",
            "tags": ["eldercare", "drones", "assistive tech"],
            "confidence_score": 8,
            "novelty_score": 7,
            "impact_score": 9,
            "strategic_relevance": "Aging population support",
            "time_horizon": "Near-term",
            "actionability": "Pilot campus eldercare services",
            "status": "Signal",
            "convergence_score": 1.5,
            "is_keeper": 1,
            "source_metadata": [{"source": "field notes", "observer": "researcher"}],
        })
        self.db.add_signal({
            "id": "sig_shadow",
            "title": "Shadow geriatric drone report",
            "description": "A duplicate observation of eldercare drones.",
            "category": "Technological",
            "time_horizon": "Near-term",
            "status": "Signal",
            "is_keeper": 0,
            "keeper_id": "sig_keeper",
        })
        self.db.close()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_read_signal_rows_returns_sqlite_schema_columns(self):
        adapter = MigrationAdapter(self.db_path, supabase_client=MockSupabase())

        rows = adapter.read_signal_rows()

        self.assertEqual(len(rows), 2)
        self.assertIn("source_metadata", rows[0])
        self.assertIn("convergence_score", rows[0])
        self.assertIn("keeper_id", rows[0])

    def test_generate_embedding_is_deterministic_384_length(self):
        adapter = MigrationAdapter(self.db_path, supabase_client=MockSupabase())

        first = adapter.generate_embedding("Autonomous helper drones for elders")
        second = adapter.generate_embedding("Autonomous helper drones for elders")

        self.assertEqual(len(first), 384)
        self.assertEqual(first, second)
        self.assertTrue(all(isinstance(value, float) for value in first))

    def test_build_node_payload_maps_signal_fields_and_metadata_field(self):
        adapter = MigrationAdapter(
            self.db_path,
            supabase_client=MockSupabase(),
            node_metadata_field="source_metadata",
        )
        row = adapter.read_signal_rows()[0]

        payload = adapter.build_node_payload(row)

        self.assertEqual(payload["title"], "Autonomous geriatric helper drones")
        self.assertEqual(payload["tags"], ["eldercare", "drones", "assistive tech"])
        self.assertEqual(payload["node_type"], "Signal")
        self.assertIs(payload["is_keeper"], True)
        self.assertEqual(len(payload["embedding"]), 384)
        self.assertEqual(payload["source_metadata"]["source_signal_id"], "sig_keeper")
        self.assertEqual(payload["source_metadata"]["provenance"], [{"source": "field notes", "observer": "researcher"}])

    def test_source_metadata_written_by_default(self):
        adapter = MigrationAdapter(self.db_path, supabase_client=MockSupabase())
        row = adapter.read_signal_rows()[0]

        payload = adapter.build_node_payload(row)

        self.assertIn("source_metadata", payload)
        self.assertEqual(payload["source_metadata"]["source_signal_id"], "sig_keeper")
        self.assertEqual(
            payload["source_metadata"]["provenance"],
            [{"source": "field notes", "observer": "researcher"}],
        )

    def test_shadow_mapping_prefers_is_keeper_over_status(self):
        adapter = MigrationAdapter(self.db_path, supabase_client=MockSupabase())
        row = adapter.read_signal_rows()[1]

        payload = adapter.build_node_payload(row)

        self.assertEqual(payload["node_type"], "Shadow")
        self.assertIs(payload["is_keeper"], False)

    def test_migrate_signals_uses_injected_supabase_client(self):
        supabase = MockSupabase()
        adapter = MigrationAdapter(self.db_path, supabase_client=supabase)

        migrated = adapter.migrate_signals()

        self.assertEqual(migrated, 2)
        self.assertEqual(len(supabase.tables["nodes"].payloads), 2)
        self.assertEqual(supabase.tables["nodes"].payloads[0]["node_type"], "Signal")
        self.assertEqual(supabase.tables["nodes"].payloads[1]["node_type"], "Shadow")


class TestShadowAndUncertaintyMapping(unittest.TestCase):
    def setUp(self):
        self.adapter = MigrationAdapter(sqlite_path=":memory:", supabase_client=object())

    def test_payload_includes_new_dimensions(self):
        row = {
            "id": "sig_1", "title": "Mall decline", "description": "d",
            "category": "Economic", "time_horizon": "Mid-term",
            "is_keeper": 1, "status": "Signal",
            "uncertainty_score": 7, "horizon_year": 2033,
            "polarity": "Shadow", "shadow_type": "Declining-System",
            "mitigation_notes": "hedge",
        }
        payload = self.adapter.build_node_payload(row)
        self.assertEqual(payload["uncertainty_score"], 7)
        self.assertEqual(payload["horizon_year"], 2033)
        self.assertEqual(payload["polarity"], "Shadow")
        self.assertEqual(payload["shadow_type"], "Declining-System")
        self.assertEqual(payload["verification"], "Verified")

    def test_raw_row_maps_to_raw_verification(self):
        row = {"id": "sig_2", "title": "t", "description": "d",
               "category": "Social", "time_horizon": "Near-term",
               "is_keeper": 0, "status": "Shadow"}
        payload = self.adapter.build_node_payload(row)
        self.assertEqual(payload["verification"], "Raw")
        self.assertEqual(payload["polarity"], "Emergent")


if __name__ == "__main__":
    unittest.main()
