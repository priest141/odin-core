import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    QUEUE_NAME: str = os.getenv("QUEUE_NAME", "raw_alerts_queue")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    
    # Database Config
    DB_NAME: str = os.getenv("DB_NAME", "civint_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "sua_senha_segura")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

settings = Config()
