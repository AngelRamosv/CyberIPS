@echo off
title CyberIPs Server (Puerto 8765)
cd /d "%~dp0"
echo.
echo  Iniciando CyberIPs Server en puerto 8765...
echo.
start http://localhost:8765
python server.py
pause
