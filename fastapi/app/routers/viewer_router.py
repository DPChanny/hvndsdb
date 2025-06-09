import json
import uuid

from fastapi import APIRouter, WebSocket
from fastapi.logger import logger
from starlette.requests import ClientDisconnect

from dtos.viewer_dto import (
    StartSessionRequestDTO,
    EndSessionRequestDTO,
    FrameDTO,
)
from managers import viewer_manager
from services.viewer_service import (
    start_session_request_service,
    end_session_request_service,
    frame_service,
)

viewer_router = APIRouter()


@viewer_router.websocket("")
async def viewer_route(websocket: WebSocket):
    client_id = "viewer-" + websocket.client.host + "-" + uuid.uuid4().hex
    await viewer_manager.start_client(client_id, websocket)

    try:
        while True:
            message = json.loads(await websocket.receive_text())
            dto_type = message["type"]
            dto_data = message.get("data", {})

            if dto_type == StartSessionRequestDTO.type:
                await start_session_request_service(
                    client_id, StartSessionRequestDTO.model_validate(dto_data)
                )
            elif dto_type == EndSessionRequestDTO.type:
                await end_session_request_service(
                    client_id, EndSessionRequestDTO.model_validate(dto_data)
                )
            elif dto_type == FrameDTO.type:
                await frame_service(
                    client_id, FrameDTO.model_validate(dto_data)
                )
            else:
                logger.error(f"Unknown DTO type {dto_type}")
    except ClientDisconnect:
        pass
    except Exception as e:
        logger.error(f"Unhandled Exception {e}")
    finally:
        await viewer_manager.end_client(client_id)
