"""
Script de prueba para verificar la integración con Cloudinary
"""
import os
import django
import sys
import traceback
from datetime import datetime

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
    print(f"API Secret: {'*' * 10}")  # No mostrar la clave secreta
    print(f"Media Storage: {settings.DEFAULT_FILE_STORAGE}")
    
    # Comprobar conexión mediante una solicitud simple
    try:
        result = cloudinary.api.ping()
        print("\n✅ Conexión a Cloudinary: EXITOSA")
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
            
        return True
    except Exception as e:
        print(f"\n❌ Error al conectar con Cloudinary: {str(e)}")
        traceback.print_exc()
        return False

def upload_test_image():
    """Subir una imagen de prueba a Cloudinary"""
    print("\n=== PRUEBA DE SUBIDA DE IMAGEN ===")
    
    # Crear una imagen de prueba simple si no se encuentra ninguna
    test_image_path = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
    if not os.path.exists(test_image_path):
        try:
            from PIL import Image
            # Crear una imagen simple de 100x100 píxeles
            img = Image.new('RGB', (100, 100), color = (30, 144, 255))
            img.save(test_image_path)
            print(f"Creada imagen de prueba: {test_image_path}")
        except ImportError:
            print("No se pudo importar PIL. Usando imagen de prueba alternativa.")
            test_image_path = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
        except Exception as e:
            print(f"Error al crear imagen de prueba: {str(e)}")
            test_image_path = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
            
    # Intentar subir la imagen
    try:
        print(f"Subiendo imagen: {test_image_path}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        result = cloudinary.uploader.upload(
            test_image_path,
            folder="test_uploads",
            public_id=f"test_{timestamp}",
            overwrite=True
        )
        
        print("\n✅ Imagen subida correctamente")
        print(f"  Public ID: {result.get('public_id')}")
        print(f"  URL: {result.get('url')}")
        print(f"  Secure URL: {result.get('secure_url')}")
        
        # Intentar eliminar la imagen de prueba para limpiar
        try:
            cloudinary.uploader.destroy(result.get('public_id'))
            print("✅ Imagen de prueba eliminada correctamente")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar la imagen de prueba: {str(e)}")
            
        return True
    except Exception as e:
        print(f"\n❌ Error al subir imagen a Cloudinary: {str(e)}")
        traceback.print_exc()
        return False

def validate_user_images():
    """Verificar URLs de imágenes de usuario"""
    print("\n=== VALIDACIÓN DE URLs DE IMÁGENES DE USUARIO ===")
    
    try:
        from django.contrib.auth import get_user_model
        import requests
        
        User = get_user_model()
        users_with_image = User.objects.filter(imagen_perfil__isnull=False)
        
        print(f"Usuarios con imagen de perfil: {users_with_image.count()}")
        
        for i, user in enumerate(users_with_image[:5]):  # Limitamos a 5 usuarios para la prueba
            print(f"\nUsuario #{i+1}: {user.email}")
            
            if user.imagen_perfil_url:
                print(f"URL almacenada: {user.imagen_perfil_url}")
                
                # Verificar que la URL sea accesible
                try:
                    response = requests.head(user.imagen_perfil_url, timeout=5)
                    if response.status_code == 200:
                        print("✅ URL accesible")
                    else:
                        print(f"❌ URL no accesible (código {response.status_code})")
                except Exception as e:
                    print(f"❌ Error al verificar URL: {str(e)}")
            else:
                print("❌ No hay URL almacenada")
                
            # Intentar generar la URL con Cloudinary
            try:
                generated_url = user.imagen_perfil.url
                print(f"URL generada: {generated_url}")
                
                if user.imagen_perfil_url != generated_url:
                    print("⚠️ La URL almacenada no coincide con la generada")
            except Exception as e:
                print(f"❌ Error al generar URL: {str(e)}")
                
        return True
    except Exception as e:
        print(f"\n❌ Error al validar imágenes de usuario: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("======= TEST DE CLOUDINARY =======")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar configuración
    config_ok = test_cloudinary_config()
    
    # Si la configuración está bien, realizar pruebas adicionales
    if config_ok:
        upload_ok = upload_test_image()
        validation_ok = validate_user_images()
        
        # Resumen
        print("\n=== RESUMEN DE PRUEBAS ===")
        print(f"Configuración de Cloudinary: {'✅ OK' if config_ok else '❌ Error'}")
        print(f"Subida de imágenes: {'✅ OK' if upload_ok else '❌ Error'}")
        print(f"Validación de URLs: {'✅ OK' if validation_ok else '❌ Error'}")
        
        if config_ok and upload_ok and validation_ok:
            print("\n✅ Cloudinary está correctamente configurado y funcionando")
        else:
            print("\n⚠️ Hay algunos problemas con la configuración de Cloudinary")
    else:
        print("\n❌ Error en la configuración básica de Cloudinary")

if __name__ == "__main__":
    main()
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
