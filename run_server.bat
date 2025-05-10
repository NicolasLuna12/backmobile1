@echo off
REM Script para iniciar y probar la implementación de Cloudinary

echo ===== VERIFICANDO INSTALACION =====
pip list | findstr cloudinary
pip list | findstr django-cloudinary-storage

echo.
echo ===== APLICANDO MIGRACIONES =====
python manage.py makemigrations
python manage.py migrate

echo.
echo ===== PROBANDO CONFIGURACION CLOUDINARY =====
python test_cloudinary.py

echo.
echo ===== INICIANDO SERVIDOR DE DESARROLLO =====
echo Para probar las APIs, abra otra terminal y ejecute:
echo   python test_api.py
echo.
python manage.py runserver
