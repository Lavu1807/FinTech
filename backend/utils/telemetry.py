import sys
import platform
from datetime import datetime, timezone
from typing import Any, Dict
from backend.state.state import FinSightState


class ExecutionTelemetry:
    """
    Deterministically generates enterprise observability exports from the final state.
    """

    @classmethod
    def _save_json(cls, workflow_id: str, filename: str, data: Dict[str, Any]):
        from backend.services.artifact_manager import ArtifactManager

        artifact_mgr = ArtifactManager(workflow_id)
        artifact_mgr.save_json("logs", filename, data)

    @classmethod
    def generate_failure_report(
        cls, state: FinSightState, error: Exception, node_name: str
    ):
        workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
        report = {
            "agent": node_name,
            "exception": str(error),
            "execution_time": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0,
            "input_state_summary": {
                "workflow_stage": state.get("session_info", {}).get("workflow_stage"),
                "completed_agents": state.get("workflow_tracking", {}).get(
                    "completed_agents", []
                ),
            },
            "recommended_fix": "Review the exception stack trace and verify that upstream dependencies were generated correctly.",
        }
        cls._save_json(
            workflow_id,
            f"failure_report_{node_name.replace(' ', '_').lower()}.json",
            report,
        )

    @classmethod
    def generate_workflow_exports(cls, state: FinSightState):
        workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
        cls._generate_agent_performance(state, workflow_id)
        cls._generate_dataset_fingerprint(state, workflow_id)
        cls._generate_workflow_explanation(state, workflow_id)
        cls._generate_run_manifest(state, workflow_id)
        cls._generate_workflow_summary(state, workflow_id)

        # Export workflow execution graph
        graph = state.get("workflow_tracking", {}).get("execution_graph", [])
        if not graph:
            graph = (
                ["START"]
                + state.get("workflow_tracking", {}).get("completed_agents", [])
                + ["END"]
            )
        cls._save_json(workflow_id, "execution_graph.json", {"execution_graph": graph})

    @classmethod
    def _generate_agent_performance(cls, state: FinSightState, workflow_id: str):
        timeline = state.get("execution_metadata", {}).get("timeline", [])

        agent_times = {}
        total_time = 0.0
        total_calls = 0
        total_tokens = 0
        total_cost = 0.0

        for event in timeline:
            name = event.get("agent_name", "Unknown")
            dur = event.get("duration", 0.0)
            agent_times[name] = agent_times.get(name, 0.0) + dur
            total_time += dur
            total_calls += event.get("llm_calls", 0)
            total_tokens += event.get("tokens_used", 0)
            total_cost += event.get("estimated_cost", 0.0)

        slowest = (
            max(agent_times.items(), key=lambda x: x[1])[0] if agent_times else None
        )
        fastest = (
            min(agent_times.items(), key=lambda x: x[1])[0] if agent_times else None
        )
        avg = (total_time / len(agent_times)) if agent_times else 0.0

        data = {
            "execution_time_by_agent": agent_times,
            "slowest_agent": slowest,
            "fastest_agent": fastest,
            "average_execution": avg,
            "total_workflow_time": total_time,
            "total_llm_calls": total_calls,
            "overall_estimated_cost": total_cost,
            "token_usage": total_tokens,
        }
        cls._save_json(workflow_id, "agent_performance.json", data)

    @classmethod
    def _generate_dataset_fingerprint(cls, state: FinSightState, workflow_id: str):
        profile = state.get("dataset_profile", {}).get("overview", {})
        quality = state.get("quality_metrics", {})
        info = state.get("dataset_info", {})

        data = {
            "dataset_hash": profile.get("dataset_hash", "Unknown"),
            "rows": profile.get("rows", 0),
            "columns": profile.get("cols", 0),
            "column_names": (
                list(state.get("dataset_profile", {}).get("columns", {}).keys())
                if state.get("dataset_profile", {}).get("columns")
                else []
            ),
            "memory_usage": profile.get("memory_mb", 0.0),
            "quality_score": quality.get("quality_grade", "Unknown"),
            "dataset_category": info.get("dataset_category", "Unknown"),
            "business_domain": info.get("business_domain", "Unknown"),
            "planner_confidence": state.get("workflow_tracking", {}).get(
                "planner_confidence", 0.0
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        cls._save_json(workflow_id, "dataset_fingerprint.json", data)

    @classmethod
    def _generate_workflow_explanation(cls, state: FinSightState, workflow_id: str):
        plan = state.get("workflow_tracking", {}).get("planner_reasoning", [])
        viz = state.get("visualization", {}).get("charts", [])
        val = state.get("validation", {}).get("validation_results", [])
        insights = state.get("ai_insights", {})

        data = {
            "why_planner_selected_analyses": plan,
            "why_charts_were_generated": (
                [
                    {"chart": c.get("chart_title"), "reason": c.get("description")}
                    for c in viz
                ]
                if isinstance(viz, list)
                else []
            ),
            "why_recommendations_made": insights.get("executive_summary", "N/A"),
            "why_validation_passed": (
                [
                    {
                        "insight": v.get("insight"),
                        "status": v.get("status"),
                        "notes": v.get("validation_notes"),
                    }
                    for v in val
                ]
                if isinstance(val, list)
                else []
            ),
        }
        cls._save_json(workflow_id, "workflow_explanation.json", data)

    @classmethod
    def _generate_run_manifest(cls, state: FinSightState, workflow_id: str):
        meta = state.get("execution_metadata", {})
        session = state.get("session_info", {})
        data = {
            "workflow_version": "1.0.0",
            "prompt_version": meta.get("prompt_version", "v3.0"),
            "provider": meta.get("provider", "Unknown"),
            "python_version": sys.version,
            "os": platform.system(),
            "graph_version": "1.0.0",
            "session_id": session.get("session_id", "Unknown"),
            "workflow_id": meta.get("workflow_id", "Unknown"),
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        cls._save_json(workflow_id, "run_manifest.json", data)

    @classmethod
    def _generate_workflow_summary(cls, state: FinSightState, workflow_id: str):
        meta = state.get("execution_metadata", {})
        info = state.get("dataset_info", {})
        quality = state.get("quality_metrics", {})
        tracking = state.get("workflow_tracking", {})
        viz = state.get("visualization", {}).get("charts", [])
        val = state.get("validation", {}).get("validation_results", [])

        success = (
            "COMPLETED"
            if "error_messages" not in state or not state["error_messages"]
            else "FAILED"
        )

        data = {
            "total_runtime": meta.get("total_execution_time", 0.0),
            "total_llm_cost": meta.get("estimated_llm_cost", 0.0),
            "total_tokens": meta.get("total_tokens", 0),
            "dataset_category": info.get("dataset_category", "Unknown"),
            "quality_grade": quality.get("quality_grade", "Unknown"),
            "planner_confidence": tracking.get("planner_confidence", 0.0),
            "charts_generated": len(viz) if isinstance(viz, list) else 0,
            "reports_generated": (
                3 if state.get("reports", {}).get("markdown_path") else 0
            ),
            "validation_status": (
                all(v.get("status") == "PASS" for v in val)
                if isinstance(val, list) and val
                else "Unknown"
            ),
            "overall_success": success,
        }
        cls._save_json(workflow_id, "workflow_summary.json", data)
