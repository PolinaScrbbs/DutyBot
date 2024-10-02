from dotenv import load_dotenv
import os

os.environ.pop("BOT_TOKEN", None)
os.environ.pop("API_URL", None)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
