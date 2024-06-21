from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from core.models import Base, db_helper
from core.config import setting
from api_v1 import router as router_v1

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=setting.api_v1_prefix)

@app.get("/")
def main():
    return "Hello World"


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
