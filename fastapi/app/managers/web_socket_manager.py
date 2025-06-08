import asyncio
from typing import Dict, Type, TypeVar

from fastapi import WebSocket
from fastapi.logger import logger
from starlette.websockets import WebSocketState

from dtos.base_dto import (
    BaseWebSocketDTO,
)

S = TypeVar("S", bound="WebsocketSession")
C = TypeVar("C", bound="WebsocketClient")


class WebsocketClient:
    def __init__(self, client_id, websocket: WebSocket, session_type: Type[S]):
        self._client_id: str = client_id
        self._websocket = websocket
        self._sessions: Dict[str, S] = {}
        self._session_type = session_type

    async def send(self, dto: BaseWebSocketDTO):
        json_str = dto.model_dump(mode="json")
        logger.debug(f"Sending\n{json_str}")
        try:
            await self._websocket.send_json(json_str)
        except Exception as e:
            logger.warning(f"Send Failed\n{e}")

    async def start_session(self, session_id: str, dto: BaseWebSocketDTO):
        if session_id in self._sessions:
            raise LookupError(f"Session {session_id} already exists")

        logger.info(f"Starting session {session_id}")

        self._sessions[session_id] = self._session_type(session_id, self)
        await self.send(dto)

    def has_session(self, session_id: str) -> bool:
        return session_id in self._sessions

    def get_session(self, session_id: str) -> S:
        session = self._sessions.get(session_id)
        if not session:
            raise LookupError(f"No session found {session_id}")

        return session

    async def end_session(self, session_id: str, dto: BaseWebSocketDTO):
        logger.info(f"Ending session {session_id}")

        session = self.get_session(session_id)
        session.set_ended()
        await self.send(dto)

        self._sessions.pop(session_id)

    async def end(self):
        if self._websocket.client_state != WebSocketState.DISCONNECTED:
            await self._websocket.close()
        for session in self._sessions.values():
            session.set_ended()
        self._sessions.clear()


class WebsocketSession:
    def __init__(self, session_id: str, client: C):
        self._session_id: str = session_id
        self._client: C = client
        self._ready: asyncio.Event = asyncio.Event()
        self._end: asyncio.Event = asyncio.Event()

    def set_ready(self):
        self._ready.set()

    def set_ended(self):
        self._end.set()

    def is_ready(self) -> bool:
        return self._ready.is_set()

    def is_ended(self) -> bool:
        return self._end.is_set()

    async def wait_ready(self):
        await self._ready.wait()

    async def wait_ended(self):
        await self._end.wait()


class WebSocketManager:
    def __init__(self, client_type: Type[C], session_type: Type[S]):
        self._clients: Dict[str, C] = {}
        self._client_type = client_type
        self._session_type = session_type

    async def start_client(self, client_id: str, websocket: WebSocket):
        if client_id in self._clients:
            raise LookupError(f"Client {client_id} already exists")

        logger.info(f"Accepting {client_id}")

        await websocket.accept()
        self._clients[client_id] = self._client_type(
            client_id, websocket, self._session_type
        )

    def get_client(self, client_id: str) -> C:
        client = self._clients.get(client_id)
        if not client:
            raise LookupError(f"No client found {client_id}")

        return client

    async def end_client(self, client_id: str):
        logger.info(f"Ending client {client_id}")

        client = self.get_client(client_id)
        await client.end()

        self._clients.pop(client_id, None)
