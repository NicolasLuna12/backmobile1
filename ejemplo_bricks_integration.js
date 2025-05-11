// Ejemplo de integración de MercadoPago Bricks en el frontend
// Coloca este código en tu aplicación React o JavaScript

// 1. Primero, obtén la configuración desde el backend
async function getBricksConfig() {
  try {
    const response = await fetch('https://backmobile1.onrender.com/api/producto/mercadopago/bricks-config/');
    return await response.json();
  } catch (error) {
    console.error('Error al obtener la configuración de Bricks:', error);
    return null;
  }
}

// 2. Inicializa el Brick de Pago con la configuración correcta
async function initBricks() {
  const config = await getBricksConfig();
  if (!config) return;
  
  const settings = {
    initialization: {
      amount: 100, // El monto del pago
      payer: {
        email: 'test@test.com',
        // Importante! Siempre incluye el entity_type para solucionar el error
        entity_type: 'individual' // Puede ser 'individual' o 'association'
      }
    },
    callbacks: {
      onReady: () => {
        // El Brick está listo para usarse
        console.log('Brick listo');
      },
      onSubmit: ({ formData }) => {
        // El usuario ha enviado el formulario
        return new Promise((resolve, reject) => {
          // Envía los datos al backend
          fetch(config.api_base_url + config.process_payment_url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              token: formData.token,
              transaction_amount: formData.transaction_amount,
              installments: formData.installments,
              payment_method_id: formData.payment_method_id,
              email: formData.payer.email,
              entity_type: formData.payer.entity_type || 'individual', // Garantiza que siempre haya un valor
              identification: formData.payer.identification
            }),
          })
            .then(response => response.json())
            .then(result => {
              // Si el pago fue exitoso
              if (result.status === 'approved') {
                resolve();
                // Redireccionar a página de éxito
                window.location.href = config.success_url;
              } else {
                // Si hubo un error
                reject(result);
                // Puedes manejar los diferentes estados (rejected, pending, etc)
                if (result.status === 'rejected') {
                  window.location.href = config.failure_url;
                } else if (result.status === 'pending') {
                  window.location.href = config.pending_url;
                }
              }
            })
            .catch(error => {
              console.error('Error:', error);
              reject(error);
            });
        });
      },
      onError: (error) => {
        // Hubo un error en el Brick
        console.error('Error en el Brick:', error);
      }
    },
    locale: 'es-AR',
    customization: {
      visual: {
        hideFormTitle: true,
        hidePaymentButton: false
      }
    },
  };

  const bricksBuilder = await mp.bricks();
  const renderPaymentBrick = async (bricksBuilder) => {
    await bricksBuilder.create(
      'payment',
      'payment-brick-container', // El ID del elemento DOM donde se renderizará el Brick
      settings
    );
  };

  renderPaymentBrick(bricksBuilder);
}

// 3. Inicializa MercadoPago y carga el Brick
window.onload = async function() {
  try {
    const config = await getBricksConfig();
    if (!config) return;

    // Inicializa el SDK de MercadoPago
    const mp = new MercadoPago(config.publicKey, {
      locale: 'es-AR'
    });
    
    // Espera a que el DOM esté listo y inicializa el Brick
    document.addEventListener('DOMContentLoaded', () => {
      initBricks(mp);
    });
  } catch (error) {
    console.error('Error al inicializar MercadoPago:', error);
  }
};

// 4. Ejemplo de HTML necesario:
/*
<!DOCTYPE html>
<html>
<head>
  <title>Pago con MercadoPago Bricks</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- SDK MercadoPago.js -->
  <script src="https://sdk.mercadopago.com/js/v2"></script>
  <!-- Tu script personalizado -->
  <script src="ejemplo_bricks_integration.js"></script>
</head>
<body>
  <h1>Pago con MercadoPago</h1>
  
  <!-- Contenedor donde se renderizará el Brick de pago -->
  <div id="payment-brick-container"></div>
</body>
</html>
*/
