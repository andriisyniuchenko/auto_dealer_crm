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
    WEBSITE_API_KEY: str = "change-me"

    class Config:
        env_file = ".env"


settings = Settings()