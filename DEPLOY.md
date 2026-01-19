# Render Deployment Guide

## Step 1: Prepare Your Code

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

## Step 2: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and deploy

### Option B: Manual Setup

1. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `billu-db`
   - Plan: Free
   - Copy the **Internal Database URL**

2. **Create Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Settings:
     - **Name**: `clothes-billing-api`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   
3. **Environment Variables**
   - Add `DATABASE_URL` (from PostgreSQL service)
   - Render automatically provides `PORT`

4. **Deploy**
   - Click **"Create Web Service"**
   - Wait for deployment to complete
   - Your API will be available at: `https://your-app-name.onrender.com`

## Step 3: Update Frontend URLs

After deployment, update `config.js`:

```javascript
const API_BASE_URL = 'https://your-app-name.onrender.com';
```

Or keep it dynamic (already configured to auto-detect).

## Step 4: Access Your Application

- **Sales Page**: `https://your-app-name.onrender.com/`
- **Admin Dashboard**: `https://your-app-name.onrender.com/admin`
- **API Docs**: `https://your-app-name.onrender.com/docs`

## Important Notes

1. **Free Tier Limitations**:
   - Service sleeps after 15 minutes of inactivity
   - First request after sleep takes ~30 seconds
   - Database has 90-day retention on free tier

2. **Database Migration**:
   - Runs automatically on startup
   - Tables are created if they don't exist

3. **Static Files**:
   - HTML files are served from root
   - `config.js` should be in root directory

4. **CORS**:
   - Currently allows all origins (`*`)
   - For production, restrict to your domain

## Troubleshooting

- **Database Connection Error**: Check `DATABASE_URL` environment variable
- **404 on Routes**: Ensure `Procfile` or start command is correct
- **Static Files Not Loading**: Check file paths in HTML

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Render)

Optional:
- `ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins
- `PORT` - Server port (auto-provided by Render)
