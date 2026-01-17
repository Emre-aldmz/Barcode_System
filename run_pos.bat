@echo off
:: Barkod Uygulaması - Windows Başlatma Scripti
cd /d "%~dp0"

:: Sanal ortam kontrolü (Windows'ta Scripts klasörü olur)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Sanal ortam bulunamadi veya farkli bir yapida (Linux venv olabilir).
    echo Sistem Python'u kullanilacak...
)

python main.py
pause
