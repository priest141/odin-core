import json
import redis
from typing import Callable, Dict, Any
from loguru import logger
from domain.interfaces import MessageConsumer

class RedisMessageConsumer(MessageConsumer):
    def __init__(self, redis_url: str, queue_name: str):
        self.redis_client = redis.from_url(redis_url)
        self.queue_name = queue_name

    def start_consuming(self, callback: Callable[[Dict[str, Any]], None]):
        logger.info(f"👁️ Odin Core waiting for reports on {self.queue_name}...")
        while True:
            # Blocking pop
            _, message = self.redis_client.brpop(self.queue_name)
            if message:
                try:
                    data = json.loads(message.decode('utf-8'))
                    callback(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
