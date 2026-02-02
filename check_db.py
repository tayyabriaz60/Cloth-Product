"""Quick script to check database connection and inventory count"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if inventory table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'inventory'
            );
        """))
        table_exists = result.fetchone()[0]
        print(f"Inventory table exists: {table_exists}")
        
        if table_exists:
            # Count inventory items
            result = conn.execute(text("SELECT COUNT(*) FROM inventory;"))
            count = result.fetchone()[0]
            print(f"Number of inventory items: {count}")
            
            # Get all inventory items
            result = conn.execute(text("SELECT * FROM inventory LIMIT 5;"))
            items = result.fetchall()
            print(f"\nFirst 5 inventory items:")
            for item in items:
                print(item)
        
        # Check sales_records table
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'sales_records'
            );
        """))
        sales_table_exists = result.fetchone()[0]
        print(f"\nSales records table exists: {sales_table_exists}")
        
        if sales_table_exists:
            result = conn.execute(text("SELECT COUNT(*) FROM sales_records;"))
            count = result.fetchone()[0]
            print(f"Number of sales records: {count}")
            
    print("\n✅ Database connection successful!")
except Exception as e:
    print(f"\n❌ Database error: {e}")
