"""
Script para verificar la generación y almacenamiento de URLs de imagen de perfil
"""
import os
import django
import sys

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Food_ISPC.settings")
django.setup()

# Importar después de configurar Django
from appUSERS.models import Usuario
from django.contrib.auth import get_user_model

def list_user_images():
    """Listar todas las imágenes de perfil y sus URLs"""
    User = get_user_model()
    users = User.objects.all()
    
    print("\n=== USUARIOS Y SUS IMÁGENES DE PERFIL ===")
    if not users.exists():
        print("No hay usuarios en la base de datos.")
        return
    
    for user in users:
        print(f"\nUsuario: {user.nombre} {user.apellido} ({user.email})")
        
        if user.imagen_perfil:
            print(f"  Imagen de perfil: SÍ")
            print(f"  Campo imagen_perfil.public_id: {user.imagen_perfil.public_id}")
            
            # Intentar obtener la URL directamente del campo CloudinaryField
            cloudinary_url = None
            try:
                cloudinary_url = user.imagen_perfil.url
                print(f"  URL generada por Cloudinary: {cloudinary_url}")
            except Exception as e:
                print(f"  Error al generar URL con Cloudinary: {str(e)}")
                
            # Verificar si tenemos URL almacenada
            if user.imagen_perfil_url:
                print(f"  URL almacenada: {user.imagen_perfil_url}")
                
                # Verificar la coincidencia de URLs
                if cloudinary_url and cloudinary_url != user.imagen_perfil_url:
                    print(f"  ¡ADVERTENCIA! Las URLs no coinciden.")
                    print(f"    URL generada: {cloudinary_url}")
                    print(f"    URL almacenada: {user.imagen_perfil_url}")
            else:
                print(f"  URL almacenada: NO (no hay URL guardada en la base de datos)")
                
                # Actualizar la URL si es necesario
                if cloudinary_url:
                    print(f"  Actualizando la URL almacenada...")
                    user.imagen_perfil_url = cloudinary_url
                    user.save(update_fields=['imagen_perfil_url'])
                    print(f"  URL actualizada a: {user.imagen_perfil_url}")
        else:
            print(f"  Imagen de perfil: NO")
            
            # Si no hay imagen pero sí URL almacenada, limpiarla
            if user.imagen_perfil_url:
                print(f"  ¡ADVERTENCIA! Hay una URL almacenada ({user.imagen_perfil_url}) pero no hay imagen")
                user.imagen_perfil_url = None
                user.save(update_fields=['imagen_perfil_url'])
                print(f"  URL limpiada.")
    
    print("\n=== FIN DEL LISTADO ===")

def update_all_urls():
    """Actualizar todas las URLs almacenadas para que coincidan con las generadas"""
    User = get_user_model()
    users = User.objects.filter(imagen_perfil__isnull=False)
    
    print("\n=== ACTUALIZANDO TODAS LAS URLS DE PERFIL ===")
    count = 0
    
    for user in users:
        try:
            if user.imagen_perfil:
                old_url = user.imagen_perfil_url
                new_url = user.imagen_perfil.url
                
                user.imagen_perfil_url = new_url
                user.save(update_fields=['imagen_perfil_url'])
                
                print(f"Usuario {user.email}:")
                print(f"  URL antigua: {old_url}")
                print(f"  URL nueva: {new_url}")
                count += 1
        except Exception as e:
            print(f"Error al actualizar {user.email}: {str(e)}")
    
    print(f"\nTotal de URLs actualizadas: {count}")
    print("=== ACTUALIZACIÓN COMPLETADA ===")

if __name__ == "__main__":
    # Pedir acción al usuario
    print("Este script permite verificar y corregir las URLs de imágenes de perfil.")
    print("Opciones:")
    print("1. Listar usuarios y sus imágenes")
    print("2. Actualizar todas las URLs")
    
    option = input("Seleccione una opción (1 o 2): ")
    
    if option == "1":
        list_user_images()
    elif option == "2":
        update_all_urls()
    else:
        print("Opción no válida.")
