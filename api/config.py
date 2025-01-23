from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        os.environ.pop("HOST", None)
        os.environ.pop("PORT", None)
        os.environ.pop("DB_NAME", None)
        os.environ.pop("DB_USER", None)
        os.environ.pop("DB_PASSWORD", None)

        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("TOKEN_LIFETIME", None)

        load_dotenv()

        # api
        self.secret_key = os.getenv("SECRET_KEY")
        self.token_lifetime = int(os.getenv("TOKEN_LIFETIME"))

        # database
        self.host = os.getenv("HOST", "localhost")
        self.port = os.getenv("PORT", "5432")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_user_password = os.getenv("DB_PASSWORD")


        self.database_url = f"postgresql+asyncpg://{self.db_user}:{self.db_user_password}@{self.host}:{self.port}/{self.db_name}"

config = Config()