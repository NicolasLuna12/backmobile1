from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet
from .mercadopago_views import MercadoPagoPreferenceView, MercadoPagoPaymentView, MercadoPagoProcessPaymentView

router = DefaultRouter()
router.register('', ProductoViewSet )

app_name = 'producto'



urlpatterns = [
    path('', include(router.urls)),
    path('mercadopago/preference/', MercadoPagoPreferenceView.as_view(), name='mercadopago-preference'),
    path('mercadopago/payment/', MercadoPagoPaymentView.as_view(), name='mercadopago-payment'),
    path('mercadopago/process-payment/', MercadoPagoProcessPaymentView.as_view(), name='mercadopago-process-payment'),
]
