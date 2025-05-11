import mercadopago
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# Puedes poner tu access token aquí o en settings.py
ACCESS_TOKEN = getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", None)

class MercadoPagoPreferenceView(APIView):
    def post(self, request):
        mp = mercadopago.SDK(ACCESS_TOKEN)
        items = request.data.get("items", [])
        if not items or not isinstance(items, list):
            return Response({"error": "Debes enviar al menos un item válido."}, status=400)
        # Validación extra de los campos requeridos por MercadoPago
        for item in items:
            if not all(k in item for k in ("title", "quantity", "currency_id", "unit_price")):
                return Response({"error": "Cada item debe tener title, quantity, currency_id y unit_price."}, status=400)
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
