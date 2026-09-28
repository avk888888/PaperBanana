@echo off
chcp 65001 >nul
title PaperBanana

rem ---------------------------------------------------------------------------
rem  NOTE: Keep this file ASCII-only.
rem  Chinese (non-ASCII) text in a .bat breaks cmd.exe parsing on Windows,
rem  even inside "rem" comment lines.
rem ---------------------------------------------------------------------------
rem  %~dp0 = folder containing this .bat, so the project can be moved anywhere
cd /d "%~dp0"

rem  Add GTK Runtime to PATH only if it is installed (optional; some drawing
rem  backends need it). Missing is fine.
if exist "C:\Program Files\Gtk-Runtime\bin" set "PATH=C:\Program Files\Gtk-Runtime\bin;%PATH%"

rem  Prefer a project-local virtualenv; fall back to python on PATH
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON=%~dp0.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

"%PYTHON%" -u PaperBanana.py
pause
