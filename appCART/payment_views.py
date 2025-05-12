import mercadopago
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from django.conf import settings
from .models import Pedido, DetallePedido, Pago
from decimal import Decimal

# Configura el cliente de Mercado Pago
ACCESS_TOKEN = settings.MERCADO_PAGO_ACCESS_TOKEN
sdk = mercadopago.SDK(ACCESS_TOKEN)

class CrearPreferenciaPago(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Obtener el pedido pendiente del usuario
            pedido = Pedido.objects.get(id_usuario=request.user.id_usuario, estado="Pendiente")
            detalles = DetallePedido.objects.filter(id_pedido=pedido).select_related('id_producto')
            
            if not detalles.exists():
                return Response({"error": "El pedido está vacío"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calcular el monto total
            monto_total = sum(detalle.subtotal for detalle in detalles)
            
            # Crear los items para la preferencia de MP
            items = []
            for detalle in detalles:
                items.append({
                    "title": detalle.id_producto.nombre_producto,
                    "quantity": detalle.cantidad_productos,
                    "currency_id": "ARS",  # Moneda Argentina
                    "unit_price": float(detalle.precio_producto),
                    "picture_url": detalle.id_producto.imageURL if hasattr(detalle.id_producto, 'imageURL') else ""
                })
            
            # URLs de retorno (ajústalas según tus rutas de frontend)
            success_url = "https://ispcfood.netlify.app/payment/success"
            failure_url = "https://ispcfood.netlify.app/payment/failure"
            pending_url = "https://ispcfood.netlify.app/payment/pending"
            
            # Datos del comprador
            payer = {
                "name": request.user.nombre if hasattr(request.user, 'nombre') else request.user.username,
                "email": request.user.email,
                "identification": {
                    "type": "DNI",
                    "number": "12345678"  # Esto debería venir del usuario
                }
            }
            
            # Configuración de la preferencia con más detalles
            preference_data = {
                "items": items,
                "back_urls": {
                    "success": success_url,
                    "failure": failure_url,
                    "pending": pending_url
                },
                "auto_return": "approved",
                "binary_mode": True,  # Solo acepta pagos aprobados o rechazados
                "statement_descriptor": "ISPC Food",  # Descripción que aparecerá en el resumen de tarjeta
                "external_reference": str(pedido.id_pedidos),
                "payer": payer,
                "notification_url": request.build_absolute_uri(reverse('webhook_mercado_pago'))
            }
            
            preference_response = sdk.preference().create(preference_data)
            
            if preference_response["status"] != 201 and preference_response["status"] != 200:
                return Response({"error": "Error al crear preferencia de pago"}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            preference = preference_response["response"]
            
            # Guardar la información del pago
            pago, created = Pago.objects.get_or_create(
                pedido=pedido,
                defaults={
                    'monto_total': Decimal(str(monto_total)),
                    'preference_id': preference["id"]
                }
            )
            
            if not created:
                pago.monto_total = Decimal(str(monto_total))
                pago.preference_id = preference["id"]
                pago.save()
            
            # Devolver la información de la preferencia
            return Response({
                "preference_id": preference["id"],
                "init_point": preference["init_point"],
                "sandbox_init_point": preference.get("sandbox_init_point"),
                "pedido_id": pedido.id_pedidos
            })
            
        except Pedido.DoesNotExist:
            return Response({"error": "No hay un pedido pendiente"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WebhookMercadoPago(APIView):
    def post(self, request):
        try:
            # Obtener datos del webhook
            data = request.data
            topic = request.query_params.get("topic") or request.query_params.get("type")
            
            # Guardar los datos en un log para depuración
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Webhook recibido: {topic}")
            logger.info(f"Datos recibidos: {data}")
            
            if topic == "payment":
                payment_id = request.query_params.get("id") or request.query_params.get("data.id")
                
                if not payment_id:
                    # Intentar obtener el ID de pago del cuerpo de la solicitud
                    if data and isinstance(data, dict):
                        payment_id = data.get("data", {}).get("id")
                
                if not payment_id:
                    return Response({"error": "ID de pago no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Verificar el pago
                payment_info = sdk.payment().get(payment_id)
                
                if payment_info["status"] == 200:
                    payment_data = payment_info["response"]
                    external_reference = payment_data.get("external_reference")
                    status_detail = payment_data.get("status_detail")
                    payment_status = payment_data.get("status")
                    payment_method = payment_data.get("payment_method_id")
                    merchant_order_id = payment_data.get("order", {}).get("id")
                    transaction_amount = payment_data.get("transaction_amount")
                    
                    logger.info(f"Pago {payment_id} - Estado: {payment_status} - Pedido: {external_reference}")
                    
                    # Buscar el pedido asociado
                    try:
                        pedido = Pedido.objects.get(id_pedidos=external_reference)
                        
                        # Actualizar o crear el pago
                        pago, created = Pago.objects.get_or_create(
                            pedido=pedido,
                            defaults={
                                'monto_total': Decimal(str(transaction_amount)) if transaction_amount else 0,
                                'estado_pago': payment_status,
                                'payment_id': payment_id,
                                'merchant_order_id': merchant_order_id,
                                'metodo_pago': payment_method
                            }
                        )
                        
                        if not created:
                            pago.estado_pago = payment_status
                            pago.payment_id = payment_id
                            pago.merchant_order_id = merchant_order_id
                            pago.metodo_pago = payment_method
                            pago.save()
                        
                        # Si el pago es aprobado, actualizar el estado del pedido
                        if payment_status == "approved":
                            pedido.estado = "Pagado"
                            pedido.save()
                            
                            # Marcar los productos del carrito como comprados
                            from .models import Carrito
                            carrito_items = Carrito.objects.filter(id_pedido=pedido)
                            for item in carrito_items:
                                item.comprado = True
                                item.save()
                        
                        return Response({"status": "webhook processed", "payment_status": payment_status}, 
                                      status=status.HTTP_200_OK)
                    
                    except Pedido.DoesNotExist:
                        logger.error(f"Pedido con ID {external_reference} no encontrado")
                        return Response({"error": f"Pedido con ID {external_reference} no encontrado"}, 
                                      status=status.HTTP_404_NOT_FOUND)
            
            return Response({"status": "webhook received"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en webhook: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultarEstadoPago(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pedido_id):
        try:
            pedido = Pedido.objects.get(id_pedidos=pedido_id, id_usuario=request.user.id_usuario)
            
            try:
                pago = Pago.objects.get(pedido=pedido)
                
                # Si hay un payment_id, consultar el estado actualizado en Mercado Pago
                if pago.payment_id:
                    payment_info = sdk.payment().get(pago.payment_id)
                    
                    if payment_info["status"] == 200:
                        payment_data = payment_info["response"]
                        nuevo_estado = payment_data.get("status")
                        
                        # Actualizar solo si el estado ha cambiado
                        if nuevo_estado and nuevo_estado != pago.estado_pago:
                            pago.estado_pago = nuevo_estado
                            pago.save()
                            
                            # Si el pago está aprobado, actualizar el pedido
                            if nuevo_estado == "approved" and pedido.estado == "Pendiente":
                                pedido.estado = "Pagado"
                                pedido.save()
                                
                                # Marcar los productos del carrito como comprados
                                from .models import Carrito
                                carrito_items = Carrito.objects.filter(id_pedido=pedido)
                                for item in carrito_items:
                                    item.comprado = True
                                    item.save()
                
                # Obtener detalles del pago para la respuesta
                detalles_pedido = DetallePedido.objects.filter(id_pedido=pedido).select_related('id_producto')
                
                # Construir respuesta detallada
                return Response({
                    "pedido": {
                        "id": pedido.id_pedidos,
                        "fecha": pedido.fecha_pedido,
                        "hora": pedido.hora_pedido,
                        "direccion": pedido.direccion_entrega,
                        "estado": pedido.estado
                    },
                    "pago": {
                        "id": pago.id_pago,
                        "estado": pago.estado_pago,
                        "monto_total": float(pago.monto_total),
                        "fecha_pago": pago.fecha_pago,
                        "metodo_pago": pago.metodo_pago,
                        "preference_id": pago.preference_id,
                        "payment_id": pago.payment_id
                    },
                    "detalles": [
                        {
                            "producto": detalle.id_producto.nombre_producto,
                            "cantidad": detalle.cantidad_productos,
                            "precio_unitario": detalle.precio_producto,
                            "subtotal": detalle.subtotal
                        } for detalle in detalles_pedido
                    ],
                    "init_point": None,  # Si necesitamos generar un nuevo punto de pago
                    "next_action": self._determinar_siguiente_accion(pago.estado_pago)
                })
                
            except Pago.DoesNotExist:
                # Si no existe información de pago, redirigir a crear preferencia
                return Response({
                    "pedido_id": pedido.id_pedidos,
                    "estado_pedido": pedido.estado,
                    "estado_pago": "Sin información de pago",
                    "next_action": "crear_preferencia"
                })
                
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    def _determinar_siguiente_accion(self, estado_pago):
        """Determina la siguiente acción basada en el estado del pago"""
        if estado_pago == "approved":
            return "ver_confirmacion"
        elif estado_pago in ["rejected", "cancelled"]:
            return "reintentar_pago"
        elif estado_pago in ["pending", "in_process", "authorized"]:
            return "esperar_confirmacion"
        else:
            return "crear_preferencia"

class FinalizarPago(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pedido_id):
        try:
            pedido = Pedido.objects.get(id_pedidos=pedido_id, id_usuario=request.user.id_usuario)
            
            try:
                pago = Pago.objects.get(pedido=pedido)
                
                if pago.estado_pago == "approved":
                    # Actualizar el estado del pedido si no estaba ya actualizado
                    if pedido.estado != "Pagado":
                        pedido.estado = "Pagado"
                        pedido.save()
                    
                    # Limpiar carrito asociado al pedido
                    from .models import Carrito
                    Carrito.objects.filter(id_pedido=pedido).delete()
                    
                    return Response({
                        "message": "Pago finalizado correctamente",
                        "pedido_id": pedido.id_pedidos,
                        "estado": "Pagado"
                    })
                else:
                    return Response({
                        "error": "El pago aún no ha sido aprobado",
                        "estado_pago": pago.estado_pago
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except Pago.DoesNotExist:
                return Response({
                    "error": "No existe información de pago para este pedido"
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)
