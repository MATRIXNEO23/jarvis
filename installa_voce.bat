@echo off
setlocal
cd /d "%~dp0"
echo Installazione opzionale per riconoscimento vocale offline italiano.
echo Il microfono resta SPENTO finche non selezioni una modalita in Jarvis.
py -3 -m pip install --user "vosk==0.3.45" "sounddevice==0.5.3"
if errorlevel 1 (
    echo Installazione non riuscita. Controlla Python 3.12 e la connessione.
    pause
    exit /b 1
)
echo Componenti installati. Segui docs\VOCE_OFFLINE.md per il modello italiano.
pause
