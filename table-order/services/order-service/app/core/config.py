from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "order_service"
    db_password: str = "password"
    db_name: str = "order_db"
    db_pool_size: int = 10

    # External Services
    menu_service_url: str = "http://menu-service:8000"
    store_service_url: str = "http://store-service:8002"
    menu_service_timeout: float = 5.0
    store_service_timeout: float = 3.0

    # SSE
    sse_heartbeat_interval: int = 30  # 초

    # Service
    service_name: str = "order-service"
    debug: bool = False

    class Config:
        env_prefix = "ORDER_"


settings = Settings()
