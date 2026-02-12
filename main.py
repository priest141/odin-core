import os
import sys
from loguru import logger

# Ensure the current directory is in sys.path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infra import RedisMessageConsumer, GeminiAnalyzerAdapter, PostgresAlertRepositoryAdapter
from app.use_cases import ProcessAlertUseCase
from config import settings

# load_dotenv() is handled in config.py

def main():
    logger.info("Initializing Odin Core...")

    # 1. Initialize Infrastructure
    # We use our adapters
    consumer = RedisMessageConsumer(settings.REDIS_URL, settings.QUEUE_NAME)
    analyzer = GeminiAnalyzerAdapter()
    repository = PostgresAlertRepositoryAdapter()

    # 2. Initialize Use Cases
    process_alert_use_case = ProcessAlertUseCase(analyzer, repository)

    # 3. Define Callback
    def alert_callback(data):
        try:
            process_alert_use_case.execute(data)
        except Exception as e:
            logger.error(f"Error executing use case: {e}")

    # 4. Start Listening
    try:
        consumer.start_consuming(alert_callback)
    except KeyboardInterrupt:
        logger.info("Odin Core stopped.")

if __name__ == "__main__":
    main()
