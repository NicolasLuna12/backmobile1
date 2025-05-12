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
                    "title": f"{detalle.id_producto.nombre}",
                    "quantity": int(detalle.cantidad_productos),
                    "unit_price": float(detalle.precio_producto),
                    "currency_id": "ARS"  # Ajustar según el país
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
            
            logger.info(f"Webhook MercadoPago recibido: {topic} - {json.dumps(data)}")
            
            if topic == 'payment':
                payment_id = request.GET.get('id', '')
                if payment_id:
                    # Procesar el pago
                    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                    payment_info = sdk.payment().get(payment_id)
                    
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
                                    "payment_id": payment_id,
                                    "status": status_payment,
                                    "monto": Decimal(str(payment_data.get("transaction_amount", 0))),
                                    "datos_pago": json.dumps(payment_data)
                                }
                            )
                            
                            if not created:
                                # Actualizar pago existente
                                pago.payment_id = payment_id
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
                        
                        except Pedido.DoesNotExist:
                            logger.error(f"Pedido no encontrado para external_reference: {external_reference}")
                    
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
            except Exception as e:
                logger.error(f"Error al consultar estado de pago a MercadoPago: {str(e)}")
        
        serializer = MercadoPagoPagoSerializer(pago)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error al consultar estado de pago: {str(e)}")
        return Response(
            {"error": "Error al consultar el estado del pago"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
