# Food ISPC - Backend

Este repositorio contiene el backend para la aplicación Food ISPC, un sistema de pedidos de comida en línea. El backend está desarrollado con Django y Django REST Framework.

## Características

- Gestión de usuarios y autenticación con JWT
- Catálogo de productos con categorías
- Sistema de carrito de compras
- Procesamiento de pedidos
- Integración con Mercado Pago para pagos en línea

## Requisitos

- Python 3.8+
- Django 4.2
- MySQL/PostgreSQL
- Otras dependencias en `requirements.txt`

## Instalación

1. Clonar el repositorio:
   ```
   git clone <url-del-repositorio>
   cd backmobile1
   ```

2. Crear y activar un entorno virtual:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   - Copiar `Food_ISPC/env.template` a `.env`
   - Completar las variables con los valores correspondientes

5. Aplicar migraciones:
   ```
   python manage.py migrate
   ```

6. Crear superusuario (opcional):
   ```
   python manage.py createsuperuser
   ```

7. Iniciar el servidor:
   ```
   python manage.py runserver
   ```

## Integración con Mercado Pago

El proyecto incluye integración con la Checkout API de Mercado Pago para procesar pagos en línea.

### Configuración

1. Obten tus credenciales de Mercado Pago desde el [Portal de Desarrolladores](https://developers.mercadopago.com)

2. Configura las siguientes variables en tu archivo `.env`:
   ```
   MERCADO_PAGO_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
   MERCADO_PAGO_PUBLIC_KEY=YOUR_PUBLIC_KEY
   MERCADO_PAGO_SUCCESS_URL=http://localhost:4200/payment/success
   MERCADO_PAGO_FAILURE_URL=http://localhost:4200/payment/failure
   MERCADO_PAGO_PENDING_URL=http://localhost:4200/payment/pending
   MERCADO_PAGO_NOTIFICATION_URL=http://localhost:8000/api/payment/webhook/
   ```

3. Para entornos de desarrollo, puedes usar [ngrok](https://ngrok.com/) para exponer temporalmente tu servidor local y recibir webhooks:
   ```
   ngrok http 8000
   ```
   
   Actualiza la `MERCADO_PAGO_NOTIFICATION_URL` con la URL proporcionada por ngrok.

### Endpoints de la API de Pagos

- **POST /api/cart/checkout/mercadopago/**: Crea una preferencia de pago para un pedido
  - Body: `{ "pedido_id": 123 }`
  - Respuesta: Información necesaria para iniciar el checkout

- **POST /api/cart/webhook/mercadopago/**: Webhook para recibir notificaciones de Mercado Pago
  - Esta ruta es llamada automáticamente por Mercado Pago

- **GET /api/cart/payment/status/{pago_id}/**: Consulta el estado de un pago
  - Respuesta: Información detallada del pago

### Documentación

Para más detalles sobre la integración con Mercado Pago, consulta los siguientes archivos:

- [Guía de Integración Frontend](docs/integracion_mercadopago.md)
- [Tarjetas de Prueba](docs/tarjetas_prueba_mercadopago.md)

## Estructura del Proyecto

- `Food_ISPC/`: Configuración principal del proyecto Django
- `appUSERS/`: Aplicación para la gestión de usuarios
- `appFOOD/`: Aplicación para la gestión de productos y categorías
- `appCART/`: Aplicación para la gestión del carrito y pedidos
- `docs/`: Documentación adicional

## API Endpoints

### Usuarios
- `POST /api/users/register/`: Registro de usuario
- `POST /api/users/login/`: Inicio de sesión (devuelve token JWT)
- `GET /api/users/profile/`: Obtener perfil de usuario actual

### Productos
- `GET /api/products/`: Listar todos los productos
- `GET /api/products/{id}/`: Detalles de un producto específico
- `GET /api/categories/`: Listar todas las categorías

### Carrito
- `GET /api/cart/ver/`: Ver productos en el carrito
- `POST /api/cart/agregar/{producto_id}/`: Agregar producto al carrito
- `DELETE /api/cart/eliminar/{carrito_id}/`: Eliminar producto del carrito
- `POST /api/cart/confirmar/`: Confirmar pedido
- `GET /api/cart/detalle_pedido/{pedido_id}/`: Ver detalles de un pedido

## Licencia

[Especificar licencia]

## Colaboradores

[Listar colaboradores]
