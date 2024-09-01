from cachetools import TTLCache
from typing import Dict, List, Tuple, Any

class CacheUtility:
    """Utility class for managing cached data."""
    
    def __init__(self, maxsize: int, ttl: int):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> Any:
        """Retrieves an item from the cache."""
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Stores an item in the cache."""
        self.cache[key] = value
