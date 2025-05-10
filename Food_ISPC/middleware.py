"""
Middleware para ayudar en el debugging de solicitudes con archivos
"""
import logging

logger = logging.getLogger(__name__)

class FileUploadDebugMiddleware:
    """
    Middleware que registra información de depuración sobre solicitudes
    que contienen archivos subidos, útil para solucionar problemas de
    carga de archivos en Cloudinary.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar solicitud antes de la vista
        if hasattr(request, 'FILES') and request.FILES:
            logger.info(f"REQUEST FILES: {request.method} {request.path}")
            for file_name, file_obj in request.FILES.items():
                logger.info(f"  - {file_name}: {file_obj.name}, {file_obj.size} bytes, {file_obj.content_type}")

            if hasattr(request, 'META'):
                content_type = request.META.get('CONTENT_TYPE', 'Unknown')
                content_length = request.META.get('CONTENT_LENGTH', 'Unknown')
                logger.info(f"Content-Type: {content_type}")
                logger.info(f"Content-Length: {content_length}")

        response = self.get_response(request)

        # Procesar respuesta después de la vista
        return response
