"""
Utility functions for AI Insight Agent.
"""

import hashlib
import json
from typing import Dict, Any


def hash_analytics(analytics: Dict[str, Any], prompt_version: str) -> str:
    """Creates a deterministic hash of the business analytics and the prompt version for caching."""
    # Convert to string deterministically
    analytics_str = json.dumps(analytics, sort_keys=True)
    hash_payload = f"{prompt_version}|{analytics_str}"
    return hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()
