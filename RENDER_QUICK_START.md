# 🚀 Render Par Deploy - Quick Start (Urdu/Hindi)

## Step 1: GitHub Par Code Push Karein

```bash
# Agar git nahi initialize hai
git init

# Files add karein
git add .

# Commit karein
git commit -m "Ready for Render deployment"

# GitHub par repository banao, phir:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**Important:** `.env` file commit mat karein! Wo already `.gitignore` mein hai.

---

## Step 2: Render Par Database Create Karein

1. https://render.com par login karein
2. **"New +"** → **"PostgreSQL"** click karein
3. Settings:
   - **Name**: `billu-db`
   - **Database**: `billu`
   - **Plan**: Free (ya Starter)
4. **"Create Database"** click karein
5. 2-3 minutes wait karein

---

## Step 3: Web Service Deploy Karein

1. **"New +"** → **"Web Service"** click karein
2. **"Connect GitHub"** → Apna repository select karein
3. Settings:
   - **Name**: `clothes-billing-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - `ALLOWED_ORIGINS` = `*`
5. **Link Database**: `billu-db` select karein
6. **"Create Web Service"** click karein
7. Build complete hone ka wait karein (5-10 minutes)

---

## Step 4: Database Tables Create Karein

Deploy complete hone ke baad:

1. Render Dashboard → Apne service par jao
2. **"Shell"** tab click karein
3. Ye command run karein:
   ```bash
   python setup_database.py
   ```

---

## Step 5: Test Karein

Browser mein kholo:
- `https://your-app.onrender.com/`
- `https://your-app.onrender.com/docs`

---

## ✅ Done!

Agar koi problem aaye to `RENDER_DEPLOY.md` mein detailed guide dekhein.

---

## 🔧 Important Notes

1. **Free Plan**: 15 min inactivity ke baad sleep ho jata hai
2. **First Request**: Slow ho sakta hai (wake up time)
3. **Database URL**: Render automatically set karega
4. **Auto-Deploy**: GitHub push se automatically deploy hoga

---

**Good Luck! 🎉**
