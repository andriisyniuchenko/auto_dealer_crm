from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FIRST_ADMIN_EMAIL: str = "admin@demo.com"
    FIRST_ADMIN_PASSWORD: str = "admin123"
    WEBSITE_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()