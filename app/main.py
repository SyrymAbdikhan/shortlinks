from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.main import api_router
from app.core.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="ShortLinks", version="1.0.0", lifespan=lifespan)
app.include_router(api_router)
