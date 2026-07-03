from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://jobpilot_user:jobpilot_secure_password@localhost:5432/jobpilot_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENROUTER_API_KEY: str = ""
    ENV: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
