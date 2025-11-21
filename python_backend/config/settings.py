"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    # Server
    port: int = 3000
    node_env: Literal['development', 'production', 'test'] = 'development'
    
    # Database
    database_url: str
    database_pool_size: int = 20
    
    # Redis
    redis_url: str
    
    # Storage
    s3_endpoint: str
    s3_bucket: str
    s3_region: str
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    
    # Secrets Manager
    secrets_manager_type: Literal['vault', 'aws', 'gcp'] = 'vault'
    secrets_manager_url: str
    
    # Virus Scanning
    clamav_host: str
    clamav_port: int
    
    # Event Bus
    event_bus_type: Literal['rabbitmq', 'eventbridge'] = 'rabbitmq'
    event_bus_url: str
    
    # Rate Limiting
    upload_rate_limit: int = 5
    upload_rate_window: int = 3600
    
    # File Limits
    max_csv_rows: int = 500
    max_mp4_size: int = 104857600  # 100MB
    max_doc_size: int = 104857600  # 100MB
    
    # Presigned URL
    presigned_url_expiry: int = 900  # 15 minutes
    
    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60
    
    # Evaluation Pipeline
    evaluation_batch_size: int = 1  # Reduced to 1 for free tier rate limits
    max_file_workers: int = 1
    max_retries: int = 3
    evaluation_timeout: int = 120
    gemini_api_key: str | None = None
    
    # Supported file extensions for extraction
    @property
    def supported_file_extensions(self) -> list:
        return ['.pdf', '.pptx', '.docx', '.mp4', '.mov', '.avi', '.jpg', '.jpeg', '.png', '.webp']
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
