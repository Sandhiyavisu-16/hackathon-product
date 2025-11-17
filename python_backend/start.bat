@echo off
echo Starting Python Backend...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found. Run: python -m venv venv
)

echo.
echo Starting FastAPI server on port 3000...
python main.py

pause
