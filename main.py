from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Numeric, DateTime, String, ForeignKey, text, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Check if we're in production (Render sets RENDER env var)
    if os.getenv("RENDER") or os.getenv("PORT"):
        raise ValueError("DATABASE_URL environment variable is required in production!")
    # Fallback for local development only
    DATABASE_URL = "postgresql://postgres:tayyab@localhost/billu"
    print("⚠ Warning: DATABASE_URL not set, using localhost fallback")
else:
    print(f"✓ DATABASE_URL found (length: {len(DATABASE_URL)})")

# Render uses postgres:// format, convert to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with connection pooling and retry logic
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections after 5 minutes
    connect_args={"connect_timeout": 10}  # 10 second timeout
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models
class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    design_code = Column(String(100), nullable=False)
    total_thans = Column(Numeric(10, 2), nullable=False)
    meters_per_than = Column(Numeric(10, 2), nullable=False)
    total_meters = Column(Numeric(10, 2), nullable=False)
    cost_price_per_meter = Column(Numeric(10, 2), nullable=False)
    total_stock_value = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SalesRecord(Base):
    __tablename__ = "sales_records"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)  # Keep for backward compatibility
    kameez_inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    shalwar_inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    company_name = Column(String(255), nullable=True)
    design_code = Column(String(100), nullable=True)
    kameez_company_name = Column(String(255), nullable=True)
    kameez_design_code = Column(String(100), nullable=True)
    shalwar_company_name = Column(String(255), nullable=True)
    shalwar_design_code = Column(String(100), nullable=True)
    kameez_meters = Column(Numeric(10, 2))
    kameez_rate = Column(Numeric(10, 2))
    kameez_total = Column(Numeric(10, 2))
    shalwar_meters = Column(Numeric(10, 2))
    shalwar_rate = Column(Numeric(10, 2))
    shalwar_total = Column(Numeric(10, 2))
    grand_total = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables - will be done on startup to ensure database is ready
# Don't create tables at module import time

# Migration function to add new columns if they don't exist
def migrate_database():
    """Add new columns to sales_records table if they don't exist"""
    try:
        with engine.begin() as conn:
            # Check existing columns
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sales_records'
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            columns_to_add = {
                'inventory_id': 'INTEGER REFERENCES inventory(id)',
                'company_name': 'VARCHAR(255)',
                'design_code': 'VARCHAR(100)',
                'kameez_inventory_id': 'INTEGER REFERENCES inventory(id)',
                'shalwar_inventory_id': 'INTEGER REFERENCES inventory(id)',
                'kameez_company_name': 'VARCHAR(255)',
                'kameez_design_code': 'VARCHAR(100)',
                'shalwar_company_name': 'VARCHAR(255)',
                'shalwar_design_code': 'VARCHAR(100)'
            }
            
            added_columns = []
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_columns:
                    try:
                        conn.execute(text(f"ALTER TABLE sales_records ADD COLUMN {col_name} {col_type}"))
                        added_columns.append(col_name)
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            print(f"⚠ Warning adding {col_name}: {str(e)}")
            
            if added_columns:
                print(f"✓ Database migration completed: Added columns {', '.join(added_columns)}")
            else:
                print("✓ Database is up to date - all columns exist")
    except Exception as e:
        error_msg = str(e).lower()
        if "already exists" in error_msg or "duplicate" in error_msg:
            print("✓ Database is up to date - columns already exist")
        else:
            print(f"⚠ Migration warning: {str(e)}")

# FastAPI app
app = FastAPI()

# Run migration on startup
@app.on_event("startup")
async def startup_event():
    """Run database migration on application startup"""
    try:
        # Create tables first
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created/verified")
        
        # Then run migration
        migrate_database()
    except Exception as e:
        print(f"⚠ Database connection error on startup: {str(e)}")
        print("⚠ Will retry on first request...")
        # Don't fail startup - let it retry on first request

# Enable CORS for frontend
# In production, you might want to restrict origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Get current directory - use __file__ location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    """Get absolute path for a file in the project directory"""
    file_path = os.path.join(BASE_DIR, filename)
    # Also try current working directory as fallback
    if not os.path.exists(file_path):
        cwd_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(cwd_path):
            return cwd_path
    return file_path

