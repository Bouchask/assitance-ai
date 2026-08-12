from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/commercial_ai"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    GENERAL_MODEL: str = "gemma4:12b-mlx"
    HEAVY_MODEL: str = "gemma4:26b-mlx"
    CODING_MODEL: str = "qwen3-coder:30b"
    REASONING_MODEL: str = "deepseek-r1:32b"
    VISION_MODEL: str = "qwen3-vl:8b"
    FAST_MODEL: str = "qwen3:8b"
    
    OPENROUTER_API_KEY: Optional[str] = None
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    JWT_SECRET: str = "your_jwt_secret_here"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    class Config:
        env_file = __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), ".env")
        env_file_encoding = 'utf-8'

# Manually override with dotenv to ensure .env takes precedence over stale shell variables
from dotenv import load_dotenv
import os
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path, override=True)

settings = Settings(
    OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY", None),
    GENERAL_MODEL=os.getenv("GENERAL_MODEL", "gemma4:12b-mlx"),
    HEAVY_MODEL=os.getenv("HEAVY_MODEL", "gemma4:12b-mlx"),
    REASONING_MODEL=os.getenv("REASONING_MODEL", "gemma4:12b-mlx"),
    CODING_MODEL=os.getenv("CODING_MODEL", "qwen3:14b"),
    VISION_MODEL=os.getenv("VISION_MODEL", "qwen3:14b"),
    FAST_MODEL=os.getenv("FAST_MODEL", "qwen3:14b")
)


def cors_origins() -> list[str]:
    return [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
