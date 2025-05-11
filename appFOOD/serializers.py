from rest_framework import serializers
from .models import Producto, CategoriaProducto, MercadoPagoPayment

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
            model = Producto
            fields = '__all__'

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
            model = CategoriaProducto
            fields = '__all__'

class MercadoPagoPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MercadoPagoPayment
        fields = '__all__'
        read_only_fields = ['id_payment', 'created_at', 'updated_at']
