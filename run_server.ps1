# Script para iniciar y probar la implementación de Cloudinary

Write-Host "===== VERIFICANDO INSTALACION =====" -ForegroundColor Green
pip list | Select-String "cloudinary"
pip list | Select-String "django-cloudinary-storage"

Write-Host ""
Write-Host "===== APLICANDO MIGRACIONES =====" -ForegroundColor Green
python manage.py makemigrations
python manage.py migrate

Write-Host ""
Write-Host "===== ACTUALIZANDO URLs DE IMÁGENES DE PERFIL =====" -ForegroundColor Green
python migrate_images.py

Write-Host ""
Write-Host "===== PROBANDO CONFIGURACION CLOUDINARY =====" -ForegroundColor Green
python test_cloudinary.py

Write-Host ""
Write-Host "===== INICIANDO SERVIDOR DE DESARROLLO =====" -ForegroundColor Green
Write-Host "Para probar las APIs, abra otra terminal y ejecute:" -ForegroundColor Yellow
Write-Host "  python test_api.py" -ForegroundColor Yellow
Write-Host "Para verificar las imágenes de perfil, ejecute:" -ForegroundColor Yellow
Write-Host "  python verify_images.py" -ForegroundColor Yellow
Write-Host ""
python manage.py runserver
