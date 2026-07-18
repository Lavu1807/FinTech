"""
KPI Strategy Engine for Advanced Analytics Agent.
Uses the Registry Pattern to allow extensible KPI calculations.
"""
import pandas as pd
from typing import Dict, Any
from abc import ABC, abstractmethod
from .utils import (
    get_revenue_col, get_customer_id_col, get_numeric_cols, 
    get_categorical_cols, get_date_col, get_quantity_col,
    get_discount_col, get_profit_col, get_cost_col
)

class KPIStrategy(ABC):
    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        pass

class GenericKPIStrategy(KPIStrategy):
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        missing_pct = float(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100) if df.shape[0] > 0 else 0
        duplicate_pct = float(df.duplicated().sum() / df.shape[0] * 100) if df.shape[0] > 0 else 0
        return {
            "Total Records": len(df), 
            "Total Columns": len(df.columns),
            "Missing Percentage": missing_pct,
            "Duplicate Percentage": duplicate_pct
        }

class NumericalKPIStrategy(KPIStrategy):
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        res = {}
        numerics = get_numeric_cols(df)
        if not numerics: return res
        
        df_num = df[numerics].apply(pd.to_numeric, errors='coerce')
        
        res["Numerical Stats"] = {}
        for col in numerics:
            s = df_num[col].dropna()
            if len(s) == 0: continue
            res["Numerical Stats"][col] = {
                "Mean": float(s.mean()),
                "Median": float(s.median()),
                "Min": float(s.min()),
                "Max": float(s.max()),
                "Std": float(s.std()),
                "Sum": float(s.sum())
            }
            # Mode can be multiple, take first
            modes = s.mode()
            if not modes.empty:
                res["Numerical Stats"][col]["Mode"] = float(modes.iloc[0])
                
        return res

class CategoricalKPIStrategy(KPIStrategy):
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        res = {}
        cats = get_categorical_cols(df)
        if not cats: return res
        
        res["Categorical Stats"] = {}
        for col in cats:
            s = df[col].dropna()
            if len(s) == 0: continue
            
            val_counts = s.value_counts()
            top_cat = str(val_counts.index[0]) if len(val_counts) > 0 else "N/A"
            cardinality = int(s.nunique())
            
            res["Categorical Stats"][col] = {
                "Cardinality": cardinality,
                "Top Category": top_cat,
                "Top Category Frequency": int(val_counts.iloc[0]) if len(val_counts) > 0 else 0,
                "Top Category %": float(val_counts.iloc[0] / len(s) * 100) if len(s) > 0 and len(val_counts) > 0 else 0.0
            }
        return res

class DateKPIStrategy(KPIStrategy):
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        date_col = get_date_col(df)
        if not date_col: return {}
        
        s = pd.to_datetime(df[date_col], errors='coerce').dropna()
        if len(s) == 0: return {}
        
        min_date = s.min()
        max_date = s.max()
        span_days = (max_date - min_date).days
        
        return {
            "Date Stats": {
                "Earliest Date": min_date.strftime('%Y-%m-%d'),
                "Latest Date": max_date.strftime('%Y-%m-%d'),
                "Time Span (Days)": span_days,
                "Total Months Spanned": len(s.dt.to_period('M').unique()),
                "Total Years Spanned": len(s.dt.to_period('Y').unique())
            }
        }

class BusinessKPIStrategy(KPIStrategy):
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        res = {}
        
        rev_col = get_revenue_col(df)
        qty_col = get_quantity_col(df)
        get_discount_col(df)
        profit_col = get_profit_col(df)
        cost_col = get_cost_col(df)
        cust_col = get_customer_id_col(df)
        
        if rev_col:
            s_rev = pd.to_numeric(df[rev_col], errors='coerce').dropna()
            if len(s_rev) > 0:
                res["Total Revenue"] = float(s_rev.sum())
                res["Average Transaction Amount"] = float(s_rev.mean())
                res["Largest Transaction"] = float(s_rev.max())
                
        if profit_col:
            s_prof = pd.to_numeric(df[profit_col], errors='coerce').dropna()
            if len(s_prof) > 0:
                res["Total Profit"] = float(s_prof.sum())
                
        if cost_col:
            s_cost = pd.to_numeric(df[cost_col], errors='coerce').dropna()
            if len(s_cost) > 0:
                res["Total Cost"] = float(s_cost.sum())
                
        if qty_col:
            s_qty = pd.to_numeric(df[qty_col], errors='coerce').dropna()
            if len(s_qty) > 0:
                res["Total Quantity Sold"] = float(s_qty.sum())
                
        if cust_col:
            s_cust = df[cust_col].dropna()
            unique_cust = s_cust.nunique()
            res["Unique Customers"] = int(unique_cust)
            if rev_col and unique_cust > 0:
                res["Average Spend per Customer"] = float(res.get("Total Revenue", 0) / unique_cust)
                
        return res

class KPIRegistry:
    """Registry to dynamically execute all loaded KPI strategies."""
    def __init__(self):
        self._strategies = [
            GenericKPIStrategy(),
            NumericalKPIStrategy(),
            CategoricalKPIStrategy(),
            DateKPIStrategy(),
            BusinessKPIStrategy()
        ]
        
    def execute_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        results = {}
        for strategy in self._strategies:
            try:
                results.update(strategy.calculate(df))
            except:
                pass
        return results
