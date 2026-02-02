# ✅ Render Deploy Checklist

## Pre-Deployment

- [ ] Code GitHub par push ho gaya
- [ ] `.env` file `.gitignore` mein hai (check karein)
- [ ] `render.yaml` file ready hai
- [ ] `requirements.txt` complete hai
- [ ] Local testing successful hai

## Render Setup

### Database
- [ ] Render account create ho gaya
- [ ] PostgreSQL database create ho gaya
- [ ] Database name: `billu-db`
- [ ] Database internal URL note kar liya

### Web Service
- [ ] GitHub repository connect ho gaya
- [ ] Web service create ho gaya
- [ ] Environment variables set ho gaye:
  - [ ] `DATABASE_URL` (database se auto-link)
  - [ ] `ALLOWED_ORIGINS` = `*`
- [ ] Database linked ho gaya

## Post-Deployment

- [ ] Build successful ho gaya
- [ ] Service "Live" status dikh raha hai
- [ ] Database tables create ho gaye (Shell se `python setup_database.py`)
- [ ] Application URLs working hain:
  - [ ] https://your-app.onrender.com/
  - [ ] https://your-app.onrender.com/docs
  - [ ] https://your-app.onrender.com/admin.html

## Testing

- [ ] Dashboard load ho raha hai
- [ ] API endpoints working hain
- [ ] Database operations working hain
- [ ] No errors in logs

---

## Quick Commands (Render Shell)

```bash
# Database setup
python setup_database.py

# Verify database
python verify_db.py

# Add sample data (optional)
python seed_data.py
```

---

**Deploy hone ke baad ye checklist follow karein!** ✅
