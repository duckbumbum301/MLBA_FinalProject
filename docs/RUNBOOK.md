# Runbook — Operating & Testing

## Launching the App
```
python -m tests.test_app
```
Expected: Login window → use demo accounts.

## Accounts
- User: `babyshark` / `123`
- Admin: `fathershark` / `123`

## Admin Tasks
- Switch Active Model: `🎯 Quản Lý ML` → select row → Set Active
- Train Model: `🎯 Quản Lý ML` → choose algorithm → Train
- Data Quality: `⚙️ Hệ Thống` → choose method → Detect Outliers / Cluster

## AI Assistant
- Requires `GeminiConfig.API_KEY` and supported model name (e.g., `gemini-2.5-flash`)
- If unconfigured, input is disabled and warning banner is shown

## Logs & Observability
- Console logging (run in a terminal to capture)
- Operational data saved to DB tables (`model_registry`, `data_quality_log`, `ai_chat_history`, etc.)

## Tests / Sanity
- Launcher sanity: `python -m tests.test_app`
- Add unit tests under `tests/` (not exhaustive in this repo)

## Backups
- Back up `outputs/models` and DB regularly
