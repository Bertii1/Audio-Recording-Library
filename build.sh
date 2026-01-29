#!/bin/bash
echo "============================================"
echo "  Audio Library Manager - Build Eseguibile"
echo "============================================"
echo

echo "[1/3] Installazione dipendenze..."
pip install -r requirements.txt pyinstaller || { echo "Errore pip"; exit 1; }

echo
echo "[2/3] Creazione eseguibile..."
pyinstaller build.spec --noconfirm || { echo "Errore pyinstaller"; exit 1; }

echo
echo "[3/3] Verifica ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg trovato nel sistema."
else
    echo "NOTA: FFmpeg non trovato. Installa con: sudo apt install ffmpeg"
fi

echo
echo "============================================"
echo "  FATTO! L'eseguibile si trova in:"
echo "  dist/AudioLibraryManager"
echo "============================================"
