from django.db import models

# Create your models here.

class CategoriaProducto(models.Model):
    id_categoria = models.AutoField(primary_key=True)  
    nombre_categoria = models.CharField(max_length=45)  
    descripcion = models.CharField(max_length=45)

    class Meta:
        managed = True
        db_table = 'categoria_producto'
        verbose_name = 'Categoriaproducto'
        verbose_name_plural = 'Categoriaproductos'
    def __unicode__(self):
        return self.nombre_categoria
    def __str__(self):
        return self.nombre_categoria


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)  
    nombre_producto = models.CharField(max_length=45)  
    descripcion = models.CharField(max_length=200)
    precio = models.FloatField()
    stock = models.IntegerField(default = 0 )
    imageURL = models.CharField( max_length=100, null=True )
    id_categoria = models.ForeignKey(CategoriaProducto, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    def __unicode__(self):
        return self.nombre_producto
    def __str__(self):
        return self.nombre_producto


class MercadoPagoPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
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

    id_payment = models.AutoField(primary_key=True)
    payment_id = models.CharField(max_length=100, unique=True)
    preference_id = models.CharField(max_length=100, blank=True, null=True)
    external_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    status_detail = models.CharField(max_length=100, blank=True, null=True)
    payment_type = models.CharField(max_length=50, blank=True, null=True)
    merchant_order_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method_id = models.CharField(max_length=50, blank=True, null=True)
    payer_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notification_data = models.JSONField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mercadopago_payment'
        verbose_name = 'Pago MercadoPago'
        verbose_name_plural = 'Pagos MercadoPago'

    def __str__(self):
        return f"Pago #{self.payment_id} - {self.status}"


