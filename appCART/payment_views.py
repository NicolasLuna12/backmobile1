import json
import logging
import mercadopago
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import Pedido, DetallePedido, MercadoPagoPago
from .serializers import MercadoPagoPreferenceSerializer, MercadoPagoPagoSerializer

logger = logging.getLogger(__name__)

class MercadoPagoCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MercadoPagoPreferenceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        pedido_id = serializer.validated_data['pedido_id']
        
        try:
            # Obtener el pedido y verificar que pertenece al usuario actual
            pedido = get_object_or_404(Pedido, id_pedidos=pedido_id)
            if pedido.id_usuario.id_usuario != request.user.id_usuario:
                return Response(
                    {"error": "No tienes permiso para acceder a este pedido"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener los detalles del pedido
            detalles = DetallePedido.objects.filter(id_pedido=pedido)
            if not detalles.exists():
                return Response(
                    {"error": "El pedido no tiene productos"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calcular el monto total
            total = sum(detalle.subtotal for detalle in detalles if detalle.subtotal)
            
            # Iniciar SDK de MercadoPago
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
              # Preparar ítems para la preferencia
            items = []
            for detalle in detalles:
                item = {
                    "title": f"{detalle.id_producto.nombre_producto}",
                    "quantity": int(detalle.cantidad_productos),
                    "unit_price": float(detalle.precio_producto),
                    "currency_id": "COP"  # Moneda: Pesos Colombianos
                }
                items.append(item)
            
            # Configurar URLs de redirección
            base_url = request.build_absolute_uri('/')[:-1]
            success_url = settings.MERCADO_PAGO_SUCCESS_URL
            failure_url = settings.MERCADO_PAGO_FAILURE_URL
            pending_url = settings.MERCADO_PAGO_PENDING_URL
            
            # Si se proporciona una URL de redirección personalizada
            if 'redirect_url' in serializer.validated_data:
                redirect_base = serializer.validated_data['redirect_url']
                success_url = f"{redirect_base}/success"
                failure_url = f"{redirect_base}/failure"
                pending_url = f"{redirect_base}/pending"
            
            # Crear la preferencia de pago
            preference_data = {
                "items": items,
                "back_urls": {
                    "success": success_url,
                    "failure": failure_url,
                    "pending": pending_url
                },
                "auto_return": "approved",
                "external_reference": str(pedido.id_pedidos),
                "notification_url": f"{base_url}{reverse('mercadopago-webhook')}"
            }
            
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            # Guardar información del pago
            mercadopago_pago = MercadoPagoPago.objects.create(
                pedido=pedido,
                preference_id=preference["id"],
                monto=Decimal(str(total)),
                datos_pago=json.dumps(preference)
            )
            
            # Actualizar estado del pedido
            pedido.estado = "en_proceso_pago"
            pedido.save()
            
            # Retornar datos para el frontend
            return Response({
                "preference_id": preference["id"],
                "public_key": settings.MERCADO_PAGO_PUBLIC_KEY,
                "init_point": preference["init_point"],
                "sandbox_init_point": preference.get("sandbox_init_point"),
                "pago_id": mercadopago_pago.id_pago
            })
            
        except Exception as e:
            logger.error(f"Error al crear preferencia de MercadoPago: {str(e)}")
            return Response(
                {"error": "Error al procesar el pago. Inténtelo más tarde."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class MercadoPagoWebhookView(APIView):
    def post(self, request):
        try:
            # Obtener datos de la notificación
            data = request.data
            topic = request.GET.get('topic', '')
            id_received = request.GET.get('id', '')
            
            logger.info(f"Webhook MercadoPago recibido: Tema:{topic}, ID:{id_received}, Data:{json.dumps(data)}")
            
            # SDK de Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            
            # Procesar según el tipo de notificación
            if topic == 'payment':
                # Notificación de pago
                if id_received:
                    payment_info = sdk.payment().get(id_received)
                    
                    if payment_info["status"] == 200:
                        payment_data = payment_info["response"]
                        external_reference = payment_data.get("external_reference")
                        status_payment = payment_data.get("status")
                        
                        # Buscar el pedido asociado
                        try:
                            pedido = Pedido.objects.get(id_pedidos=external_reference)
                            
                            # Buscar o crear pago
                            pago, created = MercadoPagoPago.objects.get_or_create(
                                pedido=pedido,
                                defaults={
                                    "payment_id": id_received,
                                    "status": status_payment,
                                    "monto": Decimal(str(payment_data.get("transaction_amount", 0))),
                                    "datos_pago": json.dumps(payment_data)
                                }
                            )
                            
                            if not created:
                                # Actualizar pago existente
                                pago.payment_id = id_received
                                pago.status = status_payment
                                pago.datos_pago = json.dumps(payment_data)
                                pago.save()
                            
                            # Actualizar estado del pedido
                            if status_payment == "approved":
                                pedido.estado = "pagado"
                            elif status_payment in ["rejected", "cancelled"]:
                                pedido.estado = "pago_fallido"
                            else:
                                pedido.estado = "pago_pendiente"
                            
                            pedido.save()
                            logger.info(f"Pago {id_received} procesado con éxito: {status_payment}")
                        
                        except Pedido.DoesNotExist:
                            logger.error(f"Pedido no encontrado para external_reference: {external_reference}")
            
            elif topic == 'merchant_order':
                # Notificación de orden de comercio
                if id_received:
                    order_info = sdk.merchant_order().get(id_received)
                    if order_info["status"] == 200:
                        order_data = order_info["response"]
                        external_reference = order_data.get("external_reference")
                        logger.info(f"Orden de comercio recibida: {id_received}, Ref: {external_reference}")
                        
                        # Procesar pagos asociados a la orden
                        payments = order_data.get("payments", [])
                        for payment in payments:
                            payment_id = payment.get("id")
                            if payment_id:
                                # Procesar cada pago (similar al código anterior)
                                logger.info(f"Procesando pago {payment_id} de la orden {id_received}")
            
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            logger.error(f"Error al procesar webhook de MercadoPago: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, pago_id):
    """
    Consultar el estado de un pago
    """
    try:
        pago = get_object_or_404(MercadoPagoPago, id_pago=pago_id)
        
        # Verificar permisos
        if pago.pedido.id_usuario.id_usuario != request.user.id_usuario:
            return Response(
                {"error": "No tienes permiso para acceder a este pago"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si el pago está pendiente, consultar a Mercado Pago
        if pago.status in ['pending', 'in_process']:
            try:
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                if pago.payment_id:
                    payment_info = sdk.payment().get(pago.payment_id)
                    
                    if payment_info["status"] == 200:
                        payment_data = payment_info["response"]
                        pago.status = payment_data.get("status", pago.status)
                        pago.datos_pago = json.dumps(payment_data)
                        pago.save()
                        
                        # Actualizar el estado del pedido
                        if pago.status == "approved":
                            pago.pedido.estado = "pagado"
                        elif pago.status in ["rejected", "cancelled"]:
                            pago.pedido.estado = "pago_fallido"
                        else:
                            pago.pedido.estado = "pago_pendiente"
                        
                        pago.pedido.save()
                        
                        logger.info(f"Estado de pago actualizado: {pago_id} -> {pago.status}")
            except Exception as e:
                logger.error(f"Error al consultar estado de pago a MercadoPago: {str(e)}")
        
        # Obtener detalles del pedido para incluir en la respuesta
        detalles = DetallePedido.objects.filter(id_pedido=pago.pedido)
        detalles_data = []
        for detalle in detalles:
            detalles_data.append({
                "producto": detalle.id_producto.nombre_producto,
                "cantidad": detalle.cantidad_productos,
                "precio_unitario": detalle.precio_producto,
                "subtotal": detalle.subtotal
            })
        
        # Preparar datos de respuesta
        serializer = MercadoPagoPagoSerializer(pago)
        response_data = serializer.data
        
        # Agregar información adicional
        response_data['detalles_pedido'] = detalles_data
        response_data['fecha_pedido'] = pago.pedido.fecha_pedido
        response_data['estado_pedido'] = pago.pedido.estado
        
        # Información de pago interpretada
        status_labels = {
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'authorized': 'Autorizado',
            'in_process': 'En Proceso',
            'in_mediation': 'En Mediación',
            'rejected': 'Rechazado',
            'cancelled': 'Cancelado',
            'refunded': 'Reembolsado',
            'charged_back': 'Contracargo'
        }
        
        response_data['estado_pago_texto'] = status_labels.get(pago.status, pago.status)
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error al consultar estado de pago: {str(e)}")
        return Response(
            {"error": "Error al consultar el estado del pago"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
