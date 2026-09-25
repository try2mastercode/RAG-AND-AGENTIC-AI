@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\uvicorn.exe" (
    echo Virtual environment not found or incomplete.
    echo Run setup first - see the "Setup" section in README.md.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Warning: .env not found - copy .env.example to .env and set GROQ_API_KEY first.
    pause
    exit /b 1
)

if not exist "chroma_data\chroma.sqlite3" (
    echo Vector index not found - building it now from data\ ...
    .venv\Scripts\python.exe -m retrieval.index_builder
    if errorlevel 1 (
        echo Failed to build the vector index.
        pause
        exit /b 1
    )
)

start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000"

echo Starting California Restaurant ^& Recipe Recommender...
echo Opening http://127.0.0.1:8000 in your browser shortly.
echo Press Ctrl+C to stop the server.
echo.

.venv\Scripts\uvicorn.exe api.main:app --host 127.0.0.1 --port 8000

pause
