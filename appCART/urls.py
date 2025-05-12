from django.urls import path
from .views import *
from .payment_views import MercadoPagoCheckoutView, MercadoPagoWebhookView, payment_status

urlpatterns = [
    path('agregar/<int:producto_id>/', AgregarProductoAlCarrito.as_view()),
    path('ver/', VerCarrito.as_view()),
    path('confirmar/', ConfirmarPedido.as_view()),
    path('eliminar/<int:carrito_id>/', EliminarProductoDelCarrito.as_view()),
    path('ver_dashboard/', VerDashboard.as_view()),
    path('modificar_cantidad/<int:carrito_id>/', ModificarCantidadProductoCarrito.as_view(), name='modificar_cantidad_producto_carrito'),
    path('detalle_pedido/<int:pedido_id>/', VerDetallePedido.as_view(), name='detalle_pedido'),
    
    # Rutas para la integración con Mercado Pago
    path('checkout/mercadopago/', MercadoPagoCheckoutView.as_view(), name='mercadopago-checkout'),
    path('webhook/mercadopago/', MercadoPagoWebhookView.as_view(), name='mercadopago-webhook'),
    path('payment/status/<int:pago_id>/', payment_status, name='payment-status'),
]

