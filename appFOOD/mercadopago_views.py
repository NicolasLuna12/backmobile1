import mercadopago
import logging
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MercadoPagoPayment

# Configuración del token de acceso de MercadoPago
MERCADOPAGO_ACCESS_TOKEN = "APP_USR-1638397842548868-051022-6da127c22d6d3b0e023d8ae29f3618c2-2435347984"

# Inicialización del SDK de MercadoPago
sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)


class MercadoPagoPreferenceView(APIView):
    """
    Vista para crear una preferencia de pago en MercadoPago
    """
    def post(self, request):
        try:
            # Obtener datos del pedido
            order_data = request.data
            if not order_data:
                return Response({"error": "Debes proporcionar los datos del pedido"}, status=400)
            
            # Registrar datos recibidos para depuración
            logging.info(f"Datos recibidos para preferencia de MercadoPago: {json.dumps(order_data, indent=2)}")
            
            # Extraer productos del carrito
            items = order_data.get('items', [])
            if not items:
                return Response({"error": "El pedido debe contener al menos un producto"}, status=400)
            
            # Crear la estructura de preferencia para MercadoPago
            preference_data = {
                "items": [
                    {
                        "title": item.get('title', 'Producto de ISPC Food'),
                        "quantity": item.get('quantity', 1),
                        "unit_price": float(item.get('unit_price', 0)),
                        "currency_id": "ARS",
                        "description": item.get('description', 'Producto de ISPC Food'),
                        "picture_url": item.get('picture_url', '')
                    } for item in items
                ],
                "back_urls": {
                    "success": "https://ispcfood.netlify.app/success",
                    "failure": "https://ispcfood.netlify.app/failure",
                    "pending": "https://ispcfood.netlify.app/pending"
                },
                "auto_return": "approved",
                "notification_url": "https://backmobile1.onrender.com/api/producto/mercadopago/payment/",
                "statement_descriptor": "ISPC Food",
                "external_reference": order_data.get('external_reference', ''),
                "expires": True,
                "expiration_date_from": None,
                "expiration_date_to": None
            }
            
            # Agregar información del comprador si está disponible
            if 'payer' in order_data:
                preference_data['payer'] = order_data['payer']
            
            # Crear la preferencia en MercadoPago
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            return Response({
                "id": preference["id"],
                "init_point": preference["init_point"],
                "sandbox_init_point": preference["sandbox_init_point"]
            })
        
        except Exception as e:
            logging.exception("Error al crear preferencia de MercadoPago")
            return Response({"error": str(e)}, status=500)


