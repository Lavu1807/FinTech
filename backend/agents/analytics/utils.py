"""
Utility heuristics for Advanced Analytics Agent.
"""
import pandas as pd
from typing import List, Optional

def get_numeric_cols(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include='number').columns.tolist()

def get_date_col(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for col in df.columns:
        if "date" in str(col).lower() or "time" in str(col).lower():
            return col
    return None

def get_categorical_cols(df: pd.DataFrame, max_card: int = 50) -> List[str]:
    cols = []
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() <= max_card:
            cols.append(col)
    return cols

def get_revenue_col(df: pd.DataFrame) -> Optional[str]:
    targets = ['revenue', 'amount', 'price', 'total', 'sales']
    numerics = get_numeric_cols(df)
    for t in targets:
        for col in numerics:
            if t in str(col).lower():
                return col
    return numerics[0] if numerics else None

def get_customer_id_col(df: pd.DataFrame) -> Optional[str]:
    targets = ['customer', 'user', 'client']
    for t in targets:
        for col in df.columns:
            if t in str(col).lower() and 'id' in str(col).lower():
                return col
    return None

def get_quantity_col(df: pd.DataFrame) -> Optional[str]:
    targets = ['quantity', 'qty', 'count', 'volume']
    numerics = get_numeric_cols(df)
    for t in targets:
        for col in numerics:
            if t in str(col).lower():
                return col
    return None

def get_discount_col(df: pd.DataFrame) -> Optional[str]:
    targets = ['discount', 'promo', 'reduction']
    numerics = get_numeric_cols(df)
    for t in targets:
        for col in numerics:
            if t in str(col).lower():
                return col
    return None

def get_profit_col(df: pd.DataFrame) -> Optional[str]:
    targets = ['profit', 'margin', 'net_income']
    numerics = get_numeric_cols(df)
    for t in targets:
        for col in numerics:
            if t in str(col).lower():
                return col
    return None

def get_cost_col(df: pd.DataFrame) -> Optional[str]:
    targets = ['cost', 'expense', 'spend']
    numerics = get_numeric_cols(df)
    for t in targets:
        for col in numerics:
            if t in str(col).lower():
                return col
    return None
