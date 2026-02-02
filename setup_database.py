"""
Simple Database Setup Script
Purane tables drop karke naye tables create karta hai
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:tayyab@localhost/billu"
    print("⚠ Using default DATABASE_URL")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("=" * 60)
print("Database Setup - Naye Tables Create Kar Raha Hoon")
print("=" * 60)
print(f"\nDatabase: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}\n")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        print("📋 Step 1: Purane tables drop kar raha hoon...")
        
        # Drop old tables if they exist
        conn.execute(text("DROP TABLE IF EXISTS sales_records CASCADE;"))
        print("  ✓ Dropped sales_records (if existed)")
        
        conn.execute(text("DROP TABLE IF EXISTS inventory CASCADE;"))
        print("  ✓ Dropped inventory (if existed)")
        
        print("\n📋 Step 2: Naye tables create kar raha hoon...")
        
        # Create customers table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                contact VARCHAR(100),
                email VARCHAR(255),
                address TEXT,
                account_type VARCHAR(20) DEFAULT 'customer',
                opening_balance DECIMAL(10, 2) DEFAULT 0,
                current_balance DECIMAL(10, 2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        print("  ✓ Created customers table")
        
        # Create items table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                purchase_rate DECIMAL(10, 2) NOT NULL,
                sale_rate DECIMAL(10, 2) NOT NULL,
                available_quantity DECIMAL(10, 2) DEFAULT 0,
                unit VARCHAR(50) DEFAULT 'pcs',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        print("  ✓ Created items table")
        
        # Create invoices table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS invoices (
                id SERIAL PRIMARY KEY,
                invoice_number VARCHAR(50) UNIQUE NOT NULL,
                invoice_type VARCHAR(20) NOT NULL,
                customer_id INTEGER REFERENCES customers(id),
                invoice_date TIMESTAMP DEFAULT NOW(),
                subtotal DECIMAL(10, 2) NOT NULL,
                discount_amount DECIMAL(10, 2) DEFAULT 0,
                delivery_charges DECIMAL(10, 2) DEFAULT 0,
                net_amount DECIMAL(10, 2) NOT NULL,
                previous_balance DECIMAL(10, 2) DEFAULT 0,
                payment_received DECIMAL(10, 2) DEFAULT 0,
                current_balance DECIMAL(10, 2) NOT NULL,
                payment_mode VARCHAR(50),
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        print("  ✓ Created invoices table")
        
        # Create invoice_items table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id SERIAL PRIMARY KEY,
                invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
                item_id INTEGER REFERENCES items(id),
                item_name VARCHAR(255) NOT NULL,
                quantity DECIMAL(10, 2) NOT NULL,
                rate DECIMAL(10, 2) NOT NULL,
                line_total DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        print("  ✓ Created invoice_items table")
        
        # Create payments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(id),
                invoice_id INTEGER REFERENCES invoices(id),
                payment_date TIMESTAMP DEFAULT NOW(),
                amount DECIMAL(10, 2) NOT NULL,
                payment_mode VARCHAR(50) NOT NULL,
                payment_source VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        print("  ✓ Created payments table")
        
        # Create invoice counter sequence
        conn.execute(text("""
            CREATE SEQUENCE IF NOT EXISTS invoice_counter START 1;
        """))
        print("  ✓ Created invoice_counter sequence")
        
    print("\n" + "=" * 60)
    print("✅ Database setup successfully complete!")
    print("=" * 60)
    print("\n📊 Created Tables:")
    print("  • customers - Customer/Supplier data")
    print("  • items - Product items")
    print("  • invoices - Sales/Purchase invoices")
    print("  • invoice_items - Invoice line items")
    print("  • payments - Payment records")
    print("\n🚀 Ab aap server start kar sakte hain:")
    print("   uvicorn main:app --reload")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Check karein:")
    print("  1. PostgreSQL service running hai?")
    print("  2. Database 'billu' create hai?")
    print("  3. Password '.env' file mein sahi hai?")
