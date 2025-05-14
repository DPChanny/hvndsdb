from fastapi import FastAPI
from .api import user, building

app = FastAPI()

app.include_router(user.router)
app.include_router(building.router)
