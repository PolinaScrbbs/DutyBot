from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        os.environ.pop("BOT_TOKEN", None)
        os.environ.pop("NGROK_URL", None)
        os.environ.pop("DOWNLOAD_FOLDER", None)
        os.environ.pop("API_URL", None)

        load_dotenv()

        self.bot_token = os.getenv("BOT_TOKEN")
        self.ngrok_url = os.getenv("NGROK_URL")
        self.api_url = os.getenv("API_URL")
        self.media_folder = os.getenv("MEDIA_FOLDER")


config = Config()
