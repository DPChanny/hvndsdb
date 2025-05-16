from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pydantic import ValidationError

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dtos.base_dto import BaseResponseDTO


class CustomException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=200,
        content=BaseResponseDTO(
            success=False,
            code=exc.code,
            message=exc.message,
            data=None,
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=200,
        content=BaseResponseDTO(
            success=False,
            code=400,
            message="wrong parameter format",
            data=None,
        ).model_dump(),
    )


def handle_exception(e: Exception, db: Session = None):
    if isinstance(e, SQLAlchemyError):
        if db:
            db.rollback()
        raise CustomException(1400, f"DB error: {str(e)}")
    elif isinstance(e, ValidationError):
        raise CustomException(1401, f"Validation error: {str(e)}")
    else:
        raise CustomException(1500, f"Unknown error: {str(e)}")
