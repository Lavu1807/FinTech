"""
Exporter for AI Insight Agent.
Outputs structured JSON files to exports/insights/.
"""

from datetime import datetime, timezone
from typing import List
from .schemas import InsightOutput


def export_insights(result: InsightOutput, workflow_id: str) -> List[str]:
    """Export all insight artifacts and return list of generated file paths."""
    from backend.services.artifact_manager import ArtifactManager

    artifact_mgr = ArtifactManager(workflow_id)

    exports = {
        "executive_summary.json": {"executive_summary": result.executive_summary},
        "key_findings.json": [k.model_dump() for k in result.key_findings],
        "opportunities.json": [o.model_dump() for o in result.business_opportunities],
        "risks.json": [r.model_dump() for r in result.business_risks],
        "recommendations.json": [r.model_dump() for r in result.recommendations],
        "next_actions.json": [a.model_dump() for a in result.next_best_actions],
    }

    generated_files = []
    for filename, data in exports.items():
        path = artifact_mgr.save_json("insights", filename, data)
        if path:
            generated_files.append(path)

    # Generate insight manifest
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_confidence": result.confidence,
        "finding_count": len(result.key_findings),
        "risk_count": len(result.business_risks),
        "opportunity_count": len(result.business_opportunities),
        "recommendation_count": len(result.recommendations),
        "action_count": len(result.next_best_actions),
        "quality_observation_count": len(result.data_quality_observations),
        "exported_files": generated_files,
    }

    manifest_path = artifact_mgr.save_json(
        "insights", "insight_manifest.json", manifest
    )
    if manifest_path:
        generated_files.append(manifest_path)

    return generated_files
