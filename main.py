from fasthtml.common import *
import pandas as pd
from datetime import datetime
from moving_average import calculate_weighted_ma
import json
import os
from fasthtml.common import Response
from fasthtml.common import Head
from utils.cache_manager import load_from_cache, cache_data
from utils.logger import log_visit
import redis
from urllib.parse import urlparse
import time
from datetime import datetime, timedelta
import zlib

# Import configurations and components
from config.party_config import PARTY_CONFIG, COALITION_CONFIG
from components.data_processing import (
    load_and_preprocess_data,
    filter_data,
    prepare_chart_datasets
)
from components.charts import create_chart_scripts

# Initialize app with static file support
app, rt = fast_app(static_dir="static")

# Replace the caching logic with Redis
def get_redis_connection():
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        return None
    try:
        if redis_url.startswith('redis://'):
            redis_url = redis_url.replace('redis://', 'rediss://', 1)
        return redis.from_url(redis_url, decode_responses=False)
    except Exception as e:
        print(f"Redis connection error: {e}")
        return None

def compress_json(data):
    return zlib.compress(json.dumps(data).encode())

def decompress_json(data):
    return json.loads(zlib.decompress(data).decode())

def store_in_redis(redis_client, key, data, expiry=3600):
    try:
        compressed = compress_json(data)
        redis_client.setex(key, expiry, compressed)
        return True
    except Exception as e:
        print(f"Error storing {key}: {e}")
        return False

def get_from_redis(redis_client, key):
    try:
        data = redis_client.get(key)
        if data:
            return decompress_json(data)
        return None
    except Exception as e:
        print(f"Error retrieving {key}: {e}")
        return None

def convert_df_to_cacheable(df):
    """Convert Pandas DataFrame to simple Python structures"""
    return [
        {
            'date': row['date'].strftime('%Y-%m-%d'),
            **{
                col: (
                    float(val) 
                    if not pd.isna(val) and not isinstance(val, (str, pd.Timestamp)) 
                    else str(val) if not pd.isna(val) else None
                )
                for col, val in row.items() 
                if col != 'date'
            }
        }
        for _, row in df.iterrows()
    ]

