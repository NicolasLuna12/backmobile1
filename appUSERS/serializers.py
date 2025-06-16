from django.contrib.auth import get_user_model,authenticate
from rest_framework import serializers
from .models import Usuario
import pyotp
import qrcode
import base64
from io import BytesIO

class UsuarioSerializer(serializers.ModelSerializer):
    imagen_perfil_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    direccion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = get_user_model()

        fields = ['email','password','nombre','apellido','telefono','direccion','imagen_perfil_url']

        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
        
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        imagen_perfil_url = validated_data.pop('imagen_perfil_url', None)
        direccion = validated_data.pop('direccion', None)
        user = super().update(instance, validated_data)

        if imagen_perfil_url is not None:
            user.imagen_perfil_url = imagen_perfil_url
            user.save()
            
        if direccion is not None:
            user.direccion = direccion
            user.save()

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password =serializers.CharField(style ={'input_type' : 'password'}, write_only=True)

    def validate(self,data):
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

class TwoFASetupSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['twofa_secret', 'twofa_enabled', 'qr_code']
        read_only_fields = ['qr_code']

    def get_qr_code(self, obj):
        if not obj.twofa_secret:
            return None
        totp = pyotp.TOTP(obj.twofa_secret)
        uri = totp.provisioning_uri(name=obj.email, issuer_name="MiApp")
        qr = qrcode.make(uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

class TwoFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField()