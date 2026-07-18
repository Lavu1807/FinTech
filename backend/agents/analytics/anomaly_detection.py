"""
Anomaly Detection Engine for Advanced Analytics Agent.
"""
import pandas as pd
from typing import List
from .utils import get_revenue_col

def detect_anomalies(df: pd.DataFrame) -> List[str]:
    anomalies = []
    
    rev_col = get_revenue_col(df)
    if rev_col:
        s = pd.to_numeric(df[rev_col], errors='coerce').dropna()
        negatives = s[s < 0]
        if len(negatives) > 0:
            anomalies.append(f"Detected {len(negatives)} negative values in {rev_col}.")
            
        # IQR Outliers
        Q1 = s.quantile(0.25)
        Q3 = s.quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR
        extreme_spikes = s[s > upper_bound]
        
        if len(extreme_spikes) > 0:
            anomalies.append(f"Detected {len(extreme_spikes)} extreme high values in {rev_col} (IQR method).")
            
    # Duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        anomalies.append(f"Detected {dup_count} exactly duplicated rows.")
        
    return anomalies
