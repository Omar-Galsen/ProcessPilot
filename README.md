# ProcessPilot AI

AI-assisted chemical engineering learning platform with Dify integration and a FastAPI engineering calculator.

## Quick start

```bash
python -m venv .venv
source .venv/Scripts/activate # Git Bash on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload
```

Open `frontend/index.html` in a browser. Start Dify separately and configure `DIFY_API_KEY` in `.env` (load environment variables before launching the API). Backend API: http://localhost:8000/docs.

## Safety
Educational calculations only; verify units, assumptions and results before professional use. Never commit `.env` or secrets. Dify commercial licensing must be reviewed before offering multi-tenant services.
