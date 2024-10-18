# Importaciones necesarias
from rest_framework import generics, authentication, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import Usuario
from .serializers import UsuarioSerializer, AuthTokenSerializer

# ================================
# Vistas para manejo de Usuarios
# ================================

class CreateUsuarioView(generics.CreateAPIView):
    """
    Vista para crear un nuevo usuario.
    """
    serializer_class = UsuarioSerializer


class RetrieveUpdateUsuarioView(generics.RetrieveUpdateAPIView):
    """
    Vista para obtener y actualizar el usuario autenticado.
    Solo permite al usuario autenticado acceder a su propio perfil.
    """
    serializer_class = UsuarioSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retorna el usuario autenticado
        return self.request.user


class DeleteUsuarioView(generics.DestroyAPIView):
    """
    Vista para eliminar un usuario por su email.
    Solo permite al usuario autenticado eliminar su propio perfil.
    """
    serializer_class = UsuarioSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_object(self):
        # Obtiene el usuario por email o lanza un 404 si no existe
        email = self.kwargs['email']
        return get_object_or_404(Usuario, email=email)

    def delete(self, request, *args, **kwargs):
        usuario = self.get_object()
        # Verifica si el usuario autenticado es el mismo que quiere eliminar
        if usuario != request.user:
            return Response(
                {"detalle": "No tienes permiso para eliminar este usuario."},
                status=status.HTTP_403_FORBIDDEN
            )
        usuario.delete()
        return Response(
            {"detalle": "Usuario eliminado exitosamente."},
            status=status.HTTP_204_NO_CONTENT
        )

# ================================
# Vistas para Autenticación
# ================================

class CreateTokenView(APIView):
    """
    Vista para generar un token de acceso (JWT) para el usuario autenticado.
    """
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Genera los tokens de acceso y refresco para el usuario
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'email': user.email,
            'user_id': user.pk,
            'refresh': str(refresh),
            'access': str(access_token),
            'nombre': user.nombre,
            'apellido': user.apellido,
            'telefono': user.telefono,
            'admin': user.is_superuser
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Vista para realizar el logout del usuario autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            return Response(
                {"detalle": "Logout Satisfactorio."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detalle": "Error inesperado."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================
# Permisos Personalizados
# ================================

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite editar o eliminar 
    solo si el usuario autenticado es el propietario del objeto.
    """
    def has_object_permission(self, request, view, obj):
        # Permitir siempre las peticiones de solo lectura
        if request.method in permissions.SAFE_METHODS:
            return True
        # Permitir edición solo si el usuario es el propietario del objeto
        return obj.id == request.user.id
