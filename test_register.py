"""
Script para probar la creación de usuarios con imágenes de perfil
"""
import requests
import os
import sys
import json
import argparse

def register_user_with_image(base_url, user_data, image_path):
    """Registrar un usuario con imagen de perfil"""
    register_url = f"{base_url}/appUSERS/register/"
    
    # Verificar si la imagen existe
    if image_path and not os.path.exists(image_path):
        print(f"Error: No se encuentra la imagen en {image_path}")
        return None
    
    # Preparar los datos del formulario
    data = user_data.copy()
    files = {}
    
    if image_path:
        with open(image_path, 'rb') as image_file:
            files = {
                'imagen_perfil': image_file
            }
    
    try:
        # Si hay imagen, usamos multipart/form-data
        if files:
            response = requests.post(register_url, data=data, files=files)
        else:
            response = requests.post(register_url, json=data)
        
        if response.status_code == 201 or response.status_code == 200:
            print("Usuario registrado correctamente")
            result = response.json()
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"Error al registrar usuario: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error en la solicitud: {str(e)}")
        return None

def login_user(base_url, email, password):
    """Iniciar sesión y obtener token JWT"""
    login_url = f"{base_url}/appUSERS/login/"
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=data)
        if response.status_code == 200:
            print("Login exitoso")
            result = response.json()
            
            # Verificar si hay imagen de perfil
            if 'imagen_perfil' in result and result['imagen_perfil']:
                print(f"Imagen de perfil URL: {result['imagen_perfil']}")
                
                # Intentar abrir la imagen en el navegador
                open_image = input("¿Desea abrir la imagen en el navegador? (s/n): ").lower()
                if open_image == 's':
                    import webbrowser
                    webbrowser.open(result['imagen_perfil'])
            else:
                print("El usuario no tiene imagen de perfil")
                
            return result
        else:
            print(f"Error al iniciar sesión: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error en la solicitud: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Prueba de registro de usuario con imagen de perfil')
    parser.add_argument('--url', type=str, default='http://localhost:8000', help='URL base del API')
    parser.add_argument('--email', type=str, required=True, help='Email del usuario')
    parser.add_argument('--password', type=str, required=True, help='Contraseña del usuario')
    parser.add_argument('--nombre', type=str, required=True, help='Nombre del usuario')
    parser.add_argument('--apellido', type=str, required=True, help='Apellido del usuario')
    parser.add_argument('--telefono', type=str, required=True, help='Teléfono del usuario')
    parser.add_argument('--imagen', type=str, help='Ruta a la imagen de perfil (opcional)')
    parser.add_argument('--login-only', action='store_true', help='Solo iniciar sesión, no registrar')
    
    args = parser.parse_args()
    
    # Datos del usuario
    user_data = {
        'email': args.email,
        'password': args.password,
        'nombre': args.nombre,
        'apellido': args.apellido,
        'telefono': args.telefono
    }
    
    if args.login_only:
        print("=== INICIANDO SESIÓN ===")
        login_user(args.url, args.email, args.password)
    else:
        print("=== REGISTRANDO USUARIO ===")
        result = register_user_with_image(args.url, user_data, args.imagen)
        
        if result:
            print("\n=== INICIANDO SESIÓN ===")
            login_user(args.url, args.email, args.password)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("1. Para registrar un usuario nuevo:")
        print("   python test_register.py --email usuario@ejemplo.com --password clave123 --nombre Juan --apellido Perez --telefono 123456789 --imagen ruta/a/imagen.jpg")
        print("2. Para solo iniciar sesión:")
        print("   python test_register.py --email usuario@ejemplo.com --password clave123 --nombre n --apellido a --telefono t --login-only")
    else:
        main()
