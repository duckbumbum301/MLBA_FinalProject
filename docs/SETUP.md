# Setup Guide (Windows / PowerShell)

This guide prepares a fresh machine to run and develop the app.

## Prerequisites
- Python 3.12+ (works with 3.10–3.14; repo uses 3.14 in examples)
- MySQL Server 8.x with a user that can create DBs
- PowerShell (default on Windows)

## Python Environment
You can install globally or use a virtual environment.

- Global (simple):
```
python -m pip install -r requirements.txt
```

- Virtual environment (recommended for isolation):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## MySQL Configuration
Edit `config/database_config.py` if your MySQL differs from defaults:
- `host`, `port`, `user`, `password`, `database`
The app auto-creates `credit_risk_db` if it doesn't exist (with UTF8MB4).

First connection logs will show:
- `✓ Đã tạo và kết nối database: credit_risk_db` or
- `✓ Đã kết nối tới database: credit_risk_db`

If you need to seed or migrate tables quickly, see:
- `quick_db_update.py`
- `update_database_schema.py`

## Gemini API Setup (Optional but recommended)
- Open `config/gemini_config.py`
- Set `GeminiConfig.API_KEY` to your key
- Ensure model is supported: `MODEL_NAME = "gemini-2.5-flash"`
- Install package if missing (already in `requirements.txt`): `google-generativeai`

## Verifying Install
```
python -m tests.test_app
```
You should see login screen; use one of the demo users.

## Paths and Outputs
- Models saved to `outputs/models/*.pkl`
- Evaluation artifacts to `outputs/evaluation/*`
- Logs are primarily console-based; DB tables include operational logs (e.g., `data_quality_log`, `model_registry`).

