import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware

import utils.database as database
from routers.analyzer_router import analyzer_router
from routers.building_router import building_router
from routers.deblur_gs_router import deblur_gs_router
from routers.unity_router import unity_router
from utils.exception import (
    CustomException,
    custom_exception_handler,
    validation_exception_handler,
)

# necessary to import all models to register them with SQLAlchemy
import entities


class LineTruncatingFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, max_line_length=1000):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.max_line_length = max_line_length

    def format(self, record):
        msg = super().format(record)
        lines = msg.splitlines()

        truncated_lines = [
            (
                line
                if len(line) <= self.max_line_length
                else line[: self.max_line_length] + " ...[truncated]"
            )
            for line in lines
        ]
        return "\n".join(truncated_lines)


logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = LineTruncatingFormatter(
        "%(filename)s %(funcName)s():%(lineno)d\n%(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    database.init_engine()
    database.Base.metadata.create_all(bind=database.engine)


app.include_router(building_router, prefix="/api/building")

app.include_router(analyzer_router, prefix="/ws/analyzer")
app.include_router(unity_router, prefix="/ws/unity")
app.include_router(deblur_gs_router, prefix="/ws/deblur_gs")

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
