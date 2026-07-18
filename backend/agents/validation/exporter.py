"""
Exporter for Validation Agent.
Outputs structured JSON files to exports/validation/.
"""
from typing import List
from .schemas import ValidationScore, ValidationSummary

def _build_summary(scores: List[ValidationScore]) -> ValidationSummary:
    """Compute aggregate statistics across all validated insights."""
    total = len(scores)
    passed = sum(1 for s in scores if s.status == "PASSED")
    failed = sum(1 for s in scores if s.status == "FAILED")
    warning_count = sum(1 for s in scores if s.status == "WARNING")
    
    avg_confidence = (sum(s.confidence_score for s in scores) / total) if total else 0.0
    avg_evidence = (sum(s.evidence_score for s in scores) / total) if total else 0.0
    hallucination_rate = (failed / total) if total else 0.0
    
    unsupported = []
    for s in scores:
        unsupported.extend(s.warnings)
    
    if failed > 0:
        overall_status = "FAILED"
    elif warning_count > 0:
        overall_status = "WARNING"
    else:
        overall_status = "PASSED"
    
    return ValidationSummary(
        total_insights=total,
        passed=passed,
        failed=failed,
        warning_count=warning_count,
        overall_status=overall_status,
        average_confidence=round(avg_confidence, 3),
        average_evidence_score=round(avg_evidence, 3),
        hallucination_rate=round(hallucination_rate, 3),
        unsupported_claims=unsupported
    )


def export_validation_report(scores: List[ValidationScore], workflow_id: str) -> str:
    """Export all validation artifacts and return the directory path."""
    from backend.services.artifact_manager import ArtifactManager
    artifact_mgr = ArtifactManager(workflow_id)
    
    summary = _build_summary(scores)
    
    # 1. Full validation results
    results_path = artifact_mgr.save_json("validation", "validation_results.json", [s.model_dump() for s in scores])
    
    # 2. Validation summary
    summary_path = artifact_mgr.save_json("validation", "validation_summary.json", summary.model_dump())
    
    # 3. Unsupported claims
    unsupported_path = artifact_mgr.save_json("validation", "unsupported_claims.json", summary.unsupported_claims)
    
    # 4. Manifest
    manifest = {
        "total_insights_validated": summary.total_insights,
        "overall_status": summary.overall_status,
        "exported_files": [
            results_path,
            summary_path,
            unsupported_path,
        ]
    }
    artifact_mgr.save_json("validation", "validation_manifest.json", manifest)
        
    return str(artifact_mgr.get_validation_dir())


def get_summary(scores: List[ValidationScore]) -> ValidationSummary:
    """Public accessor for the summary, used by agent.py to populate state."""
    return _build_summary(scores)
