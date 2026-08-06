import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

sys.path.insert(0, str(Path(__file__).parent))

from common.db import engine
from common.schemas import Base
from friends.router import friends_router
from pokes.router import pokes_router
from users.router import users_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan, prefix="/api")

app.include_router(users_router, prefix="/users")
app.include_router(friends_router, prefix="/friends")
app.include_router(pokes_router, prefix="/pokes")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
