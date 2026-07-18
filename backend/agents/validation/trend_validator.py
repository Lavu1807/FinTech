"""
Trend Validator.
Ensures LLM temporal claims align with deterministic time-series trends.
Also validates comparative claims between segments.
"""

from .validators import BaseValidator
from .schemas import ValidationScore
from backend.state.state import FinSightState


class TrendValidator(BaseValidator):
    def validate(
        self, insight: str, score: ValidationScore, state: FinSightState
    ) -> ValidationScore:
        analytics = state.get("business_analytics", {})
        trends = analytics.get("trend_analysis", {})
        segments = analytics.get("segment_analysis", {})

        insight_lower = insight.lower()
        actual_trend = str(trends.get("Overall Trend", "")).lower()

        # 1. Conflicting trend directions
        if "increas" in insight_lower and "decreas" in actual_trend:
            score.consistency_score = max(0.0, score.consistency_score - 0.4)
            score.validation_notes.append(
                f"Insight claims increase, but actual trend is '{actual_trend}'."
            )

        if "decreas" in insight_lower and "increas" in actual_trend:
            score.consistency_score = max(0.0, score.consistency_score - 0.4)
            score.validation_notes.append(
                f"Insight claims decrease, but actual trend is '{actual_trend}'."
            )

        # 2. Spike verification
        if "spike" in insight_lower or "jump" in insight_lower:
            spikes = trends.get("Detected Spikes", [])
            if not spikes:
                score.consistency_score = max(0.0, score.consistency_score - 0.3)
                score.validation_notes.append(
                    "Insight claims a spike, but no statistical spikes were detected."
                )

        # 3. Comparative claim validation ("higher than", "outperforms", "best")
        comparative_keywords = [
            "higher than",
            "lower than",
            "outperform",
            "best",
            "worst",
            "leading",
            "lagging",
        ]
        for kw in comparative_keywords:
            if kw in insight_lower:
                if not segments:
                    score.coverage_score = max(0.0, score.coverage_score - 0.2)
                    score.validation_notes.append(
                        f"Comparative claim '{kw}' found but no segmentation data available to verify."
                    )
                else:
                    if "Segmentation Engine" not in score.evidence_sources:
                        score.evidence_sources.append("Segmentation Engine")
                break

        return score
