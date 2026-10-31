@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Serve Python 3.11 o 3.12 a 64 bit. Nessuna installazione automatica.
  pause
  exit /b 1
)
if not defined LOCALAPPDATA (
  echo LOCALAPPDATA non disponibile: test annullato.
  pause
  exit /b 1
)
set "JARVIS_TRIAL_HOME=%LOCALAPPDATA%\Jarvis-Telegram50-Trial"
echo JARVIS // TELEGRAM 50 - PROFILO DI PROVA ISOLATO
echo.
py -3 prepara_test_telegram50.py
if errorlevel 1 (
  echo.
  echo Preparazione dati di prova non riuscita. Il Jarvis precedente e' intatto.
  pause
  exit /b 1
)
echo.
echo Attenzione: il test usa lo stesso account Telegram e GPT, ma una
echo copia separata delle memorie e delle impostazioni locali di Jarvis.
echo Non avviare contemporaneamente la vecchia versione di Jarvis.
echo Telegram automatico parte disattivato al primo avvio del test.
echo.
call avvia_jarvis.bat
endlocal
