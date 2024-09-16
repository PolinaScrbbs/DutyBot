from dotenv import load_dotenv
import os

os.environ.pop("DATABASE_URL", None)
os.environ.pop("SECRET_KEY", None)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
