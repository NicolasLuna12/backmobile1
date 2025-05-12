# Tarjetas de Prueba de Mercado Pago

Este documento proporciona información sobre las tarjetas de prueba que puedes utilizar para simular diferentes escenarios de pago con la integración de Mercado Pago Checkout API.

## Tarjetas de Prueba por País

### Argentina

| Tipo de Tarjeta | Número | CVV | Fecha de Vencimiento |
|-----------------|--------|-----|----------------------|
| Mastercard      | 5031 7557 3453 0604 | 123 | 11/25 |
| Visa            | 4509 9535 6623 3704 | 123 | 11/25 |
| American Express| 3711 803032 57522   | 1234| 11/25 |

### Brasil

| Tipo de Tarjeta | Número | CVV | Fecha de Vencimiento |
|-----------------|--------|-----|----------------------|
| Mastercard      | 5031 4332 1540 6351 | 123 | 11/25 |
| Visa            | 4235 6477 2802 5682 | 123 | 11/25 |
| American Express| 3753 651535 56885   | 1234| 11/25 |

### Chile

| Tipo de Tarjeta | Número | CVV | Fecha de Vencimiento |
|-----------------|--------|-----|----------------------|
| Mastercard      | 5416 7526 0258 2580 | 123 | 11/25 |
| Visa            | 4168 8188 4444 7115 | 123 | 11/25 |
| American Express| 3757 781744 61804   | 1234| 11/25 |

### Colombia

| Tipo de Tarjeta | Número | CVV | Fecha de Vencimiento |
|-----------------|--------|-----|----------------------|
| Mastercard      | 5254 1336 7440 3564 | 123 | 11/25 |
| Visa            | 4013 5406 8274 6260 | 123 | 11/25 |
| American Express| 3743 781877 55283   | 1234| 11/25 |

### México

| Tipo de Tarjeta | Número | CVV | Fecha de Vencimiento |
|-----------------|--------|-----|----------------------|
| Mastercard      | 5474 9254 3267 0366 | 123 | 11/25 |
| Visa            | 4075 5957 1648 3764 | 123 | 11/25 |
| American Express| 3766 7520 5781 151  | 1234| 11/25 |

### Perú

| Tipo de Tarjeta | Número | CVV | Fecha de Vencimiento |
|-----------------|--------|-----|----------------------|
| Mastercard      | 5031 7557 3453 0604 | 123 | 11/25 |
| Visa            | 4009 1753 3280 6176 | 123 | 11/25 |
| American Express| 3711 803032 57522   | 1234| 11/25 |

### Uruguay

| Tipo de Tarjeta | Número | CVV | Fecha de Vencimiento |
|-----------------|--------|-----|----------------------|
| Mastercard      | 5031 7557 3453 0604 | 123 | 11/25 |
| Visa            | 4009 1753 3280 6176 | 123 | 11/25 |
| American Express| 3711 803032 57522   | 1234| 11/25 |

## Escenarios de Prueba

Puedes simular diferentes resultados en los pagos utilizando los siguientes datos:

### Titular de Tarjeta

Para simular diferentes escenarios de pago, utiliza los siguientes nombres:

| Nombre del Titular | Resultado del Pago |
|--------------------|-------------------|
| APRO               | Pago aprobado     |
| CONT               | Pago pendiente    |
| OTHE               | Rechazado por error general |
| CALL               | Rechazado con validación para autorizar |
| FUND               | Rechazado por monto insuficiente |
| SECU               | Rechazado por código de seguridad inválido |
| EXPI               | Rechazado por fecha de expiración |
| FORM               | Rechazado por error en formulario |

### Ejemplo de Uso

Para simular un pago aprobado:
- Número de tarjeta: 5031 7557 3453 0604 (Mastercard Argentina)
- CVV: 123
- Fecha de vencimiento: 11/25
- Titular: APRO

Para simular un pago rechazado por fondos insuficientes:
- Número de tarjeta: 5031 7557 3453 0604 (Mastercard Argentina)
- CVV: 123
- Fecha de vencimiento: 11/25
- Titular: FUND

## Documentos de Identidad para Pruebas

Dependiendo del país, Mercado Pago puede solicitar un documento de identidad. Puedes utilizar los siguientes valores para pruebas:

### Argentina
- Tipo: DNI
- Número: 12345678

### Brasil
- Tipo: CPF
- Número: 12345678909

### Chile
- Tipo: RUT
- Número: 12345678-9

### Colombia
- Tipo: CC
- Número: 1234567890

### México
- Tipo: RFC
- Número: ABCD123456ABC

### Perú
- Tipo: DNI
- Número: 12345678

### Uruguay
- Tipo: CI
- Número: 12345678

## Notas Importantes

1. Estas tarjetas solo funcionan en el entorno de pruebas (Sandbox) de Mercado Pago.
2. No se realizan cargos reales en estas tarjetas.
3. Para pruebas en producción, deberás utilizar tarjetas reales.
4. Asegúrate de configurar la cuenta de Mercado Pago correctamente para hacer pruebas.

## Referencias

- [Documentación oficial de tarjetas de prueba de Mercado Pago](https://www.mercadopago.com.ar/developers/es/docs/checkout-api/testing/cards)
