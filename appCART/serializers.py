from rest_framework import serializers
from .models import Carrito, DetallePedido, Pago, Pedido

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

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id_pago', 'pedido', 'monto_total', 'fecha_pago', 'estado_pago', 'payment_id', 'preference_id', 'metodo_pago']

class PedidoConPagoSerializer(serializers.ModelSerializer):
    pago = PagoSerializer(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = ['id_pedidos', 'fecha_pedido', 'hora_pedido', 'direccion_entrega', 'estado', 'detalles', 'pago']
