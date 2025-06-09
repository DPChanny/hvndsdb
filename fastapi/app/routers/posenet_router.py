import json
import uuid

from fastapi import APIRouter, WebSocket
from fastapi.logger import logger
from starlette.requests import ClientDisconnect

from dtos.base_dto import BaseSessionReadyDTO
from dtos.posenet_dto import (
    ProgressDTO,
    UploadCompleteDTO,
    CancelSessionCompleteDTO,
    CompleteDTO,
    SixDOFDTO,
)
from managers import posenet_manager
from services.posenet_service import (
    complete_service,
    cancel_complete_service,
    progress_service,
    upload_complete_service,
    session_ready_service,
    six_dof_service,
)
from utils.authorization import is_valid_timestamp, verify_hmac

posenet_router = APIRouter()


@posenet_router.websocket("")
async def posenet_route(websocket: WebSocket):
    ts = websocket.query_params.get("ts")
    sig = websocket.query_params.get("sig")

    if not ts or not sig:
        await websocket.close(code=4001)
        return
    if not is_valid_timestamp(ts):
        await websocket.close(code=4002)
        return
    if not verify_hmac(ts, sig):
        await websocket.close(code=4003)
        return

    client_id = "posenet-" + websocket.client.host + "-" + uuid.uuid4().hex
    await posenet_manager.start_client(client_id, websocket)

    try:
        while True:
            message = json.loads(await websocket.receive_text())
            dto_type = message["type"]
            dto_data = message.get("data", {})

            if dto_type == CompleteDTO.type:
                await complete_service(
                    client_id=client_id,
                    dto=CompleteDTO.model_validate(dto_data),
                )
            elif dto_type == BaseSessionReadyDTO.type:
                session_ready_service(
                    client_id=client_id,
                    dto=BaseSessionReadyDTO.model_validate(dto_data),
                )
            elif dto_type == UploadCompleteDTO.type:
                await upload_complete_service(
                    client_id=client_id,
                    dto=UploadCompleteDTO.model_validate(dto_data),
                )
            elif dto_type == SixDOFDTO.type:
                await six_dof_service(
                    client_id=client_id, dto=SixDOFDTO.model_validate(dto_data)
                )
            elif dto_type == ProgressDTO.type:
                await progress_service(
                    client_id=client_id,
                    dto=ProgressDTO.model_validate(dto_data),
                )
            elif dto_type == CancelSessionCompleteDTO.type:
                await cancel_complete_service(
                    client_id=client_id,
                    dto=CancelSessionCompleteDTO.model_validate(dto_data),
                )
            else:
                logger.warning(f"Unknown DTO type {dto_type}")
    except ClientDisconnect:
        pass
    except Exception as e:
        logger.error(f"Unhandled Exception {e}")
    finally:
        await posenet_manager.end_client(client_id)
