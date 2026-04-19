@echo off
echo Starting MedScan AI Backend...
start cmd /k "cd backend && set PYTHONPATH=. && set PYTHONIOENCODING=utf8 && .\venv\Scripts\python.exe -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting MedScan AI Frontend...
start cmd /k "cd frontend && npm run dev"

echo Both servers are starting in separate windows!
echo Backend API will be available at: http://localhost:8000/docs
echo Frontend UI will be available at: http://localhost:5173
