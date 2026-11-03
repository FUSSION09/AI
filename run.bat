@echo off
title Apex UAS Server & Portal
cd /d "%~dp0"
echo ===================================================
echo Starting Apex Autonomous System (UAS) Gateway...
echo Web UI:        http://127.0.0.1:8000/
echo Swagger Docs:  http://127.0.0.1:8000/docs
echo ===================================================
python main.py start-gateway --host 0.0.0.0 --port 8000
pause

