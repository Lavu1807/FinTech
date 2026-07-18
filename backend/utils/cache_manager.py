"""
CacheManager for FinSight AI.
Handles deterministic hashing, caching, and retrieval of dataset execution plans.
Stored in exports/cache/ directory for persistence.
"""
import hashlib
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from backend.utils.logger import logger

class CacheManager:
    _cache_dir = Path(__file__).resolve().parent.parent.parent / "exports" / "cache"

    @classmethod
    def _ensure_dir(cls):
        cls._cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def generate_hash(df: pd.DataFrame) -> str:
        """Computes a fast SHA-256 hash for a DataFrame."""
        if df is None or df.empty:
            return "empty_df_hash"
            
        sample = df.head(1000)
        hash_str = f"{df.shape}|{list(df.columns)}|{pd.util.hash_pandas_object(sample, index=False).sum()}"
        return hashlib.sha256(hash_str.encode('utf-8')).hexdigest()

    @classmethod
    def get(cls, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached JSON data by key if it exists."""
        cls._ensure_dir()
        cache_file = cls._cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    logger.info(f"CacheManager: Hit for key {cache_key}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"CacheManager: Failed to read cache {cache_key}: {e}")
                
        logger.info(f"CacheManager: Miss for key {cache_key}")
        return None

    @classmethod
    def save(cls, cache_key: str, data: Dict[str, Any]) -> None:
        """Saves data to a JSON cache file."""
        cls._ensure_dir()
        cache_file = cls._cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info(f"CacheManager: Saved cache for key {cache_key}")
        except Exception as e:
            logger.error(f"CacheManager: Failed to save cache {cache_key}: {e}")
