from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Numeric, DateTime, String, ForeignKey, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:hamzagujjar@localhost/billu"
    print("⚠ Warning: DATABASE_URL not set, using localhost fallback")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"connect_timeout": 10}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# SQLAlchemy Models
# ============================================================================

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact = Column(String(100))
    email = Column(String(255))
    address = Column(Text)
    account_type = Column(String(20), default='customer')  # 'customer' or 'supplier'
    opening_balance = Column(Numeric(10, 2), default=0)
    current_balance = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    purchase_rate = Column(Numeric(10, 2), nullable=False)
    sale_rate = Column(Numeric(10, 2), nullable=False)
    available_quantity = Column(Numeric(10, 2), default=0)
    unit = Column(String(50), default='pcs')
    created_at = Column(DateTime, default=datetime.utcnow)

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_type = Column(String(20), nullable=False)  # 'sale' or 'purchase'
    customer_id = Column(Integer, ForeignKey("customers.id"))
    invoice_date = Column(DateTime, default=datetime.utcnow)
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    delivery_charges = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2), nullable=False)
    previous_balance = Column(Numeric(10, 2), default=0)
    payment_received = Column(Numeric(10, 2), default=0)
    current_balance = Column(Numeric(10, 2), nullable=False)
    payment_mode = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("items.id"))
    item_name = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)  # Can be negative for returns
    rate = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    payment_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_mode = Column(String(50), nullable=False)
    payment_source = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# Pydantic Models (Request/Response)
# ============================================================================

# Customer Models
class CustomerCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    account_type: str = 'customer'
    opening_balance: float = 0

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    opening_balance: Optional[float] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    contact: Optional[str]
    email: Optional[str]
    address: Optional[str]
    account_type: str
    opening_balance: Decimal
    current_balance: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

# Item Models
class ItemCreate(BaseModel):
    name: str
    category: Optional[str] = None
    purchase_rate: float
    sale_rate: float
    available_quantity: float = 0
    unit: str = 'pcs'

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    purchase_rate: Optional[float] = None
    sale_rate: Optional[float] = None
    available_quantity: Optional[float] = None
    unit: Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    purchase_rate: Decimal
    sale_rate: Decimal
    available_quantity: Decimal
    unit: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Invoice Models
class InvoiceItemCreate(BaseModel):
    item_id: int
    quantity: float
    rate: float

class InvoiceCreate(BaseModel):
    invoice_type: str  # 'sale' or 'purchase'
    customer_id: int
    items: List[InvoiceItemCreate]
    discount_amount: float = 0
    delivery_charges: float = 0
    payment_received: float = 0
    payment_mode: Optional[str] = 'cash'
    notes: Optional[str] = None

class InvoiceItemResponse(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: Decimal
    rate: Decimal
    line_total: Decimal
    
    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    invoice_type: str
    customer_id: int
    invoice_date: datetime
    subtotal: Decimal
    discount_amount: Decimal
    delivery_charges: Decimal
    net_amount: Decimal
    previous_balance: Decimal
    payment_received: Decimal
    current_balance: Decimal
    payment_mode: Optional[str]
    notes: Optional[str]
    items: List[InvoiceItemResponse] = []
    
    class Config:
        from_attributes = True

# Payment Models
class PaymentCreate(BaseModel):
    customer_id: int
    invoice_id: Optional[int] = None
    amount: float
    payment_mode: str
    payment_source: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    customer_id: int
    invoice_id: Optional[int]
    payment_date: datetime
    amount: Decimal
    payment_mode: str
    payment_source: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(title="Business Management System")

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Startup Event - Initialize Database
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Create database tables and sequence on startup if they don't exist"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created/verified")
        
        # Create invoice counter sequence if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text("CREATE SEQUENCE IF NOT EXISTS invoice_counter START 1;"))
            conn.commit()
        print("✓ Invoice counter sequence created/verified")
        
        print("✓ Database is ready")
    except Exception as e:
        print(f"⚠ Warning: Database initialization error: {e}")
        print("  You may need to run: python migrate_database.py")

# Get file path helper
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path):
        cwd_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(cwd_path):
            return cwd_path
    return file_path

# ============================================================================
# Static File Routes
# ============================================================================

