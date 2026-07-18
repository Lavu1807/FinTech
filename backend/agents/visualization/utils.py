"""
Utility heuristics for Visualization Agent.
"""

import pandas as pd
from typing import List, Optional


def get_numeric_cols(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_cols(df: pd.DataFrame, max_card: int = 50) -> List[str]:
    cols = []
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() <= max_card:
            cols.append(col)
    return cols


def get_date_col(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for col in df.columns:
        if "date" in str(col).lower() or "time" in str(col).lower():
            return col
    return None


def get_target_metric(df: pd.DataFrame) -> Optional[str]:
    targets = ["revenue", "amount", "price", "total", "sales", "profit", "value"]
    numerics = get_numeric_cols(df)
    for t in targets:
        for col in numerics:
            if t in str(col).lower():
                return col
    return numerics[0] if numerics else None
