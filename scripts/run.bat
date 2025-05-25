@echo off
REM ====================================================================
REM RAG PDF Pipeline - Run Script
REM This script activates the environment and starts the application
REM ====================================================================

echo.
echo ========================================
echo RAG PDF Pipeline - Starting Application
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the environment
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with your configuration
    echo You can copy from .env.example if available
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo ✓ Virtual environment activated
echo.

REM Check if required dependencies are installed
echo Checking dependencies...
python -c "import streamlit; print('✓ Streamlit available')" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Streamlit not found. Please run setup.bat first.
    pause
    exit /b 1
)

python -c "import chromadb; print('✓ ChromaDB available')" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: ChromaDB not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo ✓ Dependencies check passed
echo.

REM Check for LLM availability
echo Checking LLM availability...

REM Check Gemini API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ Gemini API key configured' if os.getenv('GEMINI_API_KEY') else '⚠ Gemini API key not configured')" 2>nul

REM Check Ollama availability
python -c "import requests; requests.get('http://localhost:11434/api/tags', timeout=2); print('✓ Ollama available')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠ Ollama not available at http://localhost:11434
    echo   Install Ollama from https://ollama.ai for local LLM support
)

echo.
echo ========================================
echo Starting Streamlit Application
echo ========================================
echo.
echo The application will open in your default web browser
echo Usually at: http://localhost:8501
echo.
echo To stop the application, press Ctrl+C in this window
echo.

REM Start the Streamlit application
streamlit run ui/streamlit_app.py --server.address localhost --server.port 8501

REM If streamlit command fails, try alternative
if %errorlevel% neq 0 (
    echo.
    echo Streamlit command failed, trying alternative...
    python -m streamlit run ui/streamlit_app.py --server.address localhost --server.port 8501
)

echo.
echo Application stopped.
pause