@rt('/')
def home(request):
    cache_start_time = time.time()
    cache_status = "❌ No cache used"
    cache_age = None
    
    # Log the visit
    log_visit({
        'request': request,
        'headers': dict(request.headers)
    })
    
    # Try to load data from Redis cache
    redis_client = get_redis_connection()
    df = None
    df_weighted_ma = None
    all_party_columns = None
    
    if redis_client:
        try:
            # Get metadata
            metadata = get_from_redis(redis_client, 'polls:metadata')
            
            if metadata:
                cache_age = datetime.now() - datetime.fromisoformat(metadata['last_update'])
                all_party_columns = set(metadata['party_columns'])
                
                # Get raw data
                raw_data = get_from_redis(redis_client, 'polls:raw_data')
                ma_data = get_from_redis(redis_client, 'polls:ma_data')
                
                if raw_data and ma_data:
                    # Convert lists of dicts to DataFrames
                    df = pd.DataFrame(raw_data)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    df_weighted_ma = pd.DataFrame(ma_data)
                    df_weighted_ma['date'] = pd.to_datetime(df_weighted_ma['date'])
                    
                    cache_status = "✅ Cache hit"
                
        except Exception as e:
            print(f"Cache read error: {e}")
            cache_status = f"❌ Cache error: {str(e)}"
    
    if df is None or df_weighted_ma is None or all_party_columns is None:
        print("🔄 Loading fresh data...")
        cache_status = "🔄 Cache miss - Loading fresh data"
        
        # Load and process data
        df, all_party_columns = load_and_preprocess_data()
        df = filter_data(df, all_party_columns)
        assert not df.empty, "df is empty"
        
        # Calculate moving averages
        df_weighted_ma = calculate_weighted_ma(df)
        
        # Cache the processed data
        if redis_client:
            try:
                # Prepare data for caching - convert to simple Python structures
                metadata = {
                    'party_columns': list(all_party_columns),
                    'last_update': datetime.now().isoformat()
                }
                
                # Convert DataFrames to lists of dicts with simple types
                raw_data = convert_df_to_cacheable(df)
                ma_data = convert_df_to_cacheable(df_weighted_ma)
                
                # Store in Redis
                store_in_redis(redis_client, 'polls:metadata', metadata, 86400)  # 24 hours
                store_in_redis(redis_client, 'polls:raw_data', raw_data, 3600)   # 1 hour
                store_in_redis(redis_client, 'polls:ma_data', ma_data, 3600)     # 1 hour
                
            except Exception as e:
                print(f"Cache write error: {e}")
                cache_status = f"❌ Cache storage error: {str(e)}"
    
    cache_time = time.time() - cache_start_time
    cache_info = f"""
    Cache Status: {cache_status}
    Cache Operation Time: {cache_time:.2f} seconds
    """
    if cache_age:
        cache_info += f"Cache Age: {cache_age}"
    print(cache_info)
    
    # Get latest values and dates
    latest_date = df_weighted_ma['date'].max()
    latest_values = df_weighted_ma.iloc[-1]
    
    # Format dates - revert to the working version
    dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
    
    # Compare with the other approach
    alternative_dates = [d.strftime('%Y-%m-%d') for d in df['date']]
    
    # Add assertions to verify date format
    assert all(isinstance(d, str) for d in dates), "All dates must be strings"
    assert all(len(d) == 10 for d in dates), "All dates must be 10 characters long (YYYY-MM-DD)"
    assert all(d[4] == '-' and d[7] == '-' for d in dates), "Dates must be in YYYY-MM-DD format"
    
    # Print first and last date for debugging
    
    today = datetime.now()
    today_str = today.strftime('%d/%m/%Y')

    # Get list of party full names
    party_names = [config['name'] for config in PARTY_CONFIG.values()]
    
    party_config = PARTY_CONFIG
    
    # Prepare data for Chart.js using normalized data
    datasets = prepare_chart_datasets(df, df_weighted_ma, dates, party_config)
    

    # Calculate coalition values
    coalition_data = {}
    for date in df_weighted_ma['date']:
        row = df_weighted_ma[df_weighted_ma['date'] == date].iloc[0]
        for coalition, config in COALITION_CONFIG.items():
            value = sum(row[f'{party}_MA'] for party in config['parties'] if f'{party}_MA' in row)
            if coalition not in coalition_data:
                coalition_data[coalition] = []
            coalition_data[coalition].append(round(value, 1))

    # Prepare coalition datasets
    coalition_datasets = []
    for coalition, config in COALITION_CONFIG.items():
        coalition_datasets.append({
            'label': coalition,
            'data': coalition_data[coalition],
            'borderColor': config['color'],
            'backgroundColor': config['color'],
            'borderWidth': 2,
            'tension': 0.4,
            'fill': False,
            'pointRadius': 0
        })

    # Calculate latest coalition values
    latest_coalition_values = {}
    latest_row = df_weighted_ma.iloc[-1]
    for coalition, config in COALITION_CONFIG.items():
        value = sum(latest_row[f'{party}_MA'] for party in config['parties'] if f'{party}_MA' in latest_row)
        latest_coalition_values[coalition] = round(value, 1)

    return Html(
        Head(
            Title("Sondaggi Politici"),
            Link(rel="icon", type="image/png", href="/static/favicon.png"),
        ),
        Body(  # Wrap the main content in Body
            Div(
                # External resources
                Link(rel="stylesheet", href="/static/styles.css"),
                Link(
                    rel="stylesheet",
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
                ),
                Script(src="https://cdn.jsdelivr.net/npm/chart.js"),
                Script(src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"),
                
                # Main content
                Div(
                    H1("Sondaggi Politici Italiani", cls="title"),
                    Div(
                        # Grafico partiti
                        Div(
                            Canvas(id="pollChart"),
                            cls="chart-card chart-container"
                        ),
                        # Riepilogo partiti
                        Div(
                            P(f"Oggi è il {today_str}. La media dei sondaggi è la seguente:", cls="summary-title"),
                            *[
                                Div(
                                    Span(f"{party_config[abbr]['name']}:", cls="party-name"),
                                    Span(f"{latest_values[abbr]:.1f}%", cls="party-value"),
                                    cls="party-row"
                                ) for abbr in party_config
                            ],
                            P(f"Ultimo sondaggio raccolto: {latest_date.strftime('%d/%m/%Y')}", cls="last-update"),
                            cls="summary-card"
                        ),
                        # Title for coalition section
                        H2("Coalizioni", cls="section-title"),
                        # Grafico coalizioni
                        Div(
                            Canvas(id="coalitionChart"),
                            cls="chart-card chart-container"
                        ),
                        # Riepilogo coalizioni
                        Div(
                            P("Media delle coalizioni:", cls="summary-title"),
                            *[
                                Div(
                                    Span(f"{coalition}:", cls="party-name"),
                                    Span(f"{value:.1f}%", cls="party-value"),
                                    cls="party-row"
                                ) for coalition, value in latest_coalition_values.items()
                            ],
                            cls="summary-card"
                        ),
                        cls="content"
                    ),
                    Div(
                        P("Sviluppato da Ruggero Marino Lazzaroni", cls="footer-text"),
                        Div(
                            A(
                                I(cls="fab fa-twitter"), 
                                "Twitter", 
                                href="https://twitter.com/ruggsea", 
                                target="_blank",
                                cls="footer-link"
                            ),
                            A(
                                I(cls="fab fa-linkedin"), 
                                "LinkedIn", 
                                href="https://www.linkedin.com/in/ruggsea/", 
                                target="_blank",
                                cls="footer-link"
                            ),
                            cls="footer-links"
                        ),
                        cls="footer"
                    ),
                    cls="container"
                ),
                
                # Chart scripts
                *create_chart_scripts(dates, datasets, coalition_datasets)
            )
        )
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    serve(host="0.0.0.0", port=port) 