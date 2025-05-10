#!/bin/bash
# Script para ejecutar antes de iniciar la aplicación

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate

# Iniciar el servidor (según lo especificado en Procfile)
echo "Iniciando la aplicación usando Procfile..."
exec "$@"
