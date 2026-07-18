"""
Pandas-based Data Profiling Engine.
Computes deterministic statistics and semantic inferences for the Data Auditor Agent.
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from .schemas import DatasetOverview, ColumnProfile, OutlierReport
from backend.utils.logger import logger

def generate_overview(df: pd.DataFrame, filename: str) -> DatasetOverview:
    """Generates high-level metadata for the dataset."""
    row_count, col_count = df.shape
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_mb = memory_bytes / (1024 * 1024)
    
    size_category = "Small"
    if row_count > 500000 or memory_mb > 100:
        size_category = "Large"
    elif row_count > 50000 or memory_mb > 10:
        size_category = "Medium"
        
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_rows / max(row_count, 1)) * 100, 2)
        
    return DatasetOverview(
        filename=filename,
        dataset_shape=(row_count, col_count),
        row_count=row_count,
        column_count=col_count,
        memory_usage_bytes=int(memory_bytes),
        memory_usage_mb=round(memory_mb, 2),
        size_category=size_category,
        duplicate_rows=duplicate_rows,
        duplicate_percentage=duplicate_pct
    )

def infer_semantic_type(series: pd.Series, name: str) -> str:
    """Heuristic-based semantic type inference."""
    name_lower = name.lower()
    str(series.dtype)
    
    if pd.api.types.is_datetime64_any_dtype(series):
        return "Date"
        
    if "date" in name_lower or "time" in name_lower:
        # Check if it can be parsed as date
        try:
            pd.to_datetime(series.dropna().head(100))
            return "Date"
        except Exception:
            pass
            
    if "email" in name_lower: return "Email"
    if "phone" in name_lower or "mobile" in name_lower: return "Phone"
    if "ssn" in name_lower or "social security" in name_lower: return "SSN"
    if "pan" in name_lower and "company" not in name_lower: return "PAN"
    if "aadhaar" in name_lower or "aadhar" in name_lower: return "Aadhaar"
    if "passport" in name_lower: return "Passport"
    if "iban" in name_lower: return "IBAN"
    if "ifsc" in name_lower: return "IFSC"
    if "credit card" in name_lower or "card number" in name_lower or "cc_" in name_lower: return "Credit Card"
    if "account number" in name_lower or "acct" in name_lower: return "Account Number"
    if "medical" in name_lower or "health" in name_lower or "diagnosis" in name_lower: return "Medical Information"
    if "salary" in name_lower or "income" in name_lower or "wage" in name_lower: return "Salary"
    if "dob" in name_lower or "birth" in name_lower: return "Birth Date"
    
    # ID inference
    if "id" in name_lower:
        if "customer" in name_lower or "user" in name_lower or "client" in name_lower:
            return "Customer ID"
        if "transaction" in name_lower or "order" in name_lower or "payment" in name_lower:
            return "Transaction ID"
        if "product" in name_lower or "item" in name_lower or "sku" in name_lower:
            return "Product ID"
            
    if pd.api.types.is_bool_dtype(series) or (series.dropna().isin([0, 1, '0', '1', 'True', 'False', True, False]).all() and series.nunique() <= 2):
        return "Boolean"
        
    if pd.api.types.is_numeric_dtype(series):
        if "amount" in name_lower or "price" in name_lower or "revenue" in name_lower or "cost" in name_lower or "currency" in name_lower:
            return "Currency"
        if "percent" in name_lower or "rate" in name_lower or series.dropna().between(0, 1).mean() > 0.9:
            return "Percentage"
        return "Numerical"
        
    unique_count = series.nunique()
    if unique_count < 100 or (unique_count / max(len(series), 1)) < 0.05:
        return "Categorical"
        
    return "Text"

def profile_numerical(series: pd.Series) -> Dict[str, Any]:
    """Generates numerical statistics."""
    s = series.dropna()
    if s.empty:
        return {}
    
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    
    return {
        "count": int(s.count()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "mode": float(s.mode().iloc[0]) if not s.mode().empty else None,
        "standard_deviation": float(s.std()) if s.count() > 1 else 0.0,
        "variance": float(s.var()) if s.count() > 1 else 0.0,
        "minimum": float(s.min()),
        "maximum": float(s.max()),
        "range": float(s.max() - s.min()),
        "quartiles": {"25%": float(q1), "50%": float(s.median()), "75%": float(q3)},
        "iqr": float(q3 - q1),
        "skewness": float(s.skew()) if s.count() > 2 else 0.0,
        "kurtosis": float(s.kurtosis()) if s.count() > 3 else 0.0
    }

def detect_outliers(series: pd.Series, col_name: str) -> Optional[OutlierReport]:
    """Detects outliers using IQR and Z-score."""
    s = series.dropna()
    if s.empty or not pd.api.types.is_numeric_dtype(s):
        return None
        
    # IQR Method
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = s[(s < lower_bound) | (s > upper_bound)]
    num_outliers = len(outliers)
    
    if num_outliers == 0:
        return None
        
    percentage = (num_outliers / len(series)) * 100
    
    action = "Investigate"
    if percentage < 1:
        action = "Remove or Cap"
    elif percentage < 5:
        action = "Cap (Winsorize)"
        
    return OutlierReport(
        column=col_name,
        number_of_outliers=num_outliers,
        percentage=round(percentage, 2),
        recommended_action=action
    )

def profile_categorical(series: pd.Series) -> Dict[str, Any]:
    """Generates categorical statistics."""
    s = series.dropna()
    if s.empty:
        return {}
        
    value_counts = s.value_counts()
    top_values = value_counts.head(5).to_dict()
    
    # Imbalance ratio: frequency of most common vs least common in top 10
    top_10 = value_counts.head(10)
    imbalance_ratio = float(top_10.iloc[0] / max(top_10.iloc[-1], 1)) if len(top_10) > 1 else 1.0
    
    return {
        "top_values": {str(k): int(v) for k, v in top_values.items()},
        "frequency": {str(k): round(float(v / len(s)), 4) for k, v in top_values.items()},
        "cardinality": int(s.nunique()),
        "imbalance_ratio": round(imbalance_ratio, 2)
    }

def profile_date(series: pd.Series) -> Dict[str, Any]:
    """Generates date statistics."""
    s = pd.to_datetime(series.dropna(), errors='coerce').dropna()
    if s.empty:
        return {}
        
    min_date = s.min()
    max_date = s.max()
    span_days = (max_date - min_date).days
    
    today = pd.Timestamp.now()
    future_dates = int((s > today).sum())
    
    return {
        "minimum_date": min_date.isoformat(),
        "maximum_date": max_date.isoformat(),
        "date_span_days": span_days,
        "future_dates_count": future_dates,
        "invalid_dates_count": int(series.dropna().shape[0] - s.shape[0])
    }

def profile_dataframe(df: pd.DataFrame) -> List[ColumnProfile]:
    """Profiles all columns in the dataframe gracefully."""
    profiles = []
    total_rows = len(df)
    
    for col in df.columns:
        try:
            series = df[col]
            null_count = int(series.isnull().sum())
            nunique = int(series.nunique())
            
            # Base stats
            cardinality_label = "High"
            if nunique < 10: cardinality_label = "Low"
            elif nunique < 100: cardinality_label = "Medium"
            
            semantic_type = infer_semantic_type(series, str(col))
            
            profile = ColumnProfile(
                name=str(col),
                datatype=str(series.dtype),
                nullable=(null_count > 0),
                unique_values=nunique,
                unique_percentage=round((nunique / max(total_rows, 1)) * 100, 2),
                missing_values=null_count,
                missing_percentage=round((null_count / max(total_rows, 1)) * 100, 2),
                duplicate_values=int(total_rows - nunique - null_count) if total_rows > nunique else 0,
                cardinality=cardinality_label,
                inferred_semantic_type=semantic_type
            )
            
            # Semantic specific stats
            if semantic_type in ["Numerical", "Currency", "Percentage", "Boolean"]:
                # Convert to numeric safely for analysis
                num_series = pd.to_numeric(series, errors='coerce')
                profile.numerical_stats = profile_numerical(num_series)
                profile.outliers = detect_outliers(num_series, str(col))
                
            elif semantic_type == "Date":
                profile.date_stats = profile_date(series)
                
            else:
                profile.categorical_stats = profile_categorical(series)
                
            profiles.append(profile)
            
        except Exception as e:
            logger.error(f"Failed to profile column '{col}': {str(e)}")
            # Push a basic profile to avoid crashing workflow
            profiles.append(ColumnProfile(
                name=str(col),
                datatype=str(df[col].dtype),
                nullable=True, unique_values=0, unique_percentage=0.0,
                missing_values=0, missing_percentage=0.0, duplicate_values=0,
                cardinality="Unknown", inferred_semantic_type="Unknown"
            ))
            
    return profiles
