"""
Quality Validator.
Flags insights derived from poor quality data.
"""
from .validators import BaseValidator
from .schemas import ValidationScore
from backend.state.state import FinSightState

class QualityValidator(BaseValidator):
    def validate(self, insight: str, score: ValidationScore, state: FinSightState) -> ValidationScore:
        metrics = state.get("quality_metrics", {})
        grade = metrics.get("quality_grade", "A")
        
        if grade in ["D", "F"]:
            score.coverage_score = max(0.0, score.coverage_score - 0.5)
            score.validation_notes.append(f"WARNING: Insight is derived from a dataset with Quality Grade {grade}. Reliability is extremely low.")
            
        return score
