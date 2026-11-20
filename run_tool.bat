@echo off
title AutoTyper Google Docs - Mo phong nguoi that
cd /d "%~dp0"
python tool_human_typer.py
if errorlevel 1 (
    echo.
    echo [LOI] Khong the khoi chay tool.
    echo Vui long kiem tra xem may tinh da cai dat Python chua (https://www.python.org).
    echo.
    pause
)

