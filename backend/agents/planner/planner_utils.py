"""
Utility heuristics for the Planner Agent.
Provides deterministic calculations prior to LLM invocation.
"""
from typing import List

def determine_complexity(rows: int, cols: int, memory_mb: float) -> str:
    """Computes dataset complexity based on dimensions and memory."""
    if rows > 1000000 or cols > 100 or memory_mb > 500:
        return "Enterprise"
    if rows > 100000 or cols > 50 or memory_mb > 100:
        return "Large"
    if rows > 10000 or cols > 20 or memory_mb > 20:
        return "Medium"
    return "Small"

def detect_domain_heuristics(col_names: List[str]) -> str:
    """Heuristically infers the business domain from column names."""
    cols = " ".join(col_names).lower()
    
    if "patient" in cols or "medical" in cols or "diagnosis" in cols: return "Healthcare"
    if "sku" in cols or "cart" in cols or "checkout" in cols: return "E-commerce"
    if "store" in cols or "pos" in cols or "inventory" in cols: return "Retail"
    if "account" in cols or "iban" in cols or "branch" in cols: return "Banking"
    if "policy" in cols or "claim" in cols or "premium" in cols: return "Insurance"
    if "factory" in cols or "batch" in cols or "yield" in cols: return "Manufacturing"
    if "sim" in cols or "data_usage" in cols or "roaming" in cols: return "Telecom"
    if "subscription" in cols or "mrr" in cols or "churn" in cols: return "SaaS"
    
    return "Generic"
