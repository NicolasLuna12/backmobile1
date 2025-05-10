from django.conf import settings
from django.core.exceptions import ValidationError
import mimetypes
import os

def validate_image_file(file):
    """
    Validar que el archivo sea una imagen y tenga una extensión válida.
    """
    # Verificar el tipo MIME del archivo
    file_mimetype = mimetypes.guess_type(file.name)[0]
    
    if not file_mimetype or not file_mimetype.startswith('image/'):
        raise ValidationError('El archivo debe ser una imagen.')
    
    # Verificar la extensión del archivo
    ext = os.path.splitext(file.name)[1].lower()[1:]
    allowed_formats = getattr(settings, 'CLOUDINARY_STORAGE_ALLOWABLE_FORMATS', ['png', 'jpg', 'jpeg', 'webp'])
    
    if ext not in allowed_formats:
        raise ValidationError(f'La extensión del archivo no es válida. Extensiones permitidas: {", ".join(allowed_formats)}')
    
    # Verificar el tamaño del archivo
    max_size = getattr(settings, 'CLOUDINARY_STORAGE_MAX_FILE_SIZE', 5 * 1024 * 1024)  # 5MB por defecto
    
    if file.size > max_size:
        raise ValidationError(f'El archivo es demasiado grande. El tamaño máximo permitido es {max_size / (1024 * 1024)}MB.')
    
    return True
