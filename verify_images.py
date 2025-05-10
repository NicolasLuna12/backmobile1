"""
Script para verificar la generación y almacenamiento de URLs de imagen de perfil
"""
import os
import django
import sys
import requests
import traceback
from datetime import datetime

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Food_ISPC.settings")
django.setup()

# Importar después de configurar Django
from appUSERS.models import Usuario
from django.contrib.auth import get_user_model
import cloudinary.api
import cloudinary.utils

# Crear directorio para logs
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Archivo de log con timestamp
log_file = os.path.join(log_dir, f'verify_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

def log_message(message):
    """Escribir mensaje en el archivo de log y mostrarlo en consola"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

def verify_cloudinary_config():
    """Verificar que la configuración de Cloudinary funciona correctamente"""
    log_message("\n===== VERIFICANDO CONFIGURACIÓN DE CLOUDINARY =====")
    try:
        # Intentar obtener información de la cuenta para verificar la conexión
        account_info = cloudinary.api.account_info()
        log_message("✅ Conexión a Cloudinary establecida correctamente")
        log_message(f"Información de la cuenta: {account_info.get('account', {}).get('name', 'Desconocido')}")
        return True
    except Exception as e:
        log_message(f"❌ Error al conectar con Cloudinary: {str(e)}")
        traceback.print_exc()
        return False

def check_image_url(url):
    """Verificar si una URL de imagen es accesible"""
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            log_message(f"  ✅ URL accesible: {url}")
            return True
        else:
            log_message(f"  ❌ URL no accesible (código {response.status_code}): {url}")
            return False
    except Exception as e:
        log_message(f"  ❌ Error al verificar URL: {str(e)}")
        return False

def list_user_images():
    """Listar todas las imágenes de perfil y sus URLs"""
    log_message("\n=== USUARIOS Y SUS IMÁGENES DE PERFIL ===")
    User = get_user_model()
    users = User.objects.all()
    
    if not users.exists():
        log_message("No hay usuarios en la base de datos.")
        return
    
    # Contadores para estadísticas
    total_users = users.count()
    users_with_image = 0
    users_with_url = 0
    users_need_fix = 0
    
    for user in users:
        log_message(f"\nUsuario: {user.nombre} {user.apellido} ({user.email})")
        
        if user.imagen_perfil:
            users_with_image += 1
            log_message(f"  Imagen de perfil: SÍ")
            
            if hasattr(user.imagen_perfil, 'public_id') and user.imagen_perfil.public_id:
                log_message(f"  Campo imagen_perfil.public_id: {user.imagen_perfil.public_id}")
            else:
                log_message(f"  Campo imagen_perfil.public_id: No disponible")
            
            # Intentar obtener la URL directamente del campo CloudinaryField
            cloudinary_url = None
            try:
                cloudinary_url = user.imagen_perfil.url
                log_message(f"  URL generada por Cloudinary: {cloudinary_url}")
                
                # Verificar si la URL es accesible
                check_image_url(cloudinary_url)
            except Exception as e:
                log_message(f"  ❌ Error al generar URL con Cloudinary: {str(e)}")
                
            # Verificar si tenemos URL almacenada
            if user.imagen_perfil_url:
                users_with_url += 1
                log_message(f"  URL almacenada: {user.imagen_perfil_url}")
                
                # Verificar la coincidencia de URLs
                if cloudinary_url and cloudinary_url != user.imagen_perfil_url:
                    log_message(f"  ⚠️ Las URLs no coinciden.")
                    log_message(f"    URL generada: {cloudinary_url}")
                    log_message(f"    URL almacenada: {user.imagen_perfil_url}")
                    
                    # Preguntar si desea actualizarla
                    users_need_fix += 1
                    response = input("¿Desea actualizar la URL almacenada? (s/n): ")
                    if response.lower() == 's':
                        user.imagen_perfil_url = cloudinary_url
                        user.save(update_fields=['imagen_perfil_url'])
                        log_message(f"  ✅ URL actualizada correctamente")
                    else:
                        log_message(f"  URL no actualizada por decisión del usuario")
                else:
                    log_message(f"  ✓ Las URLs coinciden")
                    
                # Verificar si la URL almacenada es accesible
                check_image_url(user.imagen_perfil_url)
            else:
                log_message(f"  ⚠️ No hay URL almacenada en imagen_perfil_url")
                users_need_fix += 1
                
                if cloudinary_url:
                    response = input("¿Desea guardar la URL generada? (s/n): ")
                    if response.lower() == 's':
                        user.imagen_perfil_url = cloudinary_url
                        user.save(update_fields=['imagen_perfil_url'])
                        log_message(f"  ✅ URL guardada correctamente: {cloudinary_url}")
                        users_with_url += 1
                    else:
                        log_message(f"  URL no guardada por decisión del usuario")
        else:
            log_message(f"  Imagen de perfil: NO")
            
            # Si no hay imagen pero hay URL almacenada, hay inconsistencia
            if user.imagen_perfil_url:
                log_message(f"  ⚠️ No hay imagen pero hay URL almacenada: {user.imagen_perfil_url}")
                users_need_fix += 1
                
                response = input("¿Desea limpiar la URL almacenada? (s/n): ")
                if response.lower() == 's':
                    user.imagen_perfil_url = None
                    user.save(update_fields=['imagen_perfil_url'])
                    log_message(f"  ✅ URL limpiada correctamente")
                    users_with_url -= 1
                else:
                    log_message(f"  URL no limpiada por decisión del usuario")
    
    # Mostrar estadísticas
    log_message("\n=== ESTADÍSTICAS ===")
    log_message(f"Total de usuarios: {total_users}")
    log_message(f"Usuarios con imagen: {users_with_image} ({users_with_image/total_users*100:.1f}%)")
    log_message(f"Usuarios con URL almacenada: {users_with_url} ({users_with_url/total_users*100:.1f}%)")
    log_message(f"Usuarios que necesitan corrección: {users_need_fix}")

def fix_all_urls(interactive=True):
    """Corregir todas las URLs de imágenes de perfil"""
    log_message("\n=== CORRECCIÓN AUTOMÁTICA DE URLS ===")
    User = get_user_model()
    users = User.objects.all()
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for user in users:
        log_message(f"\nUsuario: {user.email}")
        
        try:
            # Caso 1: Tiene imagen pero no URL
            if user.imagen_perfil and not user.imagen_perfil_url:
                log_message("  Caso: Tiene imagen pero no URL almacenada")
                
                try:
                    cloudinary_url = user.imagen_perfil.url
                    
                    if interactive:
                        response = input(f"¿Guardar URL {cloudinary_url}? (s/n): ")
                        if response.lower() != 's':
                            log_message("  ⏭️ Saltado por decisión del usuario")
                            skipped_count += 1
                            continue
                    
                    user.imagen_perfil_url = cloudinary_url
                    user.save(update_fields=['imagen_perfil_url'])
                    log_message(f"  ✅ URL guardada: {cloudinary_url}")
                    fixed_count += 1
                    
                except Exception as e:
                    log_message(f"  ❌ Error al generar URL: {str(e)}")
                    error_count += 1
            
            # Caso 2: URLs inconsistentes
            elif user.imagen_perfil and user.imagen_perfil_url:
                try:
                    cloudinary_url = user.imagen_perfil.url
                    
                    if cloudinary_url != user.imagen_perfil_url:
                        log_message("  Caso: URLs inconsistentes")
                        log_message(f"    URL generada: {cloudinary_url}")
                        log_message(f"    URL almacenada: {user.imagen_perfil_url}")
                        
                        if interactive:
                            response = input("¿Actualizar con la URL generada? (s/n): ")
                            if response.lower() != 's':
                                log_message("  ⏭️ Saltado por decisión del usuario")
                                skipped_count += 1
                                continue
                        
                        user.imagen_perfil_url = cloudinary_url
                        user.save(update_fields=['imagen_perfil_url'])
                        log_message(f"  ✅ URL actualizada: {cloudinary_url}")
                        fixed_count += 1
                    else:
                        log_message("  ✓ Las URLs ya coinciden")
                        
                except Exception as e:
                    log_message(f"  ❌ Error al generar URL: {str(e)}")
                    error_count += 1
            
            # Caso 3: No tiene imagen pero sí URL
            elif not user.imagen_perfil and user.imagen_perfil_url:
                log_message("  Caso: No tiene imagen pero sí URL almacenada")
                
                if interactive:
                    response = input(f"¿Limpiar URL {user.imagen_perfil_url}? (s/n): ")
                    if response.lower() != 's':
                        log_message("  ⏭️ Saltado por decisión del usuario")
                        skipped_count += 1
                        continue
                
                user.imagen_perfil_url = None
                user.save(update_fields=['imagen_perfil_url'])
                log_message("  ✅ URL limpiada")
                fixed_count += 1
            
            else:
                log_message("  ✓ No requiere corrección")
                
        except Exception as e:
            log_message(f"  ❌ Error procesando usuario: {str(e)}")
            error_count += 1
    
    # Mostrar estadísticas
    log_message("\n=== RESUMEN DE CORRECCIONES ===")
    log_message(f"URLs corregidas: {fixed_count}")
    log_message(f"URLs saltadas: {skipped_count}")
    log_message(f"Errores: {error_count}")

def main():
    """Función principal"""
    log_message(f"Inicio de verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar configuración de Cloudinary
    if verify_cloudinary_config():
        # Mostrar menú
        print("\n=== MENÚ DE VERIFICACIÓN DE IMÁGENES ===")
        print("1. Listar usuarios y sus imágenes")
        print("2. Corregir URLs (interactivo)")
        print("3. Corregir URLs (automático)")
        print("4. Salir")
        
        option = input("\nSeleccione una opción: ")
        
        if option == "1":
            list_user_images()
        elif option == "2":
            fix_all_urls(interactive=True)
        elif option == "3":
            confirm = input("¿Está seguro de corregir todas las URLs automáticamente? (s/n): ")
            if confirm.lower() == 's':
                fix_all_urls(interactive=False)
            else:
                log_message("Operación cancelada por el usuario")
        else:
            log_message("Saliendo del programa")
    else:
        log_message("No se puede continuar la verificación debido a errores en la configuración de Cloudinary")
    
    log_message(f"\nFin de verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"Archivo de log: {log_file}")

if __name__ == "__main__":
    main()
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
