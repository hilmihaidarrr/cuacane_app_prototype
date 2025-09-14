@echo off
cd /d "%~dp0"
title Cuacane Launcher
echo ========================================
echo      Menjalankan Aplikasi Cuacane
echo ========================================

REM Validasi Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python tidak ditemukan! Pastikan Python ada di PATH.
    pause
    exit /b
)

REM Validasi main.py
IF NOT EXIST "cuacane_app\main.py" (
    echo [ERROR] main.py tidak ditemukan.
    pause
    exit /b
)

REM Set environment aman
set PYTHONPATH=%cd%
set QTWEBENGINE_DISABLE_SANDBOX=1
set QT_OPENGL=angle

REM ✅ Jalankan langsung main.py, BUKAN -m
echo.
echo [INFO] Menjalankan Cuacane App...
python cuacane_app\main.py

echo.
echo [SELESAI] Tekan tombol apapun untuk keluar.
pause
