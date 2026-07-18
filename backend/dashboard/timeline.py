from typing import List
from backend.state.state import FinSightState
from .schemas import TimelineEvent


def build_timeline(state: FinSightState) -> List[TimelineEvent]:
    events = []

    # Dataset uploaded event
    execution_metadata = state.get("execution_metadata", {})
    start_time = execution_metadata.get("execution_start")
    if start_time:
        events.append(
            TimelineEvent(timestamp=start_time, event_name="Dataset Uploaded")
        )

    # Process agent logs for started/finished events
    agent_logs = state.get("agent_logs", [])

    last_timestamp = start_time
    for log in agent_logs:
        agent_name = log.get("agent_name", "Unknown Agent")
        timestamp = log.get("timestamp")

        # Estimate start time (either previous agent's finish time or workflow start time)
        if last_timestamp and timestamp:
            events.append(
                TimelineEvent(
                    timestamp=last_timestamp, event_name=f"{agent_name} Started"
                )
            )

        if timestamp:
            events.append(
                TimelineEvent(timestamp=timestamp, event_name=f"{agent_name} Finished")
            )
            last_timestamp = timestamp

    # Sort events strictly by timestamp just in case
    events.sort(key=lambda x: x.timestamp)

    return events
