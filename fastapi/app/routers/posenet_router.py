import json
import uuid
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.logger import logger
from starlette.requests import ClientDisconnect

from dtos.posenet_dto import (
    StartSessionDTO,
    AnalysisSessionDTO,
    AnalysisFrameDTO,
    AnalysisCompleteDTO,
    AnalysisErrorDTO,
    CancelSessionDTO,
    ProgressDTO,
)
from managers import posenet_manager
from services import posenet_service
from utils.authorization import is_valid_timestamp, verify_hmac

posenet_router = APIRouter()


@posenet_router.websocket("/ws/analysis/{session_id}")
async def analysis_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    client_id = None
    
    try:
        # 클라이언트 연결 및 세션 시작
        client_id = await posenet_manager.connect(websocket)
        await posenet_service.start_analysis_session(client_id, session_id)
        
        # 세션 시작 상태 전송
        await websocket.send_json(
            AnalysisSessionDTO(
                session_id=session_id,
                status="ready"
            ).dict()
        )
        
        while True:
            # 메시지 수신 및 처리
            data: Dict[str, Any] = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "analysis_frame":
                # 분석 시작 상태 전송
                await websocket.send_json(
                    AnalysisSessionDTO(
                        session_id=session_id,
                        status="analyzing"
                    ).dict()
                )
                
                dto = AnalysisFrameDTO(**data["data"])
                await posenet_service.process_frame(client_id, dto)
                
            elif message_type == "analysis_complete":
                dto = AnalysisCompleteDTO(**data["data"])
                await posenet_service.complete_analysis(client_id, dto)
                
                # 분석 완료 상태 전송
                await websocket.send_json(
                    AnalysisSessionDTO(
                        session_id=session_id,
                        status="completed"
                    ).dict()
                )
                break
                
            elif message_type == "error":
                dto = AnalysisErrorDTO(**data["data"])
                await posenet_service.complete_analysis(
                    client_id,
                    AnalysisCompleteDTO(
                        session_id=dto.session_id,
                        total_frames=0,
                        processed_frames=0,
                        results=[],
                        error_message=dto.error_message
                    )
                )
                
                # 에러 상태 전송
                await websocket.send_json(
                    AnalysisSessionDTO(
                        session_id=session_id,
                        status="error"
                    ).dict()
                )
                break
                
    except WebSocketDisconnect:
        if client_id:
            await posenet_manager.disconnect(client_id)
    except Exception as e:
        if client_id:
            await websocket.send_json(
                AnalysisErrorDTO(
                    session_id=session_id,
                    error_message=str(e)
                ).dict()
            )
            await posenet_manager.disconnect(client_id)


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

            if dto_type == StartSessionDTO.type:
                await posenet_service.start_analysis_session(
                    client_id=client_id,
                    session_id=dto_data["session_id"]
                )
                # 세션 시작 상태 전송
                await websocket.send_json(
                    AnalysisSessionDTO(
                        session_id=dto_data["session_id"],
                        status="ready"
                    ).dict()
                )
            elif dto_type == AnalysisFrameDTO.type:
                # 분석 시작 상태 전송
                await websocket.send_json(
                    AnalysisSessionDTO(
                        session_id=dto_data["session_id"],
                        status="analyzing"
                    ).dict()
                )
                await posenet_service.process_frame(
                    client_id=client_id,
                    dto=AnalysisFrameDTO.model_validate(dto_data)
                )
            elif dto_type == AnalysisCompleteDTO.type:
                await posenet_service.complete_analysis(
                    client_id=client_id,
                    dto=AnalysisCompleteDTO.model_validate(dto_data)
                )
                # 분석 완료 상태 전송
                await websocket.send_json(
                    AnalysisSessionDTO(
                        session_id=dto_data["session_id"],
                        status="completed"
                    ).dict()
                )
            elif dto_type == CancelSessionDTO.type:
                await posenet_manager.cancel_session(dto_data["session_id"])
                # 세션 취소 상태 전송
                await websocket.send_json(
                    AnalysisSessionDTO(
                        session_id=dto_data["session_id"],
                        status="error"
                    ).dict()
                )
            elif dto_type == ProgressDTO.type:
                await posenet_service.progress_service(
                    client_id=client_id,
                    dto=ProgressDTO.model_validate(dto_data)
                )
            else:
                logger.warning(f"Unknown DTO type {dto_type}")
    except ClientDisconnect:
        pass
    except Exception as e:
        logger.error(f"Unhandled Exception {e}")
    finally:
        await posenet_manager.end_client(client_id)
