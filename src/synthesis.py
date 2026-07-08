import datetime
import math
import json
import os
from typing import List, Dict, Any, Tuple, Optional

# Lazy load Gemini API
try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

class SynthesisEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.use_gemini = HAS_GEMINI_SDK and self.api_key is not None
        if self.use_gemini:
            genai.configure(api_key=self.api_key)

    def calculate_polar_coordinates(self, category: str, horizon: str) -> Tuple[float, float]:
        """
        Translates category and horizon to polar coordinates (theta in degrees, radius).
        - Social: 30 degrees
        - Technological: 90 degrees
        - Economic: 150 degrees
        - Environmental: 210 degrees
        - Political: 270 degrees
        - Legal: 330 degrees
        
        - Near-term: r = 1.0
        - Mid-term: r = 2.0
        - Long-term: r = 3.0
        """
        category_angles = {
            "Social": 30.0,
            "Technological": 90.0,
            "Economic": 150.0,
            "Environmental": 210.0,
            "Political": 270.0,
            "Legal": 330.0
        }
        
        horizon_radii = {
            "Near-term": 1.0,
            "Mid-term": 2.0,
            "Long-term": 3.0
        }

        theta = category_angles.get(category, 0.0)
        radius = horizon_radii.get(horizon, 1.5)
        return theta, radius

    def calculate_visual_parameters(self, impact_score: int, convergence_score: float) -> Tuple[float, float]:
        """
        Calculates size (diameter) and glow intensity.
        - Size: linearly mapped to impact (minimum size 8, step factor 2)
        - Glow: logarithmically mapped to convergence
        """
        size = 8.0 + (2.0 * impact_score)
        glow = math.log1p(convergence_score) # log(1.0 + convergence)
        return size, round(glow, 3)

    def generate_radar_json(self, db) -> List[Dict[str, Any]]:
        """
        Generates polar radar node coordinates and attributes for all keepers.
        Useful for canvas rendering.
        """
        signals = db.get_all_signals(filter_keeper=True)
        nodes = []
        for s in signals:
            theta, radius = self.calculate_polar_coordinates(s["category"], s["time_horizon"])
            size, glow = self.calculate_visual_parameters(s["impact_score"], s["convergence_score"])
            nodes.append({
                "id": s["id"],
                "title": s["title"],
                "category": s["category"],
                "time_horizon": s["time_horizon"],
                "impact_score": s["impact_score"],
                "convergence_score": s["convergence_score"],
                "theta_degrees": theta,
                "radius": radius,
                "visual_size": size,
                "visual_glow": glow,
                "status": s["status"],
                "duplicates_count": len(s.get("source_metadata", []))
            })
        return nodes

    def compile_markdown_report(self, db) -> str:
        """
        Generates a master Strategic Foresight Report compiling high-impact trends.
        Uses Gemini if key is present; otherwise compiles via template.
        """
        keepers = db.get_all_signals(filter_keeper=True)

        # Filter top-priority issues
        high_impact = [k for k in keepers if k["impact_score"] >= 7]
        high_convergent = [k for k in keepers if k["convergence_score"] > 1.0]

        if self.use_gemini:
            try:
                return self._compile_with_gemini(keepers, high_impact, high_convergent)
            except Exception as e:
                print(f"Gemini report compilation failed: {e}. Compiling from template.")
                return self._compile_from_template(keepers, high_impact, high_convergent)
        else:
            return self._compile_from_template(keepers, high_impact, high_convergent)

    def _compile_from_template(self, keepers: List[Dict[str, Any]], high_impact: List[Dict[str, Any]], high_convergent: List[Dict[str, Any]]) -> str:
        md = []
        today = datetime.date.today()
        md.append("# Foresight Studio: Strategic Synthesis Report")
        md.append(f"\nGenerated on: {today.strftime('%B')} {today.day}, {today.year}\n")
        md.append("## 1. Executive Summary")
        md.append("This report synthesizes the collective horizon scanning signals captured in the Foresight Studio. We have analyzed, evaluated, and semantically deduplicated raw scanning points to identify active macro vectors of shift.")

        md.append("\n## 2. High-Impact Strategic Indicators")
        md.append("Signals evaluated with an Impact Potential of 7 or higher. These observations denote high-leverage points of technological disruption, regulatory shifts, or societal mutations.")
        
        if not high_impact:
            md.append("*No high-impact signals recorded currently.*")
        for s in high_impact:
            md.append(f"\n### {s['title']} (Impact: {s['impact_score']}/10)")
            md.append(f"- **Category:** {s['category']} | **Horizon:** {s['time_horizon']}")
            md.append(f"- **Description:** {s['description']}")
            md.append(f"- **Strategic Relevance:** {s.get('strategic_relevance') or 'N/A'}")
            md.append(f"- **Actionability Recommendation:** {s.get('actionability') or 'N/A'}")

        md.append("\n## 3. Highly Converged Vector Trends")
        md.append("These issues have been validated across multiple independent signal sources, showing notable momentum.")

        if not high_convergent:
            md.append("*No highly converged trends observed yet.*")
        for s in high_convergent:
            dups = s.get("source_metadata", [])
            md.append(f"\n### {s['title']} (Convergence Score: {s['convergence_score']})")
            md.append(f"- **Category:** {s['category']} | **Horizon:** {s['time_horizon']}")
            md.append(f"- **Verified Keeper Node Summary:** {s['description']}")
            md.append(f"- **Supporting Evidence Count:** {len(dups)} duplicates merged.")
            md.append("- **Audit Log / Raw Provenance Sources:**")
            for d in dups:
                md.append(f"  * *Title:* \"{d['title']}\" | *Source URL:* {d.get('source_url') or 'N/A'}")

        return "\n".join(md)

    def _compile_with_gemini(self, keepers: List[Dict[str, Any]], high_impact: List[Dict[str, Any]], high_convergent: List[Dict[str, Any]]) -> str:
        signals_summary = []
        for idx, k in enumerate(keepers[:15]): # Pass top 15 keepers to stay context efficient
            signals_summary.append({
                "title": k["title"],
                "description": k["description"],
                "category": k["category"],
                "time_horizon": k["time_horizon"],
                "impact_score": k["impact_score"],
                "convergence_score": k["convergence_score"],
                "duplicates_count": len(k.get("source_metadata", []))
            })

        prompt = f"""
        You are a principal strategic foresight director at Foresight Studio.
        Below is a JSON dump of semantically clustered strategic signals collected from a collaborative class scan.
        
        Signals Dataset:
        {json.dumps(signals_summary, indent=2)}

        Write a professional, comprehensive, and cohesive Strategic Foresight Portfolio Report for senior executive leadership.
        
        Your report MUST include:
        1. A formal Executive Summary (2-3 paragraphs) explaining the macro forces currently shaping the competitive landscape.
        2. A STEEP/PESTLE Category Analysis (grouping signals into areas like Technological, Environmental, Social, etc.).
        3. Strategic Directions & Actionable Interventions (synthesizing clear organizational next-steps based on the signals' convergence and impact).
        4. Full transparency on evidence and provenance, citing and referencing specific signal titles and their source counts.

        Format the entire response in clean, beautiful Markdown.
        """
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
