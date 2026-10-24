@echo off
title FaceAttend - Starting Backend + Frontend
echo.
echo  =======================================
echo   FaceAttend - Full Stack Launcher
echo  =======================================
echo.

:: Start Backend
echo [1/2] Starting Backend (FastAPI) on port 8000...
start "FaceAttend Backend" cmd /k "cd /d D:\Face Sure\backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Small delay to let backend initialize
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [2/2] Starting Frontend (Vite) on port 5173...
start "FaceAttend Frontend" cmd /k "cd /d D:\Face Sure\frontend && npm run dev"

echo.
echo  Both servers launching!
echo  Backend:  http://127.0.0.1:8000
echo  Frontend: http://127.0.0.1:5173
echo  API Docs: http://127.0.0.1:8000/docs
echo.
pause
