import os
import re
import json
from typing import Dict, Any, Optional

# Try to import generativeai, but do not crash if it is not installed
try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

class AssessmentEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.use_gemini = HAS_GEMINI_SDK and self.api_key is not None
        if self.use_gemini:
            genai.configure(api_key=self.api_key)

    def assess_signal(self, title: str, description: str, category: str) -> Dict[str, Any]:
        """
        Assess a signal across four dimensions:
        1. Impact Potential (1-10)
        2. Strategic Relevance (text)
        3. Time Horizon ('Near-term', 'Mid-term', 'Long-term')
        4. Actionability (text)
        """
        if self.use_gemini:
            try:
                return self._assess_with_gemini(title, description, category)
            except Exception as e:
                # Log or print warning and fall back
                print(f"Gemini API assessment failed: {e}. Falling back to heuristic model.")
                return self._assess_with_heuristics(title, description, category)
        else:
            return self._assess_with_heuristics(title, description, category)

    def _assess_with_gemini(self, title: str, description: str, category: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following weak signal in strategic foresight under the STEEP/PESTLE category '{category}'.
        
        Signal Title: {title}
        Signal Description: {description}
        
        Evaluate this signal across these four strategic dimensions:
        1. Impact Potential (An integer from 1 to 10 determining how significantly this signal could affect organizations or societies if it scales)
        2. Strategic Relevance (A concise explanation of how this signal relates to broader societal shifts or strategic foresight)
        3. Time Horizon (Select exactly one of 'Near-term', 'Mid-term', or 'Long-term')
        4. Actionability (A concrete recommendation or next-step response an organization or speculative design studio could take based on this signal)
        5. Uncertainty (An integer 1-10: how contested/unknowable the signal's trajectory is; 10 = deeply uncertain)
        6. Horizon Year (Your best single-year estimate, e.g. 2035, for when this signal reaches mainstream impact)

        Return your analysis ONLY as a valid JSON object matching the following structure:
        {{
            "impact_score": 8,
            "strategic_relevance": "Explanation here...",
            "time_horizon": "Near-term",
            "actionability": "Concrete next steps...",
            "uncertainty_score": 7,
            "horizon_year": 2035
        }}
        """
        model_name = "gemini-2.0-flash"
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text.strip())
        
        # Clean and validate output types
        impact_score = int(data.get("impact_score", 5))
        impact_score = max(1, min(10, impact_score))
        
        horizon = data.get("time_horizon", "Mid-term")
        if horizon not in ["Near-term", "Mid-term", "Long-term"]:
            horizon = "Mid-term"

        uncertainty_score = max(1, min(10, int(data.get("uncertainty_score", 5))))
        horizon_year = data.get("horizon_year")
        horizon_year = int(horizon_year) if horizon_year and 2020 <= int(horizon_year) <= 2200 else None

        return {
            "impact_score": impact_score,
            "strategic_relevance": data.get("strategic_relevance", "N/A"),
            "time_horizon": horizon,
            "actionability": data.get("actionability", "N/A"),
            "uncertainty_score": uncertainty_score,
            "horizon_year": horizon_year
        }

    def _assess_with_heuristics(self, title: str, description: str, category: str) -> Dict[str, Any]:
        text_to_scan = f"{title} {description}".lower()

        # 1. Evaluate Time Horizon
        long_term_keywords = ["2070", "2060", "2050", "future", "century", "long-term", "decades", "generation"]
        near_term_keywords = ["current", "today", "now", "immediate", "recent", "near-term", "soon", "observation", "prototype"]
        
        horizon = "Mid-term"
        if any(w in text_to_scan for w in long_term_keywords):
            horizon = "Long-term"
        elif any(w in text_to_scan for w in near_term_keywords):
            horizon = "Near-term"

        # 2. Evaluate Impact Score (1-10)
        high_impact_keywords = ["revolutionize", "disrupt", "collapse", "catastrophic", "transform", "breakthrough", "radical", "overturn", "paralyze"]
        low_impact_keywords = ["slight", "minor", "local", "incremental", "niche", "unlikely", "isolated"]
        
        impact = 5
        if any(w in text_to_scan for w in high_impact_keywords):
            impact = 8
        elif any(w in text_to_scan for w in low_impact_keywords):
            impact = 3

        # 2b. Evaluate Uncertainty Score (1-10)
        high_uncertainty_keywords = ["might", "possibly", "speculative", "unproven", "contested", "unclear", "debate", "experimental", "rumor"]
        low_uncertainty_keywords = ["confirmed", "documented", "measured", "established", "regulation passed", "longitudinal", "official"]

        uncertainty = 5
        if any(w in text_to_scan for w in high_uncertainty_keywords):
            uncertainty = 8
        elif any(w in text_to_scan for w in low_uncertainty_keywords):
            uncertainty = 3

        # 2c. Estimate horizon year: explicit 4-digit year wins, else map horizon band
        year_match = re.search(r"\b(20[2-9][0-9]|21[0-9][0-9])\b", text_to_scan)
        if year_match:
            horizon_year = int(year_match.group(1))
        else:
            horizon_year = {"Near-term": 2028, "Mid-term": 2035, "Long-term": 2050}[horizon]

        # 3. Formulate Strategic Relevance Description
        relevance_phrases = []
        if category == "Technological":
            relevance_phrases.append("This technological development alters automation and interface paradigms.")
        elif category == "Environmental":
            relevance_phrases.append("This environmental signal highlights ecological pressures and climate adaptation needs.")
        elif category == "Social":
            relevance_phrases.append("This social signal tracks shifts in demographic behaviors, migration, and lifestyle values.")
        elif category == "Economic":
            relevance_phrases.append("This economic driver impacts business models, supply chains, or resource distribution.")
        elif category == "Political":
            relevance_phrases.append("This political shift affects policy structures, governance frameworks, or regulatory controls.")
        elif category == "Legal":
            relevance_phrases.append("This legal signal establishes new regulatory constraints or compliance precedents.")
            
        relevance_phrases.append(f"Relates to the core strategic domain '{category}' on a '{horizon.lower()}' trajectory.")
        strategic_relevance = " ".join(relevance_phrases)

        # 4. Formulate Actionability Recommendations
        action_recs = [
            f"Speculative design projects should investigate how the '{category}' parameters of this signal interact with everyday environments.",
            f"Conduct design-fiction worldbuilding around a '{horizon.lower()}' scenario where this signal is fully integrated."
        ]
        actionability = " ".join(action_recs)

        return {
            "impact_score": impact,
            "strategic_relevance": strategic_relevance,
            "time_horizon": horizon,
            "actionability": actionability,
            "uncertainty_score": uncertainty,
            "horizon_year": horizon_year,
        }
