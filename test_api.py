"""
Script para probar la API de usuario y la subida de imágenes a Cloudinary.
"""
import requests
import os
import sys
import json
import time

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
    
    print(f"Iniciando sesión como {email}...")
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login exitoso")
        
        # Verificar si hay URL de imagen
        if 'imagen_perfil' in result:
            print(f"🖼️ Imagen de perfil URL: {result['imagen_perfil']}")
        else:
            print("❌ No hay imagen de perfil")
            
        return result
    else:
        print(f"❌ Error al iniciar sesión: {response.status_code}")
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
        print(f"❌ No se encuentra el archivo: {image_path}")
        return None
    
    # Obtener información del archivo para depuración
    file_size = os.path.getsize(image_path)
    print(f"Subiendo imagen {image_path} ({file_size} bytes)...")
    
    # Abrir el archivo de imagen
    with open(image_path, 'rb') as image_file:
        files = {
            'imagen_perfil': image_file
        }
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Imagen subida correctamente")
        
        # Verificar si se devolvió la URL de la imagen
        if 'imagen_perfil' in result:
            print(f"🖼️ URL generada: {result['imagen_perfil']}")
        else:
            print("⚠️ La API devolvió respuesta exitosa pero sin URL de imagen")
            
        return result
    else:
        print(f"❌ Error al subir imagen: {response.status_code}")
        print(response.text)
        return None

def update_profile(token, user_data):
    """Actualizar perfil de usuario con datos incluyendo imagen"""
    url = f"{BASE_URL}/appUSERS/update/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Actualizando perfil con datos: {user_data}")
    
    # Si hay ruta de imagen en user_data, la procesamos
    image_path = user_data.pop('imagen_perfil_path', None)
    
    if image_path:
        # Verificar si el archivo existe
        if not os.path.exists(image_path):
            print(f"❌ No se encuentra el archivo de imagen: {image_path}")
            return None
            
        # Preparamos para envío multipart
        files = {}
        with open(image_path, 'rb') as image_file:
            files['imagen_perfil'] = image_file
            
        # Convertir datos a formulario compatible con multipart
        form_data = user_data.copy()
        
        print(f"Enviando con imagen {image_path} como multipart/form-data")
        response = requests.put(url, headers=headers, data=form_data, files=files)
    else:
        # Envío solo de datos JSON
        print("Enviando solo datos JSON")
        response = requests.put(url, headers=headers, json=user_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Perfil actualizado correctamente")
        
        # Verificar si se devolvió la URL de la imagen
        if 'imagen_perfil' in result:
            print(f"🖼️ URL de imagen: {result['imagen_perfil']}")
        
        return result
    else:
        print(f"❌ Error al actualizar perfil: {response.status_code}")
        print(response.text)
        return None

def get_profile(token):
    """Obtener datos del perfil de usuario"""
    url = f"{BASE_URL}/appUSERS/me/"  # Esta ruta debe estar definida en tu API
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("Obteniendo perfil de usuario...")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Perfil obtenido correctamente")
        
        # Mostrar datos relevantes
        for key, value in result.items():
            if key != 'imagen_perfil' and key != 'password':
                print(f"{key}: {value}")
                
        # Mostrar URL de imagen específicamente
        if 'imagen_perfil' in result and result['imagen_perfil']:
            print(f"🖼️ URL de imagen: {result['imagen_perfil']}")
        else:
            print("❌ No hay imagen de perfil")
            
        return result
    else:
        print(f"❌ Error al obtener perfil: {response.status_code}")
        print(response.text)
        return None

def test_multiple_endpoints(token):
    """Probar varios endpoints para verificar la URL de la imagen en cada uno"""
    # Primero obtenemos el perfil
    profile = get_profile(token)
    
    # Pequeña pausa
    time.sleep(1)
    
    # Luego hacemos una actualización menor
    update_result = update_profile(token, {
        "telefono": "123456789"  # Actualización simple
    })
    
    # Verificar que las URLs sean consistentes
    if profile and update_result:
        profile_img = profile.get('imagen_perfil')
        update_img = update_result.get('imagen_perfil')
        
        if profile_img and update_img:
            if profile_img == update_img:
                print("\n✅ Las URLs son consistentes entre endpoints")
            else:
                print("\n⚠️ Las URLs son diferentes entre endpoints:")
                print(f"  Perfil: {profile_img}")
                print(f"  Actualización: {update_img}")
        else:
            print("\n⚠️ No se pudieron comparar las URLs: alguna está vacía")

def main():
    """Función principal para probar todas las funcionalidades"""
    # Credenciales de prueba
    email = input("Email: ")
    password = input("Contraseña: ")
    
    # Iniciar sesión
    auth_data = login(email, password)
    if not auth_data:
        print("No se pudo iniciar sesión. Abortando pruebas.")
        return
    
    # Obtener token de autenticación
    token = auth_data.get('access')
    if not token:
        print("No se encontró token de acceso en la respuesta. Abortando pruebas.")
        return
    
    while True:
        print("\n--- MENÚ DE PRUEBAS ---")
        print("1. Ver perfil")
        print("2. Actualizar perfil (sin imagen)")
        print("3. Subir imagen de perfil")
        print("4. Actualizar perfil completo (con imagen)")
        print("5. Probar consistencia entre endpoints")
        print("6. Salir")
        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            get_profile(token)
        
        elif opcion == "2":
            # Datos de prueba para actualización
            user_data = {
                "nombre": input("Nuevo nombre (o Enter para omitir): "),
                "apellido": input("Nuevo apellido (o Enter para omitir): "),
                "telefono": input("Nuevo teléfono (o Enter para omitir): ")
            }
            # Eliminar campos vacíos
            user_data = {k: v for k, v in user_data.items() if v}
            
            if user_data:
                update_profile(token, user_data)
            else:
                print("No hay datos para actualizar")
        
        elif opcion == "3":
            image_path = input("Ruta completa de la imagen a subir: ")
            upload_image(token, image_path)
        
        elif opcion == "4":
            # Datos de prueba para actualización con imagen
            user_data = {
                "nombre": input("Nuevo nombre (o Enter para omitir): "),
                "apellido": input("Nuevo apellido (o Enter para omitir): "),
                "telefono": input("Nuevo teléfono (o Enter para omitir): ")
            }
            # Eliminar campos vacíos
            user_data = {k: v for k, v in user_data.items() if v}
            
            # Añadir imagen si se proporciona
            image_path = input("Ruta completa de la imagen (o Enter para omitir): ")
            if image_path:
                user_data['imagen_perfil_path'] = image_path
                
            if user_data:
                update_profile(token, user_data)
            else:
                print("No hay datos para actualizar")
                
        elif opcion == "5":
            test_multiple_endpoints(token)
        
        elif opcion == "6":
            print("Saliendo del programa...")
            break
        
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    main()
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
