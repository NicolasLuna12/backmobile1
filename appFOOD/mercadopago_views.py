import mercadopago
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# Vista para crear una preferencia de pago de MercadoPago
class MercadoPagoPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sdk = mercadopago.SDK("APP_USR-1638397842548868-051022-6da127c22d6d3b0e023d8ae29f3618c2-2435347984")
        items = request.data.get('items', [])
        preference_data = {
            "items": items,
            "payer": {
                "email": request.user.email
            }
        }
        preference_response = sdk.preference().create(preference_data)
        if preference_response[0] == 201:
            return Response({
                "init_point": preference_response[1]["init_point"],
                "preference_id": preference_response[1]["id"]
            })
        else:
            return Response({"error": "No se pudo crear la preferencia de pago."}, status=status.HTTP_400_BAD_REQUEST)
