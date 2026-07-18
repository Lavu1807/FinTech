"""
Segmentation Engine for Advanced Analytics Agent.
Groups data by categorical dimensions and compares performers.
"""
import pandas as pd
from typing import Dict, Any
from .utils import get_categorical_cols, get_revenue_col

def analyze_segments(df: pd.DataFrame) -> Dict[str, Any]:
    cat_cols = get_categorical_cols(df)
    target_col = get_revenue_col(df)
    
    segments = {}
    if not target_col or target_col not in df.columns:
        return segments
        
    target_series = pd.to_numeric(df[target_col], errors='coerce')
    total_val = target_series.sum()
    
    for col in cat_cols:
        grouped = target_series.groupby(df[col]).sum().sort_values(ascending=False)
        if len(grouped) == 0: continue
            
        top = grouped.head(5)
        bottom = grouped.tail(5)
        
        # Comparative Analysis: Top 1 vs Next 1 (if available)
        top_vs_next = 0.0
        if len(grouped) > 1 and grouped.iloc[1] > 0:
            top_vs_next = float(((grouped.iloc[0] - grouped.iloc[1]) / grouped.iloc[1]) * 100)
        
        segments[col] = {
            "Top Performers": {str(k): float(v) for k, v in top.to_dict().items()},
            "Bottom Performers": {str(k): float(v) for k, v in bottom.to_dict().items()},
            "Largest Contributor %": float((grouped.iloc[0] / total_val) * 100) if total_val > 0 else 0.0,
            "Smallest Contributor %": float((grouped.iloc[-1] / total_val) * 100) if total_val > 0 else 0.0,
            "Top vs Next % Difference": top_vs_next
        }
    return segments
