from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.conversations import router as conversations_router
from src.users import router as users_router
from src.data import router as data_router
from scripts.init_db import main as init_db_main
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI(
    title="AI Database Analyzer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations_router, prefix="/api/conversations")
app.include_router(users_router, prefix="/api/users")
app.include_router(data_router, prefix="/api/data")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)