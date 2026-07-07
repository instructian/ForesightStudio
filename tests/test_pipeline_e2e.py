import unittest
import os
import tempfile
import json
from src.database import Database
from src.assessment import AssessmentEngine
from src.deduplication import DeduplicationEngine
from src.synthesis import SynthesisEngine

class TestPipelineE2E(unittest.TestCase):
    def setUp(self):
        # Setup temp workspace
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "e2e_foresight_studio.db")
        self.db = Database(self.db_path)
        
        # Formulate 6 diverse raw signals
        self.raw_signals = [
            # 2 closely overlapping Tech signals (will cluster)
            {
                "title": "Eldercare Helper Drones Hayward",
                "description": "Prototype quadcopters assisting Hayward elders with water delivery and basic hydration checks.",
                "category": "Technological",
                "source_url": "https://example.com/tech1",
                "date_observed": "2026-07-06"
            },
            {
                "title": "Eldercare Companion Drone Hayward",
                "description": "Prototype quadcopters assisting Hayward elders with hydration checks and daily hydration support.",
                "category": "Technological",
                "source_url": "https://example.com/tech2",
                "date_observed": "2026-07-06"
            },
            # 1 Environmental signal (Long-term, High Impact keyword 'breakdown')
            {
                "title": "Severe Coastal Kelp Forest Breakdown in 2070",
                "description": "Marine heatwaves cause severe breakdown and collapse of coastal kelp ecosystem habitats by 2070.",
                "category": "Environmental",
                "source_url": "https://example.com/env1",
                "date_observed": "2026-07-06"
            },
            # 1 Social signal (Near-term)
            {
                "title": "CSUEB Co-Synchronous classroom study",
                "description": "A recent prototype study on co-synchronous global classroom exchanges for university students today.",
                "category": "Social",
                "source_url": "https://example.com/social1",
                "date_observed": "2026-07-06"
            },
            # 1 Legal signal (Mid-term)
            {
                "title": "Local drone airspace regulations",
                "description": "Municipal airspace restrictions limiting low-altitude commercial robotic operations over local residential neighborhoods.",
                "category": "Legal",
                "source_url": "https://example.com/legal1",
                "date_observed": "2026-07-06"
            }
        ]

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_complete_e2e_pipeline(self):
        # --- STAGE 1: INGESTION & MULTI-MODEL ASSESSMENT ---
        assessment = AssessmentEngine()
        
        for raw_sig in self.raw_signals:
            # 1. Run Assessment
            assessment_results = assessment.assess_signal(
                title=raw_sig["title"],
                description=raw_sig["description"],
                category=raw_sig["category"]
            )
            
            # 2. Add to Database
            record = {
                "title": raw_sig["title"],
                "description": raw_sig["description"],
                "category": raw_sig["category"],
                "source_url": raw_sig.get("source_url"),
                "date_observed": raw_sig.get("date_observed"),
                "impact_score": assessment_results["impact_score"],
                "time_horizon": assessment_results["time_horizon"],
                "strategic_relevance": assessment_results["strategic_relevance"],
                "actionability": assessment_results["actionability"],
                "status": "Shadow" # Starts as Shadow
            }
            self.db.add_signal(record)

        # Confirm all 5 are in the Database
        all_signals = self.db.get_all_signals()
        self.assertEqual(len(all_signals), 5)
        
        # --- STAGE 2: SEMANTIC DEDUPLICATION ---
        dedup_engine = DeduplicationEngine(threshold=0.50)
        keepers, duplicates = dedup_engine.deduplicate_database(self.db)
        
        # We expect 4 Keepers total (the 2 elder drones cluster into 1, others remain unique)
        # We expect 1 Duplicate total
        self.assertEqual(keepers, 4)
        self.assertEqual(duplicates, 1)

        # Validate Keeper state
        signals_after_dedup = self.db.get_all_signals()
        
        # Find the keeper and duplicate
        keeper_nodes = [s for s in signals_after_dedup if s["is_keeper"] == 1]
        duplicate_nodes = [s for s in signals_after_dedup if s["is_keeper"] == 0]
        
        self.assertEqual(len(keeper_nodes), 4)
        self.assertEqual(len(duplicate_nodes), 1)

        # The duplicate keeper should have a convergence score of 1.5, and status "Signal"
        clustered_keeper = [k for k in keeper_nodes if k["category"] == "Technological"][0]
        self.assertEqual(clustered_keeper["convergence_score"], 1.5)
        self.assertEqual(clustered_keeper["status"], "Signal")
        self.assertEqual(len(clustered_keeper["source_metadata"]), 1)
        self.assertEqual(clustered_keeper["source_metadata"][0]["source_url"], "https://example.com/tech2" if clustered_keeper["source_url"] == "https://example.com/tech1" else "https://example.com/tech1")

        # --- STAGE 3: RADAR SYNTHESIS & COORDINATES ---
        synthesis = SynthesisEngine()
        radar_nodes = synthesis.generate_radar_json(self.db)
        
        # Only Keepers should be outputted on the radar
        self.assertEqual(len(radar_nodes), 4)
        
        # Verify specific coordinates
        kelp_node = [n for n in radar_nodes if n["category"] == "Environmental"][0]
        self.assertEqual(kelp_node["theta_degrees"], 210.0) # Environmental -> 210 degrees
        self.assertEqual(kelp_node["radius"], 3.0) # Long-term -> r=3.0 (due to word "2070" triggering long-term fallback)
        self.assertEqual(kelp_node["impact_score"], 8) # High-impact word "collapse" -> impact=8
        self.assertEqual(kelp_node["visual_size"], 24.0) # 8.0 + 2*8 = 24.0

        # --- STAGE 4: EXECUTIVE REPORT NARRATIVE ---
        report = synthesis.compile_markdown_report(self.db)
        
        # Verify contents in report
        self.assertIn("# Foresight Studio: Strategic Synthesis Report", report)
        self.assertIn("Severe Coastal Kelp Forest Breakdown in 2070", report)
        self.assertIn("Eldercare Helper Drones Hayward", report if "Eldercare Helper Drones Hayward" in clustered_keeper["title"] else report)
        self.assertIn("1 duplicates merged", report) # Proof of convergence citation!

if __name__ == '__main__':
    unittest.main()
