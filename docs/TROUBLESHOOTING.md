# Troubleshooting

## Gemini
- Error: `Gemini not available: package not installed`
  - Fix: `python -m pip install google-generativeai`
- Error: `404 models/gemini-1.5-flash is not found for API version v1beta ...`
  - Fix: Use a supported model (e.g., `gemini-2.5-flash`) in `config/gemini_config.py`
- Warning in UI: `AI Assistant chưa cấu hình`
  - Fix: Set `GeminiConfig.API_KEY` and restart

## Database
- Error: `Unknown database` on first run
  - The app auto-creates DB; ensure MySQL user has CREATE DATABASE privilege
- Cannot connect
  - Check `config/database_config.py` host/user/password; ensure MySQL service is running

## Models
- Active model missing
  - Ensure `outputs/models/*.pkl` exists, or set another active model in `model_registry`
- Training too slow
  - Reduce dataset size or model complexity; verify no CPU throttling; run outside UI if needed

## UI Freezes
- Long jobs should run in QThreads (as in `SystemManagementWidget`). If adding new heavy tasks, follow that pattern.

## Package Paths on Windows
- If scripts are installed to user site and not on PATH, use the full `python -m` form as shown in docs.

