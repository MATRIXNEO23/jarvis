@echo off
setlocal
cd /d "%~dp0"
echo Installazione facoltativa Telegram - nessuna API a pagamento.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -m pip install --user "Telethon>=1.36,<2"
) else (
  python -m pip install --user "Telethon>=1.36,<2"
)
if errorlevel 1 (
  echo Installazione Telethon non riuscita.
  pause
  exit /b 1
)
echo Telethon installato. Per le note vocali OGG/Opus serve anche FFmpeg nel PATH.
echo Nessun nuovo servizio e nessun invio automatico e' stato attivato.
pause
