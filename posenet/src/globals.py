import asyncio
import base64
import os
import uuid
from io import BytesIO
from typing import Dict, Optional

import posenet.utils.predict_pose
from PIL import Image
from posenet.model import PoseNet

from dto import BaseWebSocketDTO, ProgressDTO, SixDOFDTO
from envs import TEMP
from tasks import download_task


class PosenetSession:
    def __init__(self, session_id: str):
        self._session_id = session_id
        self._downloader_task: Optional[asyncio.Task] = None
        self._train_task: Optional[asyncio.Task] = None
        self._model: Optional[PoseNet] = None

    async def update_6dof(self, px, py, pz, rx, ry, rz, rw):
        await Globals.posenet_client.send(
            BaseWebSocketDTO[SixDOFDTO](
                data=SixDOFDTO(
                    session_id=self._session_id,
                    px=px,
                    py=py,
                    pz=pz,
                    rx=rx,
                    ry=ry,
                    rz=rz,
                    rw=rw,
                )
            )
        )

    async def update_progress(self, progress: str):
        await Globals.posenet_client.send(
            BaseWebSocketDTO[ProgressDTO](
                data=ProgressDTO(session_id=self._session_id, progress=progress)
            )
        )

    def load_model(self, model_path):
        self._model = posenet.utils.predict_pose.load_model(model_path)

    async def infer_frame(self, frame: str):
        if frame.startswith("data:image"):
            frame = frame.split(",")[1]

        img_data = base64.b64decode(frame)
        image = Image.open(BytesIO(img_data))

        temp = uuid.uuid4().hex + ".jpg"

        image.save(os.path.join(TEMP, self._session_id, "posenet", temp))

        await self.update_6dof(
            *posenet.utils.predict_pose.predict(
                self._model,
                os.path.join(TEMP, self._session_id, "posenet", temp),
            )
        )

    def start_downloader_task(
            self,
            frames_url: str,
            colmap_url: str,
            posenet_url: Optional[str] = None,
    ):

        self._downloader_task = asyncio.create_task(
            download_task.run(
                self._session_id,
                frames_url,
                colmap_url,
                posenet_url,
            )
        )

    def start_train_task(self):
        from tasks import train_task

        self._train_task = asyncio.create_task(
            train_task.run(
                self._session_id,
                os.path.join(TEMP, self._session_id, "colmap"),
                os.path.join(TEMP, self._session_id, "frames"),
                os.path.join(TEMP, self._session_id, "posenet"),
            )
        )

    async def cancel_train_task(self):
        if self._train_task:
            self._train_task.cancel()
            try:
                await self._train_task
            except asyncio.CancelledError:
                pass
            self._train_task = None


class PosenetClient:
    def __init__(self, websocket):
        self._sessions: Dict[str, PosenetSession] = {}
        self._websocket = websocket

    def start_session(self, session_id: str) -> PosenetSession:
        if session_id in self._sessions:
            raise LookupError(f"Session {session_id} already exists")

        session = PosenetSession(session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> PosenetSession:
        session = self._sessions.get(session_id)
        if not session:
            raise LookupError(f"No session found {session_id}")
        return session

    def end_session(self, session_id: str):
        if session_id not in self._sessions:
            raise LookupError(f"No session found {session_id}")
        self._sessions.pop(session_id)

    async def send(self, dto: BaseWebSocketDTO):
        print(f"Sending {dto.json()}")
        await self._websocket.send(dto.json())


class Globals:
    posenet_client: Optional[PosenetClient] = None


def set_client(websocket):
    Globals.posenet_client = PosenetClient(websocket)


def get_client() -> PosenetClient:
    if Globals.posenet_client is None:
        raise LookupError("PosenetClient is not set")
    return Globals.posenet_client
