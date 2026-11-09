import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.conversations import router as conversations_router
from src.users import router as users_router
from src.data import router as data_router
import uvicorn


DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def get_allowed_origins() -> list[str]:
    """Read allowed origins from CORS_ORIGINS, else use the defaults.

    CORS_ORIGINS is a comma-separated list, e.g.:
        CORS_ORIGINS=https://ai-db-ana.vercel.app,http://localhost:3000
    """
    raw = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return origins or DEFAULT_CORS_ORIGINS


app = FastAPI(
    title="AI Database Analyzer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

app.include_router(conversations_router, prefix="/api/conversations")
app.include_router(users_router, prefix="/api/users")
app.include_router(data_router, prefix="/api/data")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Lightweight check the hosting platform and the browser can hit."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
