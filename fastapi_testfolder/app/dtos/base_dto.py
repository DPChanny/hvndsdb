from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class BaseResponseDTO(GenericModel, Generic[T]):
    success: bool
    code: int
    message: str
    data: Optional[T] = None 


class TimeMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
