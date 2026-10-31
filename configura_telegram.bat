@echo off
setlocal
cd /d "%~dp0"
echo JARVIS - Accesso account Telegram (contatti selezionabili in Jarvis)
echo Configurazione utente: NON invia alcun messaggio.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 configura_telegram.py
) else (
  python configura_telegram.py
)
if errorlevel 1 echo Setup incompleto: Telegram resta disabilitato.
pause
