# Environment Setup Guide

## Local Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
```bash
# Copy the example file
cp .env.example .env
```

### 3. Update .env File
Open `.env` file and update with your local database credentials:
```
DATABASE_URL=postgresql://postgres:tayyab@localhost/billu
ALLOWED_ORIGINS=*
```

### 4. Run the Application
```bash
uvicorn main:app --reload
```

## Render Production Setup

### Step 1: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Settings:
   - **Name**: `billu-db` (or any name you prefer)
   - **Database**: `billu`
   - **User**: `postgres` (default)
   - **Plan**: Free (or choose paid plan)
4. Click **"Create Database"**
5. Wait for database to be created

### Step 2: Get Database URL

1. Click on your database service
2. Go to **"Connections"** tab
3. Copy the **"Internal Database URL"**
   - Format: `postgresql://user:password@host:port/database`
   - Example: `postgresql://postgres:abc123@dpg-xxxxx-a.oregon-postgres.render.com/billu`

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Settings:
   - **Name**: `clothes-billing-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables

In the Web Service settings, go to **"Environment"** section and add:

1. **DATABASE_URL**
   - Key: `DATABASE_URL`
   - Value: Paste the Internal Database URL from Step 2
   - Example: `postgresql://postgres:abc123@dpg-xxxxx-a.oregon-postgres.render.com/billu`

2. **ALLOWED_ORIGINS** (Optional)
   - Key: `ALLOWED_ORIGINS`
   - Value: `*` (for all) or your specific domain
   - Example: `https://your-app.onrender.com`

### Step 5: Link Database to Web Service (Optional but Recommended)

1. In Web Service settings
2. Go to **"Environment"** tab
3. Click **"Link Database"**
4. Select your PostgreSQL database
5. Render will automatically add `DATABASE_URL` environment variable

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment to complete
3. Your app will be live at: `https://your-app-name.onrender.com`

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `*` or `https://app.com` |
| `PORT` | Server port (auto-set by Render) | `10000` |

## Important Notes

1. **Never commit .env file** - It's already in `.gitignore`
2. **Use Internal Database URL** on Render (not External)
3. **Database migration** runs automatically on startup
4. **Free tier** databases sleep after inactivity

## Troubleshooting

### Database Connection Error
- Check `DATABASE_URL` format (should start with `postgresql://`)
- Verify database is running on Render
- Check if database is linked to web service

### CORS Issues
- Update `ALLOWED_ORIGINS` in environment variables
- Use `*` for development, specific domains for production

### Migration Errors
- Check database connection
- Verify all required columns exist
- Check Render logs for detailed errors
