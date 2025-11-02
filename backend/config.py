from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://eqip:eqip@localhost:5432/eqip"
    jwt_secret: str = "devsecret"
    api_base: str = "http://localhost:8000"
    vector_db_url: str = "http://localhost:6333"
    openai_api_key: str | None = None
    minio_endpoint: str = "http://localhost:9000"
    minio_bucket: str = "eqip"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    
    # RAG Configuration
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072
    chunk_size: int = 1000
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
