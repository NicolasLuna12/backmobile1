# Integración de Cloudinary para Imágenes de Perfil

## Descripción
Este proyecto integra Cloudinary para almacenar y gestionar las imágenes de perfil de los usuarios. Cloudinary es un servicio que permite alojar imágenes en la nube, optimizarlas automáticamente y entregarlas a través de una CDN para mayor rendimiento.

## Configuración Implementada

### Dependencias Instaladas
- `cloudinary`: Biblioteca principal para interactuar con la API de Cloudinary
- `django-cloudinary-storage`: Integración de Cloudinary con Django para almacenamiento de medios

### Configuración en settings.py
```python
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': "djp80kwaj",
    'API_KEY': "285359299675698",
    'API_SECRET': "CILwUfSuiDsJ977SrrCvPQcgJz4",
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### Modelo de Usuario Modificado
Se ha añadido un campo `CloudinaryField` para la imagen de perfil y un campo adicional `imagen_perfil_url` para almacenar la URL generada:

```python
imagen_perfil = CloudinaryField('imagen_perfil', blank=True, null=True,
                               folder='perfil_usuarios',
                               transformation={
                                   'quality': 'auto:good',
                                   'fetch_format': 'auto',
                                   'width': 300, 
                                   'height': 300, 
                                   'crop': 'fill',
                                   'gravity': 'face'
                               })
imagen_perfil_url = models.URLField(max_length=500, blank=True, null=True)
```

El modelo sobrescribe el método `save()` para actualizar automáticamente la URL cuando se cambia la imagen:

```python
def save(self, *args, **kwargs):
    if self.imagen_perfil:
        self.imagen_perfil_url = self.imagen_perfil.url
    super().save(*args, **kwargs)
```

## Endpoints Implementados

### Actualización de Perfil
- **URL**: `/appUSERS/update/`
- **Método**: PUT
- **Autenticación**: JWT Bearer Token
- **Formato**: multipart/form-data (para enviar archivos) o application/json
- **Descripción**: Actualiza los datos del perfil de usuario, incluida la imagen de perfil

### Subida de Imagen de Perfil
- **URL**: `/appUSERS/upload-image/`
- **Método**: POST
- **Autenticación**: JWT Bearer Token
- **Formato**: multipart/form-data
- **Campos**: `imagen_perfil` (archivo de imagen)
- **Descripción**: Endpoint específico para cargar o actualizar solo la imagen de perfil

### Obtener Perfil
- **URL**: `/appUSERS/me/`
- **Método**: GET
- **Autenticación**: JWT Bearer Token
- **Descripción**: Obtiene todos los datos del perfil, incluida la URL de la imagen

## Scripts de Utilidad

### migrate_images.py
Migra las URLs de imágenes existentes para asegurarse de que todos los usuarios tengan correctamente guardada la URL de su imagen de perfil.

### verify_images.py
Verifica la integridad de las imágenes de perfil, comprobando que las URLs sean accesibles y estén correctamente almacenadas.

### test_api.py
Cliente de prueba para interactuar con la API, incluyendo funciones para:
- Iniciar sesión y obtener token JWT
- Subir imágenes de perfil
- Actualizar datos de perfil
- Verificar respuestas de la API

## Solución de Problemas Comunes

### URLs de imágenes incorrectas o vacías
Si las URLs de las imágenes no se muestran correctamente, ejecuta:
```
python migrate_images.py
```

### Verificar la configuración de Cloudinary
Para asegurarte de que la conexión con Cloudinary funciona correctamente:
```
python test_cloudinary.py
```

### Problemas con la carga de imágenes
1. Asegúrate de que estás enviando la solicitud como `multipart/form-data`
2. El campo de imagen debe llamarse `imagen_perfil`
3. Verifica los formatos permitidos (PNG, JPG, JPEG, WebP)
4. El tamaño máximo permitido es de 5MB

## Notas de Implementación

1. Se ha implementado almacenamiento redundante de URLs para mejorar la eficiencia:
   - La URL generada por Cloudinary se guarda en el campo `imagen_perfil_url`
   - Esto evita tener que regenerar la URL cada vez que se consulta el perfil

2. Se utilizan transformaciones automáticas de Cloudinary:
   - Redimensionamiento a 300x300px
   - Optimización de calidad
   - Recorte inteligente enfocado en rostros

3. Las imágenes se almacenan en la carpeta `perfil_usuarios` en Cloudinary

4. Se implementó logging extensivo para facilitar la depuración de problemas

## Despliegue en Producción

Antes de desplegar en producción, asegúrate de:

1. Aplicar las migraciones:
```
python manage.py migrate
```

2. Ejecutar el script de migración de imágenes:
```
python migrate_images.py
```

3. Verificar la integridad de las imágenes:
```
python verify_images.py
```
