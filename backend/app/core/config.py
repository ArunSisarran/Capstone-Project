from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    frontend_url: str = 'https://localhost:5173'
    vision_url: str = 'http://localhost:8001'  # serve.py address -Arun
    password_reset_expire_minutes: int = 30

    email_backend: str = "console"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 597
    smtp_username: str = ""
    smtp_password: str = ""
    mail_from: str = ""

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"


settings = Settings()