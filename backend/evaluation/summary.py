import json
from pathlib import Path
from typing import List, Dict, Any
from backend.utils.logger import logger


def export_evaluation_summary(
    metrics: Dict[str, Any], results: List[Dict[str, Any]], export_dir: Path
):
    """
    Exports evaluation_summary.json and leaderboard.json.
    """
    export_dir.mkdir(parents=True, exist_ok=True)

    # 1. Summary
    summary_path = export_dir / "evaluation_summary.json"
    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)
        logger.info(f"Exported {summary_path}")
    except Exception as e:
        logger.error(f"Failed to export summary: {e}")

    # 2. Leaderboard
    leaderboard_path = export_dir / "leaderboard.json"

    # Ranking heuristic: success first, then a blend of planner and validation confidence, minus hallucination
    def rank_score(r):
        if r.get("status") != "SUCCESS":
            return -9999
        score = (
            r.get("planner_confidence", 0) * 0.3
            + r.get("validation_confidence", 0) * 0.4
            + r.get("evidence_score", 0) * 0.3
            - r.get("hallucination_rate", 0) * 1.5
        )
        return score

    try:
        sorted_results = sorted(results, key=rank_score, reverse=True)
        leaderboard = []
        for rank, r in enumerate(sorted_results, 1):
            if r.get("status") == "SUCCESS":
                leaderboard.append(
                    {
                        "rank": rank,
                        "dataset_name": r.get("dataset_name"),
                        "business_domain": r.get("business_domain"),
                        "overall_score": round(rank_score(r), 2),
                        "planner_confidence": r.get("planner_confidence"),
                        "validation_confidence": r.get("validation_confidence"),
                        "hallucination_rate": r.get("hallucination_rate"),
                    }
                )

        with open(leaderboard_path, "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=4)
        logger.info(f"Exported {leaderboard_path}")
    except Exception as e:
        logger.error(f"Failed to export leaderboard: {e}")
