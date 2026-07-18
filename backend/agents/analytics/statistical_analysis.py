"""
Statistical Engine for Advanced Analytics Agent.
Computes Variance, Skewness, Kurtosis, and Significant Correlations.
"""

import pandas as pd
from typing import Dict, Any
from .utils import get_numeric_cols, get_revenue_col


def compute_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    numerics = get_numeric_cols(df)
    if not numerics:
        return {"status": "No numeric columns found."}

    df_num = df[numerics].apply(pd.to_numeric, errors="coerce")

    # Base stats
    stats = {
        "Variance": df_num.var().fillna(0).to_dict(),
        "Standard Deviation": df_num.std().fillna(0).to_dict(),
        "Skewness": df_num.skew().fillna(0).to_dict(),
        "Kurtosis": df_num.kurt().fillna(0).to_dict(),
    }

    # Correlation Matrix
    if len(numerics) > 1:
        corr = df_num.corr()
        abs_corr = corr.abs()
        sig_corr = {}
        weak_corr = {}
        for col in corr.columns:
            high_corr = corr[col][(abs_corr[col] > 0.5) & (abs_corr[col] < 0.99)]
            if not high_corr.empty:
                sig_corr[col] = high_corr.to_dict()

            low_corr = corr[col][(abs_corr[col] < 0.3) & (abs_corr[col] > 0.0)]
            if not low_corr.empty:
                weak_corr[col] = low_corr.to_dict()

        stats["Highly Correlated Features"] = sig_corr
        stats["Weak Correlations"] = weak_corr

        # Feature Importance (Heuristic based on correlation to revenue)
        rev_col = get_revenue_col(df)
        if rev_col and rev_col in df_num.columns:
            rev_corr = corr[rev_col].drop(rev_col).fillna(0)
            top_features = rev_corr.abs().sort_values(ascending=False).head(5).to_dict()
            stats["Feature Importance (Correlation to Revenue)"] = top_features

    return stats
