import pickle
from datetime import datetime, timedelta
import os
from typing import Dict, Any, Optional
import pandas as pd

CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "data_cache.pkl")
CACHE_EXPIRY_HOURS = 6

def ensure_cache_dir():
    """Ensure the cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def save_to_cache(data: Dict[str, Any]) -> None:
    """Save data to cache file with timestamp"""
    ensure_cache_dir()
    cache_data = {
        'timestamp': datetime.now(),
        'data': data
    }
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache_data, f)
    print(f"💾 Cache saved at {cache_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

def load_from_cache() -> Optional[Dict[str, Any]]:
    """Load data from cache if it exists and is not expired"""
    if not os.path.exists(CACHE_FILE):
        print("❌ No cache file found")
        return None
    
    try:
        with open(CACHE_FILE, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Check if cache is expired
        cache_age = datetime.now() - cache_data['timestamp']
        if cache_age > timedelta(hours=CACHE_EXPIRY_HOURS):
            print(f"❌ Cache expired (age: {cache_age.total_seconds() / 3600:.1f} hours)")
            return None
        
        print(f"✅ Using cache from {cache_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Cache age: {cache_age.total_seconds() / 3600:.1f} hours")
        return cache_data['data']
    except (pickle.PickleError, KeyError, ValueError) as e:
        print(f"❌ Cache loading error: {e}")
        return None

def cache_data(data: Dict[str, Any]) -> None:
    """Cache the data directly"""
    cache_dict = {
        'df': data['df'],
        'df_weighted_ma': data['df_weighted_ma'],
        'all_party_columns': data['all_party_columns']
    }
    save_to_cache(cache_dict) 