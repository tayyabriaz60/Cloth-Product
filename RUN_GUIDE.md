# 🚀 Application Run Karne Ka Complete Guide

## Database Kya Hai?
**PostgreSQL** - Ye ek powerful database hai jo data store karta hai.

## Method 1: Docker Se Run (Sabse Aasan) ⭐

### Step 1: Docker Install Karein
- Agar Docker installed nahi hai, to pehle install karein:
  - Download: https://www.docker.com/products/docker-desktop
  - Install karke Docker Desktop start karein

### Step 2: Project Folder Mein Jao
```bash
cd Cloth-Product-master
```

### Step 3: Docker Compose Se Run Karein
```bash
docker-compose up --build
```

**Ye automatically:**
- ✅ PostgreSQL database start karega
- ✅ Database `billu` create karega
- ✅ Backend server start karega
- ✅ Port 8000 par application chalega

### Step 4: Browser Mein Open Karein
- **Dashboard**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin.html
- **Sales**: http://localhost:8000/sales

### Stop Karne Ke Liye:
```bash
Ctrl + C  (terminal mein)
```

---

## Method 2: Direct PostgreSQL Se Run

### Prerequisites:
1. **PostgreSQL Installed** hona chahiye
2. **Python 3.8+** installed hona chahiye

### Step 1: PostgreSQL Setup

#### Windows:
1. PostgreSQL install karein (agar nahi hai)
2. PostgreSQL service start karein:
   - Services app kholo
   - "postgresql" service ko start karo

#### Database Create Karein:
```sql
-- PostgreSQL command line ya pgAdmin se:
CREATE DATABASE billu;
```

Ya PowerShell/Command Prompt se:
```bash
psql -U postgres
CREATE DATABASE billu;
\q
```

### Step 2: Python Dependencies Install Karein

```bash
# Virtual environment create karein (recommended)
python -m venv venv

# Activate karein
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Dependencies install karein
pip install -r requirements.txt
```

### Step 3: .env File Banao

Project folder mein `.env` file banao aur ye content paste karein:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/billu
ALLOWED_ORIGINS=*
```

**Important:** `YOUR_PASSWORD` ki jagah apna PostgreSQL password likhein.

**Agar password nahi hai ya blank hai:**
```env
DATABASE_URL=postgresql://postgres@localhost/billu
```

### Step 4: Database Tables Create Karein

```bash
# Option 1: Migration script se
python migrate_database.py

# Option 2: Seed data se (tables auto create honge)
python seed_data.py
```

### Step 5: Backend Server Start Karein

```bash
uvicorn main:app --reload
```

### Step 6: Browser Mein Check Karein

- **Dashboard**: http://localhost:8000/
- **Admin Dashboard**: http://localhost:8000/admin.html
- **Sales Page**: http://localhost:8000/sales
- **API Documentation**: http://localhost:8000/docs

---

## ✅ Verification Steps

### 1. Database Connection Check:
```bash
python check_db.py
```

### 2. Database Verify:
```bash
python verify_db.py
```

### 3. Browser Console Check:
- Browser mein F12 press karein
- Console tab check karein
- Koi errors nahi hone chahiye

---

## 🔧 Troubleshooting

### Problem 1: Database Connection Error
```
Error: could not connect to server
```

**Solution:**
1. PostgreSQL service running hai ya nahi check karein
2. `.env` file mein correct password hai ya nahi
3. Database `billu` create hai ya nahi

**Check karne ke liye:**
```bash
psql -U postgres -l
```

### Problem 2: Port Already in Use
```
Error: [Errno 48] Address already in use
```

**Solution:**
```bash
# Different port use karein
uvicorn main:app --port 8001 --reload
```

Ya jo process port 8000 use kar raha hai, usko stop karein.

### Problem 3: Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Problem 4: Database Tables Missing
```
relation "customers" does not exist
```

**Solution:**
```bash
python migrate_database.py
```

---

## 📊 Database Details

- **Database Type**: PostgreSQL
- **Database Name**: `billu`
- **Default User**: `postgres`
- **Default Port**: `5432`
- **Tables**:
  - `customers` - Customer/Supplier data
  - `items` - Product items
  - `invoices` - Sales/Purchase invoices
  - `invoice_items` - Invoice line items
  - `payments` - Payment records

---

## 🎯 Quick Commands Summary

```bash
# Docker se run
docker-compose up

# Direct run
uvicorn main:app --reload

# Database check
python check_db.py

# Database verify
python verify_db.py

# Seed sample data
python seed_data.py

# Database migration
python migrate_database.py
```

---

## 📝 Important Notes

1. **Docker method** sabse aasan hai - automatically sab setup ho jata hai
2. **Direct method** ke liye PostgreSQL pehle se installed hona chahiye
3. **.env file** zaroor banao - database connection ke liye
4. **Port 8000** default hai - agar busy hai to change kar sakte hain
5. **Database password** `.env` file mein sahi hona chahiye

---

## 🆘 Help

Agar koi problem aaye to:
1. Terminal/Console errors check karein
2. Browser console (F12) check karein
3. Database connection verify karein
4. `.env` file settings check karein
