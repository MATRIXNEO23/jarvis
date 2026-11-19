@echo off
setlocal
cd /d "%~dp0"
echo Voci Microsoft Edge (Isabella, Elsa, Diego, Giuseppe): gratuite ma ONLINE.
echo Il testo da leggere viene inviato al servizio di sintesi di Microsoft.
py -3 -m pip install --user "edge-tts>=7.2,<8"
if errorlevel 1 goto error
py -3 -c "import edge_tts; print(\"Voci Edge pronte.\")"
if errorlevel 1 goto error
echo.
echo Fatto. Riavvia Lumi, poi in Impostazioni ^> Voce scegli una voce "Edge:".
pause
exit /b 0
:error
echo.
echo Installazione NON completata. Le altre voci restano disponibili.
pause
exit /b 1
