@echo off
REM Start All Services Script for Windows

echo Starting Innovation Idea Submission Platform...

REM Start LiteLLM Service
echo Starting LiteLLM Service...
cd litellm_service
start "LiteLLM Service" cmd /k python main.py
cd ..

REM Wait for LiteLLM to start
timeout /t 3 /nobreak >nul

REM Start Node.js Backend
echo Starting Node.js Backend...
start "Node.js Backend" cmd /k npm run dev

echo.
echo All services started!
echo   - LiteLLM Service: http://localhost:8001
echo   - Node.js Backend: http://localhost:3000
echo.
echo Close the terminal windows to stop the services
