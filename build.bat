@echo off
echo ============================================
echo   Audio Library Manager - Build Eseguibile
echo ============================================
echo.

REM Controlla Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato. Installa Python 3.11+ da python.org
    echo Assicurati di spuntare "Add Python to PATH" durante l'installazione.
    pause
    exit /b 1
)

echo [1/3] Installazione dipendenze...
pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo ERRORE durante l'installazione delle dipendenze.
    pause
    exit /b 1
)

echo.
echo [2/3] Creazione eseguibile (puo' richiedere qualche minuto)...
pyinstaller build.spec --noconfirm
if errorlevel 1 (
    echo ERRORE durante la creazione dell'eseguibile.
    pause
    exit /b 1
)

echo.
echo [3/3] Copia FFmpeg se presente...
where ffmpeg >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('where ffmpeg') do copy "%%i" "dist\" >nul 2>&1
    for /f "tokens=*" %%i in ('where ffprobe') do copy "%%i" "dist\" >nul 2>&1
    echo FFmpeg copiato nella cartella dist.
) else (
    echo NOTA: FFmpeg non trovato nel PATH.
    echo L'app funziona ma per i formati M4A/OGG serve FFmpeg.
    echo Scaricalo da https://www.gyan.dev/ffmpeg/builds/ e metti
    echo ffmpeg.exe nella stessa cartella di AudioLibraryManager.exe
)

echo.
echo ============================================
echo   FATTO! L'eseguibile si trova in:
echo   dist\AudioLibraryManager.exe
echo ============================================
echo.
pause
