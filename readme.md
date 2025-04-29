# Currency App

A desktop application for managing currencies, deposits, debts and user audit logs, with a FastAPI backend (Oracle DB) and a PyQt5 frontend.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Configure environment](#2-configure-environment)
  - [3. Build & Run Backend](#3-build--run-backend)
  - [4. Build Frontend Executable (optional)](#4-build-frontend-executable-optional)
  - [5. Launcher (optional)](#5-launcher-optional)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Prerequisites

- **Docker** (Engine & CLI) installed and running
- **Oracle Database** reachable at `host.docker.internal:1521` (or update `DATABASE_URL`)
- Windows environment (for PyQt5 executable)

## Architecture

```
┌────────────┐      HTTP       ┌──────────────┐
│ PyQt5 GUI  │ <────────────> │ FastAPI API  │
└────────────┘                 └──────────────┘
      ↑                              ↑
      │ SQLite/Oracle via Docker     │ Oracle
      │                              │
┌────────────┐                 ┌──────────────┐
│GestiFin pro.exe │           │ alembic     │
└────────────┘                 └──────────────┘
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/mdmdm1/currency_app.git
cd currency_app
```

### 2. Configure environment

Copy `.env.example` to `.env` and update your Oracle database credentials if needed:

```env
DATABASE_URL=oracle+cx_oracle://admin:2024@host.docker.internal:1521/?service_name=management4


```

default app user: username: admin password: admin123

2.1 Create Oracle Database (if not yet created)
Ensure you have an Oracle database instance available. You can create one locally using Oracle XE or any edition.

To create a service named management4 with user admin and password 2024:

Log into Oracle SQLPlus or use any Oracle client:

sql
Copier
Modifier
-- Connect as system user
sqlplus sys as sysdba
Create a user and service:

sql
Copier
Modifier
-- Create user
CREATE USER admin IDENTIFIED BY 2024;

-- Grant privileges
GRANT CONNECT, RESOURCE, DBA TO admin;

-- (Optional) Create a pluggable database or service alias if using Oracle XE:
-- You may need to configure tnsnames.ora to reflect a SERVICE_NAME = management4
📝 If you're using Docker for Oracle, make sure to expose port 1521 and allow remote access. Then verify your service_name is set to management4 inside your container's database setup.

yaml
Copier
Modifier

---

### 3. Build & Run Backend

1. **Build Docker image**
   ```bash
   docker build -t currency-backend-container ./backend
   ```
2. **Run the container**

   ```bash
   docker run -d -p 8000:8000 --name currency-backend-container currency-backend
   ```

3. **Verify**
   Visit http://localhost:8000/docs in your browser.

### 4. Build Frontend Executable

_In a Windows dev environment with Python3:_

```bash
cd frontend
pip install -r requirements.txt
python -m PyInstaller  main.spec
# The EXE will be under dist/frontend.exe
```

### 5. Launcher

```bash
cd dist
python -m PyInstaller --name "GestiFin Pro" --onefile --windowed `
    --add-data "C:\Users\medma\Desktop\Currency_app\frontend\dist\main.exe;." `
    --add-data "C:\Users\medma\Desktop\Currency_app\frontend\translations;translations" `
    --add-data "C:\Users\medma\Desktop\Currency_app\frontend\icons;icons" `
    --add-data "C:\Users\medma\Desktop\Currency_app\frontend\style.css;." `
    --icon "C:\Users\medma\Desktop\Currency_app\frontend\icons\app-icon.ico" `
    --hidden-import PyQt5 `
    --hidden-import PyQt5.QtCore `
    --hidden-import PyQt5.QtGui `
    --hidden-import PyQt5.QtWidgets `
    --hidden-import requests `
    --hidden-import database `
    --hidden-import utils `
    --hidden-import pages `
    --hidden-import dialogs `
    launcher.py

```

Double‑click `GestiFin Pro.exe` to:

1. Ensure the backend container is running
2. Launch the GUI

---

## Usage

- **Login** with an existing user.
  username:admin, password:admin123
- Navigate tabs: Currencies, Deposits, Debts, Users, Audit Logs.
- All actions are logged in the audit table and visible under "Recent Activities".

## Troubleshooting

- **Listener errors**: Ensure Oracle listener is up on port 1521;
  update `host.docker.internal` if using Linux host.
- **cx_Oracle DPI-1047**: Install Oracle Instant Client within Docker.
- **Port conflicts**: Change `-p 8000:8000` mapping or host port.

## License

MIT © DevGiants Mohamed Mahmoud Hawbett
