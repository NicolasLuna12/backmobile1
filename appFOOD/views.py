from rest_framework import viewsets
from .models import Producto
from .serializers import ProductoSerializer
from .mercadopago_views import MercadoPagoPreferenceView

# Create your views here.


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()
