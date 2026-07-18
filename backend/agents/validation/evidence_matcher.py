"""
Evidence Matcher for Validation Agent.
Cross-references insight text against deterministic analytics to find supporting evidence.
"""
import re
from typing import List, Dict, Any, Tuple
from backend.state.state import FinSightState


def _flatten_kpis(kpis: Dict[str, Any], prefix: str = "") -> Dict[str, float]:
    """Recursively flatten nested KPI dicts into {full_key: numeric_value}."""
    flat: Dict[str, float] = {}
    for k, v in kpis.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            flat.update(_flatten_kpis(v, full_key))
        else:
            try:
                flat[full_key] = float(v)
            except (ValueError, TypeError):
                pass
    return flat


def _extract_numbers(text: str) -> List[float]:
    """Extract all numeric values from a text string."""
    raw = re.findall(r'[-+]?\d*\.?\d+', text.replace(",", ""))
    values = []
    for r in raw:
        try:
            val = float(r)
            # Skip tiny contextual numbers (ranks, ordinals) and very large IDs / years
            if 10 < val < 9_999_999_999:
                values.append(val)
        except ValueError:
            pass
    return values


def match_evidence(insight: str, state: FinSightState) -> Tuple[List[str], List[str], float]:
    """
    Searches all deterministic sources for evidence supporting the insight.
    Returns (supporting_metrics, evidence_sources, evidence_score).
    """
    analytics = state.get("business_analytics", {})
    quality = state.get("quality_metrics", {})

    supporting_metrics: List[str] = []
    evidence_sources: List[str] = []
    matches_found = 0
    checks_made = 0

    insight_lower = insight.lower()

    # 1. KPI Evidence
    kpis = analytics.get("calculated_kpis", {})
    flat_kpis = _flatten_kpis(kpis)
    insight_numbers = _extract_numbers(insight)

    for num in insight_numbers:
        checks_made += 1
        for kpi_name, kpi_val in flat_kpis.items():
            if kpi_val == 0:
                continue
            tolerance = abs(kpi_val * 0.05)  # 5% tolerance
            if abs(num - kpi_val) <= tolerance:
                matches_found += 1
                supporting_metrics.append(f"{kpi_name}={kpi_val}")
                evidence_sources.append("KPI Engine")
                break

    # 2. Trend Evidence
    trends = analytics.get("trend_analysis", {})
    if trends:
        actual_trend = str(trends.get("Overall Trend", "")).lower()
        if actual_trend:
            checks_made += 1
            if actual_trend in insight_lower or any(
                word in insight_lower for word in actual_trend.split()
            ):
                matches_found += 1
                supporting_metrics.append(f"Overall Trend={actual_trend}")
                evidence_sources.append("Trend Engine")

    # 3. Segmentation Evidence
    segments = analytics.get("segment_analysis", {})
    for seg_key, seg_data in segments.items():
        if isinstance(seg_data, dict):
            top_performers = seg_data.get("Top Performers", {})
            for name in top_performers:
                if str(name).lower() in insight_lower:
                    checks_made += 1
                    matches_found += 1
                    supporting_metrics.append(f"Segment: {seg_key}.{name}")
                    evidence_sources.append("Segmentation Engine")

    # 4. Quality Evidence
    grade = quality.get("quality_grade", "")
    if grade and grade.lower() in insight_lower:
        checks_made += 1
        matches_found += 1
        supporting_metrics.append(f"Quality Grade={grade}")
        evidence_sources.append("Data Auditor")

    # Calculate evidence score
    evidence_score = (matches_found / checks_made) if checks_made > 0 else 0.5

    return supporting_metrics, list(set(evidence_sources)), round(evidence_score, 3)
