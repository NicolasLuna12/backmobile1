
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet
from .payu_views import (
    PayUConfigView,
    PayUProcessPaymentView,
    PayUNotificationView
)

router = DefaultRouter()
router.register('', ProductoViewSet )

app_name = 'producto'


urlpatterns = [
    path('', include(router.urls)),
    
    # PayU endpoints
    path('payu/config/', PayUConfigView.as_view(), name='payu-config'),
    path('payu/process-payment/', PayUProcessPaymentView.as_view(), name='payu-process-payment'),
    path('payu/notification/', PayUNotificationView.as_view(), name='payu-notification'),
]
