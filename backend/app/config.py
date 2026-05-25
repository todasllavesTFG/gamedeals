from pathlib import Path

from dotenv import load_dotenv
import os

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

RAWG_API_KEY = os.getenv("RAWG_API_KEY", "")
