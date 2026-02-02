# 🚀 Quick Start Guide (Urdu/Hindi)

## Database Kya Hai?
**PostgreSQL** - Ye application ka database hai jo sab data store karta hai (customers, items, invoices, etc.)

## ⚡ Sabse Tez Tarika (Docker)

### Step 1: Docker Desktop Install Karein
- https://www.docker.com/products/docker-desktop se download karein
- Install karke start karein

### Step 2: Terminal Mein Ye Command Chalao
```bash
docker-compose up --build
```

### Step 3: Browser Mein Kholo
- http://localhost:8000/

**Bas! Ho gaya!** 🎉

---

## 📋 Manual Setup (Agar Docker Nahi Hai)

### Step 1: PostgreSQL Install & Setup
1. PostgreSQL install karein (agar nahi hai)
2. Database create karein:
```sql
CREATE DATABASE billu;
```

### Step 2: .env File Banao
Project folder mein `.env` file banao:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/billu
ALLOWED_ORIGINS=*
```
**Note:** `YOUR_PASSWORD` ki jagah apna PostgreSQL password likhein.

### Step 3: Dependencies Install
```bash
pip install -r requirements.txt
```

### Step 4: Database Tables Create
```bash
python migrate_database.py
```
Ya:
```bash
python seed_data.py
```

### Step 5: Server Start
```bash
uvicorn main:app --reload
```

### Step 6: Browser Mein Kholo
- http://localhost:8000/

---

## ✅ Check Karne Ke Liye

### Database Connection:
```bash
python check_db.py
```

### Database Verify:
```bash
python verify_db.py
```

---

## 🔧 Common Problems

### Database Connection Error?
- PostgreSQL service running hai check karein
- `.env` file mein password sahi hai check karein
- Database `billu` create hai check karein

### Port Busy?
```bash
uvicorn main:app --port 8001 --reload
```

### Module Not Found?
```bash
pip install -r requirements.txt
```

---

## 📝 Important Files

- `main.py` - Main application code
- `.env` - Database configuration (aapko banana hoga)
- `docker-compose.yml` - Docker setup
- `requirements.txt` - Python dependencies
- `migrate_database.py` - Database setup script

---

## 🎯 Summary

**Docker Method (Recommended):**
```bash
docker-compose up
```

**Manual Method:**
1. PostgreSQL install + database create
2. `.env` file banao
3. `pip install -r requirements.txt`
4. `python migrate_database.py`
5. `uvicorn main:app --reload`

---

**Detailed guide ke liye `RUN_GUIDE.md` dekhein!**
