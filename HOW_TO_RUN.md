# Backend Run Karne Ka Guide

## Quick Start (3 Steps)

### Step 1: Dependencies Install
```bash
pip install -r requirements.txt
```

### Step 2: .env File Banao
`.env` file banao project folder mein aur ye content paste karein:
```
DATABASE_URL=postgresql://postgres:tayyab@localhost/billu
ALLOWED_ORIGINS=*
```

**Note**: Agar aapka PostgreSQL password different hai, to `tayyab` ki jagah apna password likhein.

### Step 3: Backend Run
```bash
uvicorn main:app --reload
```

## Complete Steps

### 1. PostgreSQL Setup
- PostgreSQL installed aur running hona chahiye
- Database `billu` create hona chahiye:
  ```sql
  CREATE DATABASE billu;
  ```

### 2. Virtual Environment (Optional but Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
`.env` file banao:
```
DATABASE_URL=postgresql://postgres:tayyab@localhost/billu
ALLOWED_ORIGINS=*
```

### 5. Run Backend
```bash
uvicorn main:app --reload
```

## Verify Backend Running

Browser mein check karein:
- **Sales Page**: http://localhost:8000/
- **Admin Dashboard**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api

## Expected Output

Terminal mein dikhega:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✓ DATABASE_URL found
✓ Database tables created/verified
✓ Database is up to date - all columns exist
```

## Common Commands

```bash
# Run with reload (development)
uvicorn main:app --reload

# Run on specific port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run without reload (production)
uvicorn main:app --host 0.0.0.0 --port 8000

# Stop server
Ctrl + C
```

## Troubleshooting

### Database Connection Error
- PostgreSQL service running hai ya nahi check karein
- `.env` file mein correct `DATABASE_URL` hai ya nahi verify karein
- Database `billu` create hai ya nahi check karein

### Port Already in Use
```bash
# Different port use karein
uvicorn main:app --port 8001 --reload
```

### Module Not Found
```bash
# Dependencies install karein
pip install -r requirements.txt
```
