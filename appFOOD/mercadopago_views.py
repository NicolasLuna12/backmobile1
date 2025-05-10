import mercadopago
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# Puedes poner tu access token aquí o en settings.py
ACCESS_TOKEN = "TEST-1322376657026626-051018-f027bd9d4ce077b4578cca4640d4c13c-146918484"

class MercadoPagoPreferenceView(APIView):
    def post(self, request):
        mp = mercadopago.SDK(ACCESS_TOKEN)
        items = request.data.get("items", [])
        if not items or not isinstance(items, list):
            return Response({"error": "Debes enviar al menos un item válido."}, status=400)
        preference_data = {
            "items": items
        }
        try:
            preference_response = mp.preference().create(preference_data)
            if preference_response["status"] == 201:
                return Response({
                    "init_point": preference_response["response"]["init_point"],
                    "preference_id": preference_response["response"]["id"]
                }, status=status.HTTP_201_CREATED)
            else:
                logging.error(f"MercadoPago error: {preference_response}")
                return Response({
                    "error": "No se pudo crear la preferencia de pago.",
                    "detalle": preference_response
                }, status=500)
        except Exception as e:
            logging.exception("Error inesperado al crear preferencia MercadoPago")
            return Response({"error": str(e)}, status=500)
