from setuptools import setup, find_packages

setup(
    name="audio-library-manager",
    version="1.0.0",
    description="Desktop audio library manager with Whisper transcription",
    author="",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
        "pydub>=0.25.1",
        "faster-whisper>=1.0.0",
        "mutagen>=1.47.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "audio-library-manager=src.main:main",
        ],
    },
)
