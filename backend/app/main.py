from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import router as v1_router
from app.scheduler import schedule_jobs, shutdown_jobs


@asynccontextmanager
async def lifespan(_: FastAPI):
    schedule_jobs()
    yield
    shutdown_jobs()


app = FastAPI(title="AI Trading Platform API", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:3001",
        "http://localhost:3001",
        "http://127.0.0.1:3010",
        "http://localhost:3010",
        "http://127.0.0.1:3020",
        "http://localhost:3020",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
