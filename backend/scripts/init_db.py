import os
import sys
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.models import User
from db.session import engine, normalize_database_url
from src.auth import hash_password

# Ensure python can find project module if run from the script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

env_path = os.path.join(project_dir, ".env")
load_dotenv(env_path)

DB_URL = normalize_database_url(os.environ.get("DATABASE_URL"))

parsed_url = urlparse(DB_URL)
target_db = parsed_url.path.lstrip('/')
user = parsed_url.username
password = parsed_url.password
host = parsed_url.hostname
port = parsed_url.port or 5432

def create_database_if_not_exists():
    # Connect to the default 'postgres' database
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        # Allows CREATE DATABASE outside of transaction block
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if target db exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{target_db}' does not exist. Creating...")
            cursor.execute(f'CREATE DATABASE "{target_db}"')
            print(f"Database '{target_db}' created successfully.")
            created = True
        else:
            print(f"Database '{target_db}' already exists.")
            created = False

        cursor.close()
        conn.close()
        return created

    except Exception as e:
        print(f"An error occurred while checking/creating the database: {e}")
        sys.exit(1)

def main():
    print(f"Checking for database connection from: {env_path}")
    created = create_database_if_not_exists()
    
    if created:
        print("\nRunning database population logic from csv_to_postgresql.py...")
        import scripts.csv_to_postgresql as db_populator
        db_populator.main()
    else:
        print("\nDatabase already exists, skipping population.")
        
    with Session(engine) as session:
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
