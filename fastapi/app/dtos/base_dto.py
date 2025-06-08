from datetime import datetime
from typing import Generic, Optional, TypeVar, ClassVar

from pydantic import BaseModel, model_validator


class BaseDataDTO(BaseModel):
    def get_type(self) -> Optional[str]:
        return getattr(self.__class__, "type", None)


T = TypeVar("T", bound=BaseDataDTO)


class BaseWebSocketDTO(BaseModel, Generic[T]):
    data: Optional[T] = None
    type: str = ""

    @model_validator(mode="after")
    def set_type_from_data(self) -> "BaseWebSocketDTO":
        if self.type:
            return self
        if self.data:
            self.type = self.data.get_type()
        return self


class BaseSessionDataDTO(BaseDataDTO):
    session_id: str


class BaseStartSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "start_session"


class BaseSessionReadyDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "session_ready"


class BaseEndSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "end_session"


D = TypeVar("D")


class BaseResponseDTO(BaseModel, Generic[D]):
    success: bool
    code: int
    message: str
    data: Optional[D] = None


class TimeMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
