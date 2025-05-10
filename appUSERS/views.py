from rest_framework import generics,authentication, permissions,status
from appCART.models import Carrito, Pedido
from appUSERS.serializers import UsuarioSerializer, AuthTokenSerializer 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser


class CreateUsuarioView(generics.CreateAPIView):
    serializer_class = UsuarioSerializer


class RetrieveUpdateUsuarioView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    

    def get_object(self):
        return self.request.user



class CreateTokenView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        response_data = {
            'email': user.email,
            'user_id': user.pk, 
            'refresh': str(refresh),
            'access': str(access_token),
            'nombre': user.nombre, 
            'apellido': user.apellido,
            'telefono': user.telefono,
            'admin': user.is_superuser
        }
        
        # Incluir la URL de la imagen de perfil si existe
        # Primero verificamos si hay una URL ya almacenada
        if user.imagen_perfil_url:
            response_data['imagen_perfil'] = user.imagen_perfil_url
            print(f"Login - Usando URL almacenada: {user.imagen_perfil_url}")
        # Si no hay URL almacenada pero sí hay imagen, la generamos y guardamos
        elif user.imagen_perfil:
            try:
                url = user.imagen_perfil.url
                response_data['imagen_perfil'] = url
                
                # Guardar la URL para uso futuro
                user.imagen_perfil_url = url
                user.save(update_fields=['imagen_perfil_url'])
                print(f"Login - URL generada y guardada: {url}")
            except Exception as e:
                print(f"Login - Error al generar URL: {str(e)}")
                import traceback
                print(traceback.format_exc())
        else:
            print(f"Login - Usuario {user.email} no tiene imagen de perfil")
            
        print(f"Login - Datos de respuesta: {response_data}")
        return Response(response_data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):       
        try:           
            return Response({"detalle": "Logout Satisfactorio."}, status=status.HTTP_200_OK)
        except Exception as e:
            
            return Response({"detalle": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        user = request.user
        # Manejar datos multipart/form-data y application/json
        data = request.data.copy()
        
        # Para depuración
        print(f"Datos recibidos: {data}")
        print(f"Archivos recibidos: {request.FILES}")
            
        serializer = UsuarioSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            try:
                user_updated = serializer.save()
                
                # Asegurarse de que la imagen_perfil_url esté actualizada
                if user_updated.imagen_perfil and not user_updated.imagen_perfil_url:
                    user_updated.imagen_perfil_url = user_updated.imagen_perfil.url
                    user_updated.save(update_fields=['imagen_perfil_url'])
                    print(f"URL generada y guardada en PUT: {user_updated.imagen_perfil_url}")
                
                # Construir la respuesta con todos los datos
                response_data = serializer.data
                if user_updated.imagen_perfil_url:
                    response_data['imagen_perfil'] = user_updated.imagen_perfil_url
                elif user_updated.imagen_perfil:
                    response_data['imagen_perfil'] = user_updated.imagen_perfil.url
                    
                # Asegurarnos de que la respuesta incluya la URL de imagen
                print(f"Datos de respuesta: {response_data}")
                return Response(response_data, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error al actualizar el perfil: {str(e)}")
                import traceback
                print(traceback.format_exc())
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        carrito = Carrito.objects.filter(usuario=user).first()

        if carrito and carrito.productos.exists():
            #return Response({"detalle": "No se puede eliminar el perfil porque el carrito contiene productos."}, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
        
        if carrito:
            carrito.delete()

        
        pedidos = Pedido.objects.filter(id_usuario=user)
        if pedidos.exists():
       
            user.delete()
            return Response({"detalle": "Perfil eliminado satisfactoriamente."}, status=status.HTTP_200_OK)

        user.delete()
        return Response({"detalle": "Perfil y carrito eliminados satisfactoriamente."}, status=status.HTTP_200_OK)

class UploadProfileImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        user = request.user
        if 'imagen_perfil' not in request.FILES:
            return Response({"detalle": "No se ha proporcionado ninguna imagen."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener el archivo de imagen
        imagen = request.FILES['imagen_perfil']
        print(f"Imagen recibida: {imagen.name}, {imagen.size} bytes, {imagen.content_type}")
        
        # Validar la imagen usando nuestra función de utilidad
        try:
            from appUSERS.utils import validate_image_file
            validate_image_file(imagen)
        except Exception as e:
            print(f"Error de validación: {str(e)}")
            return Response({"detalle": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        # Guardamos la imagen en Cloudinary a través del modelo
        try:
            # Eliminar imagen anterior si existe (para ahorrar espacio)
            if user.imagen_perfil:
                try:
                    import cloudinary.uploader
                    if hasattr(user.imagen_perfil, 'public_id'):
                        cloudinary.uploader.destroy(user.imagen_perfil.public_id)
                        print(f"Imagen anterior eliminada: {user.imagen_perfil.public_id}")
                except Exception as e:
                    print(f"Error al eliminar imagen anterior: {str(e)}")
            
            # Asignar nueva imagen
            user.imagen_perfil = imagen
            # Guardar para que se suba a Cloudinary
            user.save()
            
            # Obtener la URL generada y guardarla explícitamente
            if user.imagen_perfil:
                try:
                    url = user.imagen_perfil.url
                    user.imagen_perfil_url = url
                    user.save(update_fields=['imagen_perfil_url'])
                    print(f"URL generada y guardada en POST: {url}")
                except Exception as e:
                    print(f"Error al generar URL: {str(e)}")
            
            # Preparar respuesta
            response_data = {
                "detalle": "Imagen de perfil actualizada correctamente.",
                "imagen_perfil": user.imagen_perfil_url or (user.imagen_perfil.url if user.imagen_perfil else None)
            }
            print(f"URL en respuesta: {response_data['imagen_perfil']}")
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(f"Error al subir la imagen: {str(e)}")
            print(traceback.format_exc())
            return Response({"detalle": f"Error al procesar la imagen: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UsuarioSerializer(user)
        
        # Obtener datos serializados
        data = serializer.data
        
        # Asegurarse de que la URL de la imagen esté presente
        if user.imagen_perfil_url:
            data['imagen_perfil'] = user.imagen_perfil_url
            print(f"Profile GET - Usando URL almacenada: {user.imagen_perfil_url}")
        elif user.imagen_perfil:
            try:
                url = user.imagen_perfil.url
                data['imagen_perfil'] = url
                
                # Guardar la URL para uso futuro
                user.imagen_perfil_url = url
                user.save(update_fields=['imagen_perfil_url'])
                print(f"Profile GET - URL generada y guardada: {url}")
            except Exception as e:
                print(f"Profile GET - Error al generar URL: {str(e)}")
        else:
            print(f"Profile GET - Usuario {user.email} no tiene imagen de perfil")
            
        print(f"Profile GET - Datos de respuesta: {data}")
        return Response(data, status=status.HTTP_200_OK)