class MercadoPagoPaymentView(APIView):
    """
    Vista para recibir notificaciones de pagos de MercadoPago
    """
    @csrf_exempt
    def post(self, request):
        try:
            # Datos de la notificación
            notification_data = request.data
            logging.info(f"Notificación de MercadoPago recibida: {json.dumps(notification_data, indent=2)}")
            
            # Verificar el tipo de notificación
            if 'type' not in notification_data:
                return Response({"error": "Tipo de notificación no especificado"}, status=400)
            
            notification_type = notification_data['type']
            
            if notification_type == 'payment':
                # Obtener ID de pago de la notificación
                payment_id = notification_data.get('data', {}).get('id')
                if not payment_id:
                    return Response({"error": "ID de pago no encontrado en la notificación"}, status=400)
                
                # Obtener detalles del pago desde MercadoPago
                payment_info = sdk.payment().get(payment_id)
                if payment_info["status"] != 200:
                    return Response({"error": "No se pudo obtener información del pago"}, status=400)
                
                payment_data = payment_info["response"]
                
                # Guardar o actualizar el pago en nuestra base de datos
                payment, created = MercadoPagoPayment.objects.update_or_create(
                    payment_id=str(payment_id),
                    defaults={
                        'preference_id': payment_data.get('preference_id'),
                        'external_reference': payment_data.get('external_reference'),
                        'status': payment_data.get('status'),
                        'status_detail': payment_data.get('status_detail'),
                        'payment_type': payment_data.get('payment_type_id'),
                        'merchant_order_id': payment_data.get('order', {}).get('id'),
                        'transaction_amount': payment_data.get('transaction_amount', 0),
                        'payment_method_id': payment_data.get('payment_method_id'),
                        'payer_email': payment_data.get('payer', {}).get('email'),
                        'notification_data': notification_data
                    }
                )
                
                logging.info(f"Pago {'creado' if created else 'actualizado'}: {payment}")
                
                # Aquí podrías añadir lógica adicional según el estado del pago
                # Por ejemplo, actualizar el stock de productos, notificar al usuario, etc.
                
            return Response({"status": "OK"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logging.exception("Error procesando notificación de MercadoPago")
            return Response({"error": str(e)}, status=500)


class MercadoPagoProcessPaymentView(APIView):
    """
    Vista para procesar pagos a través de la API de Pagos de MercadoPago
    """
    def post(self, request):
        try:
            # Obtener datos del pago
            payment_data = request.data
            if not payment_data:
                return Response({"error": "Debes proporcionar los datos del pago"}, status=400)
            
            # Registrar datos recibidos para depuración
            logging.info(f"Datos recibidos para procesar pago de MercadoPago: {json.dumps(payment_data, indent=2)}")
            
            # Validar campos requeridos para la API de Pagos
            required_fields = ["transaction_amount", "token", "description", "installments", 
                              "payment_method_id", "payer.email"]
            
            # Crear el pago a través de la API de MercadoPago
            payment_response = sdk.payment().create(payment_data)
            
            if payment_response["status"] != 201 and payment_response["status"] != 200:
                return Response({
                    "error": "Error al crear el pago",
                    "details": payment_response.get("response", {})
                }, status=400)
                
            payment = payment_response["response"]
            
            # Guardar el pago en nuestra base de datos
            mp_payment = MercadoPagoPayment.objects.create(
                payment_id=str(payment.get('id')),
                preference_id=payment.get('preference_id'),
                external_reference=payment.get('external_reference'),
                status=payment.get('status'),
                status_detail=payment.get('status_detail'),
                payment_type=payment.get('payment_type_id'),
                merchant_order_id=payment.get('order', {}).get('id'),
                transaction_amount=payment.get('transaction_amount', 0),
                payment_method_id=payment.get('payment_method_id'),
                payer_email=payment.get('payer', {}).get('email'),
                notification_data=payment
            )
            
            logging.info(f"Pago almacenado en base de datos: {mp_payment}")
            
            # Devolver el resultado
            return Response({
                "status": payment["status"],
                "status_detail": payment["status_detail"],
                "id": payment["id"]
            })
            
        except Exception as e:
            logging.exception("Error procesando pago con MercadoPago")
            return Response({"error": str(e)}, status=500)


class MercadoPagoBricksConfigView(APIView):
    """
    Vista para obtener la configuración necesaria para inicializar Bricks de MercadoPago en el frontend
    """
    def get(self, request):
        try:
            return Response({
                "public_key": "APP_USR-7552529630821540-051100-8923ae58494d373f3e3e00c335057d3e-146918484",
                "site_id": "MLA",
                "locale": "es-AR"
            })
        except Exception as e:
            logging.exception("Error al obtener configuración de MercadoPago Bricks")
            return Response({"error": str(e)}, status=500)


class MercadoPagoPaymentListView(APIView):
    """
    Vista para listar pagos de MercadoPago
    """
    def get(self, request):
        try:
            # Filtrar por estado si se proporciona
            status_filter = request.query_params.get('status', None)
            if status_filter:
                payments = MercadoPagoPayment.objects.filter(status=status_filter).order_by('-created_at')
            else:
                payments = MercadoPagoPayment.objects.all().order_by('-created_at')
            
            # Serializar los pagos
            from .serializers import MercadoPagoPaymentSerializer
            serializer = MercadoPagoPaymentSerializer(payments, many=True)
            
            return Response(serializer.data)
        except Exception as e:
            logging.exception("Error al listar pagos de MercadoPago")
            return Response({"error": str(e)}, status=500)


class MercadoPagoPaymentDetailView(APIView):
    """
    Vista para obtener detalles de un pago específico
    """
    def get(self, request, payment_id):
        try:
            # Buscar pago en nuestra base de datos
            try:
                payment = MercadoPagoPayment.objects.get(payment_id=payment_id)
                from .serializers import MercadoPagoPaymentSerializer
                serializer = MercadoPagoPaymentSerializer(payment)
                return Response(serializer.data)
            except MercadoPagoPayment.DoesNotExist:
                # Si no existe en nuestra BD, consultar a MercadoPago
                payment_info = sdk.payment().get(payment_id)
                if payment_info["status"] != 200:
                    return Response({"error": "Pago no encontrado"}, status=404)
                
                return Response(payment_info["response"])
                
        except Exception as e:
            logging.exception(f"Error al obtener detalles del pago {payment_id}")
            return Response({"error": str(e)}, status=500)
