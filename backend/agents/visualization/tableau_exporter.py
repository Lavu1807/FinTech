"""
Tableau Exporter for Visualization Agent.
Exports flattened datasets, analytics, chart metadata, and dashboard layouts.
"""

import pandas as pd
from typing import Dict, Any
from .schemas import VisualizationResult


def export_to_tableau(
    df: pd.DataFrame,
    state: Dict[str, Any],
    result: VisualizationResult,
    workflow_id: str,
) -> str:
    from backend.services.artifact_manager import ArtifactManager

    artifact_mgr = ArtifactManager(workflow_id)
    tableau_dir = artifact_mgr.get_tableau_dir()

    try:
        # 1. Export Raw/Cleaned Dataset
        dataset_path = tableau_dir / "dataset.csv"
        df.to_csv(dataset_path, index=False)

        # 2. Export Aggregated Analytics from state
        analytics = state.get("business_analytics", {})

        kpis = analytics.get("calculated_kpis", {})
        if kpis:
            pd.DataFrame(list(kpis.items()), columns=["KPI_Name", "Value"]).to_csv(
                tableau_dir / "kpis.csv", index=False
            )

        trends = analytics.get("trend_analysis", {})
        if trends:
            pd.DataFrame(
                list(trends.items()), columns=["Trend_Metric", "Value"]
            ).to_csv(tableau_dir / "trend_analysis.csv", index=False)

        # 3. Export Chart Metadata
        artifact_mgr.save_json(
            "tableau", "chart_metadata.json", [c.model_dump() for c in result.charts]
        )

        # 4. Generate Dashboard Metadata (Layout)
        dashboard_layout = {
            "dashboard_title": f"FinSight Dashboard - {state.get('dataset_info', {}).get('filename', 'Dataset')}",
            "chart_order": [c.chart_id for c in result.charts],
            "categories": list(set(c.source_analysis for c in result.charts)),
            "recommended_sections": [
                {
                    "section": "Overview",
                    "charts": [
                        c.chart_id
                        for c in result.charts
                        if c.chart_type in ["Pie Chart", "Bar Chart"]
                    ],
                },
                {
                    "section": "Deep Dive",
                    "charts": [
                        c.chart_id
                        for c in result.charts
                        if c.chart_type not in ["Pie Chart", "Bar Chart"]
                    ],
                },
            ],
            "drill_down_enabled": True,
        }
        artifact_mgr.save_json("tableau", "dashboard_layout.json", dashboard_layout)

        return str(dataset_path)
    except Exception as e:
        from backend.utils.logger import logger

        logger.error(f"Tableau Exporter failed: {str(e)}")
        return ""
