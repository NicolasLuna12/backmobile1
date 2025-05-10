"""
Middleware para depuración de subida de archivos en la aplicación Food_ISPC.
"""

class FileUploadDebugMiddleware:
    """
    Middleware para depurar solicitudes de carga de archivos.
    Registra información relevante sobre las solicitudes que contienen archivos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Procesar la solicitud antes de la vista
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.FILES:
                # Imprimir información sobre los archivos subidos para depuración
                print("\n" + "="*50)
                print("DEBUG: Archivo detectado en la solicitud")
                print(f"Método: {request.method}")
                print(f"Ruta: {request.path}")
                print(f"Usuario: {request.user}")
                
                for filename, fileobj in request.FILES.items():
                    print(f"Archivo: {filename}")
                    print(f"Nombre: {fileobj.name}")
                    print(f"Tamaño: {fileobj.size} bytes")
                    print(f"Tipo de contenido: {fileobj.content_type}")
                print("="*50 + "\n")
                
        # Continuar con el flujo normal
        response = self.get_response(request)
        
        # Procesar la respuesta después de la vista (opcional)
        return response
