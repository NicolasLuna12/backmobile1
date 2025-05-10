"""
Script de prueba para verificar la integración con Cloudinary
"""
import os
import django
import sys

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Food_ISPC.settings")
django.setup()

# Importar después de configurar Django
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings

def test_cloudinary_config():
    """Verificar que la configuración de Cloudinary sea correcta"""
    print("=== CONFIGURACIÓN DE CLOUDINARY ===")
    
    config = settings.CLOUDINARY_STORAGE
    print(f"Cloud Name: {config.get('CLOUD_NAME')}")
    print(f"API Key: {config.get('API_KEY')}")
    
    # Comprobar conexión mediante una solicitud simple
    try:
        result = cloudinary.api.ping()
        print("Conexión a Cloudinary: EXITOSA")
        print(f"Resultado del ping: {result}")
        
        # Intentar obtener información básica de la cuenta
        account_info = cloudinary.api.usage()
        print(f"\nInformación de uso de la cuenta:")
        print(f"  - Plan: {account_info.get('plan', 'No disponible')}")
        print(f"  - Créditos: {account_info.get('credits', 'No disponible')}")
        print(f"  - Recursos: {account_info.get('resources', 'No disponible')}")
        print(f"  - Almacenamiento utilizado: {account_info.get('storage', {}).get('used', 'No disponible')}")
        
        # Listar algunas imágenes existentes en la carpeta de perfiles
        print("\nImágenes en la carpeta 'perfil_usuarios':")
        resources = cloudinary.api.resources(type="upload", prefix="perfil_usuarios", max_results=5)
        if 'resources' in resources and resources['resources']:
            for resource in resources['resources']:
                print(f"  - {resource.get('public_id')}: {resource.get('secure_url')}")
                print(f"    Creado: {resource.get('created_at')}, Tamaño: {resource.get('bytes')} bytes")
        else:
            print("  - No hay imágenes en esta carpeta o no se pudo acceder a ellas.")
            
    except Exception as e:
        print(f"Error de conexión a Cloudinary: {str(e)}")
    
    print("\n=== INFORMACIÓN DE TRANSFORMACIONES CONFIGURADAS ===")
    try:
        from appUSERS.models import Usuario
        print("Transformaciones para imágenes de perfil:")
        print(f"  - Carpeta: {Usuario.imagen_perfil.field.options.get('folder', 'No especificada')}")
        transformations = Usuario.imagen_perfil.field.options.get('transformation', {})
        for key, value in transformations.items():
            print(f"  - {key}: {value}")
    except Exception as e:
        print(f"Error al obtener información de transformaciones: {str(e)}")
    
    print("=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    test_cloudinary_config()
