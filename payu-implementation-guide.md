# Guía de Implementación de PayU Latam en ISPC Food

Esta guía te ayudará a implementar PayU Latam como método de pago en tu aplicación ISPC Food.

## 1. Configuración del Backend

Ya hemos implementado las siguientes vistas en el backend:

- `PayUConfigView`: Proporciona la configuración necesaria para el frontend
- `PayUProcessPaymentView`: Procesa los pagos a través de la API de PayU
- `PayUNotificationView`: Recibe notificaciones de PayU sobre cambios en el estado de los pagos

## 2. Credenciales de Prueba de PayU

Las credenciales de prueba para Argentina que estamos utilizando son:

```
API Login: pRRXKOl8ikMmt9u
API Key: 4Vj8eK4rloUd272L48hsrarnUA
Merchant ID: 508029
Account ID: 512322
```

## 3. Tarjetas de Prueba

Según la documentación de PayU, puedes usar las siguientes configuraciones para probar diferentes escenarios:

- **Para transacciones aprobadas**:
  - Incluye `APPROVED` en el nombre del tarjetahabiente
  - Utiliza `777` como CVV (para AMEX, utiliza `7777`)
  - Mes de expiración menor a 6 (ejemplo: 05/25)

- **Para transacciones rechazadas**:
  - Incluye `REJECTED` en el nombre del tarjetahabiente
  - Utiliza `666` como CVV (para AMEX, utiliza `6666`)
  - Mes de expiración mayor a 6 (ejemplo: 07/25)

- **Números de tarjeta de prueba**:
  - VISA: 4111111111111111
  - MasterCard: 5500000000000004
  - AMEX: 370000000000002

## 4. Implementación en el Frontend

### 4.1 Agregar el Servicio PayU

1. Copia el archivo `payu-service.ts` en tu proyecto Angular
2. Agrégalo a los providers de tu módulo:

```typescript
import { PayUService } from './services/payu-service';

@NgModule({
  providers: [PayUService],
  // ...
})
export class AppModule { }
```

### 4.2 Agregar el Componente de Checkout

1. Copia el archivo `payu-checkout.component.ts` en tu proyecto Angular
2. Agrégalo a las declaraciones de tu módulo:

```typescript
import { PayUCheckoutComponent } from './components/payu-checkout.component';

@NgModule({
  declarations: [PayUCheckoutComponent],
  // ...
})
export class AppModule { }
```

### 4.3 Usar el Componente en tu Página de Checkout

En tu página de checkout, puedes incluir el componente de pago de PayU:

```html
<div class="payment-checkout">
  <h2>Finalizar compra</h2>
  
  <!-- Componente de pago de PayU -->
  <app-payu-checkout [amount]="totalAmount" [description]="orderDescription"></app-payu-checkout>
</div>
```

## 5. Flujo de Pago con PayU Latam

1. El usuario selecciona sus productos y procede al checkout
2. Selecciona PayU como método de pago
3. Completa el formulario de tarjeta de crédito
4. Al hacer clic en "Pagar", se envían los datos al backend
5. El backend procesa el pago con PayU y devuelve el resultado
6. Según el resultado, se muestra un mensaje de éxito o error

## 6. Consideraciones Importantes

### Seguridad

- **Nunca** almacenes datos de tarjetas de crédito en tu base de datos
- **Siempre** usa HTTPS para toda comunicación relacionada con pagos
- Mantén las credenciales de PayU seguras, idealmente en variables de entorno

### Despliegue a Producción

Para pasar a producción con PayU Latam, necesitarás:

1. Crear una cuenta real en PayU Latam
2. Obtener credenciales de producción
3. Actualizar las credenciales en tu backend
4. Cambiar el parámetro `test` a `false` en las solicitudes
5. Actualizar la URL de la API al endpoint de producción

## 7. Depuración y Solución de Problemas

### Logs

Hemos implementado logging extensivo en el backend para ayudarte a depurar:

```python
logging.info(f"PayU payment data received: {json.dumps(payment_data, indent=2)}")
```

### Errores Comunes

- **Firma inválida**: Revisa que estés generando correctamente la firma MD5
- **Datos de tarjeta incorrectos**: Verifica que estés usando los datos de prueba correctos
- **Error de comunicación**: Asegúrate de que las URLs de API sean correctas

## 8. Recursos Adicionales

- [Documentación oficial de PayU Latam](https://developers.payulatam.com/latam/es/docs.html)
- [Guía de pruebas de PayU](https://developers.payulatam.com/latam/es/docs/getting-started/test-your-solution.html)
- [API de PayU Latam](https://developers.payulatam.com/latam/es/docs/integrations/api-integration.html)

¡Buena suerte con la implementación de PayU Latam en ISPC Food!