@app.get("/")
async def read_root():
    file_path = get_file_path("index.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(file_path)

@app.get("/index.html")
async def index_html():
    file_path = get_file_path("index.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(file_path)

@app.get("/admin")
async def admin_page():
    file_path = get_file_path("admin.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="admin.html not found")
    return FileResponse(file_path)

@app.get("/config.js")
async def config_js():
    file_path = get_file_path("config.js")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="config.js not found")
    return FileResponse(file_path, media_type="application/javascript")

# Pydantic models for request/response
class StockCreate(BaseModel):
    company_name: str
    design_code: str
    total_thans: float
    meters_per_than: float
    cost_price_per_meter: float

class StockUpdate(BaseModel):
    company_name: Optional[str] = None
    design_code: Optional[str] = None
    total_thans: Optional[float] = None
    meters_per_than: Optional[float] = None
    cost_price_per_meter: Optional[float] = None

class InventoryResponse(BaseModel):
    id: int
    company_name: str
    design_code: str
    total_thans: Decimal
    meters_per_than: Decimal
    total_meters: Decimal
    cost_price_per_meter: Decimal
    total_stock_value: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class InventoryStatus(BaseModel):
    id: int
    company_name: str
    design_code: str
    total_thans: Decimal
    meters_per_than: Decimal
    total_meters: Decimal
    cost_price_per_meter: Decimal
    total_stock_value: Decimal
    sold_meters: Decimal
    remaining_meters: Decimal
    remaining_stock_value: Decimal

class BillCreate(BaseModel):
    inventory_id: Optional[int] = None  # For backward compatibility
    kameez_inventory_id: Optional[int] = None
    shalwar_inventory_id: Optional[int] = None
    company_name: Optional[str] = None  # For backward compatibility
    design_code: Optional[str] = None  # For backward compatibility
    kameez_company_name: Optional[str] = None
    kameez_design_code: Optional[str] = None
    shalwar_company_name: Optional[str] = None
    shalwar_design_code: Optional[str] = None
    kameez_meters: float
    kameez_rate: float
    shalwar_meters: float
    shalwar_rate: float

class BillResponse(BaseModel):
    id: int
    inventory_id: Optional[int]
    kameez_inventory_id: Optional[int]
    shalwar_inventory_id: Optional[int]
    company_name: Optional[str]
    design_code: Optional[str]
    kameez_company_name: Optional[str]
    kameez_design_code: Optional[str]
    shalwar_company_name: Optional[str]
    shalwar_design_code: Optional[str]
    kameez_meters: Decimal
    kameez_rate: Decimal
    kameez_total: Decimal
    shalwar_meters: Decimal
    shalwar_rate: Decimal
    shalwar_total: Decimal
    grand_total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

@app.post("/add-stock", response_model=InventoryResponse)
def add_stock(stock: StockCreate):
    try:
        db = SessionLocal()
        
        # Calculate total meters and stock value
        total_meters = Decimal(str(stock.total_thans)) * Decimal(str(stock.meters_per_than))
        total_stock_value = total_meters * Decimal(str(stock.cost_price_per_meter))
        
        # Create inventory record
        inventory = Inventory(
            company_name=stock.company_name,
            design_code=stock.design_code,
            total_thans=Decimal(str(stock.total_thans)),
            meters_per_than=Decimal(str(stock.meters_per_than)),
            total_meters=total_meters,
            cost_price_per_meter=Decimal(str(stock.cost_price_per_meter)),
            total_stock_value=total_stock_value
        )
        
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        db.close()
        
        return inventory
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update-stock/{stock_id}", response_model=InventoryResponse)
def update_stock(stock_id: int, stock_update: StockUpdate):
    db = None
    try:
        db = SessionLocal()
        
        # Get existing inventory
        inventory = db.query(Inventory).filter(Inventory.id == stock_id).first()
        if not inventory:
            raise HTTPException(status_code=404, detail="Stock item not found")
        
        # Update fields if provided
        if stock_update.company_name is not None:
            inventory.company_name = stock_update.company_name
        if stock_update.design_code is not None:
            inventory.design_code = stock_update.design_code
        if stock_update.total_thans is not None:
            inventory.total_thans = Decimal(str(stock_update.total_thans))
        if stock_update.meters_per_than is not None:
            inventory.meters_per_than = Decimal(str(stock_update.meters_per_than))
        if stock_update.cost_price_per_meter is not None:
            inventory.cost_price_per_meter = Decimal(str(stock_update.cost_price_per_meter))
        
        # Recalculate total meters and stock value
        inventory.total_meters = inventory.total_thans * inventory.meters_per_than
        inventory.total_stock_value = inventory.total_meters * inventory.cost_price_per_meter
        
        db.commit()
        db.refresh(inventory)
        
        return inventory
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()

@app.delete("/delete-stock/{stock_id}")
def delete_stock(stock_id: int):
    db = None
    try:
        db = SessionLocal()
        
        # Get inventory item
        inventory = db.query(Inventory).filter(Inventory.id == stock_id).first()
        if not inventory:
            db.close()
            raise HTTPException(status_code=404, detail=f"Stock item with ID {stock_id} not found")
        
        # Check if there are any sales records linked to this inventory
        # Use or_() for proper SQL OR clause
        from sqlalchemy import or_
        sales_count = db.query(SalesRecord).filter(
            or_(
                SalesRecord.inventory_id == stock_id,
                SalesRecord.kameez_inventory_id == stock_id,
                SalesRecord.shalwar_inventory_id == stock_id
            )
        ).count()
        
        if sales_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete stock item. {sales_count} sales record(s) are linked to this inventory."
            )
        
        # Delete inventory
        db.delete(inventory)
        db.commit()
        
        return {"message": f"Stock item {stock_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()

@app.get("/get-inventory", response_model=List[InventoryStatus])
def get_inventory():
    db = None
    try:
        db = SessionLocal()
        
        # Get all inventory items
        inventory_items = db.query(Inventory).all()
        
        # Calculate sold meters and remaining stock for each item
        result = []
        for item in inventory_items:
            # Calculate total sold meters for this inventory item
            # Check old inventory_id field (backward compatibility) and new separate fields
            sales_old = db.query(SalesRecord).filter(
                SalesRecord.inventory_id == item.id
            ).all()
            
            sales_kameez = db.query(SalesRecord).filter(
                SalesRecord.kameez_inventory_id == item.id
            ).all()
            
            sales_shalwar = db.query(SalesRecord).filter(
                SalesRecord.shalwar_inventory_id == item.id
            ).all()
            
            sold_meters = Decimal('0')
            
            # Old method: count both kameez and shalwar from inventory_id
            for sale in sales_old:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                sold_meters += kameez_m + shalwar_m
            
            # New method: count only kameez meters from kameez_inventory_id
            for sale in sales_kameez:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                sold_meters += kameez_m
            
            # New method: count only shalwar meters from shalwar_inventory_id
            for sale in sales_shalwar:
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                sold_meters += shalwar_m
            
            remaining_meters = item.total_meters - sold_meters
            remaining_stock_value = remaining_meters * item.cost_price_per_meter
            
            result.append(InventoryStatus(
                id=item.id,
                company_name=item.company_name,
                design_code=item.design_code,
                total_thans=item.total_thans,
                meters_per_than=item.meters_per_than,
                total_meters=item.total_meters,
                cost_price_per_meter=item.cost_price_per_meter,
                total_stock_value=item.total_stock_value,
                sold_meters=sold_meters,
                remaining_meters=remaining_meters,
                remaining_stock_value=remaining_stock_value
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()

@app.get("/get-inventory-simple", response_model=List[dict])
def get_inventory_simple():
    """Simplified inventory list for dropdown selection"""
    db = None
    db_temp = None
    try:
        db = SessionLocal()
        inventory_items = db.query(Inventory).all()
        
        result = []
        for item in inventory_items:
            # Calculate remaining meters
            db_temp = SessionLocal()
            # Check old inventory_id and new separate fields
            sales_old = db_temp.query(SalesRecord).filter(
                SalesRecord.inventory_id == item.id
            ).all()
            
            sales_kameez = db_temp.query(SalesRecord).filter(
                SalesRecord.kameez_inventory_id == item.id
            ).all()
            
            sales_shalwar = db_temp.query(SalesRecord).filter(
                SalesRecord.shalwar_inventory_id == item.id
            ).all()
            
            sold_meters = Decimal('0')
            
            # Old method
            for sale in sales_old:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                sold_meters += kameez_m + shalwar_m
            
            # New method - kameez only
            for sale in sales_kameez:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                sold_meters += kameez_m
            
            # New method - shalwar only
            for sale in sales_shalwar:
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                sold_meters += shalwar_m
            
            remaining_meters = float(item.total_meters - sold_meters)
            db_temp.close()
            db_temp = None
            
            if remaining_meters > 0:  # Only return items with stock
                result.append({
                    "id": item.id,
                    "company_name": item.company_name,
                    "design_code": item.design_code,
                    "remaining_meters": remaining_meters
                })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db_temp:
            db_temp.close()
        if db:
            db.close()

@app.post("/create-bill", response_model=BillResponse)
def create_bill(bill: BillCreate):
    db = None
    try:
        db = SessionLocal()
        
        # Handle separate kameez and shalwar inventory
        kameez_company_name = bill.kameez_company_name
        kameez_design_code = bill.kameez_design_code
        shalwar_company_name = bill.shalwar_company_name
        shalwar_design_code = bill.shalwar_design_code
        
        # Check and validate kameez inventory if provided
        if bill.kameez_inventory_id:
            kameez_inventory = db.query(Inventory).filter(Inventory.id == bill.kameez_inventory_id).first()
            if not kameez_inventory:
                raise HTTPException(status_code=404, detail="Kameez inventory item not found")
            
            # Calculate sold kameez meters from this inventory
            sales_kameez = db.query(SalesRecord).filter(
                (SalesRecord.kameez_inventory_id == bill.kameez_inventory_id) |
                ((SalesRecord.inventory_id == bill.kameez_inventory_id) & (SalesRecord.kameez_inventory_id.is_(None)))
            ).all()
            
            sold_kameez_meters = Decimal('0')
            for sale in sales_kameez:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                # For old records with inventory_id, count kameez only
                if sale.kameez_inventory_id is None and sale.inventory_id == bill.kameez_inventory_id:
                    sold_kameez_meters += kameez_m
                elif sale.kameez_inventory_id == bill.kameez_inventory_id:
                    sold_kameez_meters += kameez_m
            
            remaining_kameez = kameez_inventory.total_meters - sold_kameez_meters
            kameez_needed = Decimal(str(bill.kameez_meters))
            
            if kameez_needed > remaining_kameez:
                raise HTTPException(
                    status_code=400,
                    detail=f"Kameez: Insufficient stock. Available: {remaining_kameez}m, Required: {kameez_needed}m"
                )
            
            kameez_company_name = kameez_company_name or kameez_inventory.company_name
            kameez_design_code = kameez_design_code or kameez_inventory.design_code
        
        # Check and validate shalwar inventory if provided
        if bill.shalwar_inventory_id:
            shalwar_inventory = db.query(Inventory).filter(Inventory.id == bill.shalwar_inventory_id).first()
            if not shalwar_inventory:
                raise HTTPException(status_code=404, detail="Shalwar inventory item not found")
            
            # Calculate sold shalwar meters from this inventory
            sales_shalwar = db.query(SalesRecord).filter(
                (SalesRecord.shalwar_inventory_id == bill.shalwar_inventory_id) |
                ((SalesRecord.inventory_id == bill.shalwar_inventory_id) & (SalesRecord.shalwar_inventory_id.is_(None)))
            ).all()
            
            sold_shalwar_meters = Decimal('0')
            for sale in sales_shalwar:
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                # For old records with inventory_id, count shalwar only
                if sale.shalwar_inventory_id is None and sale.inventory_id == bill.shalwar_inventory_id:
                    sold_shalwar_meters += shalwar_m
                elif sale.shalwar_inventory_id == bill.shalwar_inventory_id:
                    sold_shalwar_meters += shalwar_m
            
            remaining_shalwar = shalwar_inventory.total_meters - sold_shalwar_meters
            shalwar_needed = Decimal(str(bill.shalwar_meters))
            
            if shalwar_needed > remaining_shalwar:
                raise HTTPException(
                    status_code=400,
                    detail=f"Shalwar: Insufficient stock. Available: {remaining_shalwar}m, Required: {shalwar_needed}m"
                )
            
            shalwar_company_name = shalwar_company_name or shalwar_inventory.company_name
            shalwar_design_code = shalwar_design_code or shalwar_inventory.design_code
        
        # Backward compatibility: handle old inventory_id method
        if bill.inventory_id and not bill.kameez_inventory_id and not bill.shalwar_inventory_id:
            inventory = db.query(Inventory).filter(Inventory.id == bill.inventory_id).first()
            if not inventory:
                raise HTTPException(status_code=404, detail="Inventory item not found")
            
            total_meters_needed = Decimal(str(bill.kameez_meters)) + Decimal(str(bill.shalwar_meters))
            sales = db.query(SalesRecord).filter(SalesRecord.inventory_id == bill.inventory_id).all()
            sold_meters = Decimal('0')
            for sale in sales:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                sold_meters += kameez_m + shalwar_m
            
            remaining_meters = inventory.total_meters - sold_meters
            if total_meters_needed > remaining_meters:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: {remaining_meters}m, Required: {total_meters_needed}m"
                )
            
            company_name = bill.company_name or inventory.company_name
            design_code = bill.design_code or inventory.design_code
        else:
            company_name = bill.company_name
            design_code = bill.design_code
        
        # Calculate totals
        kameez_total = Decimal(str(bill.kameez_meters)) * Decimal(str(bill.kameez_rate))
        shalwar_total = Decimal(str(bill.shalwar_meters)) * Decimal(str(bill.shalwar_rate))
        grand_total = kameez_total + shalwar_total
        
        # Create sales record
        sales_record = SalesRecord(
            inventory_id=bill.inventory_id,  # For backward compatibility
            kameez_inventory_id=bill.kameez_inventory_id,
            shalwar_inventory_id=bill.shalwar_inventory_id,
            company_name=company_name,  # For backward compatibility
            design_code=design_code,  # For backward compatibility
            kameez_company_name=kameez_company_name,
            kameez_design_code=kameez_design_code,
            shalwar_company_name=shalwar_company_name,
            shalwar_design_code=shalwar_design_code,
            kameez_meters=Decimal(str(bill.kameez_meters)),
            kameez_rate=Decimal(str(bill.kameez_rate)),
            kameez_total=kameez_total,
            shalwar_meters=Decimal(str(bill.shalwar_meters)),
            shalwar_rate=Decimal(str(bill.shalwar_rate)),
            shalwar_total=shalwar_total,
            grand_total=grand_total
        )
        
        db.add(sales_record)
        db.commit()
        db.refresh(sales_record)
        
        return sales_record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()

@app.get("/get-profit-loss")
def get_profit_loss():
    """Calculate profit/loss per design"""
    db = None
    try:
        db = SessionLocal()
        
        # Get all inventory items
        inventory_items = db.query(Inventory).all()
        
        result = []
        for item in inventory_items:
            # Get all sales for this inventory item - check all possible links
            # Old method: inventory_id
            sales_old = db.query(SalesRecord).filter(
                SalesRecord.inventory_id == item.id
            ).all()
            
            # New method: kameez_inventory_id
            sales_kameez = db.query(SalesRecord).filter(
                SalesRecord.kameez_inventory_id == item.id
            ).all()
            
            # New method: shalwar_inventory_id
            sales_shalwar = db.query(SalesRecord).filter(
                SalesRecord.shalwar_inventory_id == item.id
            ).all()
            
            total_revenue = Decimal('0')
            total_cost = Decimal('0')
            total_meters_sold = Decimal('0')
            
            # Process old method sales (both kameez and shalwar count)
            for sale in sales_old:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                meters_sold = kameez_m + shalwar_m
                revenue = sale.grand_total if sale.grand_total is not None else Decimal('0')
                cost = meters_sold * item.cost_price_per_meter
                
                total_revenue += revenue
                total_cost += cost
                total_meters_sold += meters_sold
            
            # Process kameez sales (only kameez meters count)
            for sale in sales_kameez:
                kameez_m = Decimal(str(sale.kameez_meters)) if sale.kameez_meters is not None else Decimal('0')
                # Only count revenue portion for kameez
                revenue_per_meter = sale.kameez_rate if sale.kameez_rate is not None else Decimal('0')
                revenue = kameez_m * revenue_per_meter
                cost = kameez_m * item.cost_price_per_meter
                
                total_revenue += revenue
                total_cost += cost
                total_meters_sold += kameez_m
            
            # Process shalwar sales (only shalwar meters count)
            for sale in sales_shalwar:
                shalwar_m = Decimal(str(sale.shalwar_meters)) if sale.shalwar_meters is not None else Decimal('0')
                # Only count revenue portion for shalwar
                revenue_per_meter = sale.shalwar_rate if sale.shalwar_rate is not None else Decimal('0')
                revenue = shalwar_m * revenue_per_meter
                cost = shalwar_m * item.cost_price_per_meter
                
                total_revenue += revenue
                total_cost += cost
                total_meters_sold += shalwar_m
            
            profit = total_revenue - total_cost
            
            if total_meters_sold > 0:  # Only include items with sales
                result.append({
                    "company_name": item.company_name,
                    "design_code": item.design_code,
                    "meters_sold": float(total_meters_sold),
                    "cost_price_per_meter": float(item.cost_price_per_meter),
                    "total_cost": float(total_cost),
                    "total_revenue": float(total_revenue),
                    "profit": float(profit),
                    "profit_percentage": float((profit / total_cost * 100)) if total_cost > 0 else 0
                })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()

@app.get("/api")
def read_root():
    return {"message": "Billing API is running"}
