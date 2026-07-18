"""
Trend Engine for Advanced Analytics Agent.
"""
import pandas as pd
from typing import Dict, Any
from .utils import get_date_col, get_revenue_col

def analyze_trends(df: pd.DataFrame) -> Dict[str, Any]:
    date_col = get_date_col(df)
    rev_col = get_revenue_col(df)
    
    if not date_col or not rev_col:
        return {"status": "Missing date or metric columns."}
        
    date_series = pd.to_datetime(df[date_col], errors='coerce')
    rev_series = pd.to_numeric(df[rev_col], errors='coerce')
    
    valid_mask = date_series.notna() & rev_series.notna()
    if not valid_mask.any():
        return {"status": "Insufficient valid data."}
        
    date_series = date_series[valid_mask]
    rev_series = rev_series[valid_mask]
    
    daily = rev_series.groupby(date_series.dt.date).sum().reset_index()
    daily.columns = ['Date', 'Value']
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily = daily.sort_values('Date')
    
    if len(daily) < 3:
        return {"status": "Insufficient time-series length."}
        
    first_val = daily['Value'].iloc[0]
    last_val = daily['Value'].iloc[-1]
    growth = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
    
    mean_val = daily['Value'].mean()
    
    return {
        "Overall Trend": "Increasing" if growth > 0 else "Decreasing",
        "Growth Percentage": float(round(growth, 2)),
        "Average Daily Value": float(round(mean_val, 2))
    }
