"""
Script para migrar datos existentes y actualizar las URLs de imágenes de perfil
"""
import os
import django
import sys
import traceback

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Food_ISPC.settings")
django.setup()

# Importar después de configurar Django
from django.contrib.auth import get_user_model
import cloudinary.api

def verify_cloudinary_config():
    """Verificar que la configuración de Cloudinary funciona correctamente"""
    try:
        # Intentar obtener información de la cuenta para verificar la conexión
        account_info = cloudinary.api.account_info()
        print("✅ Conexión a Cloudinary establecida correctamente")
        print(f"Información de la cuenta: {account_info.get('account', {}).get('name', 'Desconocido')}")
        return True
    except Exception as e:
        print(f"❌ Error al conectar con Cloudinary: {str(e)}")
        return False

def migrate_image_urls():
    """Migrar las URLs de imágenes de perfil para todos los usuarios existentes"""
    User = get_user_model()
    users = User.objects.filter(imagen_perfil__isnull=False)
    
    print(f"Encontrados {users.count()} usuarios con imágenes de perfil.")
    
    for user in users:
        try:
            if not user.imagen_perfil:
                print(f"Usuario {user.email}: No tiene imagen de perfil")
                continue
                
            # Intentar generar la URL
            try:
                url = user.imagen_perfil.url
                print(f"Usuario {user.email}: URL generada: {url}")
                
                # Actualizar el campo en la base de datos si no hay URL o es diferente
                if not user.imagen_perfil_url or user.imagen_perfil_url != url:
                    old_url = user.imagen_perfil_url or "ninguna"
                    user.imagen_perfil_url = url
                    user.save(update_fields=['imagen_perfil_url'])
                    print(f"  ✅ URL actualizada: {old_url} -> {url}")
                else:
                    print(f"  ✓ URL ya correcta: {url}")
                    
            except Exception as e:
                print(f"  ❌ Error al generar URL para {user.email}: {str(e)}")
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Error procesando usuario {user.email}: {str(e)}")
            traceback.print_exc()
            
def fix_corrupted_images():
    """Identificar y corregir imágenes que pueden estar corruptas"""
    User = get_user_model()
    users = User.objects.filter(imagen_perfil__isnull=False)
    
    for user in users:
        try:
            if user.imagen_perfil:
                # Verificar si podemos acceder a la imagen en Cloudinary
                try:
                    # Intentar obtener la URL de la imagen
                    url = user.imagen_perfil.url
                    
                    # Si llegamos aquí, la URL se generó correctamente
                    print(f"Usuario {user.email}: Imagen válida - {url}")
                    
                    # Actualizar la URL almacenada si es necesario
                    if not user.imagen_perfil_url or user.imagen_perfil_url != url:
                        user.imagen_perfil_url = url
                        user.save(update_fields=['imagen_perfil_url'])
                        print(f"  URL actualizada: {url}")
                        
                except Exception as e:
                    print(f"Usuario {user.email}: Imagen corrupta - {str(e)}")
                    
                    # Opcional: Limpiar la imagen corrupta
                    # user.imagen_perfil = None
                    # user.imagen_perfil_url = None
                    # user.save(update_fields=['imagen_perfil', 'imagen_perfil_url'])
                    # print(f"  Imagen corrupta eliminada")
        except Exception as e:
            print(f"Error procesando usuario {user.email}: {str(e)}")

if __name__ == "__main__":
    print("======= Verificando configuración de Cloudinary =======")
    if verify_cloudinary_config():
        print("\n======= Migrando URLs de imágenes de perfil =======")
        migrate_image_urls()
        
        print("\n======= Verificando posibles imágenes corruptas =======")
        fix_corrupted_images()
    else:
        print("No se puede continuar debido a errores de configuración de Cloudinary")
    
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
