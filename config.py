import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
NOTIFY_CHANNEL_ID = int(
    os.getenv("NOTIFY_CHANNEL_ID")
)