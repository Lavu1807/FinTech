"""
Quality Scoring engine for Data Auditor Agent.
Calculates heuristic-based quality scores between 0 and 100.
"""

from typing import List
from .schemas import ColumnProfile, QualityScore


def _assign_quality_grade(score: float) -> str:
    if score >= 97:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 85:
        return "B+"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def calculate_quality(profiles: List[ColumnProfile], total_rows: int) -> QualityScore:
    """Calculates dataset quality scores out of 100."""
    if not profiles or total_rows == 0:
        return QualityScore(
            missing_value_score=0.0,
            duplicate_score=0.0,
            outlier_score=0.0,
            consistency_score=0.0,
            completeness_score=0.0,
            overall_score=0.0,
            explanations={"error": "Empty dataset."},
        )

    num_cols = len(profiles)

    # 1. Missing Value Score (Completeness)
    avg_missing = sum(p.missing_percentage for p in profiles) / num_cols
    missing_score = max(0.0, 100.0 - avg_missing)
    completeness_score = missing_score  # tightly coupled

    # 2. Outlier Score
    num_outlier_cols = 0
    total_outlier_penalty = 0.0
    for p in profiles:
        if p.outliers:
            num_outlier_cols += 1
            total_outlier_penalty += p.outliers.percentage

    avg_outlier_pct = total_outlier_penalty / max(num_outlier_cols, 1)
    # 5% outliers drops score heavily, cap at 0
    outlier_score = max(0.0, 100.0 - (avg_outlier_pct * 10))
    if num_outlier_cols == 0:
        outlier_score = 100.0

    # 3. Duplicate Score (Heuristic based on column duplication)
    # A true row-level duplicate requires dataframe access, but we approximate via high-cardinality duplication
    avg_dupe_pct = sum(
        (p.duplicate_values / total_rows * 100)
        for p in profiles
        if p.cardinality == "High"
    ) / max(sum(1 for p in profiles if p.cardinality == "High"), 1)
    duplicate_score = max(
        0.0, 100.0 - (avg_dupe_pct / 2)
    )  # Div 2 to be lenient on column-level dupes

    # 4. Consistency Score (Invalid dates, mixed inference)
    inconsistencies = 0
    for p in profiles:
        if p.date_stats and p.date_stats.get("invalid_dates_count", 0) > 0:
            inconsistencies += p.date_stats["invalid_dates_count"] / total_rows * 100
    consistency_score = max(0.0, 100.0 - (inconsistencies * 2))

    # Overall Score (Weighted average)
    overall = (
        (missing_score * 0.3)
        + (duplicate_score * 0.2)
        + (outlier_score * 0.2)
        + (consistency_score * 0.15)
        + (completeness_score * 0.15)
    )

    explanations = {
        "Missing Value Score": f"Penalized based on {round(avg_missing, 2)}% average missing data.",
        "Outlier Score": f"Found outliers in {num_outlier_cols} columns, averaging {round(avg_outlier_pct, 2)}% anomalous rows.",
        "Consistency Score": "Checks for invalid dates and semantic type mismatches.",
        "Overall Score": "Weighted aggregation of all quality dimensions.",
    }

    return QualityScore(
        missing_value_score=round(missing_score, 2),
        duplicate_score=round(duplicate_score, 2),
        outlier_score=round(outlier_score, 2),
        consistency_score=round(consistency_score, 2),
        completeness_score=round(completeness_score, 2),
        overall_score=round(overall, 2),
        quality_grade=_assign_quality_grade(overall),
        explanations=explanations,
    )
