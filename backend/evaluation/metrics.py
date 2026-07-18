from typing import List, Dict, Any


def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates aggregated benchmarking metrics across multiple workflow executions.
    """
    total_runs = len(results)
    if total_runs == 0:
        return {"status": "No runs to evaluate."}

    successful_runs = [r for r in results if r.get("status") == "SUCCESS"]
    success_rate = (len(successful_runs) / total_runs) * 100

    total_execution_time = sum([r.get("execution_time", 0.0) for r in results])
    avg_execution_time = total_execution_time / total_runs

    # Confidence metrics
    avg_planner_confidence = (
        sum([r.get("planner_confidence", 0.0) for r in results]) / total_runs
    )
    avg_validation_confidence = (
        sum([r.get("validation_confidence", 0.0) for r in results]) / total_runs
    )
    avg_hallucination_rate = (
        sum([r.get("hallucination_rate", 0.0) for r in results]) / total_runs
    )
    avg_evidence_score = (
        sum([r.get("evidence_score", 0.0) for r in results]) / total_runs
    )

    # Cost metrics
    total_cost = sum([r.get("estimated_cost", 0.0) for r in results])
    total_tokens = sum([r.get("total_tokens", 0) for r in results])

    # Content metrics
    total_charts = sum([r.get("generated_charts", 0) for r in results])
    total_insights = sum([r.get("generated_insights", 0) for r in results])

    return {
        "total_datasets_evaluated": total_runs,
        "successful_executions": len(successful_runs),
        "overall_workflow_success_rate": round(success_rate, 2),
        "average_execution_time": round(avg_execution_time, 2),
        "average_planner_confidence": round(avg_planner_confidence, 2),
        "average_validation_confidence": round(avg_validation_confidence, 2),
        "average_hallucination_rate": round(avg_hallucination_rate, 2),
        "average_evidence_score": round(avg_evidence_score, 2),
        "total_llm_cost": round(total_cost, 4),
        "total_tokens": total_tokens,
        "total_generated_charts": total_charts,
        "total_generated_insights": total_insights,
    }
