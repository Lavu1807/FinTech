"""
AI Insight Agent LangGraph Node.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any

from backend.state.state import FinSightState, AgentLog
from backend.services.llm_gateway import llm_gateway
from backend.utils.cache_manager import CacheManager
from backend.utils.logger import logger

from .schemas import InsightOutput
from .context_builder import build_xml_context
from .prompt_builder import build_insight_prompt
from .recommendation_engine import (
    process_recommendations,
    calculate_deterministic_confidence,
)
from .exporter import export_insights
from .utils import hash_analytics

PROMPT_VERSION = "v4.0"


def insight_node(state: FinSightState) -> Dict[str, Any]:
    """LangGraph node execution block."""
    start_time = time.time()
    agent_name = "Insight Agent"

    analytics = state.get("business_analytics", {})
    if not analytics:
        logger.warning(f"{agent_name}: No business analytics found. Skipping.")
        return {
            "agent_logs": [
                {
                    "agent_name": agent_name,
                    "status": "FAILED",
                    "timestamp": datetime.now(timezone.utc),
                    "message": "Missing analytics context.",
                    "provider_used": "None",
                    "llm_calls": 0,
                    "estimated_tokens": 0,
                    "estimated_cost": 0.0,
                    "warnings": [],
                }
            ]
        }

    # Generate Cache Key
    cache_key = hash_analytics(analytics, PROMPT_VERSION)
    execution_metadata = state.get("execution_metadata", {})

    # Check Cache
    cached_response = CacheManager.get(cache_key)
    if cached_response:
        logger.info(f"{agent_name}: Cache HIT for {cache_key}.")
        llm_output = InsightOutput(**cached_response["data"])
        provider = "Cache"
        est_tokens = 0
        est_cost = 0.0
    else:
        logger.info(f"{agent_name}: Cache MISS. Building context and invoking LLM.")
        try:
            # Build Context & Prompt
            context_dict = build_xml_context(state)
            prompt = build_insight_prompt(context_dict)

            # Invoke Gateway
            gateway_response = llm_gateway.invoke_structured(
                prompt=prompt,
                output_schema=InsightOutput,
                calling_agent=agent_name,
                temperature=0.3,
            )

            if not gateway_response:
                raise Exception("Gateway returned None.")

            llm_output = gateway_response.data
            provider = gateway_response.provider
            est_tokens = gateway_response.estimated_tokens
            est_cost = gateway_response.estimated_cost

            # Post-Process: Sort by priority
            llm_output = process_recommendations(llm_output)

            # Override confidence with deterministic calculation
            deterministic_conf = calculate_deterministic_confidence(llm_output, state)
            llm_output.confidence = deterministic_conf

            # Save Cache
            CacheManager.save(
                cache_key,
                {"data": llm_output.model_dump(), "prompt_version": PROMPT_VERSION},
            )

        except Exception as e:
            logger.error(f"{agent_name} failed: {str(e)}")
            # Deterministic Fallback Output
            llm_output = InsightOutput(
                executive_summary="AI interpretation unavailable due to service error.",
                key_findings=[],
                business_risks=[],
                business_opportunities=[],
                recommendations=[],
                next_best_actions=[],
                data_quality_observations=["Insufficient evidence."],
                confidence=0.0,
            )
            provider = "Fallback"
            est_tokens = 0
            est_cost = 0.0

    # Exporter
    workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
    export_paths = export_insights(llm_output, workflow_id)

    # Telemetry Tracking
    execution_duration = time.time() - start_time
    total_tokens = execution_metadata.get("total_tokens", 0) + est_tokens
    total_cost = execution_metadata.get("estimated_llm_cost", 0.0) + est_cost
    total_llm = execution_metadata.get("total_llm_calls", 0) + (
        0 if provider == "Cache" else 1
    )

    insight_count = (
        len(llm_output.key_findings)
        + len(llm_output.business_risks)
        + len(llm_output.business_opportunities)
        + len(llm_output.recommendations)
        + len(llm_output.next_best_actions)
    )

    log: AgentLog = {
        "agent_name": agent_name,
        "status": "COMPLETED",
        "timestamp": datetime.now(timezone.utc),
        "message": (
            f"Generated {insight_count} insights with confidence {llm_output.confidence}. "
            f"Provider: {provider}. Tokens: {est_tokens}. Exports: {len(export_paths)} files."
        ),
        "provider_used": provider,
        "llm_calls": 0 if provider == "Cache" else 1,
        "estimated_tokens": est_tokens,
        "estimated_cost": est_cost,
        "warnings": [],
    }

    workflow_tracking = state.get("workflow_tracking", {})

    return {
        "ai_insights": llm_output.model_dump(),
        "execution_metadata": {
            **execution_metadata,
            "provider": provider,
            "prompt_version": PROMPT_VERSION,
            "prompt_hash": cache_key,
            "input_tokens": est_tokens,
            "output_tokens": 0,
            "total_tokens": total_tokens,
            "latency": execution_duration,
            "estimated_llm_cost": total_cost,
            "total_llm_calls": total_llm,
        },
        "workflow_tracking": {
            **workflow_tracking,
            "current_agent": agent_name,
            "completed_agents": workflow_tracking.get("completed_agents", [])
            + [agent_name],
            "execution_time": execution_duration,
        },
        "agent_logs": [log],
    }
