import unittest
from unittest.mock import MagicMock
from src.deduplication import FallbackTFIDF, DeduplicationEngine

class TestDeduplication(unittest.TestCase):
    def test_fallback_tfidf_similarity(self):
        engine = FallbackTFIDF()
        docs = [
            "Autonomous geriatric companion drones today helping elders with hydration.",
            "Autonomous geriatric companion drones today helping elders with hydration and water services.",
            "Completely unrelated topic about global shipping logistics and supply chain systems."
        ]
        matrix = engine.compute_similarity_matrix(docs)
        
        # Doc 0 and Doc 1 are extremely similar and share many identical words
        self.assertGreater(matrix[0][1], 0.70)
        # Doc 0 and Doc 2 should have extremely low similarity
        self.assertLess(matrix[0][2], 0.15)
        # Self similarity must be 1.0
        self.assertAlmostEqual(matrix[0][0], 1.0)

    def test_clustering_and_medoid_selection(self):
        # Set threshold suitable for fallback TF-IDF
        engine = DeduplicationEngine(threshold=0.45)
        engine.model = None # ensure fallback is used

        signals = [
            # Cluster A (High word overlap)
            {"id": "sig_1", "title": "Elderly companion drones in Hayward", "description": "Geriatric helper drones observed assisting elders in California with hydration."},
            {"id": "sig_2", "title": "Elderly companion drones Hayward", "description": "Geriatric helper drones observed assisting elders in California with hydration and water."},
            {"id": "sig_3", "title": "Helper drones for elderly Hayward", "description": "Geriatric helper drones observed assisting elders in California with companion services."},
            # Cluster B (Unrelated topic, high internal overlap)
            {"id": "sig_4", "title": "Global shipping crisis container shortage", "description": "Logistics bottlenecks and supply chain container shortages in ports."},
            {"id": "sig_5", "title": "Global shipping crisis port bottlenecks", "description": "Logistics bottlenecks and supply chain container shortages slowing global cargo."}
        ]

        clusters = engine.cluster_signals(signals)
        # We expect exactly 2 clusters
        self.assertEqual(len(clusters), 2)
        
        # Verify sizes
        cluster_sizes = sorted([len(c) for c in clusters])
        self.assertEqual(cluster_sizes, [2, 3])

    def test_database_deduplication_execution(self):
        # Setup mock DB
        mock_db = MagicMock()
        signals = [
            {"id": "s1", "title": "Companion robot drone", "description": "Robot drones assisting geriatric demographics with hydration support.", "is_keeper": 1, "keeper_id": None},
            {"id": "s2", "title": "Companion robot drone support", "description": "Robot drones assisting geriatric demographics with hydration support and aid.", "is_keeper": 1, "keeper_id": None},
            {"id": "s3", "title": "Unrelated marine heatwave", "description": "Severe thermal stress affecting coastal kelp forest habitats in California.", "is_keeper": 1, "keeper_id": None}
        ]
        mock_db.get_all_signals.return_value = signals

        engine = DeduplicationEngine(threshold=0.45)
        num_keepers, num_dups = engine.deduplicate_database(mock_db)

        # We expect s1 and s2 to cluster together (1 keeper, 1 duplicate)
        # and s3 to remain independent (1 keeper, 0 duplicate)
        # Total keepers: 2, Total duplicates: 1
        self.assertEqual(num_keepers, 2)
        self.assertEqual(num_dups, 1)

        # Verify database calls
        # There should be exactly 3 updates
        self.assertEqual(mock_db.update_signal_deduplication_status.call_count, 3)

if __name__ == '__main__':
    unittest.main()
