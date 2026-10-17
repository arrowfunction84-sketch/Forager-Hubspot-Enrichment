import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    forager_api_key: str = os.getenv("FORAGER_API_KEY", "default")
    forager_account_id: str = os.getenv("FORAGER_ACCOUNT_ID", "default")
    hubspot_access_token: str = os.getenv("HUBSPOT_ACCESS_TOKEN", "default")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "default")
    forager_base_url: str = "https://api-v2.forager.ai"

def get_settings() -> Settings:
    return Settings()
