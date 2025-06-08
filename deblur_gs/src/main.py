import asyncio
import json
import subprocess
import time

import websockets

from dto import (
    UploadDTO,
    StartSessionDTO,
    CancelSessionDTO,
    PLYUrlResponseDTO,
    BaseEndSessionDTO,
)
from envs import SERVER_URL, VISDOM_HOST, VISDOM_PORT, WS_KEY
from service import (
    ply_url_response_service,
    start_session_service,
    cancel_session_service,
    upload_service,
    end_session_service,
)
from utils import generate_hmac_signature


async def router():
    ts = str(int(time.time()))
    sig = generate_hmac_signature(ts, WS_KEY)
    url = f"{SERVER_URL}?ts={ts}&sig={sig}"

    async with websockets.connect(url) as websocket:
        from globals import set_client

        set_client(websocket)

        print("Connected")

        async for request in websocket:
            try:
                message = json.loads(request)
                print(f"Received {message}")
                dto_type = message["type"]
                dto_data = message.get("data", {})

                if dto_type == StartSessionDTO.type:
                    start_session_service(StartSessionDTO.parse_obj(dto_data))

                elif dto_type == CancelSessionDTO.type:
                    await cancel_session_service(
                        CancelSessionDTO.parse_obj(dto_data)
                    )

                elif dto_type == UploadDTO.type:
                    await upload_service(UploadDTO.parse_obj(dto_data))

                elif dto_type == PLYUrlResponseDTO.type:
                    await ply_url_response_service(
                        PLYUrlResponseDTO.parse_obj(dto_data)
                    )
                elif dto_type == BaseEndSessionDTO.type:
                    end_session_service(BaseEndSessionDTO.parse_obj(dto_data))
                else:
                    print(f"Unknown DTO type: {dto_type}")
            except Exception as e:
                print(f"[Router] Message handling failed: {e}")


async def keep_running():
    retry_delay = 5  # seconds
    while True:
        try:
            await router()
        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            print(
                f"[WebSocket] Disconnected: {e}. Retrying in {retry_delay}s..."
            )
            await asyncio.sleep(retry_delay)
        except Exception as e:
            print(
                f"[WebSocket] Unexpected error: {e}. Retrying in {retry_delay}s..."
            )
            await asyncio.sleep(retry_delay)


if __name__ == "__main__":
    subprocess.Popen(
        [
            "python",
            "-m",
            "visdom.server",
            "-p",
            str(VISDOM_PORT),
            "--host",
            VISDOM_HOST,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Visdom server started at http://{VISDOM_HOST}:{VISDOM_PORT}")

    asyncio.run(keep_running())
