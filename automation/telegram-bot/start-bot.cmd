@echo off
cd /d "%~dp0"
echo Окно не закрывайте — пока оно открыто, бот слушает Telegram.
echo Остановка: Ctrl+C
echo.
".venv\Scripts\python.exe" bot.py
echo.
if errorlevel 1 pause
