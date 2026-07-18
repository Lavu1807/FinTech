"""
Validation Agent LangGraph Node.
Orchestrates the deterministic Strategy Pattern registry.
"""
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

from backend.state.state import FinSightState, AgentLog
from backend.utils.logger import logger

from .validators import ValidatorRegistry
from .numerical_validator import NumericalValidator
from .trend_validator import TrendValidator
from .quality_validator import QualityValidator
from .privacy_validator import PrivacyValidator
from .exporter import export_validation_report, get_summary


def _extract_insights(state: FinSightState) -> List[str]:
    """
    Extract every validatable string from the nested AIInsights structure.
    Covers key_findings, risks, opportunities, recommendations, and next_best_actions.
    """
    ai_insights = state.get("ai_insights", {})
    insights: List[str] = []

    # Key Findings
    for kf in ai_insights.get("key_findings", []):
        text = kf.get("headline", "")
        explanation = kf.get("explanation", "")
        if text:
            insights.append(f"{text}. {explanation}" if explanation else text)

    # Business Risks
    for risk in ai_insights.get("business_risks", []):
        text = risk.get("risk_type", "")
        impact = risk.get("business_impact", "")
        if text:
            insights.append(f"{text}. {impact}" if impact else text)

    # Business Opportunities
    for opp in ai_insights.get("business_opportunities", []):
        text = opp.get("headline", "")
        explanation = opp.get("explanation", "")
        if text:
            insights.append(f"{text}. {explanation}" if explanation else text)

    # Recommendations
    for rec in ai_insights.get("recommendations", []):
        text = rec.get("recommendation", "")
        reason = rec.get("reason", "")
        if text:
            insights.append(f"{text}. {reason}" if reason else text)

    # Next Best Actions
    for nba in ai_insights.get("next_best_actions", []):
        text = nba.get("action", "")
        benefit = nba.get("expected_benefit", "")
        if text:
            insights.append(f"{text}. {benefit}" if benefit else text)

    # Filter out empties and "Insufficient evidence." placeholders
    return [i for i in insights if i and i.strip() != "Insufficient evidence."]


def validation_node(state: FinSightState) -> Dict[str, Any]:
    """Main execution block for Validation Agent."""
    start_time = time.time()
    agent_name = "Validation Agent"
    
    insights = _extract_insights(state)
    if not insights:
        logger.info(f"{agent_name}: No insights found to validate.")
        return {
            "validation": {
                "validation_results": [],
                "overall_status": "PASSED",
                "average_confidence": 0.0,
                "hallucination_rate": 0.0,
                "unsupported_claims": []
            },
            "agent_logs": [{
                "agent_name": agent_name,
                "status": "COMPLETED",
                "timestamp": datetime.now(timezone.utc),
                "message": "No insights to validate.",
                "provider_used": "Deterministic",
                "llm_calls": 0,
                "estimated_tokens": 0,
                "estimated_cost": 0.0,
                "warnings": []
            }]
        }
        
    # Build Strategy Registry
    registry = ValidatorRegistry()
    registry.register(PrivacyValidator())
    registry.register(QualityValidator())
    registry.register(NumericalValidator())
    registry.register(TrendValidator())
    
    # Run Validations
    scores = registry.validate_all(insights, state)
    
    # Export Validation Output
    workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
    export_dir = export_validation_report(scores, workflow_id)
    
    # Compute Summary
    summary = get_summary(scores)
    
    # Telemetry
    log: AgentLog = {
        "agent_name": agent_name,
        "status": "COMPLETED",
        "timestamp": datetime.now(timezone.utc),
        "message": (
            f"Validated {summary.total_insights} insights. "
            f"Passed: {summary.passed}, Failed: {summary.failed}, Warnings: {summary.warning_count}. "
            f"Hallucination Rate: {summary.hallucination_rate:.1%}."
        ),
        "provider_used": "Deterministic Strategy Engine",
        "llm_calls": 0,
        "estimated_tokens": 0,
        "estimated_cost": 0.0,
        "warnings": [f"Failed validations: {summary.failed}"] if summary.failed > 0 else []
    }
    
    workflow_tracking = state.get("workflow_tracking", {})
    
    return {
        "validation": {
            "validation_results": [s.model_dump() for s in scores],
            "overall_status": summary.overall_status,
            "average_confidence": summary.average_confidence,
            "hallucination_rate": summary.hallucination_rate,
            "unsupported_claims": summary.unsupported_claims
        },
        "workflow_tracking": {
            **workflow_tracking,
            "current_agent": agent_name,
            "completed_agents": workflow_tracking.get("completed_agents", []) + [agent_name],
            "execution_time": time.time() - start_time
        },
        "agent_logs": [log]
    }
