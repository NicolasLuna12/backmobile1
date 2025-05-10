import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings

def configurar_cloudinary():
    """Configura Cloudinary con las credenciales proporcionadas"""
    cloudinary.config(
        cloud_name="djp80kwaj",
        api_key="285359299675698",
        api_secret="CILwUfSuiDsJ977SrrCvPQcgJz4"
    )

def subir_imagen_a_cloudinary(imagen, nombre_usuario):
    """
    Sube una imagen a Cloudinary
    
    Args:
        imagen: Archivo de imagen subido
        nombre_usuario: Nombre del usuario para identificar la imagen
        
    Returns:
        URL de la imagen en Cloudinary
    """
    # Configurar Cloudinary
    configurar_cloudinary()
    
    # Subir imagen a Cloudinary con un nombre único basado en el usuario
    resultado = cloudinary.uploader.upload(
        imagen,
        public_id=f"perfil_{nombre_usuario}_{imagen.name}",
        folder="perfiles_usuarios"
    )
    
    # Retornar la URL segura de la imagen
    return resultado['secure_url']
