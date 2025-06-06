from typing import Optional, List, Dict, Any, ClassVar

from dtos.base_dto import (
    BaseStartSessionDTO,
    BaseSessionDataDTO,
)


class StartSessionDTO(BaseStartSessionDTO):
    colmap_url: str
    deblur_gs_url: Optional[str] = None


class CancelSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_session"
    session_id: str


class AnalysisSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "analysis_session"
    session_id: str
    status: str  # ready, analyzing, completed, error


class AnalysisFrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "analysis_frame"
    session_id: str
    frame_data: bytes
    frame_index: int


class AnalysisResultDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "analysis_result"
    session_id: str
    frame_index: int
    pose: Dict[str, float]  # x, y, z, qx, qy, qz, qw
    confidence: float


class AnalysisErrorDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "analysis_error"
    session_id: str
    error_message: str


class AnalysisCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "analysis_complete"
    session_id: str
    total_frames: int
    processed_frames: int
    results: List[AnalysisResultDTO]


class UploadDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload"
    session_id: str
    deblur_gs_url: str


class UploadCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload_complete"
    session_id: str


class CompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "complete"
    session_id: str


class ProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "progress"
    session_id: str
    progress: str


class PLYUrlRequestDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "ply_url_request"
    session_id: str


class PLYUrlResponseDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "ply_url_response"
    session_id: str
    ply_url: str


class CancelSessionCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_session_complete"
    session_id: str
