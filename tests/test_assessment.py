import unittest
import sys
from unittest.mock import MagicMock, patch

# Dynamically mock google.generativeai module if it's not present
# to ensure test suite robustness under different environments
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

# Force HAS_GEMINI_SDK to be True for testing the Gemini code paths
import src.assessment
src.assessment.HAS_GEMINI_SDK = True
src.assessment.genai = mock_genai

from src.assessment import AssessmentEngine

class TestAssessmentEngine(unittest.TestCase):
    def test_heuristic_assessment_near_term(self):
        # Temporarily force use_gemini to False to test heuristics
        engine = AssessmentEngine(api_key=None)
        engine.use_gemini = False

        title = "Geriatric Companion Drones Today"
        desc = "A recent prototype drone was seen helping elders with hydration today."
        category = "Technological"

        result = engine.assess_signal(title, desc, category)
        self.assertEqual(result["time_horizon"], "Near-term")
        # No high impact words, so default impact is 5
        self.assertEqual(result["impact_score"], 5)
        self.assertIn("technological", result["strategic_relevance"].lower())
        self.assertIn("near-term", result["actionability"].lower())

    def test_heuristic_assessment_long_term_high_impact(self):
        engine = AssessmentEngine(api_key=None)
        engine.use_gemini = False
        title = "Colossal Climate Migration Collapse in 2070"
        desc = "A catastrophic breakdown of borders will revolutionize speculative migration patterns by 2070."
        category = "Social"

        result = engine.assess_signal(title, desc, category)
        self.assertEqual(result["time_horizon"], "Long-term")
        # Has high impact words "catastrophic" and "revolutionize" -> impact 8
        self.assertEqual(result["impact_score"], 8)
        self.assertIn("social", result["strategic_relevance"].lower())

    def test_gemini_assessment_mock(self):
        # Setup mock model response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"impact_score": 9, "strategic_relevance": "Important strategic link.", "time_horizon": "Long-term", "actionability": "Examine variables."}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Initialize with an API key to force Gemini mode
        engine = AssessmentEngine(api_key="mock_key")
        self.assertTrue(engine.use_gemini)

        result = engine.assess_signal("Title", "Description", "Technological")
        self.assertEqual(result["impact_score"], 9)
        self.assertEqual(result["time_horizon"], "Long-term")
        self.assertEqual(result["strategic_relevance"], "Important strategic link.")
        self.assertEqual(result["actionability"], "Examine variables.")

if __name__ == '__main__':
    unittest.main()
