from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "ATT&CK Gap Analysis API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ATTACK_TAXII_SERVER: str = "https://cti-taxii.mitre.org/taxii/"
    ATTACK_COLLECTION_ID: str = "95ecc380-afe9-11e4-9b6c-751b66dd541e"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    class Config:
        env_file = ".env"
@lru_cache()
def get_settings():
    return Settings()
    