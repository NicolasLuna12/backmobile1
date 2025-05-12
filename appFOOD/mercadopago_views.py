import mercadopago
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# Puedes poner tu access token aquí o en settings.py
ACCESS_TOKEN = "APP_USR-1638397842548868-051022-6da127c22d6d3b0e023d8ae29f3618c2-2435347984"

class MercadoPagoPreferenceView(APIView):
    def post(self, request):
        mp = mercadopago.SDK(ACCESS_TOKEN)
        items = request.data.get("items", [])
        preference_data = {
            "items": items
        }
        preference_response = mp.preference().create(preference_data)
        if preference_response["status"] == 201:
            return Response({
                "init_point": preference_response["response"]["init_point"],
                "preference_id": preference_response["response"]["id"]
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No se pudo crear la preferencia de pago."}, status=500)
