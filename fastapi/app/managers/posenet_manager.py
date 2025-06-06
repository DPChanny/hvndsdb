import asyncio
from typing import Optional, Dict
import torch

from dtos.base_dto import BaseWebSocketDTO
from dtos.posenet_dto import CancelSessionDTO, StartSessionDTO, AnalysisSessionDTO
from managers.web_socket_manager import (
    WebSocketManager,
    WebsocketClient,
    WebsocketSession,
)
from utils.s3 import get_presigned_download_url, is_key_exists
from libs.posenet.posenet.model import PoseNet


class PosenetClient(WebsocketClient):
    def get_session_count(self) -> int:
        return len(self._sessions)

    async def start_session(
            self, building_id: str, dto: BaseWebSocketDTO[StartSessionDTO]
    ):
        await super().start_session(building_id, dto)

    async def start_analysis_session(
            self, session_id: str, dto: BaseWebSocketDTO[AnalysisSessionDTO]
    ):
        await super().start_session(session_id, dto)

    async def cancel_session(self, building_id: str):
        await self.get_session(building_id).put_progress(None)
        await self.send(
            BaseWebSocketDTO[CancelSessionDTO](
                data=CancelSessionDTO(session_id=building_id)
            ),
        )

    async def end_session(self, building_id: str, dto: BaseWebSocketDTO):
        await self.get_session(building_id).put_progress(None)
        await super().end_session(building_id, dto)


class PosenetSession(WebsocketSession):
    def __init__(self, session_id: str, client: PosenetClient):
        super().__init__(session_id, client)
        self._progress: asyncio.Queue = asyncio.Queue()
        self._analysis_queue: asyncio.Queue = asyncio.Queue()
        self._is_analyzing: bool = False
        self.set_ready()

    async def put_progress(self, progress: str | None):
        await self._progress.put(progress)

    async def get_progress(self):
        return await self._progress.get()

    async def put_analysis_frame(self, frame_data: bytes):
        await self._analysis_queue.put(frame_data)

    async def get_analysis_frame(self):
        return await self._analysis_queue.get()

    def set_analyzing(self, is_analyzing: bool):
        self._is_analyzing = is_analyzing

    def is_analyzing(self) -> bool:
        return self._is_analyzing


class PosenetManager(WebSocketManager):
    def __init__(self):
        super().__init__(PosenetClient, PosenetSession)
        self._model: Optional[PoseNet] = None
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._model_lock = asyncio.Lock()

    def get_client(self, client_id: str) -> PosenetClient:
        return super().get_client(client_id)

    async def load_model(self, model_path: str):
        async with self._model_lock:
            if self._model is None:
                self._model = PoseNet()
                self._model.load_state_dict(torch.load(model_path, map_location=self._device))
                self._model.to(self._device)
                self._model.eval()

    async def get_model(self) -> PoseNet:
        async with self._model_lock:
            if self._model is None:
                raise RuntimeError("Model not loaded")
            return self._model

    async def start_analysis_session(self, session_id: str) -> str:
        if not self._clients:
            raise LookupError("No clients connected")

        selected_client_id = next(iter(self._clients.keys()))
        for client_id in self._clients.keys():
            if self.get_client(client_id).has_session(session_id):
                return client_id

            if (
                    self.get_client(client_id).get_session_count()
                    < self.get_client(selected_client_id).get_session_count()
            ):
                selected_client_id = client_id

        await self.get_client(selected_client_id).start_analysis_session(
            session_id,
            BaseWebSocketDTO[AnalysisSessionDTO](
                data=AnalysisSessionDTO(
                    session_id=session_id,
                    status="ready"
                ),
            ),
        )

        return selected_client_id

    async def start_session(self, building_id: str) -> str:
        if not self._clients:
            raise LookupError("No clients connected")

        selected_client_id = next(iter(self._clients.keys()))
        for client_id in self._clients.keys():
            if self.get_client(client_id).has_session(building_id):
                return client_id

            if (
                    self.get_client(client_id).get_session_count()
                    < self.get_client(selected_client_id).get_session_count()
            ):
                selected_client_id = client_id

        await self.get_client(selected_client_id).start_session(
            building_id,
            BaseWebSocketDTO[StartSessionDTO](
                data=StartSessionDTO(
                    session_id=building_id,
                    frames_url=get_presigned_download_url(
                        building_id + "/frames.zip"
                    ),
                    colmap_url=get_presigned_download_url(
                        building_id + "/colmap.zip"
                    ),
                    deblur_gs_url=(
                        get_presigned_download_url(
                            building_id + "/deblur_gs.zip"
                        )
                        if is_key_exists(building_id + "/deblur_gs.zip")
                        else None
                    ),
                ),
            ),
        )

        return selected_client_id

    async def cancel_session(self, building_id: str):
        for client in self._clients.values():
            if client.has_session(building_id):
                await client.cancel_session(building_id)
                return

        raise LookupError(f"No session found {building_id}")
