# Food ISPC API

## Descripción
API RESTful para la aplicación Food ISPC, desarrollada con Django y Django Rest Framework.

## Nuevas Funcionalidades

### Gestión de Imágenes de Perfil con Cloudinary

Se ha implementado la funcionalidad para que los usuarios puedan subir y gestionar imágenes de perfil utilizando el servicio Cloudinary.

#### Características principales:
- Almacenamiento seguro de imágenes en la nube
- Transformaciones automáticas (redimensionamiento, recorte enfocado en rostros)
- Optimización automática de calidad y formato
- Acceso a URLs seguras (HTTPS)

## Instalación

### Requisitos previos
- Python 3.8 o superior
- MySQL o PostgreSQL
- Cuenta en Cloudinary (gratuita o de pago)

### Pasos de instalación

1. Clonar el repositorio:
```
git clone <url-del-repositorio>
cd backmobile1
```

2. Crear un entorno virtual e instalar dependencias:
```
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar variables de entorno (o en settings.py):
```
# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

4. Aplicar migraciones:
```
python manage.py makemigrations
python manage.py migrate
```

5. Ejecutar el servidor:
```
python manage.py runserver
```

## API Endpoints

### Autenticación y Gestión de Usuarios

- `POST /appUSERS/register/` - Registrar un nuevo usuario
- `POST /appUSERS/login/` - Iniciar sesión y obtener token JWT
- `POST /appUSERS/logout/` - Cerrar sesión
- `GET /appUSERS/me/` - Obtener datos del perfil del usuario actual
- `PUT /appUSERS/update/` - Actualizar datos del perfil, incluida la imagen
- `DELETE /appUSERS/delete/` - Eliminar cuenta de usuario
- `POST /appUSERS/upload-image/` - Subir o actualizar imagen de perfil

### Productos

- `GET /api/producto/` - Listar todos los productos
- `GET /api/producto/<id>/` - Obtener detalle de un producto específico

### Carrito y Pedidos

- `GET /appCART/carrito/` - Ver el carrito actual
- `POST /appCART/carrito/add/` - Añadir producto al carrito
- `DELETE /appCART/carrito/remove/<producto_id>/` - Eliminar producto del carrito
- `POST /appCART/pedido/create/` - Crear un nuevo pedido

## Testing

Para probar la funcionalidad de Cloudinary:

```
python test_cloudinary.py
```

Para probar la API completa, incluyendo la gestión de imágenes:

```
python test_api.py
```

## Documentación de APIs

### API de Actualización de Perfil

#### Request
```
PUT /appUSERS/update/
Content-Type: multipart/form-data
Authorization: Bearer {token}

{
  "nombre": "Nuevo Nombre",
  "apellido": "Nuevo Apellido",
  "telefono": "123456789",
  "imagen_perfil": [ARCHIVO]
}
```

#### Response
```json
{
  "email": "usuario@ejemplo.com",
  "nombre": "Nuevo Nombre",
  "apellido": "Nuevo Apellido",
  "telefono": "123456789",
  "imagen_perfil": "https://res.cloudinary.com/djp80kwaj/image/upload/v1234567890/perfil_usuarios/abcdef123456.jpg"
}
```

### API de Subida de Imagen

#### Request
```
POST /appUSERS/upload-image/
Content-Type: multipart/form-data
Authorization: Bearer {token}

{
  "imagen_perfil": [ARCHIVO]
}
```

#### Response
```json
{
  "detalle": "Imagen de perfil actualizada correctamente.",
  "imagen_perfil": "https://res.cloudinary.com/djp80kwaj/image/upload/v1234567890/perfil_usuarios/abcdef123456.jpg"
}
```

## Contribuir
1. Crea un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Sube los cambios a tu fork (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia
Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE.md para más detalles.
