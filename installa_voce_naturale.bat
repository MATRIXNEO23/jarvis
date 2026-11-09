@echo off
setlocal
cd /d "%~dp0"
echo Installazione FACOLTATIVA delle voci naturali (motore Piper, offline).
echo Il motore e GPL-3.0; le voci si scaricano poi da Impostazioni ^> Voce.
py -3 -m pip install --user "piper-tts>=1.4,<2"
if errorlevel 1 goto error
echo Verifica del motore in un processo separato...
py -3 -c "import piper; print(\"Motore Piper pronto.\")"
if errorlevel 1 goto cpu
echo.
echo Fatto. In Impostazioni ^> Voce premi "Scarica Paola" o "Scarica Serena",
echo poi scegli la voce e premi "Prova voce".
pause
exit /b 0
:cpu
echo.
echo Il motore e installato ma non si avvia su questo PC (possibile limite della CPU).
echo Jarvis continuera a usare le voci di Windows.
pause
exit /b 1
:error
echo.
echo Installazione NON completata. Le voci di Windows restano disponibili.
pause
exit /b 1
