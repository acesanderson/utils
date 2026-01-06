"""
Provides a decorator for implementing exponential backoff with jittered retry logic on function execution. When a decorated function raises an exception, the decorator automatically retries up to a configurable maximum number of times with exponentially increasing delays between attempts, capped at a maximum delay value. Random jitter is added to each delay to prevent thundering herd problems in distributed systems.

The decorator applies standard exponential backoff mathematics—each retry waits `base_delay * 2^attempt` seconds (up to `max_delay`)—and logs retry attempts with timing information to stdout. On the final retry failure, the original exception is re-raised. This is commonly used throughout the codebase for network-dependent operations like Google Sheets and Trends API calls.

Usage:
```python
from utils.exponential_backoff import exponential_backoff

@exponential_backoff(max_retries=3, base_delay=2, max_delay=30)
def fetch_data_from_api():
    # This will retry up to 3 times with exponential backoff if it raises an exception
    return requests.get("https://api.example.com/data").json()

result = fetch_data_from_api()
```
"""

import time
import random
from functools import wraps


def exponential_backoff(max_retries=5, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = min(base_delay * (2**attempt), max_delay)
                    jittered_delay = delay * (0.5 + random.random())
                    print(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {jittered_delay:.2f}s..."
                    )
                    time.sleep(jittered_delay)

        return wrapper

    return decorator
