@echo off
setlocal
title SPIT SWIFT Launcher

set "BASE=%~dp0"
set "BACKEND=%BASE%backend"
set "FRONTEND=%BASE%frontend"

echo.
echo ============================================================
echo   SPIT SWIFT Clinical Screening System v2.0
echo ============================================================
echo.

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 goto :python_error

echo [2/4] Checking Node.js...
call npm --version >nul 2>&1
if errorlevel 1 goto :node_error

echo [3/4] Checking backend dependencies...
python -c "import fastapi, uvicorn, joblib, numpy, pandas, sklearn" >nul 2>&1
if errorlevel 1 goto :dependency_error

if not exist "%FRONTEND%\node_modules\vite\bin\vite.js" (
    echo Installing frontend dependencies...
    pushd "%FRONTEND%"
    call npm install
    if errorlevel 1 (
        popd
        goto :npm_error
    )
    popd
)

echo [4/4] Starting backend and frontend...
start "SPIT SWIFT Backend" /D "%BACKEND%" cmd.exe /K python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
start "SPIT SWIFT Frontend" /D "%FRONTEND%" cmd.exe /K npm run dev

timeout /t 5 /nobreak >nul
start "" http://localhost:5173

echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000/docs
echo.
echo Two server windows were opened. Leave them running.
pause
exit /b 0

:python_error
echo [ERROR] Python was not found on PATH.
pause
exit /b 1

:node_error
echo [ERROR] Node.js/npm was not found on PATH.
pause
exit /b 1

:dependency_error
echo [ERROR] Backend packages are missing. Run:
echo         python -m pip install -r "%BACKEND%\requirements.txt"
pause
exit /b 1

:npm_error
echo [ERROR] npm install failed.
pause
exit /b 1
