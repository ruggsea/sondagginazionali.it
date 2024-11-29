from datetime import datetime
import json
import os
import redis

def get_redis_connection():
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        return None
    try:
        if redis_url.startswith('redis://'):
            redis_url = redis_url.replace('redis://', 'rediss://', 1)
        return redis.from_url(
            redis_url,
            decode_responses=True
        )
    except Exception as e:
        print(f"Redis connection error: {e}")
        return None

def get_client_ip(request):
    """Extract client IP from various headers that might be present"""
    headers = dict(request.headers)
    
    # Check common headers for IP address
    ip_headers = [
        'x-forwarded-for',  # Most common for proxies
        'x-real-ip',        # Used by some proxies
        'cf-connecting-ip', # Cloudflare
        'x-client-ip'      # Some CDNs
    ]
    
    for header in ip_headers:
        if header in headers:
            # Get first IP if there are multiple
            return headers[header].split(',')[0].strip()
    
    # If no headers found, return None
    return None

def log_visit(data):
    redis_client = get_redis_connection()
    if not redis_client:
        print("Redis not configured, skipping logging")
        return

    try:
        timestamp = datetime.now().isoformat()
        
        # Clean up the data to ensure it's serializable
        clean_data = {
            'timestamp': timestamp,
            'ip': get_client_ip(data.get('request')) if 'request' in data else None,
            'headers': data.get('headers', {})
        }
        
        # Add to a Redis list with key 'visit_logs'
        redis_client.lpush('visit_logs', json.dumps(clean_data))
        
        # Optional: Trim the log to keep only last 1000 entries
        redis_client.ltrim('visit_logs', 0, 999)
    except Exception as e:
        print(f"Error logging visit: {e}")