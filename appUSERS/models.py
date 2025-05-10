from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        PermissionsMixin,
                                        BaseUserManager)
<<<<<<< HEAD
from cloudinary.models import CloudinaryField
from appUSERS.utils import validate_image_file
=======
>>>>>>> parent of 640a78d (storage de iamgenes)


# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_user(self,email,password, **extra_fields):
        if not email:
            raise ValueError('Falta Email')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)

        return user


    def create_superuser(self,email,password,**extra_fields):
        user = self.create_user(email=email,password=password,**extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)

        return user


class Usuario(AbstractBaseUser,PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)  
    nombre = models.CharField(max_length=45)
    email = models.EmailField(unique=True)  
    apellido = models.CharField(max_length=45)
    telefono = models.CharField(max_length=13)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)  
    is_active = models.BooleanField(default=True)
<<<<<<< HEAD
    imagen_perfil = CloudinaryField('imagen_perfil', blank=True, null=True,
                                   folder='perfil_usuarios',
                                   transformation={
                                       'quality': 'auto:good',
                                       'fetch_format': 'auto',
                                       'width': 300, 
                                       'height': 300, 
                                       'crop': 'fill',
                                       'gravity': 'face'
                                   })
    # Campo adicional para guardar la URL completa de la imagen
    imagen_perfil_url = models.URLField(max_length=500, blank=True, null=True)
=======
>>>>>>> parent of 640a78d (storage de iamgenes)

    class Meta:
        managed = True
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __unicode__(self):
        return self.nombre
        
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Si hay una imagen de perfil y no hay URL o se ha cambiado la imagen
        # entonces actualizamos la URL
        if self.imagen_perfil:
            self.imagen_perfil_url = self.imagen_perfil.url
        
        super().save(*args, **kwargs)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'