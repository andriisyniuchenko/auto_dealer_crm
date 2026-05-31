from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_ADMIN_FIRST_NAME: str
    FIRST_ADMIN_LAST_NAME: str
    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str
    POSTGRES_PASSWORD: str
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    WEBSITE_API_KEY: str
    COOKIE_SECURE: bool = False

    class Config:
        env_file = ".env"


settings = Settings()