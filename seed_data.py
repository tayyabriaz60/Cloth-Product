import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
from main import Base, Customer, Item, Invoice, InvoiceItem, Payment, DATABASE_URL

# Setup DB connection
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_data():
    print("re-creating database tables...")
    Base.metadata.create_all(bind=engine)

    print("Checking for existing data...")
    customers_exist = db.query(Customer).count() > 0
    items_exist = db.query(Item).count() > 0
    invoices_exist = db.query(Invoice).count() > 0

    if customers_exist and items_exist and invoices_exist:
        print("Data already exists. Skipping seed.")
        return

    if not customers_exist:
        print("Seeding Customers...")
        customers = [
            Customer(name="Ahmed Khan", contact="0300-1234567", email="ahmed@example.com", account_type="customer", address="Lahore"),
            Customer(name="Bilal Sports", contact="0321-7654321", email="bilal@example.com", account_type="customer", address="Karachi"),
            Customer(name="ChenOne", contact="042-111222333", email="info@chenone.com", account_type="customer", address="Islamabad"),
        ]
        suppliers = [
            Customer(name="Fabric Mills Ltd", contact="0300-9876543", email="contact@fabricmills.com", account_type="supplier", address="Faisalabad"),
            Customer(name="Hassan Traders", contact="0333-5555555", email="hassan@traders.com", account_type="supplier", address="Lahore"),
        ]
        
        for c in customers + suppliers:
            db.add(c)
        db.commit()

    if not items_exist:
        print("Seeding Items...")
        items = [
            Item(name="Cotton Fabric Premium", category="Fabric", purchase_rate=150, sale_rate=250, available_quantity=1000, unit="meters"),
            Item(name="Silk Blended", category="Fabric", purchase_rate=300, sale_rate=500, available_quantity=500, unit="meters"),
            Item(name="Denim Jeans", category="Garments", purchase_rate=800, sale_rate=1500, available_quantity=100, unit="pcs"),
            Item(name="T-Shirt Plain", category="Garments", purchase_rate=200, sale_rate=400, available_quantity=200, unit="pcs"),
            Item(name="Buttons Large", category="Accessories", purchase_rate=5, sale_rate=10, available_quantity=5000, unit="pcs"),
        ]
        for i in items:
            db.add(i)
        db.commit()
    
    # Refresh to get IDs
    customers = db.query(Customer).filter(Customer.account_type=="customer").all()
    suppliers = db.query(Customer).filter(Customer.account_type=="supplier").all()
    items = db.query(Item).all()

    if invoices_exist:
        print("Invoices already exist. Skipping invoice generation.")
        return

    print("Seeding Invoices & Payments...")
    
    # Create some Purchase Invoices
    for i in range(5):
        supplier = random.choice(suppliers)
        date = datetime.now() - timedelta(days=random.randint(1, 60))
        
        invoice = Invoice(
            invoice_number=f"PUR-{i+1:03d}",
            invoice_type="purchase",
            customer_id=supplier.id,
            invoice_date=date,
            subtotal=0, net_amount=0, current_balance=0 # Will calc below
        )
        db.add(invoice)
        db.flush()
        
        subtotal = 0
        for _ in range(random.randint(1, 3)):
            item = random.choice(items)
            qty = random.randint(10, 100)
            rate = item.purchase_rate
            line_total = qty * rate
            subtotal += line_total
            
            # Update stock
            item.available_quantity += qty
            
            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                item_id=item.id,
                item_name=item.name,
                quantity=qty,
                rate=rate,
                line_total=line_total
            )
            db.add(inv_item)
            
        invoice.subtotal = subtotal
        invoice.net_amount = subtotal
        invoice.payment_received = random.choice([0, subtotal/2, subtotal])
        
        # Update supplier balance
        supplier.current_balance += (invoice.net_amount - invoice.payment_received)
        invoice.current_balance = supplier.current_balance
        
        # Record payment if any
        if invoice.payment_received > 0:
            payment = Payment(
                customer_id=supplier.id,
                payment_date=date,
                amount=invoice.payment_received,
                payment_mode="bank",
                notes=f"Payment for {invoice.invoice_number}"
            )
            db.add(payment)

    # Create some Sales Invoices
    for i in range(10):
        customer = random.choice(customers)
        date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        invoice = Invoice(
            invoice_number=f"INV-{i+1:03d}",
            invoice_type="sale",
            customer_id=customer.id,
            invoice_date=date,
            subtotal=0, net_amount=0, current_balance=0
        )
        db.add(invoice)
        db.flush()
        
        subtotal = 0
        for _ in range(random.randint(1, 3)):
            item = random.choice(items)
            qty = random.randint(1, 10)
            rate = item.sale_rate
            line_total = qty * rate
            subtotal += line_total
            
            # Update stock
            item.available_quantity -= qty
            
            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                item_id=item.id,
                item_name=item.name,
                quantity=qty,
                rate=rate,
                line_total=line_total
            )
            db.add(inv_item)
            
        invoice.subtotal = subtotal
        invoice.net_amount = subtotal
        invoice.payment_received = random.choice([0, subtotal/2, subtotal])
        
        # Update customer balance
        # For sales: Customer owes us (+), payment reduces it (-)
        # Wait, if my implementation for customer balance is: + for Receivable, - for Payable
        # Sale increases simple balance?
        # Let's check logic:
        # main.py:
        # if invoice.invoice_type == "sale":
        #    customer.current_balance += (db_invoice.net_amount - db_invoice.payment_received)
        
        customer.current_balance += (invoice.net_amount - invoice.payment_received)
        invoice.current_balance = customer.current_balance
        
        if invoice.payment_received > 0:
            payment = Payment(
                customer_id=customer.id,
                payment_date=date,
                amount=invoice.payment_received,
                payment_mode="cash",
                notes=f"Payment for {invoice.invoice_number}"
            )
            db.add(payment)

    db.commit()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_data()
