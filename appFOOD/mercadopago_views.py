import mercadopago
import logging
import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


ACCESS_TOKEN = getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", None)

class MercadoPagoBricksConfigView(APIView):
    """
    Vista para obtener la configuración necesaria para inicializar Mercado Pago Bricks en el frontend
    """
    def get(self, request):
        try:
            # Obtener la configuración desde settings
            public_key = "TEST-31a1ec17-44f8-4781-a611-a9ed80afed62"  # Clave pública de prueba de MercadoPago
            
            return Response({
                "publicKey": public_key,
                "site_url": "https://ispcfood.netlify.app",
                "success_url": "https://ispcfood.netlify.app/success",
                "failure_url": "https://ispcfood.netlify.app/failure",
                "pending_url": "https://ispcfood.netlify.app/pending",
                "api_base_url": "https://backmobile1.onrender.com/api/producto",
                "process_payment_url": "/mercadopago/process-payment/",
                "merchant_id": "146918484",  # Tu merchant ID de MercadoPago
                "preference_id": "",  # Se llena dinámicamente cuando se crea una preferencia
                "access_token": ACCESS_TOKEN.split("-")[1] if ACCESS_TOKEN else "",  # No enviar el token completo, solo usar para depuración
                "mode": "test" if ACCESS_TOKEN and ACCESS_TOKEN.startswith("TEST-") else "prod"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logging.exception("Error al obtener configuración de Bricks")
            return Response({"error": str(e)}, status=500)

class MercadoPagoPaymentView(APIView):
    def post(self, request):
        mp = mercadopago.SDK(ACCESS_TOKEN)
        
        # Obtener datos del pago
        payment_data = request.data.get("payment_data", {})
        if not payment_data:
            return Response({"error": "Debes proporcionar los datos del pago."}, status=400)
            
        # Validar campos requeridos
        required_fields = ["transaction_amount", "token", "description", "installments", 
                           "payment_method_id", "payer"]
        
        for field in required_fields:
            if field not in payment_data:
                return Response({"error": f"El campo '{field}' es requerido."}, status=400)
                
        # Asegurarse de que el pagador tenga email
        if "email" not in payment_data.get("payer", {}):
            return Response({"error": "El email del pagador es requerido."}, status=400)
            
        try:
            # Crear el pago utilizando la API de Pagos
            payment_response = mp.payment().create(payment_data)
            
            if payment_response["status"] == 201 or payment_response["status"] == 200:
                return Response({
                    "status": payment_response["response"]["status"],
                    "status_detail": payment_response["response"]["status_detail"],
                    "id": payment_response["response"]["id"]
                }, status=status.HTTP_201_CREATED)
            else:
                logging.error(f"MercadoPago error: {payment_response}")
                return Response({
                    "error": "No se pudo procesar el pago.",
                    "detalle": payment_response
                }, status=500)
        except Exception as e:
            logging.exception("Error inesperado al procesar pago con MercadoPago")
            return Response({"error": str(e)}, status=500)
            
            
class MercadoPagoProcessPaymentView(APIView):
    def post(self, request):
        mp = mercadopago.SDK(ACCESS_TOKEN)
        
        # Obtener datos del pago
        payment_data = request.data
        if not payment_data:
            return Response({"error": "Debes proporcionar los datos del pago."}, status=400)
        
        # Registrar la solicitud para depuración
        logging.info(f"Payment data received: {json.dumps(payment_data, indent=2)}")
        
        # Verificar si los datos vienen en formato Brick o en formato directo
        if 'formData' in payment_data:
            # Es formato Brick
            formData = payment_data.get('formData', {})
            payment_data = formData
        
        # Validaciones específicas para Process Payment API
        if 'transaction_amount' not in payment_data or 'token' not in payment_data:
            return Response({"error": "Se requieren los campos 'transaction_amount' y 'token'."}, status=400)
            
        # Valores por defecto si no están presentes
        if 'installments' not in payment_data:
            payment_data['installments'] = 1
            
        if 'payment_method_id' not in payment_data:
            return Response({"error": "Se requiere el campo 'payment_method_id'."}, status=400)
            
        # Obtener el email del pagador (puede estar en diferentes lugares según formato)
        email = None
        if 'email' in payment_data:
            email = payment_data['email']
        elif 'payer' in payment_data and 'email' in payment_data['payer']:
            email = payment_data['payer']['email']
            
        if not email:
            return Response({"error": "Se requiere el email del pagador."}, status=400)
              
        # Formatear los datos según la API de proceso de pago
        formatted_payment_data = {
            "transaction_amount": float(payment_data['transaction_amount']),
            "token": payment_data['token'],
            "description": payment_data.get('description', 'Compra en ISPC Food'),
            "installments": int(payment_data['installments']),
            "payment_method_id": payment_data['payment_method_id'],
            "payer": {
                "email": email,
                "entity_type": payment_data.get('entity_type', 'individual')  # Aseguramos que tenga un valor válido
            }
        }
        
        # Agregar datos adicionales si están presentes
        if 'issuer_id' in payment_data:
            formatted_payment_data['issuer_id'] = payment_data['issuer_id']
            
        if 'identification' in payment_data:
            formatted_payment_data['payer']['identification'] = payment_data['identification']
        
        try:
            # Crear el pago utilizando la API de Pagos
            payment_response = mp.payment().create(formatted_payment_data)
            
            if payment_response["status"] == 201 or payment_response["status"] == 200:
                logging.info(f"Pago procesado: ID {payment_response['response']['id']}")
                return Response({
                    "status": payment_response["response"]["status"],
                    "status_detail": payment_response["response"]["status_detail"],
                    "id": payment_response["response"]["id"],
                    "payment_method_id": payment_response["response"]["payment_method_id"],
                    "payment_type_id": payment_response["response"]["payment_type_id"],
                    "transaction_amount": payment_response["response"]["transaction_amount"],
                    "date_created": payment_response["response"]["date_created"],
                    "message": "Pago procesado correctamente"
                }, status=status.HTTP_201_CREATED)
            else:
                logging.error(f"MercadoPago error: {payment_response}")
                return Response({
                    "error": "No se pudo procesar el pago.",
                    "detalle": payment_response["response"] if "response" in payment_response else payment_response
                }, status=500)
        except Exception as e:
            logging.exception("Error inesperado al procesar pago con MercadoPago")
            return Response({"error": str(e)}, status=500)


class MercadoPagoPreferenceView(APIView):
    def post(self, request):
        mp = mercadopago.SDK(ACCESS_TOKEN)
        items = request.data.get("items", [])
        if not items or not isinstance(items, list):
            return Response({"error": "Debes enviar al menos un item válido."}, status=400)        # Validación extra de los campos requeridos por MercadoPago
        for item in items:
            if not all(k in item for k in ("title", "quantity", "currency_id", "unit_price")):
                return Response({"error": "Cada item debe tener title, quantity, currency_id y unit_price."}, status=400)
                
        preference_data = {
            "items": items,
            "back_urls": {
                "success": "https://ispcfood.netlify.app/success",
                "failure": "https://ispcfood.netlify.app/failure",
                "pending": "https://ispcfood.netlify.app/pending"
            },
            "auto_return": "approved"
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