@app.get("/")
async def read_root():
    file_path = get_file_path("dashboard.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="dashboard.html not found")
    return FileResponse(file_path)

@app.get("/sales")
async def sales_page():
    file_path = get_file_path("sales.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="sales.html not found")
    return FileResponse(file_path)

@app.get("/customers")
async def customers_page():
    file_path = get_file_path("customers.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="customers.html not found")
    return FileResponse(file_path)

@app.get("/items")
async def items_page():
    file_path = get_file_path("items.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="items.html not found")
    return FileResponse(file_path)

@app.get("/purchases")
async def purchases_page():
    file_path = get_file_path("purchases.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="purchases.html not found")
    return FileResponse(file_path)

@app.get("/payments")
async def payments_page():
    file_path = get_file_path("payments.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="payments.html not found")
    return FileResponse(file_path)

@app.get("/reports")
async def reports_page():
    file_path = get_file_path("reports.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="reports.html not found")
    return FileResponse(file_path)

@app.get("/config.js")
async def config_js():
    file_path = get_file_path("config.js")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="config.js not found")
    return FileResponse(file_path, media_type="application/javascript")

# ============================================================================
# Customer API Endpoints
# ============================================================================

@app.post("/api/customers", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate):
    db = SessionLocal()
    try:
        db_customer = Customer(
            name=customer.name,
            contact=customer.contact,
            email=customer.email,
            address=customer.address,
            account_type=customer.account_type,
            opening_balance=Decimal(str(customer.opening_balance)),
            current_balance=Decimal(str(customer.opening_balance))
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/customers", response_model=List[CustomerResponse])
def get_customers(account_type: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(Customer)
        if account_type:
            query = query.filter(Customer.account_type == account_type)
        customers = query.all()
        return customers
    finally:
        db.close()

@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    finally:
        db.close()

@app.put("/api/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer_update: CustomerUpdate):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        if customer_update.name is not None:
            customer.name = customer_update.name
        if customer_update.contact is not None:
            customer.contact = customer_update.contact
        if customer_update.email is not None:
            customer.email = customer_update.email
        if customer_update.address is not None:
            customer.address = customer_update.address
        if customer_update.opening_balance is not None:
            customer.opening_balance = Decimal(str(customer_update.opening_balance))
        
        db.commit()
        db.refresh(customer)
        return customer
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: int):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Check if customer has invoices
        invoice_count = db.query(Invoice).filter(Invoice.customer_id == customer_id).count()
        if invoice_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete customer. {invoice_count} invoice(s) are linked."
            )
        
        db.delete(customer)
        db.commit()
        return {"message": "Customer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# ============================================================================
# Item API Endpoints
# ============================================================================

@app.post("/api/items", response_model=ItemResponse)
def create_item(item: ItemCreate):
    db = SessionLocal()
    try:
        db_item = Item(
            name=item.name,
            category=item.category,
            purchase_rate=Decimal(str(item.purchase_rate)),
            sale_rate=Decimal(str(item.sale_rate)),
            available_quantity=Decimal(str(item.available_quantity)),
            unit=item.unit
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/items", response_model=List[ItemResponse])
def get_items(category: Optional[str] = None, search: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(Item)
        if category:
            query = query.filter(Item.category == category)
        if search:
            query = query.filter(Item.name.ilike(f"%{search}%"))
        items = query.all()
        return items
    finally:
        db.close()

@app.get("/api/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    finally:
        db.close()

@app.put("/api/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        if item_update.name is not None:
            item.name = item_update.name
        if item_update.category is not None:
            item.category = item_update.category
        if item_update.purchase_rate is not None:
            item.purchase_rate = Decimal(str(item_update.purchase_rate))
        if item_update.sale_rate is not None:
            item.sale_rate = Decimal(str(item_update.sale_rate))
        if item_update.available_quantity is not None:
            item.available_quantity = Decimal(str(item_update.available_quantity))
        if item_update.unit is not None:
            item.unit = item_update.unit
        
        db.commit()
        db.refresh(item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        db.delete(item)
        db.commit()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# ============================================================================
# Invoice API Endpoints
# ============================================================================

def generate_invoice_number(db):
    """Generate next invoice number in format INV-001"""
    result = db.execute(text("SELECT nextval('invoice_counter')"))
    counter = result.fetchone()[0]
    return f"INV-{counter:03d}"

@app.post("/api/invoices", response_model=InvoiceResponse)
def create_invoice(invoice_data: InvoiceCreate):
    db = SessionLocal()
    try:
        # Get customer
        customer = db.query(Customer).filter(Customer.id == invoice_data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Calculate totals
        subtotal = Decimal('0')
        invoice_items = []
        
        for item_data in invoice_data.items:
            # Get item
            item = db.query(Item).filter(Item.id == item_data.item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
            
            quantity = Decimal(str(item_data.quantity))
            rate = Decimal(str(item_data.rate))
            line_total = quantity * rate
            subtotal += line_total
            
            # Check stock for sales
            if invoice_data.invoice_type == 'sale' and quantity > 0:
                if item.available_quantity < quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for {item.name}. Available: {item.available_quantity}"
                    )
            
            invoice_items.append({
                'item': item,
                'quantity': quantity,
                'rate': rate,
                'line_total': line_total
            })
        
        # Calculate net amount
        discount = Decimal(str(invoice_data.discount_amount))
        delivery = Decimal(str(invoice_data.delivery_charges))
        net_amount = subtotal - discount + delivery
        
        # Calculate balance
        previous_balance = customer.current_balance
        payment_received = Decimal(str(invoice_data.payment_received))
        current_balance = previous_balance + net_amount - payment_received
        
        # Generate invoice number
        invoice_number = generate_invoice_number(db)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            invoice_type=invoice_data.invoice_type,
            customer_id=invoice_data.customer_id,
            subtotal=subtotal,
            discount_amount=discount,
            delivery_charges=delivery,
            net_amount=net_amount,
            previous_balance=previous_balance,
            payment_received=payment_received,
            current_balance=current_balance,
            payment_mode=invoice_data.payment_mode,
            notes=invoice_data.notes
        )
        db.add(invoice)
        db.flush()  # Get invoice ID
        
        # Create invoice items and update stock
        for item_info in invoice_items:
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                item_id=item_info['item'].id,
                item_name=item_info['item'].name,
                quantity=item_info['quantity'],
                rate=item_info['rate'],
                line_total=item_info['line_total']
            )
            db.add(invoice_item)
            
            # Update stock
            if invoice_data.invoice_type == 'sale':
                item_info['item'].available_quantity -= item_info['quantity']
            else:  # purchase
                item_info['item'].available_quantity += item_info['quantity']
        
        # Update customer balance
        customer.current_balance = current_balance
        
        # Create payment record if payment received
        if payment_received > 0:
            payment = Payment(
                customer_id=customer.id,
                invoice_id=invoice.id,
                amount=payment_received,
                payment_mode=invoice_data.payment_mode or 'cash',
                notes=f"Payment for {invoice_number}"
            )
            db.add(payment)
        
        db.commit()
        db.refresh(invoice)
        
        # Load items for response
        invoice.items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
        
        return invoice
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/invoices", response_model=List[InvoiceResponse])
def get_invoices(
    invoice_type: Optional[str] = None,
    customer_id: Optional[int] = None,
    limit: int = 50
):
    db = SessionLocal()
    try:
        query = db.query(Invoice)
        if invoice_type:
            query = query.filter(Invoice.invoice_type == invoice_type)
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        
        invoices = query.order_by(Invoice.created_at.desc()).limit(limit).all()
        
        # Load items for each invoice
        for invoice in invoices:
            invoice.items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
        
        return invoices
    finally:
        db.close()

@app.get("/api/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int):
    db = SessionLocal()
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice.items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
        return invoice
    finally:
        db.close()

@app.delete("/api/invoices/{invoice_id}")
def delete_invoice(invoice_id: int):
    db = SessionLocal()
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Reverse stock changes
        items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).all()
        for invoice_item in items:
            item = db.query(Item).filter(Item.id == invoice_item.item_id).first()
            if item:
                if invoice.invoice_type == 'sale':
                    item.available_quantity += invoice_item.quantity
                else:  # purchase
                    item.available_quantity -= invoice_item.quantity
        
        # Reverse customer balance
        customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
        if customer:
            customer.current_balance = customer.current_balance - invoice.net_amount + invoice.payment_received
        
        db.delete(invoice)
        db.commit()
        return {"message": "Invoice deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# ============================================================================
# Payment API Endpoints
# ============================================================================

@app.post("/api/payments", response_model=PaymentResponse)
def create_payment(payment_data: PaymentCreate):
    db = SessionLocal()
    try:
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.id == payment_data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Create payment
        payment = Payment(
            customer_id=payment_data.customer_id,
            invoice_id=payment_data.invoice_id,
            amount=Decimal(str(payment_data.amount)),
            payment_mode=payment_data.payment_mode,
            payment_source=payment_data.payment_source,
            notes=payment_data.notes
        )
        db.add(payment)
        
        # Update customer balance
        customer.current_balance -= Decimal(str(payment_data.amount))
        
        db.commit()
        db.refresh(payment)
        return payment
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/payments", response_model=List[PaymentResponse])
def get_payments(customer_id: Optional[int] = None, limit: int = 50):
    db = SessionLocal()
    try:
        query = db.query(Payment)
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        
        payments = query.order_by(Payment.payment_date.desc()).limit(limit).all()
        return payments
    finally:
        db.close()

# ============================================================================
# Reports API Endpoints
# ============================================================================

@app.get("/api/reports/stock")
def get_stock_report():
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        return [{
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "available_quantity": float(item.available_quantity),
            "unit": item.unit,
            "purchase_rate": float(item.purchase_rate),
            "sale_rate": float(item.sale_rate),
            "stock_value": float(item.available_quantity * item.purchase_rate)
        } for item in items]
    finally:
        db.close()

@app.get("/api/reports/customer-balance")
def get_customer_balance_report(account_type: str = 'customer'):
    db = SessionLocal()
    try:
        customers = db.query(Customer).filter(Customer.account_type == account_type).all()
        return [{
            "id": customer.id,
            "name": customer.name,
            "contact": customer.contact,
            "opening_balance": float(customer.opening_balance),
            "current_balance": float(customer.current_balance),
            "balance_type": "Receivable" if customer.current_balance > 0 else "Payable" if customer.current_balance < 0 else "Clear"
        } for customer in customers]
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
