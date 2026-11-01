@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Serve Python 3.11 o 3.12 x64. Nessuna installazione automatica.
  pause
  exit /b 1
)
if not defined LOCALAPPDATA (
  echo LOCALAPPDATA non disponibile: avvio annullato.
  pause
  exit /b 1
)
rem Questa ZIP e' una prova: il launcher UNICO usa sempre dati isolati.
rem Il vecchio Jarvis nella sua cartella mantiene il suo launcher originale.
set "JARVIS_TRIAL_HOME=%LOCALAPPDATA%\Jarvis-AccessoFile-Trial"
set "JARVIS_TRIAL_SOURCE=%LOCALAPPDATA%\Jarvis"
if exist "%LOCALAPPDATA%\Jarvis-Telegram50-Trial\settings.json" set "JARVIS_TRIAL_SOURCE=%LOCALAPPDATA%\Jarvis-Telegram50-Trial"
echo JARVIS // ACCESSO FILE - AVVIO IN PROFILO ISOLATO
echo.
py -3 prepara_test_telegram50.py
if errorlevel 1 (
  echo Preparazione del profilo di prova non riuscita. Jarvis originale intatto.
  pause
  exit /b 1
)
echo.
echo ATTENZIONE: GPT e Telegram sono account reali quando attivati.
echo Telegram automatico inizialmente OFF; microfono ON all'avvio se disponibile.
echo Non usare due istanze Telegram contemporaneamente.
echo.
py -3 jarvis.py
if errorlevel 1 (
  echo Jarvis non e' stato avviato correttamente. Leggi l'errore qui sopra.
  pause
  exit /b 1
)
endlocal
