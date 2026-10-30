@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Jarvis richiede Python 3.11 x64. Nessun software viene installato automaticamente.
  echo Scarica Python solo dal sito ufficiale python.org.
  pause
  exit /b 1
)
py -3 jarvis.py
if errorlevel 1 (
  echo Jarvis non e' stato avviato correttamente. Controlla gli errori qui sopra.
  pause
  exit /b 1
)
endlocal
