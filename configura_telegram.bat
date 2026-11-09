@echo off
setlocal
cd /d "%~dp0"
rem Stesso profilo dati di avvia_lumi.bat anche se aperto da Esplora file:
rem prima le credenziali finivano nel profilo base e Lumi non le vedeva.
if not defined JARVIS_TRIAL_HOME set "JARVIS_TRIAL_HOME=%LOCALAPPDATA%\Jarvis-AccessoFile-Trial"
echo Profilo dati: %JARVIS_TRIAL_HOME%
echo LUMI - Accesso account Telegram (contatti selezionabili in Lumi)
echo Configurazione utente: NON invia alcun messaggio.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 configura_telegram.py
) else (
  python configura_telegram.py
)
if errorlevel 1 echo Setup incompleto: Telegram resta disabilitato.
pause
