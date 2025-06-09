import os

from dotenv import load_dotenv

load_dotenv(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
)

FASTAPI_HOST = os.getenv("FASTAPI_HOST")
FASTAPI_PORT = os.getenv("FASTAPI_PORT")
WS_KEY = os.getenv("WS_KEY")

TEMP = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp"))
SERVER_URL = f"ws://{FASTAPI_HOST}:{FASTAPI_PORT}/ws/posenet"
