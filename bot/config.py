from dotenv import load_dotenv
import os

os.environ.pop("DATABASE_URL", None)
os.environ.pop("SECRET_KEY", None)

os.environ.pop("BOT_TOKEN", None)
os.environ.pop("DOWNLOAD_FOLDER", None)
os.environ.pop("API_URL", None)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")
API_URL = os.getenv("API_URL")
