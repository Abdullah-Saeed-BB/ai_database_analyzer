"""
Convert data.csv to a PostgreSQL database using SQLAlchemy.

Schema:
  - Customers: id (from CustomerID), name (random), email (random), passwords (random)
  - Products:  id (random UUID), title (from Description), rate (random 0.0-5.0), in_stock (random 0-125)
  - Orders:    id (from InvoiceNo), invoice_date, country, customer_id (FK -> Customers)
  - OrderItem: id (auto), invoice_no (FK -> Orders), product_id (FK -> Products), quantity, unit_price
"""

import os
import random
import uuid
import sys
import pandas as pd
import psycopg2
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from dotenv import load_dotenv

# Ensure python can find project modules if run from any directory.
# This MUST happen before importing project modules (models, db, src).
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir) # Go up only once, from scripts/ to project/
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

load_dotenv(os.path.join(project_dir, ".env"))

from models.models import Base, Customer, Product, Order, OrderItem

# ── Config ─────────────────────────────────────────────────────────────────────
CSV_PATH  = os.path.join(project_dir, "data", "data.csv")
# Change these credentials to match your PostgreSQL setup
DB_URL    = os.environ.get("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/ecommerce_db")
# Strip quotes and normalize the scheme: SQLAlchemy has no "postgres" dialect.
DB_URL = DB_URL.strip().strip('"\'')
if DB_URL.startswith("postgres://"):
    DB_URL = "postgresql://" + DB_URL[len("postgres://"):]
# Force psycopg2: SQLAlchemy 2.1 defaults bare postgresql:// URLs to psycopg 3.
if DB_URL.startswith("postgresql://"):
    DB_URL = "postgresql+psycopg2://" + DB_URL[len("postgresql://"):]
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

# ── ORM Models are imported from models.models ─────────────────────────

# ── Helpers ────────────────────────────────────────────────────────────────────
def clean_customer_id(raw) -> int | None:
    """Convert CustomerID to int; return None for NaN / non-numeric values."""
    try:
        if pd.isna(raw):
            return None
        return int(float(raw))
    except (ValueError, TypeError):
        return None


def build_customers(df: pd.DataFrame) -> dict[int, Customer]:
    """Return a mapping { customer_id -> Customer } with random data."""
    unique_ids = {
        clean_customer_id(cid)
        for cid in df["CustomerID"].unique()
    }
    unique_ids.discard(None)

    customers: dict[int, Customer] = {}
    for cid in sorted(unique_ids):
        customers[cid] = Customer(
            id        = cid, 
            name      = fake.name(),
            email     = fake.email(),
            password  = fake.password()
        )
    return customers


def build_products(df: pd.DataFrame) -> dict[str, Product]:
    """Return a mapping { description -> Product } with random stock & rating."""
    products: dict[str, Product] = {}
    for desc in df["Description"].unique():
        desc = str(desc).strip()
        if not desc:
            continue
        products[desc] = Product(
            id       = str(uuid.uuid4()),
            title    = desc,
            rate     = round(random.uniform(0.0, 5.0), 1),
            in_stock = random.randint(0, 125),
        )
    return products


# ── Main ───────────────────────────────────────────────────────────────────────
def main(db_url: str | None = None):
    # Allow callers (e.g. init_db.py --global) to target another database.
    engine = create_engine(db_url or DB_URL, echo=False)
    print("Reading CSV …")
    df = pd.read_csv(CSV_PATH, encoding="ISO-8859-1", dtype=str)
    print(f"  Loaded {len(df):,} rows.")

    # ── Data Cleaning ──────────────────────────────────────────────────────────
    # Drop rows with any null values
    df.dropna(inplace=True)
    
    # Drop StockCode column
    if "StockCode" in df.columns:
        df.drop(columns=["StockCode"], inplace=True)
        
    # Make the dates to close to curr date
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    now = datetime.now()
    recent_date = df['InvoiceDate'].max()
    gap = now - recent_date
    df['InvoiceDate'] = df['InvoiceDate'] + gap

    df['InvoiceDate'] = df['InvoiceDate'].dt.strftime('%Y-%m-%d %H:%M')
        
    print(f"  After cleaning: {len(df):,} rows, columns: {list(df.columns)}")

    # Build lookup dicts
    customers = build_customers(df)
    products  = build_products(df)
    print(f"  Unique customers : {len(customers):,}")
    print(f"  Unique products  : {len(products):,}")

    # Create DB
    # Optional: ensure we can drop/create smoothly
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    print("Inserting data …")
    with Session(engine) as session:
        # Customers
        session.add_all(customers.values())
        session.flush()

        # Products
        session.add_all(products.values())
        session.flush()

        # Build Orders
        unique_orders = {}
        for _, row in df.iterrows():
            invoice_no = str(row.get("InvoiceNo", "")).strip()
            
            if invoice_no not in unique_orders:
                cid = clean_customer_id(row.get("CustomerID"))
                customer = customers.get(cid)
                if customer:
                    unique_orders[invoice_no] = Order(
                        id           = invoice_no,
                        invoice_date = str(row.get("InvoiceDate", "")).strip(),
                        country      = str(row.get("Country", "")).strip(),
                        customer_id  = customer.id
                    )
        
        session.add_all(unique_orders.values())
        session.flush()
        print(f"  Unique orders    : {len(unique_orders):,}")

        # Build Order Items
        order_items = []
        skipped = 0
        for _, row in df.iterrows():
            invoice_no = str(row.get("InvoiceNo", "")).strip()
            if invoice_no not in unique_orders:
                skipped += 1
                continue

            desc = str(row.get("Description", "")).strip()
            product = products.get(desc)
            if product is None:
                skipped += 1
                continue

            try:
                quantity   = int(float(row["Quantity"]))
                unit_price = float(row["UnitPrice"])
            except (ValueError, TypeError):
                skipped += 1
                continue

            order_items.append(
                OrderItem(
                    invoice_no   = invoice_no,
                    product_id   = product.id,
                    quantity     = quantity,
                    unit_price   = unit_price
                )
            )

            # Batch insert every 5,000 rows
            if len(order_items) >= 5_000:
                session.add_all(order_items)
                session.flush()
                order_items = []

        if order_items:
            session.add_all(order_items)

        session.commit()

    print(f"Done! Skipped {skipped:,} invalid order items.")
    print(f"Database populated at -> {DB_URL}")


if __name__ == "__main__":
    main()
