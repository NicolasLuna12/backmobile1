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
echo ===== ACTUALIZANDO URLs DE IMÁGENES DE PERFIL =====
python migrate_images.py

echo.
echo ===== PROBANDO CONFIGURACION CLOUDINARY =====
python test_cloudinary.py

echo.
echo ===== INICIANDO SERVIDOR DE DESARROLLO =====
echo Para probar las APIs, abra otra terminal y ejecute:
echo   python test_api.py
echo Para verificar las imágenes de perfil, ejecute:
echo   python verify_images.py
echo.
python manage.py runserver
