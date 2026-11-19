@echo off
setlocal
cd /d "%~dp0"
echo Installazione FACOLTATIVA del riconoscimento vocale italiano offline.
echo Nessuna attivazione automatica del microfono.
echo Installazione pacchetti Python per l'utente corrente...
py -3 -m pip install --user "vosk==0.3.45" "sounddevice==0.5.3"
if errorlevel 1 goto error
echo Download sicuro del modello italiano ufficiale...
py -3 installa_modello_voce.py
if errorlevel 1 goto error
echo.
echo Componenti e modello installati. Avvia avvia_lumi.bat.
echo All'avvio Lumi usa la preferenza microfono salvata.
pause
exit /b 0
:error
echo.
echo Installazione NON completata. I comandi scritti e GPT restano disponibili.
echo Consulta docs\VOCE_OFFLINE.md per diagnosi.
pause
exit /b 1
