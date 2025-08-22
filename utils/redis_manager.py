from typing import Any, Optional

import redis
from django.conf import settings


class RedisManager:
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one Redis connection instance."""
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            # Use connection pool for efficiency
            pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=getattr(settings, 'REDIS_PASSWORD', None),
                decode_responses=True
            )
            cls._instance.client = redis.Redis(connection_pool=pool)
        return cls._instance

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Store a value in Redis with an optional expiration time.

        Args:
            key (str): The key to store the value under
            value (Any): The value to store (converted to string if needed)
            expire (int, optional): Time in seconds after which the key expires

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not isinstance(value, (str, bytes)):
                value = str(value)
            return self.client.set(key, value, ex=expire)
        except redis.RedisError as e:
            print(f"Error setting key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from Redis by key.

        Args:
            key (str): The key to retrieve

        Returns:
            str or None: The value if found, None if not
        """
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            print(f"Error getting key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.

        Args:
            key (str): The key to delete

        Returns:
            bool: True if deleted, False if not found or error
        """
        try:
            return self.client.delete(key) > 0
        except redis.RedisError as e:
            print(f"Error deleting key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key (str): The key to check

        Returns:
            bool: True if exists, False otherwise
        """
        try:
            return self.client.exists(key) > 0
        except redis.RedisError as e:
            print(f"Error checking key {key}: {e}")
            return False

    def close(self):
        """Close the Redis connection pool."""
        self.client.connection_pool.disconnect()
