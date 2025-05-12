from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet
from .mercadopago_views import (
    MercadoPagoPreferenceView, 
    MercadoPagoPaymentView, 
    MercadoPagoProcessPaymentView,
    MercadoPagoBricksConfigView,
    MercadoPagoPaymentListView,
    MercadoPagoPaymentDetailView
)

router = DefaultRouter()
router.register('', ProductoViewSet )

app_name = 'producto'

urlpatterns = [
    path('', include(router.urls)),
    # Endpoints MercadoPago
    path('mercadopago/preference/', MercadoPagoPreferenceView.as_view(), name='mercadopago-preference'),
    path('mercadopago/payment/', MercadoPagoPaymentView.as_view(), name='mercadopago-payment'),
    path('mercadopago/process-payment/', MercadoPagoProcessPaymentView.as_view(), name='mercadopago-process-payment'),
    path('mercadopago/bricks-config/', MercadoPagoBricksConfigView.as_view(), name='mercadopago-bricks-config'),
    path('mercadopago/payments/', MercadoPagoPaymentListView.as_view(), name='mercadopago-payments-list'),
    path('mercadopago/payments/<str:payment_id>/', MercadoPagoPaymentDetailView.as_view(), name='mercadopago-payment-detail'),
]
