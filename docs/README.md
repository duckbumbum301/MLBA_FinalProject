# Credit Risk Scoring System — Handover Guide

This repository contains a role-based desktop application (PyQt6) for credit risk scoring with:
- Two roles: `User` and `Admin`
- ML model registry and switching (XGBoost, LightGBM, Logistic, CatBoost, RandomForest, NeuralNet, Voting, Stacking)
- Data quality analysis (outliers + clustering)
- Gemini AI assistant integration for explanations and reports
- MySQL backend with 7 core tables

If you are an AI IDE or a new developer, start here. This README orients you and links into deeper docs.

## Quick Start (Windows, PowerShell)

1) Install dependencies
```
python -m pip install -r requirements.txt
```

2) Configure database (MySQL 8+)
- Edit `config/database_config.py` if needed (host/user/password/database)
- First run auto-creates DB if missing

3) Configure Gemini API (optional but recommended)
- Open `config/gemini_config.py`
- Set `GeminiConfig.API_KEY = "<your-key>"`
- Ensure `GeminiConfig.MODEL_NAME = "gemini-2.5-flash"`

4) Run the app launcher test
```
python -m tests.test_app
```
Login with sample accounts:
- User: `babyshark` / `123`
- Admin: `fathershark` / `123`

## Project Map
- App entry (launcher): `tests/test_app.py`
- Config: `config/` (DB + Gemini)
- DB access: `database/` (connector + SQL)
- Services: `services/` (AI, model mgmt, data quality, queries)
- UI widgets: `ui/` (tabs, main window)
- Models/entities: `models/`
- Scripts: migration + utilities in root or `database/`/`scripts/`

## Role-Based Tabs
- User: Dự Báo Rủi Ro, Dashboard, AI Trợ Lý
- Admin: + Quản Lý ML, + Hệ Thống

## Read Next
- `docs/SETUP.md` — Environment, DB, API keys, paths
- `docs/ARCHITECTURE.md` — Layers, data flow, key classes
- `docs/DATABASE.md` — Tables, constraints, migrations
- `docs/SERVICES.md` — Service APIs and contracts
- `docs/UI.md` — Widgets, signals/slots, permissions
- `docs/ML_MODELS.md` — Model registry, training, adding models
- `docs/RUNBOOK.md` — Operate, test, common admin tasks
- `docs/TROUBLESHOOTING.md` — Known issues and fixes

