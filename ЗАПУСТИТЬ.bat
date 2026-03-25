@echo off
echo.
echo  Запускаю ВолонтёрМДК сервер...
echo.
python server.py
if errorlevel 1 (
    echo.
    echo  Попробую python3...
    python3 server.py
)
pause
