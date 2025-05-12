from rest_framework import serializers
from .models import Carrito, DetallePedido, Pedido, MercadoPagoPago

class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        fields = ['id', 'producto', 'cantidad', 'usuario']

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ["cantidad_productos", "precio_producto", "subtotal"]

class ModificarCantidadSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(min_value=1)

class MercadoPagoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MercadoPagoPago
        fields = ['id_pago', 'pedido', 'payment_id', 'preference_id', 'status', 'monto', 
                 'fecha_creacion', 'fecha_actualizacion', 'datos_pago']
        read_only_fields = ['id_pago', 'fecha_creacion', 'fecha_actualizacion']

class MercadoPagoPreferenceSerializer(serializers.Serializer):
    pedido_id = serializers.IntegerField()
    redirect_url = serializers.URLField(required=False)
