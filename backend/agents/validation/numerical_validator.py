"""
Numerical Validator.
Extracts numbers from LLM insights and cross-checks them against deterministic KPIs.
"""

from .validators import BaseValidator
from .schemas import ValidationScore
from .evidence_matcher import _flatten_kpis, _extract_numbers
from backend.state.state import FinSightState


class NumericalValidator(BaseValidator):
    def validate(
        self, insight: str, score: ValidationScore, state: FinSightState
    ) -> ValidationScore:
        analytics = state.get("business_analytics", {})
        kpis = analytics.get("calculated_kpis", {})
        stats = analytics.get("statistical_analysis", {})

        # Deep flatten both KPIs and statistics for maximum coverage
        flat = {**_flatten_kpis(kpis), **_flatten_kpis(stats)}

        numbers = _extract_numbers(insight)
        if not numbers:
            return score

        for val in numbers:
            matched = False
            for kpi_name, kpi_val in flat.items():
                if kpi_val == 0:
                    continue
                tolerance = abs(kpi_val * 0.05)
                if abs(val - kpi_val) <= tolerance:
                    matched = True
                    if f"{kpi_name}={kpi_val}" not in score.supporting_metrics:
                        score.supporting_metrics.append(f"{kpi_name}={kpi_val}")
                    break

            if not matched:
                score.consistency_score = max(0.0, score.consistency_score - 0.2)
                score.validation_notes.append(
                    f"Numerical claim '{val}' deviates from deterministic KPIs by >5%."
                )

        return score
