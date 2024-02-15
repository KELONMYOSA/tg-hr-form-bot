from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str

    EMAIL_SMTP_HOST: str
    EMAIL_SMTP_PORT: int
    EMAIL_SENDER: str
    EMAIL_RECIPIENT: str


settings = Settings()
