# Sleepsia Reporting — Setup Guide

A complete local setup guide for the Sleepsia Agentic Business Reporting System — MySQL, FastAPI backend, and the React/Vite dashboard — covering macOS/Linux and Windows, plus a reference for which database table changes show up on which dashboard screen.

## Stack overview

| Layer | Technology | Port |
|---|---|---|
| Database | MySQL 8 (via Docker) | 3306 (or 3307 if 3306 is already taken) |
| Backend | FastAPI + SQLAlchemy | 8000 |
| Frontend | React + Vite | 3000 |

Data flow: `MySQL → FastAPI (/api/*) → React dashboard`. There is no caching layer anywhere in this chain — every request hits MySQL live. The dashboard only re-fetches on page load or when a filter changes; it does not poll or auto-refresh.

---

## Prerequisites (all platforms)

- **Docker Desktop** — for MySQL. On Windows this requires WSL2 (Docker Desktop installer offers to enable it).
- **Python 3.11+**
- **Node.js 18+** and npm
- **Git**

You do **not** need to install a separate MySQL client — schema loading is done through `docker exec` into the container, so nothing extra is required on the host.

---

## macOS / Linux setup

```bash
# 1. Clone and enter the repo
cd /path/to/Sleepsia-Agentic-Report

# 2. Start MySQL
docker compose up -d

# 3. Wait for MySQL to accept connections, then load the schema + views
until docker exec sleepsia-mysql mysqladmin ping -h 127.0.0.1 -u root -proot --silent; do sleep 2; done
docker exec -i sleepsia-mysql mysql -u sleepsia -psleepsia sleepsia_reporting < sql/schema.sql

# 4. Set up the backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Load the actual business data from the Excel workbook
python etl/run_etl.py

# 6. Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In a second terminal:

```bash
cd /path/to/Sleepsia-Agentic-Report/dashboard
npm install
npm run dev
```

Open `http://localhost:3000`.

---

## Windows setup (PowerShell)

Everything is the same *shape* as macOS/Linux — the differences are venv activation, path separators, and how you redirect a `.sql` file into a command.

```powershell
# 1. Enter the repo
cd C:\path\to\Sleepsia-Agentic-Report

# 2. Start MySQL (Docker Desktop must be running first)
docker compose up -d

# 3. Wait for MySQL, then load the schema + views
# (PowerShell doesn't support "<" redirection into external commands — pipe with Get-Content instead)
do { Start-Sleep -Seconds 2 } while (-not (docker exec sleepsia-mysql mysqladmin ping -h 127.0.0.1 -u root -proot --silent))
Get-Content sql\schema.sql | docker exec -i sleepsia-mysql mysql -u sleepsia -psleepsia sleepsia_reporting

# 4. Set up the backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 5. Load business data
python etl\run_etl.py

# 6. Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In a second PowerShell window:

```powershell
cd C:\path\to\Sleepsia-Agentic-Report\dashboard
npm install
npm run dev
```

Open `http://localhost:3000`.

### Windows-specific notes

- **Script execution blocked?** If `Activate.ps1` refuses to run, PowerShell's execution policy is blocking it. Run once per session: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
- **Using Command Prompt (cmd.exe) instead of PowerShell?** Venv activation is `venv\Scripts\activate.bat`, and `<` redirection *does* work in cmd, so you can use the same `docker exec -i ... mysql ... < sql\schema.sql` form as macOS/Linux.
- **Windows Firewall prompt** on first `docker compose up` or `uvicorn`/`npm run dev` — allow access on private networks; it's just Windows asking permission for a new listener on 8000/3000/3306.
- **Line endings:** if you hand-edit `backend\.env` in Notepad, save as UTF-8 without BOM. Editors that insert CRLF are fine — Python's `dotenv` handles it, but avoid stray trailing whitespace after values.

---

## Port conflict (either platform)

If `docker compose up -d` fails with `address already in use` on port 3306, something else on the machine already has MySQL bound there (very common on Windows if MySQL Server was ever installed as a Windows Service, or on macOS if it was installed via the MySQL installer/Homebrew outside Docker). Fix by moving Docker's MySQL to a different host port:

1. In `docker-compose.yml`, change `"3306:3306"` → `"3307:3306"`.
2. In `backend/.env`, change `DB_PORT=3306` → `DB_PORT=3307`.
3. Re-run `docker compose up -d` and the schema-load command (adjust `-P 3307` if connecting from a GUI client like MySQL Workbench).

Everything else — the ETL, the API, the dashboard — is unaffected, since they all read the port from `backend/.env`.

---

## Verifying it worked

```bash
curl http://localhost:8000/health   # {"status": "healthy", ...}
curl http://localhost:8000/ready    # {"ready": true, ...}  <- confirms DB connectivity
```

On the dashboard, the Executive Dashboard should show non-zero KPI tiles immediately. If everything is zero, the ETL step didn't run or pointed at the wrong database — re-check step 5/6 and that `backend/.env`'s `DB_NAME` matches what you loaded the schema into.

---

## Data → screen mapping

Which table to edit when you want to see a specific number change on a specific screen, traced through the actual views and API services (not guessed):

| Table | Feeds | Screens affected |
|---|---|---|
| `daily_sales` | `vw_product_platform_daily` → `vw_daily_kpi_summary` | Executive Dashboard (KPI tiles, revenue trend chart, top/bottom product widgets), Platform Analysis, Product Analysis, Profitability |
| `advertising` | `vw_product_platform_daily` | Executive Dashboard (ad spend/ROAS), Advertising page, Platform Analysis (ROAS/ACOS), Product Analysis (ROAS/ACOS), Profitability |
| `daily_costs` | `vw_product_platform_daily` (contribution_inr, profit_margin_pct) | Executive Dashboard (profit/margin KPI), Platform Analysis (margin), Product Analysis (margin, "bottom products" ranking), Profitability |
| `returns` | `vw_product_platform_daily` | Executive Dashboard (return-rate KPI), Platform Analysis (return-rate column) |
| `cancellations` | `vw_product_platform_daily` | Executive Dashboard (cancellation-rate KPI) |
| `products` | joined into `vw_product_platform_daily`, `vw_inventory_health` | Only relabels product names. **Note:** `products.product_cost` is *not* used in any profit calculation — `daily_costs.product_cost` is. Editing the former changes nothing on screen. |
| `platforms` | joined into every view | Only relabels platform names. **Note:** `platforms.default_platform_fee_pct` is unused — `daily_costs.platform_fee` is what actually drives margin. |
| `warehouses` | `vw_warehouse_summary`, `vw_inventory_health`, queried directly | Inventory & Warehouse page — map pins, warehouse list. A null lat/lng will crash the map (known open issue). |
| `inventory_daily` | `vw_inventory_health`, `vw_warehouse_summary` | Inventory & Warehouse page, entirely. Warehouse health badges only ever reflect the single latest `inventory_date` row per warehouse, regardless of any date filter. |
| `replenishment_alerts` | queried directly | Alerts page, plus the alert-count badge on the Executive Dashboard |
| `regional_sales` | `vw_regional_performance` (view exists, unused) | Nothing yet — no page or API route reads this table. Matches the not-yet-built "Regional demand analysis" feature. |

**Two things to remember when testing by editing data directly:**

1. Changes don't appear until you reload the dashboard tab or touch a filter — there's no push/auto-refresh, but also no cache, so a refresh always shows the true current state.
2. `inventory_daily` / `replenishment_alerts` changes only show up on Inventory/Alerts if the row's date is *today's actual date* on the server — both endpoints match on an exact date rather than falling back to the latest available one. If you're testing with historical dates, this is why the page will look empty.
