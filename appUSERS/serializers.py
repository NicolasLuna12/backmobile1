from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
import cloudinary.uploader
from appUSERS.utils import validate_image_file

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'nombre', 'apellido', 'telefono', 'imagen_perfil', 'imagen_perfil_url']
        extra_kwargs = {
            'password': {'write_only': True},
            'imagen_perfil_url': {'read_only': True}  # Aseguramos que este campo sea solo de lectura
        }

    def create(self, validate_data):
        return get_user_model().objects.create_user(**validate_data)

    def update(self, instance, validate_data):
        password = validate_data.pop('password', None)
        
        # Si hay una imagen en la solicitud y es un archivo (no una URL de Cloudinary)
        imagen_perfil = validate_data.get('imagen_perfil', None)
        if imagen_perfil and not isinstance(imagen_perfil, str):
            try:
                # Validar el archivo de imagen
                validate_image_file(imagen_perfil)
            except Exception as e:
                raise serializers.ValidationError({'imagen_perfil': str(e)})
        
        user = super().update(instance, validate_data)

        if password:
            user.set_password(password)
            user.save()

        return user
        
    def to_representation(self, instance):
        """
        Asegurarse de que la URL de la imagen de perfil sea completa
        """
        ret = super().to_representation(instance)
        
        # Si tenemos URL almacenada, la usamos directamente
        if instance.imagen_perfil_url:
            ret['imagen_perfil'] = instance.imagen_perfil_url
            print(f"Usando URL almacenada: {instance.imagen_perfil_url}")
        # Si no hay URL almacenada pero sí hay imagen, generamos la URL
        elif instance.imagen_perfil:
            try:
                imagen_url = instance.imagen_perfil.url
                ret['imagen_perfil'] = imagen_url
                # Actualizar la URL en la base de datos para futuros usos
                instance.imagen_perfil_url = imagen_url
                instance.save(update_fields=['imagen_perfil_url'])
                print(f"URL generada y guardada: {imagen_url}")
            except Exception as e:
                print(f"Error al generar URL: {str(e)}")
        else:
            print(f"Usuario {instance.email} no tiene imagen de perfil")
        
        return ret

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style ={'input_type' : 'password'}, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(
            request = self.context.get('request'),
            username = email,
            password = password
        )

        if not user:
            raise serializers.ValidationError('No se pudo Autenticar', code = 'autorizacion')
        
        data['user'] = user
        return data