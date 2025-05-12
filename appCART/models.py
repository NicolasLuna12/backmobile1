from django.db import models
from appUSERS.models import Usuario
from appFOOD.models import Producto
from django.conf import settings

class Pedido(models.Model):
    id_pedidos = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING)
    fecha_pedido = models.DateField(null=True)  
    hora_pedido = models.TimeField(null=True)  
    direccion_entrega = models.CharField(max_length=100, null=True)
    estado = models.CharField(max_length=50, default='pendiente', null=True)  

    class Meta:
        managed = True
        db_table = 'pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    def __unicode__(self):
        return self.id_pedidos
    #def __str__(self):
    #    return self.id_pedidos 

class Carrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='carrito_producto')
    cantidad = models.PositiveIntegerField(default=1)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comprado = models.BooleanField(default=False)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    class Meta:
        db_table = 'carrito'
    
class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)  
    id_pedido = models.ForeignKey(Pedido, models.DO_NOTHING, related_name='detalles')
    id_producto = models.ForeignKey(Producto, models.DO_NOTHING)
    cantidad_productos = models.IntegerField(null=True)  
    precio_producto = models.FloatField()
    subtotal = models.FloatField(null=True)  
    class Meta:
        managed = True
        db_table = 'detalle_pedido'
        verbose_name = 'Detallepedido'
        verbose_name_plural = 'Detallepedidos'
    def __unicode__(self):
        return self.id_detalle
    #def __str__(self):
    #    return self.id_detalle

class MercadoPagoPago(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('authorized', 'Autorizado'),
        ('in_process', 'En Proceso'),
        ('in_mediation', 'En Mediación'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
        ('charged_back', 'Contracargo'),
    ]

    id_pago = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    preference_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    datos_pago = models.JSONField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mercadopago_pago'
        verbose_name = 'Pago Mercado Pago'
        verbose_name_plural = 'Pagos Mercado Pago'

    def __str__(self):
        return f"Pago {self.id_pago} - Pedido {self.pedido.id_pedidos} - Estado: {self.status}"