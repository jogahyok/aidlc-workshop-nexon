from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "menu_service"
    db_password: str = "password"
    db_name: str = "menu_db"
    db_pool_size: int = 10

    # S3
    s3_bucket_name: str = "table-order-menu-images"
    s3_region: str = "ap-northeast-2"
    s3_presigned_url_expiry: int = 600  # 10분

    # Service
    service_name: str = "menu-service"
    debug: bool = False

    class Config:
        env_prefix = "MENU_"


settings = Settings()
