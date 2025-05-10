"""
Script para migrar datos existentes y actualizar las URLs de imágenes de perfil
"""
import os
import django
import sys

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Food_ISPC.settings")
django.setup()

# Importar después de configurar Django
from django.contrib.auth import get_user_model
import cloudinary.api

def migrate_image_urls():
    """Migrar las URLs de imágenes de perfil para todos los usuarios existentes"""
    User = get_user_model()
    users = User.objects.filter(imagen_perfil__isnull=False)
    
    print(f"Encontrados {users.count()} usuarios con imágenes de perfil.")
    
    for user in users:
        try:
            if user.imagen_perfil and not user.imagen_perfil_url:
                # Generar la URL directamente con Cloudinary
                url = user.imagen_perfil.url
                
                # Actualizar el campo en la base de datos
                user.imagen_perfil_url = url
                user.save(update_fields=['imagen_perfil_url'])
                
                print(f"Usuario {user.email}: URL actualizada a {url}")
            elif user.imagen_perfil and user.imagen_perfil_url:
                # Verificar que la URL almacenada coincida con la generada
                generated_url = user.imagen_perfil.url
                
                if generated_url != user.imagen_perfil_url:
                    print(f"Usuario {user.email}: URL desactualizada")
                    print(f"  Almacenada: {user.imagen_perfil_url}")
                    print(f"  Generada: {generated_url}")
                    
                    # Actualizar la URL
                    user.imagen_perfil_url = generated_url
                    user.save(update_fields=['imagen_perfil_url'])
                    print(f"  URL actualizada.")
                else:
                    print(f"Usuario {user.email}: URL correcta ({user.imagen_perfil_url})")
        except Exception as e:
            print(f"Error procesando usuario {user.email}: {str(e)}")
    
    # Verificar usuarios con URL pero sin imagen
    users_with_url_no_image = User.objects.filter(
        imagen_perfil__isnull=True, 
        imagen_perfil_url__isnull=False
    )
    
    if users_with_url_no_image.exists():
        print(f"\nEncontrados {users_with_url_no_image.count()} usuarios con URL pero sin imagen:")
        
        for user in users_with_url_no_image:
            print(f"Usuario {user.email}: tiene URL ({user.imagen_perfil_url}) pero no imagen")
            
            # Limpiar la URL
            user.imagen_perfil_url = None
            user.save(update_fields=['imagen_perfil_url'])
            print(f"  URL limpiada.")

def list_cloudinary_resources():
    """Listar recursos de imagen en Cloudinary"""
    print("\nRecursos en Cloudinary:")
    
    try:
        resources = cloudinary.api.resources(type="upload", prefix="perfil_usuarios", max_results=30)
        
        if 'resources' in resources and resources['resources']:
            for resource in resources['resources']:
                print(f"  - {resource.get('public_id')}: {resource.get('secure_url')}")
                print(f"    Creado: {resource.get('created_at')}, Tamaño: {resource.get('bytes')} bytes")
        else:
            print("  - No hay imágenes en esta carpeta o no se pudo acceder a ellas.")
    except Exception as e:
        print(f"Error al listar recursos: {str(e)}")

if __name__ == "__main__":
    print("=== INICIANDO MIGRACIÓN DE URLs DE IMÁGENES DE PERFIL ===")
    migrate_image_urls()
    
    print("\n=== RECURSOS EN CLOUDINARY ===")
    list_cloudinary_resources()
    
    print("\n=== MIGRACIÓN COMPLETADA ===")
