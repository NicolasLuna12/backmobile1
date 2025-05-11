import json
import logging
import hashlib
import requests
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


# Credenciales de prueba para PayU Latam Argentina
PAYU_API_KEY = "4Vj8eK4rloUd272L48hsrarnUA"
PAYU_API_LOGIN = "pRRXKOl8ikMmt9u"
PAYU_MERCHANT_ID = "508029"
PAYU_ACCOUNT_ID = "512322"  # Argentina
API_URL = "https://sandbox.api.payulatam.com/payments-api/4.0/service.cgi"


class PayUConfigView(APIView):
    """
    Vista para obtener la configuración necesaria para inicializar PayU en el frontend
    """
    def get(self, request):
        try:
            return Response({
                "merchant_id": PAYU_MERCHANT_ID,
                "account_id": PAYU_ACCOUNT_ID,
                "api_key": PAYU_API_KEY,
                "api_login": PAYU_API_LOGIN,
                "is_test": True,
                "payment_url": API_URL,
                "currency": "ARS",
                "success_url": "https://ispcfood.netlify.app/success",
                "failure_url": "https://ispcfood.netlify.app/failure",
                "pending_url": "https://ispcfood.netlify.app/pending",
                "api_base_url": "https://backmobile1.onrender.com/api/producto",
                "process_payment_url": "/payu/process-payment/"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logging.exception("Error al obtener configuración de PayU")
            return Response({"error": str(e)}, status=500)


class PayUProcessPaymentView(APIView):
    """
    Vista para procesar pagos a través de PayU Latam
    """
    def post(self, request):
        # Obtener datos del pago
        payment_data = request.data
        if not payment_data:
            return Response({"error": "Debes proporcionar los datos del pago."}, status=400)
        
        # Registrar la solicitud para depuración
        logging.info(f"PayU payment data received: {json.dumps(payment_data, indent=2)}")
        
        # Validar campos requeridos
        required_fields = ["transaction_amount", "credit_card_number", "credit_card_expiration_date", 
                           "credit_card_security_code", "payment_method", "payer_name", "payer_email"]
        
        missing_fields = [field for field in required_fields if field not in payment_data]
        if missing_fields:
            return Response({
                "error": f"Faltan campos requeridos: {', '.join(missing_fields)}"
            }, status=400)
            
        # Extraer datos del pago
        transaction_amount = float(payment_data['transaction_amount'])
        credit_card_number = payment_data['credit_card_number']
        credit_card_expiration_date = payment_data['credit_card_expiration_date']
        credit_card_security_code = payment_data['credit_card_security_code']
        payment_method = payment_data['payment_method']
        payer_name = payment_data['payer_name']
        payer_email = payment_data['payer_email']
        
        # Valores opcionales
        description = payment_data.get('description', 'Compra en ISPC Food')
        installments = payment_data.get('installments', 1)
        
        # Generar referencia única
        reference = f"ISPCFOOD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Generar firma (signature)
        signature_string = f"{PAYU_API_KEY}~{PAYU_MERCHANT_ID}~{reference}~{transaction_amount}~ARS"
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
        
        # Preparar la solicitud para PayU
        payload = {
            "language": "es",
            "command": "SUBMIT_TRANSACTION",
            "merchant": {
                "apiKey": PAYU_API_KEY,
                "apiLogin": PAYU_API_LOGIN
            },
            "transaction": {
                "order": {
                    "accountId": PAYU_ACCOUNT_ID,
                    "referenceCode": reference,
                    "description": description,
                    "language": "es",
                    "signature": signature,
                    "notifyUrl": "https://backmobile1.onrender.com/api/producto/payu/notification/",
                    "additionalValues": {
                        "TX_VALUE": {
                            "value": transaction_amount,
                            "currency": "ARS"
                        }
                    },
                    "buyer": {
                        "fullName": payer_name,
                        "emailAddress": payer_email,
                        "dniNumber": payment_data.get('payer_document', "")
                    }
                },
                "payer": {
                    "fullName": payer_name,
                    "emailAddress": payer_email,
                    "dniNumber": payment_data.get('payer_document', "")
                },
                "creditCard": {
                    "number": credit_card_number,
                    "securityCode": credit_card_security_code,
                    "expirationDate": credit_card_expiration_date,
                    "name": payer_name
                },
                "extraParameters": {
                    "INSTALLMENTS_NUMBER": installments
                },
                "type": "AUTHORIZATION_AND_CAPTURE",
                "paymentMethod": payment_method,
                "paymentCountry": "AR",
                "deviceSessionId": payment_data.get('device_session_id', ""),
                "ipAddress": request.META.get('REMOTE_ADDR', '127.0.0.1'),
                "cookie": payment_data.get('cookie', ""),
                "userAgent": request.META.get('HTTP_USER_AGENT', '')
            },
            "test": True
        }
        
        try:
            # Enviar solicitud a PayU
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
            )
            
            # Procesar la respuesta
            if response.status_code == 200:
                response_data = response.json()
                logging.info(f"PayU response: {json.dumps(response_data, indent=2)}")
                
                if response_data.get('code') == 'SUCCESS':
                    transaction_info = response_data.get('transactionResponse', {})
                    return Response({
                        "status": transaction_info.get('state'),
                        "response_code": transaction_info.get('responseCode'),
                        "response_message": transaction_info.get('responseMessage'),
                        "transaction_id": transaction_info.get('transactionId'),
                        "order_id": transaction_info.get('orderId'),
                        "reference_code": reference,
                        "message": "Pago procesado correctamente" 
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        "error": "No se pudo procesar el pago.",
                        "code": response_data.get('code'),
                        "error_message": response_data.get('error')
                    }, status=400)
            else:
                logging.error(f"PayU error: {response.text}")
                return Response({
                    "error": "Error al comunicarse con PayU.",
                    "detail": response.text
                }, status=500)
        except Exception as e:
            logging.exception("Error inesperado al procesar pago con PayU")
            return Response({"error": str(e)}, status=500)


class PayUNotificationView(APIView):
    """
    Vista para recibir notificaciones de PayU
    """
    @csrf_exempt
    def post(self, request):
        try:
            notification_data = request.data
            logging.info(f"PayU notification received: {json.dumps(notification_data, indent=2)}")
            
            # Aquí procesarías la notificación según tus necesidades
            # Por ejemplo, actualizar el estado de un pedido en tu base de datos
            
            return Response({"status": "OK"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.exception("Error procesando notificación de PayU")
            return Response({"error": str(e)}, status=500)
