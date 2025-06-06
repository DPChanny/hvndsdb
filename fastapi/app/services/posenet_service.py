from dtos.posenet_dto import (
    AnalysisSessionDTO,
    AnalysisFrameDTO,
    AnalysisResultDTO,
    AnalysisErrorDTO,
    AnalysisCompleteDTO,
    UploadDTO,
    UploadCompleteDTO,
    CompleteDTO,
    ProgressDTO,
    PLYUrlRequestDTO,
    PLYUrlResponseDTO,
    CancelSessionCompleteDTO,
)
from managers import posenet_manager
from managers.posenet_manager import PosenetSession
from utils.s3 import get_presigned_upload_url


async def start_analysis_session(client_id: str, session_id: str):
    try:
        session: PosenetSession = posenet_manager.get_client(client_id).get_session(session_id)
        session.set_analyzing(True)
        
        await posenet_manager.get_client(client_id).send(
            AnalysisSessionDTO(
                session_id=session_id,
                status="ready"
            ).dict()
        )
    except Exception as e:
        await posenet_manager.get_client(client_id).send(
            AnalysisErrorDTO(
                session_id=session_id,
                error_message=str(e)
            ).dict()
        )


async def process_frame(client_id: str, dto: AnalysisFrameDTO):
    try:
        session: PosenetSession = posenet_manager.get_client(client_id).get_session(dto.session_id)
        
        ## TODO: 실제 프레임 처리 로직 구현 => 추론 세션과 함께 구현 필요
        await posenet_manager.get_client(client_id).send(
            AnalysisResultDTO(
                session_id=dto.session_id,
                frame_index=dto.frame_index,
                pose={
                    # 'x': 0.0,
                    # 'y': 0.0,
                    # 'z': 0.0,
                    # 'qx': 0.0,
                    # 'qy': 0.0,
                    # 'qz': 0.0,
                    # 'qw': 1.0
                },
                confidence=1.0
            ).dict()
        )
    except Exception as e:
        await posenet_manager.get_client(client_id).send(
            AnalysisErrorDTO(
                session_id=dto.session_id,
                error_message=str(e)
            ).dict()
        )


async def complete_analysis(client_id: str, dto: AnalysisCompleteDTO):
    try:
        session: PosenetSession = posenet_manager.get_client(client_id).get_session(dto.session_id)
        session.set_analyzing(False)
        
        await posenet_manager.get_client(client_id).send(dto.dict())
    except Exception as e:
        await posenet_manager.get_client(client_id).send(
            AnalysisErrorDTO(
                session_id=dto.session_id,
                error_message=str(e)
            ).dict()
        )


async def upload_service(client_id: str, building_id: str):
    await posenet_manager.get_client(client_id).send(
        UploadDTO(
            session_id=building_id,
            deblur_gs_url=get_presigned_upload_url(
                # building_id + "/deblur_gs.zip",
                # "application/zip",
            ),
        ).dict()
    )


async def complete_service(client_id: str, dto: CompleteDTO):
    await upload_service(client_id, dto.session_id)


async def upload_complete_service(client_id: str, dto: UploadCompleteDTO):
    await posenet_manager.get_client(client_id).end_session(dto.session_id)


async def progress_service(client_id: str, dto: ProgressDTO):
    session: PosenetSession = posenet_manager.get_client(client_id).get_session(dto.session_id)
    await session.put_progress(dto.progress)


async def ply_url_request_service(client_id: str, dto: PLYUrlRequestDTO):
    await posenet_manager.get_client(client_id).send(
        PLYUrlResponseDTO(
            session_id=dto.session_id,
            ply_url=get_presigned_upload_url(
                # dto.session_id + "/point_cloud.ply",
                # "application/octet-stream",
            ),
        ).dict()
    )


async def cancel_complete_service(client_id: str, dto: CancelSessionCompleteDTO):
    await upload_service(client_id, dto.session_id)
