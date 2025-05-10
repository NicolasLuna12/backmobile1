#!/bin/bash
# Script de despliegue para Render

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Aplicando migraciones..."
python manage.py migrate

echo "Migrando URLs de imágenes de perfil..."
python migrate_images.py

echo "Verificando imágenes..."
python verify_images.py 3 # Opción 3: corrección automática

echo "Iniciando el servidor Gunicorn..."
gunicorn Food_ISPC.wsgi:application
