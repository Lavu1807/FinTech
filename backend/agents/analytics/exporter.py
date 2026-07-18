"""
Exporter for Advanced Analytics Agent.
Outputs JSON files to exports/analytics/.
"""
from typing import List
from .schemas import AnalyticsResult

def export_analytics(result: AnalyticsResult, workflow_id: str) -> List[str]:
    from backend.services.artifact_manager import ArtifactManager
    artifact_mgr = ArtifactManager(workflow_id)
    
    exports = {
        "business_kpis.json": result.calculated_kpis,
        "trend_analysis.json": result.trend_analysis,
        "segment_analysis.json": result.segment_analysis,
        "statistics.json": result.statistical_analysis,
        "anomalies.json": result.anomaly_summary
    }
    
    generated_files = []
    for filename, data in exports.items():
        path = artifact_mgr.save_json("analytics", filename, data)
        if path:
            generated_files.append(path)
        
    return generated_files
