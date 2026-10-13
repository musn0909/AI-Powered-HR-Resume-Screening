
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name
        )


settings = Settings(
    db_host=os.getenv("DB_HOST", "localhost"),
    db_port=int(os.getenv("DB_PORT", "5432")),
    db_name=os.environ["DB_NAME"],
    db_user=os.environ["DB_USER"],
    db_password=os.environ["DB_PASSWORD"],
    secret_key=os.environ["SECRET_KEY"],
    algorithm=os.getenv("ALGORITHM", "HS256"),
    access_token_expire_minutes=int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
)
