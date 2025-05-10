from rest_framework import generics,authentication, permissions,status
from appCART.models import Carrito, Pedido
from appUSERS.serializers import UsuarioSerializer, AuthTokenSerializer 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class CreateUsuarioView(generics.CreateAPIView):
    serializer_class = UsuarioSerializer


class RetrieveUpdateUsuarioView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    authentication_classes = [authentication.TokenAuthentication]
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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):       
        try:           
            return Response({"detalle": "Logout Satisfactorio."}, status=status.HTTP_200_OK)
        except Exception as e:
            
            return Response({"detalle": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UsuarioSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteProfileView(APIView):
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