@echo off
echo === DPA Agricole - Demarrage Backend ===
cd /d %~dp0backend

REM Activer le virtualenv si existant
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtualenv introuvable. Creation en cours...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

echo Demarrage du serveur Django sur http://localhost:8000
python manage.py runserver
pause
