from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    llm_temperature: float = 0
    database_url: str
    agent_max_steps: int = 12
    agent_max_replans: int = 3
    agent_step_timeout_seconds: int = 60

settings = Settings()
