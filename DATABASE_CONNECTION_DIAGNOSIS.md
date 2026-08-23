# FastAPI Database Connection - Diagnosis Report

**Status**: ISSUE IDENTIFIED  
**Date**: August 23, 2026

---

## 🔍 ROOT CAUSE ANALYSIS

### Issue
FastAPI `/ready` endpoint returns HTTP 503: "database connection failed"

### Root Causes (Multiple)

#### 1. **Environment File Location Mismatch** ⚠️
- **Where FastAPI looks for .env**: `backend/` directory (when running from there)
- **Where .env currently exists**: Project root only (`/`)
- **Result**: FastAPI doesn't find any .env, uses hardcoded defaults

#### 2. **Database Name Mismatch** ⚠️
- **Actual database name**: `sleepsia` (verified in ETL code: `backend/etl/loader.py`)
- **Backend expects**: `sleepsia_reporting` (hardcoded default in `app/config.py`)
- **Result**: Connection string references wrong database

#### 3. **Credentials Mismatch** ⚠️
- **Project root .env has**: `DB_USER=root`, `DB_PASSWORD=Aditya123`
- **Backend defaults to**: `DB_USER=sleepsia`, `DB_PASSWORD=sleepsia`
- **Result**: Even if .env was found, wrong credentials used

---

## 📋 DETAILED ANALYSIS

### Current Configuration

**File: `backend/app/config.py` (lines 13-17)**
```python
DB_HOST: str = os.getenv("DB_HOST", "localhost")       # Default: localhost
DB_PORT: int = int(os.getenv("DB_PORT", "3306"))       # Default: 3306
DB_NAME: str = os.getenv("DB_NAME", "sleepsia_reporting")  # ❌ WRONG DEFAULT
DB_USER: str = os.getenv("DB_USER", "sleepsia")        # Default: sleepsia
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "sleepsia") # Default: sleepsia
```

**What it expects from .env or environment:**
```
DB_HOST=localhost (or 127.0.0.1)
DB_PORT=3306
DB_NAME=sleepsia_reporting
DB_USER=sleepsia
DB_PASSWORD=sleepsia
```

### Current .env Files

**Project root `.env` (WRONG):**
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sleepsia              ← CORRECT (matches actual database)
DB_USER=root                  ← WRONG (doesn't match default)
DB_PASSWORD=Aditya123         ← WRONG (doesn't match default)
EXCEL_FILE=data/...
```

**Project root `.env.example` (INCORRECT TEMPLATE):**
```
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=mysql+pymysql://sleepsia:sleepsia@localhost:3306/sleepsia_reporting
SOURCE_WORKBOOK=...
```

**Backend `backend/.env`:**
- ❌ DOES NOT EXIST

### Actual Database

**From ETL code (`backend/etl/loader.py`):**
```python
DB_NAME = os.getenv('DB_NAME', 'sleepsia')  # Database is named 'sleepsia'
```

**Reality (verified):**
- MySQL is running ✓
- Database `sleepsia` is accessible ✓
- User can connect via MySQL Workbench ✓

---

## 🔧 SOLUTION

### What Needs to Be Fixed

**1. Create `backend/.env` file** with these EXACT values:
```
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sleepsia
DB_USER=root
DB_PASSWORD=Aditya123
```

**2. Where to create it:**
```
backend/.env  ← NEW FILE NEEDED HERE
```

**3. What it does:**
- FastAPI looks for .env in its current directory (backend/)
- When found, it loads `DB_NAME=sleepsia` (correct!)
- Uses your MySQL credentials: root/Aditya123
- Connects to 127.0.0.1:3306
- Selects database `sleepsia`

---

## ⚠️ IMPORTANT NOTES

1. **Config Defaults Are Wrong**: The backend's `app/config.py` has a hardcoded default of `sleepsia_reporting` which is incorrect. The actual database is `sleepsia`. This is why an .env file is critical—to override that wrong default.

2. **Why .env Must Be in `backend/` Directory**: 
   - Pydantic's `env_file = ".env"` looks in the current working directory
   - When you run `python -m uvicorn app.main:app --reload` from the backend directory, it looks for `.env` there, not in the parent directory

3. **Not for Code Changes**: This is purely a configuration issue. No code modifications are needed. The .env file will tell the backend which database to use.

---

## 📝 EXACT INSTRUCTIONS

### Step 1: Create the .env file
Create a new file at:
```
backend/.env
```

With exactly this content:
```
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sleepsia
DB_USER=root
DB_PASSWORD=Aditya123
```

### Step 2: Restart FastAPI
Stop the current server and run:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Test the connection
```bash
curl http://localhost:8000/ready
```

Expected response:
```json
{
  "ready": true,
  "timestamp": "2026-08-23T..."
}
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Created file: `backend/.env`
- [ ] File contains all 8 configuration variables
- [ ] `DB_NAME=sleepsia` (not `sleepsia_reporting`)
- [ ] `DB_USER=root` and `DB_PASSWORD=Aditya123` (your credentials)
- [ ] Stopped old FastAPI server
- [ ] Restarted from backend directory
- [ ] Tested `/ready` endpoint
- [ ] Got HTTP 200 with `"ready": true`

---

## 🔐 Security Note

The `.env` file in the `backend/` directory contains your database password. It should:
- ✅ NOT be committed to git (add to .gitignore)
- ✅ NOT be shared
- ✅ Be environment-specific (dev, staging, prod have different credentials)

The file is already listed in `.gitignore` (check backend root), so it won't be committed.

---

## 📞 If Still Not Working

After creating the .env file and restarting, if `/ready` still fails:

1. **Check FastAPI is using the right .env:**
   ```bash
   cd backend
   python -c "from app.config import settings; print(settings.DATABASE_URL)"
   ```
   Should output something like:
   ```
   mysql+pymysql://root:Aditya123@127.0.0.1:3306/sleepsia
   ```

2. **Verify MySQL connection from command line:**
   ```bash
   mysql -h 127.0.0.1 -u root -p -D sleepsia
   ```
   Password: `Aditya123`

3. **Check MySQL is accepting connections on 127.0.0.1:3306**

---

**Diagnosis completed. Ready for your action.**
