"""
Database Migration Script
Drops old tables and creates new Business Management System schema
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("=" * 60)
print("Business Management System - Database Migration")
print("=" * 60)
print(f"\nDatabase: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
print("\n⚠️  WARNING: This will drop all existing tables!")
print("=" * 60)

confirm = input("\nType 'YES' to proceed with migration: ")
if confirm != "YES":
    print("❌ Migration cancelled.")
    exit(0)

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        print("\n📋 Step 1: Dropping old tables...")
        
        # Drop old tables
        conn.execute(text("DROP TABLE IF EXISTS sales_records CASCADE;"))
        print("  ✓ Dropped sales_records")
        
        conn.execute(text("DROP TABLE IF EXISTS inventory CASCADE;"))
        print("  ✓ Dropped inventory")
        
        print("\n📋 Step 2: Creating new tables...")
        
        # Create customers table
        conn.execute(text("""
            CREATE TABLE customers (
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
            CREATE TABLE items (
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
            CREATE TABLE invoices (
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
            CREATE TABLE invoice_items (
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
            CREATE TABLE payments (
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
        
        print("\n📋 Step 3: Inserting sample data...")
        
        # Insert sample customers
        conn.execute(text("""
            INSERT INTO customers (name, contact, email, address, account_type, opening_balance, current_balance)
            VALUES 
                ('Ahmed Khan', '0300-1234567', 'ahmed@example.com', '123 Main St, Karachi', 'customer', 0, 0),
                ('Fatima Ali', '0321-9876543', 'fatima@example.com', '456 Park Ave, Lahore', 'customer', 5000, 5000),
                ('Hassan Traders', '0333-5555555', 'hassan@traders.com', '789 Business St, Islamabad', 'supplier', 0, 0),
                ('Ayesha Boutique', '0345-7777777', 'ayesha@boutique.com', '321 Fashion St, Karachi', 'customer', -2000, -2000),
                ('Bilal Textiles', '0301-8888888', 'bilal@textiles.com', '654 Mill Rd, Faisalabad', 'supplier', 10000, 10000);
        """))
        print("  ✓ Inserted 5 sample customers")
        
        # Insert sample items
        conn.execute(text("""
            INSERT INTO items (name, category, purchase_rate, sale_rate, available_quantity, unit)
            VALUES 
                ('Premium Cotton Fabric', 'Fabrics', 150, 200, 500, 'meters'),
                ('Silk Fabric', 'Fabrics', 300, 400, 200, 'meters'),
                ('Polyester Fabric', 'Fabrics', 100, 150, 800, 'meters'),
                ('Thread Spool (White)', 'Accessories', 50, 75, 100, 'pcs'),
                ('Thread Spool (Black)', 'Accessories', 50, 75, 80, 'pcs'),
                ('Buttons (Pack of 10)', 'Accessories', 30, 50, 150, 'pcs'),
                ('Zipper (12 inch)', 'Accessories', 20, 35, 200, 'pcs'),
                ('Lace Trim', 'Trims', 80, 120, 300, 'meters'),
                ('Elastic Band', 'Trims', 40, 60, 250, 'meters'),
                ('Embroidery Thread', 'Accessories', 100, 150, 60, 'pcs');
        """))
        print("  ✓ Inserted 10 sample items")
        
        # Create invoice counter sequence
        conn.execute(text("""
            CREATE SEQUENCE IF NOT EXISTS invoice_counter START 1;
        """))
        print("  ✓ Created invoice counter sequence")
        
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("=" * 60)
    print("\n📊 Summary:")
    print("  • 5 tables created")
    print("  • 5 sample customers added")
    print("  • 10 sample items added")
    print("  • Invoice numbering: INV-001, INV-002, etc.")
    print("\n🚀 You can now start the application!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
