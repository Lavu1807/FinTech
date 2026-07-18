"""
Risk Detection and Recommendation engine for Data Auditor Agent.
"""

from typing import List
from .schemas import ColumnProfile, CleaningRecommendation, DatasetRisk


def detect_risks(profiles: List[ColumnProfile]) -> List[DatasetRisk]:
    """Detects PII and sensitive business information."""
    pii_types = {
        "Email",
        "Phone",
        "SSN",
        "PAN",
        "Aadhaar",
        "Passport",
        "IBAN",
        "IFSC",
        "Credit Card",
        "Account Number",
        "Medical Information",
        "Salary",
        "Birth Date",
    }

    risks = []

    # Check for PII
    pii_columns = [p.name for p in profiles if p.inferred_semantic_type in pii_types]
    if pii_columns:
        risks.append(
            DatasetRisk(
                risk_level="Critical",
                risk_type="PII / Sensitive Data Exposure",
                affected_columns=pii_columns,
                recommendation="Mask or drop these columns before running business analytics or exposing to LLMs.",
            )
        )

    return risks


def generate_recommendations(
    profiles: List[ColumnProfile],
) -> List[CleaningRecommendation]:
    """Generates structured cleaning recommendations based on profile metrics."""
    recommendations = []

    for p in profiles:
        # High Missing Values
        if p.missing_percentage > 50:
            recommendations.append(
                CleaningRecommendation(
                    column=p.name,
                    issue="High Missing Values",
                    severity="High",
                    recommended_action="Drop Column",
                    reason=f"{p.missing_percentage}% of the data is missing.",
                    expected_impact="Reduces noise, but loses any residual signal.",
                )
            )
        elif p.missing_percentage > 0:
            action = (
                "Median Imputation"
                if p.inferred_semantic_type in ["Numerical", "Currency", "Percentage"]
                else "Mode Imputation"
            )
            recommendations.append(
                CleaningRecommendation(
                    column=p.name,
                    issue="Missing Values",
                    severity="Medium",
                    recommended_action=action,
                    reason=f"{p.missing_percentage}% missing values detected.",
                    expected_impact="Preserves row count while filling gaps.",
                )
            )

        # Constant / Nearly Constant
        if p.unique_values == 1 and not p.missing_percentage == 100:
            recommendations.append(
                CleaningRecommendation(
                    column=p.name,
                    issue="Constant Column",
                    severity="Low",
                    recommended_action="Drop Column",
                    reason="Column contains only 1 unique value.",
                    expected_impact="Reduces dimensionality with zero information loss.",
                )
            )

        # Outliers
        if p.outliers and p.outliers.percentage > 0:
            sev = "High" if p.outliers.percentage > 5 else "Medium"
            recommendations.append(
                CleaningRecommendation(
                    column=p.name,
                    issue="Outliers Detected",
                    severity=sev,
                    recommended_action=p.outliers.recommended_action,
                    reason=f"Found {p.outliers.number_of_outliers} outliers ({p.outliers.percentage}%).",
                    expected_impact="Normalizes distribution for stable analytics.",
                )
            )

        # High Cardinality IDs (Leakage Risk in ML)
        if p.unique_percentage > 90 and p.inferred_semantic_type in [
            "Text",
            "Categorical",
        ]:
            recommendations.append(
                CleaningRecommendation(
                    column=p.name,
                    issue="High Cardinality",
                    severity="Low",
                    recommended_action="Drop for ML / Keep for DB",
                    reason=f"{p.unique_percentage}% unique text values (potential ID).",
                    expected_impact="Prevents model overfitting.",
                )
            )

    return recommendations
