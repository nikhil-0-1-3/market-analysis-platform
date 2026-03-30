from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-trading-platform"
    env: str = "dev"
    api_port: int = 8000
    postgres_dsn: str = "postgresql+psycopg://postgres:postgres@localhost:5432/trading"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap: str = "localhost:9092"
    opensearch_url: str = "http://localhost:9200"
    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "trading-artifacts"
    jwt_secret: str = "change-me"
    mlflow_tracking_uri: str = "http://localhost:5000"

    connectors_refresh_minutes: int = 3
    connectors_default_limit: int = 20
    connectors_india_only: bool = True

    x_bearer_token: str | None = None
    x_query: str = "(NSE OR BSE OR NIFTY OR SENSEX OR RBI OR Indian stocks) lang:en -is:retweet"


settings = Settings()
