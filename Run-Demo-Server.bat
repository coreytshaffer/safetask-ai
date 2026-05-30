@echo off
title SafeTask AI Local Server
cd /d "%~dp0"
echo =============================================================
echo SafeTask AI Local Server is Starting...
echo Bypassing browser local file CORS restrictions.
echo =============================================================
echo Serving SafeTask AI at: http://localhost:8080
echo Keep this command window open while using the application.
echo Close this window to stop the server.
echo =============================================================
start "" "http://localhost:8080"
python server.py
