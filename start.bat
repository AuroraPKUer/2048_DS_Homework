@echo off
title 2048 AI Solver Launcher

echo ======================================================
echo           2048 AI Solver - Launcher
echo ======================================================
echo.

:: 1. Check and install dependencies
echo [Step 1/2] Checking dependencies...
echo Running: pip install -r requirements.txt
pip install -r requirements.txt

echo.

:: 2. Launch the main script
echo [Step 2/2] Launching the game...
echo Running: python main.py
python main.py

:: Check if the program crashed
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The program crashed or failed to start.
    echo Please check if Python is added to your System PATH.
)

echo.
echo ======================================================
echo   Process finished. Press any key to exit.
echo ======================================================
pause > nul