from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import database

# nessesary to import all models to register them with SQLAlchemy
import entities

from exception import (
    CustomException,
    custom_exception_handler,
    validation_exception_handler,
)
from routers.comment_router import comment_router
from routers.post_router import post_router
from routers.group_router import group_router
from routers.crop_router import crop_router
from routers.schedule_router import schedule_router
from routers.sensor_router import sensor_router

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


app.include_router(group_router, prefix="/api/group")
app.include_router(crop_router, prefix="/api/crop")
app.include_router(schedule_router, prefix="/api/schedule")
app.include_router(sensor_router, prefix="/api/sensor")
app.include_router(post_router, prefix="/api/post")
app.include_router(comment_router, prefix="/api/comment")

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
