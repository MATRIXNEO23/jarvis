@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0installa_gpt.ps1"
if errorlevel 1 (
  echo.
  echo Installazione GPT non riuscita. Controlla il messaggio precedente.
) else (
  echo.
  echo Modulo GPT installato. Avvia Lumi e usa il pulsante Connetti ChatGPT.
)
pause
endlocal
