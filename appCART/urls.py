from django.urls import path
from .views import *
from .payment_views import CrearPreferenciaPago, WebhookMercadoPago, ConsultarEstadoPago, FinalizarPago

urlpatterns = [
    path('agregar/<int:producto_id>/', AgregarProductoAlCarrito.as_view()),
    path('ver/', VerCarrito.as_view()),
    path('confirmar/', ConfirmarPedido.as_view()),
    path('eliminar/<int:carrito_id>/', EliminarProductoDelCarrito.as_view()),
    path('ver_dashboard/', VerDashboard.as_view()),
    path('modificar_cantidad/<int:carrito_id>/', ModificarCantidadProductoCarrito.as_view(), name='modificar_cantidad_producto_carrito'),
    path('detalle_pedido/<int:pedido_id>/', VerDetallePedidoConPago.as_view(), name='detalle_pedido_con_pago'),
    
    # URLs para pagos con Mercado Pago
    path('crear-preferencia/', CrearPreferenciaPago.as_view(), name='crear_preferencia_pago'),
    path('webhook/', WebhookMercadoPago.as_view(), name='webhook_mercado_pago'),
    path('estado-pago/<int:pedido_id>/', ConsultarEstadoPago.as_view(), name='consultar_estado_pago'),
    path('finalizar-pago/<int:pedido_id>/', FinalizarPago.as_view(), name='finalizar_pago'),
]

