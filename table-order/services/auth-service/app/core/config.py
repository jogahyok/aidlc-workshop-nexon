from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "auth_user"
    db_password: str = "change_me"
    db_name: str = "auth_db"

    # JWT
    jwt_secret_key: str = "change_me_to_a_secure_random_string_at_least_32_chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 16

    # Rate Limiting
    login_max_attempts: int = 5
    login_lockout_minutes: int = 15

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
