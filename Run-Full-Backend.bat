@echo off
title SafeTask AI Full Backend
cd /d "%~dp0"
echo =============================================================
echo SafeTask AI Full Backend is Starting...
echo Running Python Flask server with SQLite and PDF Engine.
echo =============================================================
echo Serving SafeTask AI at: http://localhost:8080
echo Keep this command window open while using the application.
echo Close this window to stop the server.
echo =============================================================
start "" "http://localhost:8080"
python app.py
