# ISPC Food - Integración de PayU Latam

## Descripción

Este proyecto es el backend de la aplicación ISPC Food, y ahora utiliza exclusivamente PayU Latam como plataforma de procesamiento de pagos.

## Configuración de PayU Latam

El proyecto está configurado con credenciales de prueba para PayU Latam Argentina:

```
API Login: pRRXKOl8ikMmt9u
API Key: 4Vj8eK4rloUd272L48hsrarnUA
Merchant ID: 508029
Account ID: 512322
```

## Endpoints API de PayU

- `GET /api/producto/payu/config/`: Obtiene la configuración necesaria para iniciar pagos con PayU
- `POST /api/producto/payu/process-payment/`: Procesa pagos a través de la API de PayU
- `POST /api/producto/payu/notification/`: Recibe notificaciones de cambios en el estado de los pagos

## Tarjetas de Prueba

Para probar diferentes escenarios en el entorno de sandbox:

### Para transacciones aprobadas:
- Nombre: Incluir "APPROVED" en el nombre del titular
- CVV: 777 (para AMEX, usar 7777)
- Mes de expiración: Menor a 6 (ejemplo: 05/25)
- Tarjeta VISA: 4111111111111111

### Para transacciones rechazadas:
- Nombre: Incluir "REJECTED" en el nombre del titular
- CVV: 666 (para AMEX, usar 6666)
- Mes de expiración: Mayor a 6 (ejemplo: 07/25)
- Tarjeta MasterCard: 5500000000000004

## Integración Frontend

Se incluyen componentes de ejemplo para Angular:
- `payu-service.ts`: Servicio para interactuar con los endpoints de PayU
- `payu-checkout.component.ts`: Componente para mostrar el formulario de pago

Para más detalles, consulta el archivo `payu-implementation-guide.md`.

## Dependencias principales

- Django 4.2
- Django Rest Framework 3.15.1
- Requests 2.32.3 (para comunicación con la API de PayU)

## Despliegue

La aplicación está configurada para desplegarse en Render.com con la URL base: https://backmobile1.onrender.com/

## Recordatorios para producción

Al pasar a producción, será necesario:
1. Obtener credenciales de producción de PayU Latam
2. Cambiar el parámetro `test` a `false` en las solicitudes
3. Actualizar la URL de API al endpoint de producción
