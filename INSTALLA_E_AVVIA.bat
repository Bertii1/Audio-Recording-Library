@echo off
chcp 65001 >nul 2>&1
title Audio Library Manager - Primo Avvio

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Python non trovato!
    echo.
    echo  Devi installare Python per usare questa applicazione.
    echo  Ora si aprira' la pagina di download...
    echo.
    echo  IMPORTANTE: durante l'installazione spunta la casella
    echo  "Add Python to PATH" nella prima schermata!
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Controlla se le dipendenze sono installate
echo Controllo dipendenze...
pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installazione dipendenze in corso...
    echo Questo succede solo al primo avvio.
    echo.
    pip install --user PyQt6 pydub mutagen numpy faster-whisper
    if errorlevel 1 (
        echo.
        echo Errore durante l'installazione. Riprova.
        pause
        exit /b 1
    )
    echo.
    echo Dipendenze installate!
    echo.
)

REM Avvia l'applicazione
echo Avvio Audio Library Manager...
cd /d "%~dp0"
pythonw src/main.py
if errorlevel 1 (
    python src/main.py
)
