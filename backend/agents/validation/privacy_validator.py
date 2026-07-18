"""
Privacy Validator.
Redacts PII from AI generated insights.
"""

import re
from .validators import BaseValidator
from .schemas import ValidationScore
from backend.state.state import FinSightState


class PrivacyValidator(BaseValidator):
    def validate(
        self, insight: str, score: ValidationScore, state: FinSightState
    ) -> ValidationScore:
        original = insight

        # Generic Regex for Emails
        insight = re.sub(r"[\w\.-]+@[\w\.-]+", "[REDACTED_EMAIL]", insight)

        # Generic Regex for standard Phone Numbers (Simplified for demo)
        insight = re.sub(r"\+?\d{10,13}", "[REDACTED_PHONE/ID]", insight)

        # Credit Card (Visa, Mastercard formats roughly 16 digits)
        insight = re.sub(
            r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b", "[REDACTED_CC]", insight
        )

        if original != insight:
            score.insight = insight
            score.validation_notes.append(
                "PII patterns detected and redacted from insight."
            )

        return score
