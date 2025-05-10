"""
Script para probar la API de usuario y la subida de imágenes a Cloudinary.
"""
import requests
import os
import sys
import json

# URL base para pruebas locales (cambiar según entorno)
BASE_URL = "http://localhost:8000"  # Para desarrollo local
# BASE_URL = "https://backmobile1.onrender.com"  # Para producción

def login(email, password):
    """Iniciar sesión y obtener token JWT"""
    url = f"{BASE_URL}/appUSERS/login/"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al iniciar sesión: {response.status_code}")
        print(response.text)
        return None

def upload_image(token, image_path):
    """Subir una imagen de perfil a través de la API"""
    url = f"{BASE_URL}/appUSERS/upload-image/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Verificar si el archivo existe
    if not os.path.exists(image_path):
        print(f"No se encuentra el archivo: {image_path}")
        return None
    
    # Abrir el archivo de imagen
    with open(image_path, 'rb') as image_file:
        files = {
            'imagen_perfil': image_file
        }
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al subir imagen: {response.status_code}")
        print(response.text)
        return None

def update_profile(token, user_data):
    """Actualizar perfil de usuario con datos incluyendo imagen"""
    url = f"{BASE_URL}/appUSERS/update/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Si hay ruta de imagen en user_data, la procesamos
    image_path = user_data.pop('imagen_perfil_path', None)
    
    if image_path:
        # Preparamos para envío multipart
        files = {}
        with open(image_path, 'rb') as image_file:
            files['imagen_perfil'] = image_file
        
        response = requests.put(url, headers=headers, data=user_data, files=files)
    else:
        # Envío solo de datos JSON
        response = requests.put(url, headers=headers, json=user_data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al actualizar perfil: {response.status_code}")
        print(response.text)
        return None

def get_profile(token):
    """Obtener datos del perfil de usuario"""
    url = f"{BASE_URL}/appUSERS/me/"  # Esta ruta debe estar definida en tu API
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener perfil: {response.status_code}")
        print(response.text)
        return None

def main():
    """Función principal para probar todas las funcionalidades"""
    # Credenciales de prueba
    email = input("Email: ")
    password = input("Password: ")
    
    # Iniciar sesión
    print("\n=== Iniciando sesión ===")
    auth_data = login(email, password)
    
    if not auth_data:
        print("No se pudo iniciar sesión. Fin de las pruebas.")
        return
    
    access_token = auth_data.get('access')
    print(f"Login exitoso. Token obtenido: {access_token[:20]}...")
    
    # Mostrar si hay imagen de perfil
    if 'imagen_perfil' in auth_data and auth_data['imagen_perfil']:
        print(f"Imagen de perfil actual: {auth_data['imagen_perfil']}")
    else:
        print("No hay imagen de perfil")
    
    # Preguntar si se quiere subir una imagen
    upload_option = input("\n¿Desea subir una imagen de perfil? (s/n): ").lower()
    if upload_option == 's':
        image_path = input("Ruta de la imagen a subir: ")
        
        print("\n=== Subiendo imagen ===")
        upload_result = upload_image(access_token, image_path)
        
        if upload_result:
            print("Imagen subida correctamente")
            print(f"URL de la imagen: {upload_result.get('imagen_perfil')}")
    
    # Preguntar si se quiere actualizar el perfil
    update_option = input("\n¿Desea actualizar datos del perfil? (s/n): ").lower()
    if update_option == 's':
        print("\n=== Actualizando perfil ===")
        
        user_data = {}
        for field in ['nombre', 'apellido', 'telefono']:
            value = input(f"{field.capitalize()}: ")
            if value:
                user_data[field] = value
        
        # Preguntar si se quiere incluir una imagen en la actualización
        include_image = input("¿Incluir imagen en la actualización? (s/n): ").lower()
        if include_image == 's':
            image_path = input("Ruta de la imagen: ")
            user_data['imagen_perfil_path'] = image_path
        
        update_result = update_profile(access_token, user_data)
        
        if update_result:
            print("Perfil actualizado correctamente")
            print(json.dumps(update_result, indent=2))

if __name__ == "__main__":
    main()
