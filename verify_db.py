"""Verify new database schema"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:tayyab@localhost/billu"
    print("⚠ Using default DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check customers
        result = conn.execute(text("SELECT COUNT(*) FROM customers;"))
        print(f"✓ Customers: {result.fetchone()[0]} records")
        
        # Check items
        result = conn.execute(text("SELECT COUNT(*) FROM items;"))
        print(f"✓ Items: {result.fetchone()[0]} records")
        
        # Check invoices
        result = conn.execute(text("SELECT COUNT(*) FROM invoices;"))
        print(f"✓ Invoices: {result.fetchone()[0]} records")
        
        # Check invoice_items
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_items;"))
        print(f"✓ Invoice Items: {result.fetchone()[0]} records")
        
        # Check payments
        result = conn.execute(text("SELECT COUNT(*) FROM payments;"))
        print(f"✓ Payments: {result.fetchone()[0]} records")
        
        print("\n✅ Database migration successful!")
        
except Exception as e:
    print(f"❌ Error: {e}")
