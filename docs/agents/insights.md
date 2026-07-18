# Insight Agent

The Insight Agent translates deterministic JSON calculations into executive narratives. It interprets the heavy mathematical outputs of the Analytics Agent and extracts the "so what?" factor for business stakeholders.

## Responsibilities
- Identifies primary drivers of growth or decline from the dataset.
- Crafts bulleted strategic recommendations based entirely on the provided metrics.
- Formats insights into Pydantic models for structured downstream consumption.

## I/O Contract
**Reads from State:**
- `state["business_analytics"]`
- `state["dataset_info"]["business_domain"]`

**Writes to State:**
- `state["ai_insights"]`

## Constraints
The prompt for the Insight Agent utilizes **strict grounding directives**. It is explicitly instructed never to hallucinate percentages, totals, or trends that are not explicitly present in `state["business_analytics"]`.

## Failure Handling
Leverages Instructor's validation engine. If the LLM generates a narrative citing a metric that is mathematically impossible based on the Pydantic schema validation bounds, the response is discarded and re-prompted.
