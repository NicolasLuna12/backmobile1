# filepath: e:\backmobile1\appUSERS\serializers.py
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

class UsuarioSerializer(serializers.ModelSerializer):
    imagen_perfil = serializers.ImageField(required=False, write_only=True)
    
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'nombre', 'apellido', 'telefono', 'imagen_perfil', 'imagen_perfil_url']
        extra_kwargs = {
            'password': {'write_only': True},
            'imagen_perfil_url': {'read_only': True}
        }

    def create(self, validated_data):
        imagen_perfil = validated_data.pop('imagen_perfil', None)
        user = get_user_model().objects.create_user(**validated_data)
        
        if imagen_perfil:
            from appUSERS.utils import subir_imagen_a_cloudinary
            # Subir la imagen a Cloudinary y guardar la URL
            url_imagen = subir_imagen_a_cloudinary(imagen_perfil, user.email)
            user.imagen_perfil_url = url_imagen
            user.save()
            
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        imagen_perfil = validated_data.pop('imagen_perfil', None)
        
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
            
        if imagen_perfil:
            from appUSERS.utils import subir_imagen_a_cloudinary
            # Subir la imagen a Cloudinary y guardar la URL
            url_imagen = subir_imagen_a_cloudinary(imagen_perfil, user.email)
            user.imagen_perfil_url = url_imagen
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError('No se pudo Autenticar', code='autorizacion')
        
        data['user'] = user
        return data
