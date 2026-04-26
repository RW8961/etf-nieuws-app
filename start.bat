@echo off
title ETF Nieuws App

echo Starten...

start "ETF Nieuws - Backend" /MIN powershell.exe -NoExit -Command "Set-Location '%~dp0backend'; .\.venv\Scripts\python.exe -m uvicorn main:app --port 8000"

start "ETF Nieuws - Frontend" /MIN powershell.exe -NoExit -Command "Set-Location '%~dp0frontend'; $env:PATH = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); npm run dev"

timeout /t 6 /nobreak >nul

start http://localhost:5173
