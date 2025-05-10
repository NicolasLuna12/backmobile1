"""
Script para crear un usuario de prueba con imagen de perfil directamente en la base de datos
"""
import os
import django
import sys
import cloudinary.uploader
from django.core.files.uploadedfile import SimpleUploadedFile

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Food_ISPC.settings")
django.setup()

# Importar después de configurar Django
from django.contrib.auth import get_user_model
import argparse

def create_test_user(email, password, nombre, apellido, telefono, imagen_path=None):
    """Crear un usuario de prueba con imagen de perfil"""
    User = get_user_model()
    
    # Verificar si el usuario ya existe
    if User.objects.filter(email=email).exists():
        print(f"El usuario con email {email} ya existe. Eliminando...")
        User.objects.filter(email=email).delete()
    
    # Crear el usuario
    user = User.objects.create_user(
        email=email,
        password=password,
        nombre=nombre,
        apellido=apellido,
        telefono=telefono
    )
    
    print(f"Usuario creado: {user.email} (ID: {user.pk})")
    
    # Si se proporciona una imagen, añadirla al perfil
    if imagen_path and os.path.exists(imagen_path):
        print(f"Cargando imagen desde: {imagen_path}")
        
        try:
            # Cargar la imagen a Cloudinary directamente
            with open(imagen_path, 'rb') as img_file:
                # Subir la imagen a Cloudinary
                upload_result = cloudinary.uploader.upload(
                    img_file,
                    folder="perfil_usuarios",
                    transformation={
                        'quality': 'auto:good',
                        'fetch_format': 'auto',
                        'width': 300, 
                        'height': 300, 
                        'crop': 'fill',
                        'gravity': 'face'
                    }
                )
                
                # Actualizar el campo imagen_perfil con el public_id de Cloudinary
                user.imagen_perfil = upload_result['public_id']
                
                # Guardar la URL generada
                user.imagen_perfil_url = upload_result['secure_url']
                
                user.save()
                
                print(f"Imagen cargada correctamente:")
                print(f"  Public ID: {upload_result['public_id']}")
                print(f"  URL: {upload_result['secure_url']}")
                
                # Intentar acceder a la URL de la imagen a través del modelo
                try:
                    model_url = user.imagen_perfil.url
                    print(f"URL generada por el modelo: {model_url}")
                    
                    if model_url != user.imagen_perfil_url:
                        print(f"ADVERTENCIA: La URL del modelo ({model_url}) no coincide con la URL almacenada ({user.imagen_perfil_url})")
                except Exception as e:
                    print(f"Error al acceder a la URL del modelo: {str(e)}")
        except Exception as e:
            print(f"Error al cargar la imagen: {str(e)}")
    else:
        if imagen_path:
            print(f"No se encontró la imagen en la ruta: {imagen_path}")
        else:
            print("No se proporcionó imagen de perfil.")
    
    return user

def main():
    parser = argparse.ArgumentParser(description='Crear un usuario de prueba con imagen de perfil')
    parser.add_argument('--email', type=str, default='test@example.com', help='Email del usuario')
    parser.add_argument('--password', type=str, default='testpassword', help='Contraseña del usuario')
    parser.add_argument('--nombre', type=str, default='Usuario', help='Nombre del usuario')
    parser.add_argument('--apellido', type=str, default='Prueba', help='Apellido del usuario')
    parser.add_argument('--telefono', type=str, default='123456789', help='Teléfono del usuario')
    parser.add_argument('--imagen', type=str, help='Ruta a la imagen de perfil')
    
    args = parser.parse_args()
    
    print("=== CREANDO USUARIO DE PRUEBA ===")
    user = create_test_user(
        args.email, 
        args.password, 
        args.nombre, 
        args.apellido, 
        args.telefono, 
        args.imagen
    )
    
    print("\n=== RESULTADO ===")
    print(f"Usuario creado: {user.email}")
    print(f"Nombre: {user.nombre} {user.apellido}")
    print(f"Teléfono: {user.telefono}")
    print(f"Imagen de perfil: {'Sí' if user.imagen_perfil else 'No'}")
    print(f"URL de imagen: {user.imagen_perfil_url if user.imagen_perfil_url else 'No disponible'}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python create_test_user.py --imagen ruta/a/tu/imagen.jpg")
        print("     (Los demás parámetros son opcionales)")
    else:
        main()
