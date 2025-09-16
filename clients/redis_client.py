import redis
import os
import json
from datetime import datetime, timezone
from interfaces.clients.cache_interface import ICache


class RedisClient(ICache):
    debounce_seconds: int = int(os.getenv("DEBOUNCE_SECONDS", 5))
    queue_key = "message_queue"

    def __init__(self):
        self._redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=True,
        )

    def add_to_queue(
        self, queue_key: str, key: str, value: str, append: bool = False
    ) -> int:
        queue = self.get_queue(queue_key) or {}
        now = datetime.now(timezone.utc).timestamp()
        expired_at = now + self.debounce_seconds

        if key in queue:
            data = json.loads(queue[key])
            data["expired_at"] = expired_at
            data["value"] = f"{data['value']} {value}" if append else value

            self._redis.hset(queue_key, key, json.dumps(data))
            return data["expired_at"] - now

        self._redis.hset(
            queue_key,
            key,
            json.dumps({"value": value, "expired_at": expired_at}),
        )
        return self.debounce_seconds

    def get_queue(self, queue_key: str):
        return self._redis.hgetall(queue_key)

    def delete_queue(self, queue_key: str, keys_to_delete: list[str]):
        return self._redis.hdel(queue_key, *keys_to_delete)

    def clear_queue(self, queue_key: str):
        return self._redis.delete(queue_key)
