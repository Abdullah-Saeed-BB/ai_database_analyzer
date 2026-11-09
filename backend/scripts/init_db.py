import argparse
import os
import sys
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ensure python can find project modules if run from any directory.
# This MUST happen before importing project modules (models, db, src).
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models.models import User
from db.session import engine, normalize_database_url
from src.auth import hash_password

env_path = os.path.join(project_dir, ".env")
load_dotenv(env_path)

DB_URL = normalize_database_url(os.environ.get("DATABASE_URL"))

def create_database_if_not_exists(db_url: str) -> bool:
    """Create the target database on the given URL's server if it is missing.

    Self-hosted PostgreSQL allows CREATE DATABASE; most managed providers
    (Neon, Render, Aiven, ...) already provision the database and disallow
    it, so failures here are reported but don't abort initialization.
    """
    parsed = urlparse(db_url)
    target = parsed.path.lstrip('/')
    user_ = parsed.username
    password_ = parsed.password
    host_ = parsed.hostname
    port_ = parsed.port or 5432

    # Connect to the default 'postgres' database
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user_,
            password=password_,
            host=host_,
            port=port_
        )
        # Allows CREATE DATABASE outside of transaction block
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if target db exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{target}' does not exist. Creating...")
            cursor.execute(f'CREATE DATABASE "{target}"')
            print(f"Database '{target}' created successfully.")
            created = True
        else:
            print(f"Database '{target}' already exists.")
            created = False

        cursor.close()
        conn.close()
        return created

    except Exception as e:
        print(f"Could not check/create the database ({e}).")
        print("Continuing anyway — managed providers usually provision it already.")
        return False

def parse_args():
    parser = argparse.ArgumentParser(
        description="Initialize the database: create it if missing, create tables, seed data."
    )
    parser.add_argument(
        "--global",
        dest="global_url",
        metavar="DATABASE_URL",
        help=(
            "Initialize a global/remote database instead of the local DATABASE_URL "
            "from backend/.env. Pass the database URL, e.g. "
            "postgresql://user:password@host:5432/dbname"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    global_url = None
    if args.global_url:
        global_url = normalize_database_url(args.global_url)
        db_engine = create_engine(global_url, pool_pre_ping=True)
        target = urlparse(global_url).path.lstrip('/')
        print(f"Initializing GLOBAL database '{target}'...")
        create_database_if_not_exists(global_url)
    else:
        db_engine = engine
        print(f"Checking for database connection from: {env_path}")
        created = create_database_if_not_exists(DB_URL)

        if created:
            print("\nRunning database population logic from csv_to_postgresql.py...")
            import scripts.csv_to_postgresql as db_populator
            db_populator.main()
        else:
            print("\nDatabase already exists, skipping population.")

    # Always (re)create tables and seed the CSV data + admin user on the
    # chosen database. csv_to_postgresql drops and recreates them, so this
    # is idempotent for both local and global targets.
    if global_url:
        print("\nRunning database population logic from csv_to_postgresql.py...")
        import scripts.csv_to_postgresql as db_populator
        db_populator.main(db_url=global_url)

    with Session(db_engine) as session:
        query = select(User).where(User.email == "admin@ad.min")
        admin_user = session.execute(query).scalar()
        if not admin_user:
            print("Admin user not found. Creating...")
            new_user = User(
                email="admin@ad.min",
                password_hash=hash_password("admin"),
                first_name="Admin",
                last_name="Admin",
                role="admin",
            )
            session.add(new_user)
            session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")

    print("\nInitialization Complete!")

if __name__ == "__main__":
    main()
