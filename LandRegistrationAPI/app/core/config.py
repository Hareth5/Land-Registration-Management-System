from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str

    DATABASE_NAME: str

    MONGODB_HOST: str
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_APP_NAME: str

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    ALGORITHM: str

    @property
    def MONGODB_URL(self):
        return (
            f"mongodb+srv://{self.MONGODB_USER}:"
            f"{self.MONGODB_PASSWORD}@"
            f"{self.MONGODB_HOST}/"
            f"{self.DATABASE_NAME}"
            f"?retryWrites=true&w=majority"
            f"&appName={self.MONGODB_APP_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
