import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Load backend/.env explicitly so this works regardless of the current
# working directory (local scripts, uvicorn, and Vercel all differ).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def normalize_database_url(raw_url: str | None) -> str:
    """Return a URL that SQLAlchemy can actually load as a dialect.

    Managed providers (Aiven, Heroku, Neon, Render, ...) usually hand out
    ``postgres://...`` URLs, but SQLAlchemy only registers ``postgresql://``.
    Passing the former raises:
        NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres

    The scheme is also forced to the psycopg2 driver. SQLAlchemy 2.1 switched
    bare ``postgresql://`` URLs to psycopg 3, which is not what this project
    installs.

    Environment variables pasted into hosting dashboards also often keep
    surrounding quotes, so those are stripped as well.
    """
    if not raw_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to backend/.env locally and to "
            "the project's Environment Variables on Vercel."
        )

    url = raw_url.strip().strip('"\'')

    # postgres:// -> postgresql://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    # SQLAlchemy 2.1 changed the default driver for bare ``postgresql://``
    # URLs to psycopg 3. This project ships psycopg2-binary, so force the
    # psycopg2 driver explicitly instead of relying on the version default.
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    elif url.startswith("postgresql+psycopg://"):
        url = "postgresql+psycopg2://" + url[len("postgresql+psycopg://"):]
    elif not url.startswith("postgresql+psycopg2://"):
        scheme = url.split("://", 1)[0]
        raise RuntimeError(
            f"Unsupported DATABASE_URL scheme '{scheme}'. "
            "Use 'postgresql://' (not 'postgres://')."
        )

    return url


DB_URL = normalize_database_url(os.getenv("DATABASE_URL"))

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
