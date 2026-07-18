import csv
from pathlib import Path
from typing import List

from backend.config.settings import settings
from backend.utils.logger import logger
from .dataset_runner import evaluate_datasets
from .metrics import calculate_metrics
from .summary import export_evaluation_summary

def run_benchmark(dataset_paths: List[str]):
    """
    Main orchestrator for the FinSight AI Evaluation Framework.
    """
    logger.info("Evaluation Framework: Starting benchmark run.")
    
    export_dir = Path(settings.EXPORTS_DIR) / "evaluation"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Evaluate
    results = evaluate_datasets(dataset_paths)
    
    # 2. Metrics
    metrics = calculate_metrics(results)
    
    # 3. Export CSV
    csv_path = export_dir / "benchmark_results.csv"
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "dataset_name", "execution_time", "planner_confidence",
                "validation_confidence", "hallucination_rate", "quality_grade",
                "business_domain", "generated_charts", "generated_insights", "status"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        logger.info(f"Evaluation Framework: Exported {csv_path}")
    except Exception as e:
        logger.error(f"Evaluation Framework: Failed to export CSV: {e}")
        
    # 4. Export JSONs
    export_evaluation_summary(metrics, results, export_dir)
    
    logger.info("Evaluation Framework: Benchmark complete.")

if __name__ == "__main__":
    # Example usage: Evaluate sample dataset(s)
    sample_dataset = Path("finsight_sample_sales_dataset.csv")
    if sample_dataset.exists():
        run_benchmark([str(sample_dataset)])
    else:
        logger.warning("No sample datasets found for benchmarking.")
