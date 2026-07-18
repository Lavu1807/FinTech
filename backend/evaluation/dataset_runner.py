import pandas as pd
from typing import List, Dict, Any
from pathlib import Path

from backend.graph.workflow_runner import run_workflow
from backend.utils.logger import logger

def extract_execution_result(state: dict, status: str = "SUCCESS") -> Dict[str, Any]:
    """Flattens the FinSightState into a benchmark result row."""
    meta = state.get("execution_metadata", {})
    tracking = state.get("workflow_tracking", {})
    val = state.get("validation", {})
    ai = state.get("ai_insights", {})
    charts = state.get("visualization", {}).get("generated_files", [])
    
    agent_logs = state.get("agent_logs", [])
    total_tokens = sum([log.get("estimated_tokens", 0) for log in agent_logs])
    total_cost = sum([log.get("estimated_cost", 0.0) for log in agent_logs])
    
    return {
        "dataset_name": state.get("dataset_info", {}).get("filename", "unknown"),
        "business_domain": state.get("dataset_info", {}).get("business_domain", "Unknown"),
        "execution_time": meta.get("total_execution_time", 0.0),
        "planner_confidence": tracking.get("planner_confidence", 0.0) * 100,
        "validation_confidence": val.get("average_confidence", 0.0) * 100,
        "hallucination_rate": val.get("hallucination_score", 0.0) * 100,
        "evidence_score": val.get("evidence_score", 0.0) * 100,
        "quality_grade": state.get("quality_metrics", {}).get("scores", {}).get("overall_quality_grade", "N/A"),
        "total_tokens": max(meta.get("total_tokens", 0), total_tokens),
        "estimated_cost": max(meta.get("estimated_llm_cost", 0.0), total_cost),
        "generated_charts": len(charts),
        "generated_insights": len(ai.get("key_findings", [])),
        "status": status
    }

def evaluate_datasets(dataset_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Iterates over multiple CSV datasets, executing the FinSight AI workflow for each.
    Gracefully handles failures.
    """
    results = []
    
    for path_str in dataset_paths:
        p = Path(path_str)
        if not p.exists() or p.suffix.lower() != '.csv':
            logger.warning(f"DatasetRunner: Skipping invalid dataset path {path_str}")
            continue
            
        logger.info(f"DatasetRunner: Starting evaluation for dataset {p.name}")
        try:
            df = pd.read_csv(p)
            # Execute workflow
            final_state = run_workflow(df, filename=p.name)
            result = extract_execution_result(final_state, status="SUCCESS")
            results.append(result)
            
        except Exception as e:
            logger.error(f"DatasetRunner: Critical failure on {p.name} - {e}")
            results.append({
                "dataset_name": p.name,
                "status": "FAILED"
            })
            
    return results
