# 🚀 Server Start Karne Ka Guide

## ✅ Database Setup Complete!

Aapka database ready hai:
- ✓ customers table
- ✓ items table  
- ✓ invoices table
- ✓ invoice_items table
- ✓ payments table

## Ab Server Start Karein:

### Step 1: Server Start
```bash
uvicorn main:app --reload
```

### Step 2: Browser Mein Kholo
- **Dashboard**: http://localhost:8000/
- **Admin Dashboard**: http://localhost:8000/admin.html
- **Sales Page**: http://localhost:8000/sales
- **API Documentation**: http://localhost:8000/docs

## Expected Output:

Terminal mein aisa dikhega:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Database tables created/verified
✓ Invoice counter sequence created/verified
✓ Database is ready
INFO:     Application startup complete.
```

## Sample Data Add Karne Ke Liye (Optional):

Agar test data chahiye:
```bash
python seed_data.py
```

Ye automatically:
- Sample customers add karega
- Sample items add karega
- Sample invoices add karega

## Server Stop Karne Ke Liye:
```
Ctrl + C
```

---

## 🎯 Quick Commands:

```bash
# Server start
uvicorn main:app --reload

# Sample data add
python seed_data.py

# Database verify
python verify_db.py

# Database check
python check_db.py
```

---

**Ab server start karein aur browser mein http://localhost:8000/ kholo!** 🎉
