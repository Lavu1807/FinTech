"""
Abstract Base Class and Registry for Validation Strategies.
"""
from abc import ABC, abstractmethod
from typing import List
from backend.state.state import FinSightState
from .schemas import ValidationScore
from .evidence_matcher import match_evidence
from .hallucination_detector import detect_hallucinations

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, insight: str, score: ValidationScore, state: FinSightState) -> ValidationScore:
        """
        Validates an insight and mutates/returns the ValidationScore.
        """
        pass

class ValidatorRegistry:
    """Registry to dynamically run all loaded validators."""
    def __init__(self):
        self._validators: List[BaseValidator] = []
        
    def register(self, validator: BaseValidator):
        self._validators.append(validator)
        
    def validate_all(self, insights: List[str], state: FinSightState) -> List[ValidationScore]:
        results = []
        for insight in insights:
            score = ValidationScore(insight=insight)
            
            # Phase 1: Evidence Matching
            metrics, sources, ev_score = match_evidence(insight, state)
            score.supporting_metrics = metrics
            score.evidence_sources = sources
            score.evidence_score = ev_score
            
            # Phase 2: Hallucination Detection
            hall_score, unsupported = detect_hallucinations(insight, state)
            score.hallucination_score = hall_score
            if unsupported:
                score.warnings.extend(unsupported)
            
            # Phase 3: Strategy Validators (Privacy, Quality, Numerical, Trend)
            for validator in self._validators:
                try:
                    score = validator.validate(insight, score, state)
                except Exception as e:
                    score.validation_notes.append(f"Validator {validator.__class__.__name__} failed: {str(e)}")
            
            # Phase 4: Compute final confidence
            score.confidence_score = round(
                (score.evidence_score * 0.4)
                + (score.consistency_score * 0.3)
                + (score.coverage_score * 0.2)
                + ((1.0 - score.hallucination_score) * 0.1),
                3
            )
            
            # Phase 5: Determine overall status
            if score.hallucination_score > 0.5 or score.consistency_score < 0.5:
                score.status = "FAILED"
            elif score.warnings or score.validation_notes:
                score.status = "WARNING"
            else:
                score.status = "PASSED"
                
            results.append(score)
        return results
