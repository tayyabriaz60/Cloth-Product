# 🚀 Render Par Deploy Karne Ka Complete Guide

## Prerequisites
1. **GitHub Account** - Code ko GitHub par push karna hoga
2. **Render Account** - https://render.com par sign up karein

---

## Step 1: Code Ko GitHub Par Push Karein

### Option A: Agar Already GitHub Par Hai
- Skip karein, directly Step 2 par jao

### Option B: Naya Repository Banana Hai

```bash
# Git initialize (agar nahi hai)
git init

# .gitignore check karein (important files add karein)
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# All files add karein
git add .

# Commit karein
git commit -m "Initial commit - Cloth Billing System"

# GitHub par naya repository banao, phir:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Important:** `.env` file ko **NEVER** commit karein! Wo already `.gitignore` mein hona chahiye.

---

## Step 2: Render Par Database Create Karein

### 2.1 Render Dashboard Mein Jao
1. https://render.com par login karein
2. Dashboard par **"New +"** button click karein
3. **"PostgreSQL"** select karein

### 2.2 Database Configuration
- **Name**: `billu-db` (ya koi bhi naam)
- **Database**: `billu`
- **User**: `postgres` (default)
- **Region**: Aapka nearest region select karein
- **PostgreSQL Version**: Latest (15 ya 16)
- **Plan**: **Free** (testing ke liye) ya **Starter** (production ke liye)

### 2.3 Database Create Karein
- **"Create Database"** button click karein
- Database create hone ka wait karein (2-3 minutes)
- **Internal Database URL** note karein (ye automatically `render.yaml` mein use hoga)

---

## Step 3: Web Service Deploy Karein

### 3.1 New Web Service
1. Render Dashboard mein **"New +"** click karein
2. **"Web Service"** select karein
3. **"Connect GitHub"** click karein (pehli baar)
4. Apna GitHub repository select karein

### 3.2 Service Configuration

**Basic Settings:**
- **Name**: `clothes-billing-api` (ya koi bhi naam)
- **Region**: Same region jahan database hai
- **Branch**: `main` (ya `master`)
- **Root Directory**: (blank rakhein, ya `.`)

**Build & Deploy:**
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

**OR** `render.yaml` file use karein (recommended):
- **"Infrastructure as Code"** section mein `render.yaml` automatically detect hoga
- Ya manually **"Advanced"** section mein specify karein

### 3.3 Environment Variables

**"Environment"** tab mein ye variables add karein:

1. **DATABASE_URL**
   - Value: Apne database ka **Internal Database URL** (Render automatically provide karega)
   - Ya manually: Database dashboard se **"Internal Database URL"** copy karein

2. **ALLOWED_ORIGINS**
   - Value: `*` (sab allow karne ke liye)
   - Ya specific domain: `https://your-app.onrender.com`

3. **PYTHON_VERSION** (optional)
   - Value: `3.11.0`

### 3.4 Database Link

**"Link Database"** section mein:
- Apna `billu-db` database select karein
- Ye automatically `DATABASE_URL` set kar dega

### 3.5 Deploy

- **"Create Web Service"** click karein
- Build process start hoga (5-10 minutes)
- Deploy complete hone ka wait karein

---

## Step 4: Database Tables Create Karein

Deploy complete hone ke baad, database tables create karni hongi.

### Option A: Render Shell Se (Recommended)

1. Render Dashboard mein apne **Web Service** par jao
2. **"Shell"** tab click karein
3. Ye command run karein:
   ```bash
   python setup_database.py
   ```

### Option B: Local Se (Agar Render Shell Available Nahi Hai)

1. Apne local machine se Render database connect karein
2. `DATABASE_URL` ko temporarily local `.env` mein set karein (Render se copy karein)
3. `python setup_database.py` run karein

### Option C: Seed Data Se

```bash
# Render Shell mein:
python seed_data.py
```

Ye automatically tables create karega + sample data add karega.

---

## Step 5: Verify Deployment

### 5.1 Check Service Status
- Render Dashboard mein service **"Live"** status dikhna chahiye
- **"Logs"** tab mein koi errors nahi hone chahiye

### 5.2 Test URLs
Browser mein ye URLs check karein:
- **Dashboard**: `https://your-app.onrender.com/`
- **Admin**: `https://your-app.onrender.com/admin.html`
- **Sales**: `https://your-app.onrender.com/sales`
- **API Docs**: `https://your-app.onrender.com/docs`

### 5.3 Database Verify
Render Shell mein:
```bash
python verify_db.py
```

---

## Step 6: Custom Domain (Optional)

1. **"Settings"** tab mein jao
2. **"Custom Domains"** section
3. Apna domain add karein
4. DNS settings configure karein (Render instructions dega)

---

## 🔧 Troubleshooting

### Problem 1: Build Fails
**Error**: `ModuleNotFoundError`

**Solution**:
- `requirements.txt` mein sab dependencies check karein
- Build logs check karein

### Problem 2: Database Connection Error
**Error**: `could not connect to server`

**Solution**:
- Environment variables check karein
- Database **Internal URL** use karein (external URL nahi)
- Database service running hai check karein

### Problem 3: Tables Not Found
**Error**: `relation "customers" does not exist`

**Solution**:
- Render Shell se `python setup_database.py` run karein
- Ya `python seed_data.py` run karein

### Problem 4: Port Error
**Error**: `Address already in use`

**Solution**:
- `$PORT` environment variable use karein (Render automatically set karta hai)
- `main.py` mein `os.getenv("PORT", 8000)` check karein

### Problem 5: Static Files Not Loading
**Solution**:
- HTML files project root mein hain check karein
- File paths correct hain check karein

---

## 📝 Important Notes

1. **Free Plan Limitations**:
   - Service 15 minutes inactivity ke baad sleep ho jata hai
   - First request slow ho sakta hai (wake up time)
   - Database 90 days inactivity ke baad delete ho sakta hai

2. **Environment Variables**:
   - `.env` file Render par kaam nahi karega
   - Sab variables Render Dashboard se set karni hongi

3. **Database URL**:
   - **Internal URL** use karein (same region mein)
   - External URL slow hoga

4. **Auto-Deploy**:
   - GitHub par push karne se automatically deploy hoga
   - Manual deploy bhi kar sakte hain

5. **Logs**:
   - Render Dashboard mein **"Logs"** tab se sab logs dekh sakte hain
   - Errors debugging ke liye useful hain

---

## 🎯 Quick Checklist

- [ ] Code GitHub par push ho gaya
- [ ] Render account create ho gaya
- [ ] PostgreSQL database create ho gaya
- [ ] Web service create ho gaya
- [ ] Environment variables set ho gaye
- [ ] Database linked ho gaya
- [ ] Build successful ho gaya
- [ ] Database tables create ho gaye
- [ ] Application working hai

---

## 🚀 Production Tips

1. **Starter Plan** use karein (free plan se better)
2. **Environment Variables** properly set karein
3. **Database Backups** enable karein
4. **Custom Domain** setup karein
5. **Monitoring** enable karein
6. **Error Tracking** (Sentry) add karein

---

## 📞 Support

Agar koi problem aaye:
1. Render Dashboard mein **"Logs"** check karein
2. Render documentation: https://render.com/docs
3. Render community: https://community.render.com

---

**Good Luck! 🎉**
