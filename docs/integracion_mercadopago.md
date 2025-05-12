# Integración de Mercado Pago Checkout API - Guía de Implementación Frontend

## Descripción

Este documento proporciona instrucciones para integrar la pasarela de pago Checkout API de Mercado Pago en el frontend de tu aplicación.

## Requisitos previos

1. Tener una cuenta de Mercado Pago Developers
2. Obtener credenciales de prueba (Access Token y Public Key)
3. Configurar las variables de entorno en el backend:
   - `MERCADO_PAGO_ACCESS_TOKEN`
   - `MERCADO_PAGO_PUBLIC_KEY`
   - `MERCADO_PAGO_SUCCESS_URL`
   - `MERCADO_PAGO_FAILURE_URL`
   - `MERCADO_PAGO_PENDING_URL`
   - `MERCADO_PAGO_NOTIFICATION_URL`

## Implementación en Angular

### 1. Instalar el SDK de Mercado Pago

```bash
npm install @mercadopago/sdk-js
```

### 2. Crear servicio para integración con Mercado Pago

Crea un archivo `mercado-pago.service.ts`:

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class MercadoPagoService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  /**
   * Crea una preferencia de pago para el pedido especificado
   * @param pedidoId ID del pedido a pagar
   * @param redirectUrl URL base para redirecciones (opcional)
   */
  createPaymentPreference(pedidoId: number, redirectUrl?: string): Observable<any> {
    const payload: any = { pedido_id: pedidoId };
    
    if (redirectUrl) {
      payload.redirect_url = redirectUrl;
    }
    
    return this.http.post(`${this.apiUrl}/cart/checkout/mercadopago/`, payload);
  }

  /**
   * Consulta el estado de un pago
   * @param pagoId ID del pago a consultar
   */
  getPaymentStatus(pagoId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/cart/payment/status/${pagoId}/`);
  }
}
```

### 3. Crear componente de Checkout

Crea un componente para manejar el checkout con Mercado Pago:

```typescript
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MercadoPagoService } from '../../services/mercado-pago.service';
import { loadMercadoPago } from "@mercadopago/sdk-js";

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.scss']
})
export class CheckoutComponent implements OnInit {
  pedidoId: number;
  isLoading = false;
  error: string | null = null;
  preferenceId: string | null = null;
  publicKey: string | null = null;
  pagoId: number | null = null;

  constructor(
    private route: ActivatedRoute,
    private mercadoPagoService: MercadoPagoService
  ) {
    this.pedidoId = 0;
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.pedidoId = +params['id']; // Convertir a número
      if (this.pedidoId) {
        this.createPaymentPreference();
      }
    });
  }

  createPaymentPreference() {
    this.isLoading = true;
    this.error = null;

    this.mercadoPagoService.createPaymentPreference(this.pedidoId)
      .subscribe({
        next: (response) => {
          this.preferenceId = response.preference_id;
          this.publicKey = response.public_key;
          this.pagoId = response.pago_id;
          this.initMercadoPago();
        },
        error: (error) => {
          this.isLoading = false;
          this.error = 'Error al crear la preferencia de pago. Por favor, inténtelo de nuevo más tarde.';
          console.error('Error creating payment preference:', error);
        }
      });
  }

  async initMercadoPago() {
    try {
      if (!this.preferenceId || !this.publicKey) {
        throw new Error('Faltan datos para inicializar el checkout');
      }

      const mp = await loadMercadoPago();
      const bricksBuilder = mp.bricks();
      
      const renderComponent = async () => {
        if (mp) {
          await bricksBuilder.create("wallet", "mercadopago-container", {
            initialization: {
              preferenceId: this.preferenceId
            },
            callbacks: {
              onReady: () => {
                console.log('Checkout listo');
                this.isLoading = false;
              },
              onSubmit: () => {
                console.log('Pago iniciado');
              },
              onError: (error) => {
                console.error('Error en checkout:', error);
                this.error = 'Error en el proceso de pago. Por favor, inténtelo de nuevo.';
                this.isLoading = false;
              }
            }
          });
        }
      };

      renderComponent();
    } catch (error) {
      console.error('Error loading MercadoPago:', error);
      this.error = 'Error al cargar el checkout de MercadoPago. Por favor, inténtelo de nuevo.';
      this.isLoading = false;
    }
  }

  checkPaymentStatus() {
    if (!this.pagoId) return;
    
    this.mercadoPagoService.getPaymentStatus(this.pagoId)
      .subscribe({
        next: (response) => {
          console.log('Estado del pago:', response);
          // Actualizar UI según el estado del pago
        },
        error: (error) => {
          console.error('Error al consultar estado del pago:', error);
        }
      });
  }
}
```

### 4. Crear plantilla HTML para el componente

```html
<div class="checkout-container">
  <h2>Finalizar Compra</h2>
  
  <div *ngIf="isLoading" class="loading">
    <p>Cargando opciones de pago...</p>
    <!-- Loader spinner aquí -->
  </div>
  
  <div *ngIf="error" class="error-message">
    <p>{{ error }}</p>
    <button (click)="createPaymentPreference()">Reintentar</button>
  </div>
  
  <!-- Contenedor para el botón de pago de Mercado Pago -->
  <div id="mercadopago-container" *ngIf="!isLoading && !error"></div>
  
  <div class="payment-info" *ngIf="pagoId">
    <button (click)="checkPaymentStatus()">Verificar estado del pago</button>
  </div>
</div>
```

### 5. Añadir estilos CSS para el componente

```scss
.checkout-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  
  h2 {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .loading {
    text-align: center;
    padding: 20px;
  }
  
  .error-message {
    background-color: #ffeeee;
    border: 1px solid #ffcccc;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 4px;
    
    button {
      margin-top: 10px;
      padding: 8px 16px;
      background-color: #0066cc;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      
      &:hover {
        background-color: #0055aa;
      }
    }
  }
  
  .payment-info {
    margin-top: 20px;
    text-align: center;
    
    button {
      padding: 10px 20px;
      background-color: #28a745;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      
      &:hover {
        background-color: #218838;
      }
    }
  }
}
```

### 6. Agregar rutas para el checkout

Actualiza tu archivo de rutas:

```typescript
const routes: Routes = [
  // ... otras rutas
  { path: 'checkout/:id', component: CheckoutComponent },
  { path: 'payment/success', component: PaymentSuccessComponent },
  { path: 'payment/failure', component: PaymentFailureComponent },
  { path: 'payment/pending', component: PaymentPendingComponent },
];
```

### 7. Crear componentes para manejar las redirecciones

Crea componentes para manejar los diferentes estados del pago (success, failure, pending) que mostrarán mensajes apropiados y permitirán al usuario continuar con su experiencia.

## Implementación en React

### 1. Instalar el SDK de Mercado Pago

```bash
npm install @mercadopago/sdk-react
```

### 2. Crear servicio para integración con la API

```javascript
// src/services/mercadoPagoService.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

export const createPaymentPreference = async (pedidoId, redirectUrl = null) => {
  const payload = { pedido_id: pedidoId };
  
  if (redirectUrl) {
    payload.redirect_url = redirectUrl;
  }
  
  try {
    const response = await axios.post(`${API_URL}/cart/checkout/mercadopago/`, payload, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error al crear preferencia de pago:', error);
    throw error;
  }
};

export const getPaymentStatus = async (pagoId) => {
  try {
    const response = await axios.get(`${API_URL}/cart/payment/status/${pagoId}/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error al consultar estado del pago:', error);
    throw error;
  }
};
```

### 3. Crear componente de Checkout

```jsx
// src/components/Checkout/Checkout.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { initMercadoPago, Wallet } from '@mercadopago/sdk-react';
import { createPaymentPreference, getPaymentStatus } from '../../services/mercadoPagoService';
import './Checkout.css';

const Checkout = () => {
  const { id: pedidoId } = useParams();
  const navigate = useNavigate();
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [preferenceId, setPreferenceId] = useState(null);
  const [publicKey, setPublicKey] = useState(null);
  const [pagoId, setPagoId] = useState(null);
  
  useEffect(() => {
    if (pedidoId) {
      initializeCheckout();
    }
  }, [pedidoId]);
  
  const initializeCheckout = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await createPaymentPreference(pedidoId);
      setPreferenceId(response.preference_id);
      setPublicKey(response.public_key);
      setPagoId(response.pago_id);
      
      // Inicializar Mercado Pago
      initMercadoPago(response.public_key);
      
      setIsLoading(false);
    } catch (error) {
      setError('Error al crear la preferencia de pago. Por favor, inténtelo de nuevo más tarde.');
      setIsLoading(false);
    }
  };
  
  const checkPaymentStatus = async () => {
    if (!pagoId) return;
    
    try {
      const response = await getPaymentStatus(pagoId);
      console.log('Estado del pago:', response);
      // Actualizar UI según el estado del pago
    } catch (error) {
      console.error('Error al consultar estado del pago:', error);
    }
  };
  
  return (
    <div className="checkout-container">
      <h2>Finalizar Compra</h2>
      
      {isLoading && (
        <div className="loading">
          <p>Cargando opciones de pago...</p>
          {/* Loader spinner aquí */}
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={initializeCheckout}>Reintentar</button>
        </div>
      )}
      
      {!isLoading && !error && preferenceId && (
        <div className="payment-button">
          <Wallet 
            initialization={{ preferenceId }}
            onReady={() => console.log('Checkout listo')} 
            onError={(error) => console.error('Error en checkout:', error)}
          />
        </div>
      )}
      
      {pagoId && (
        <div className="payment-info">
          <button onClick={checkPaymentStatus}>Verificar estado del pago</button>
        </div>
      )}
    </div>
  );
};

export default Checkout;
```

### 4. Crear estilos CSS para el componente

```css
/* src/components/Checkout/Checkout.css */
.checkout-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.checkout-container h2 {
  margin-bottom: 20px;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 20px;
}

.error-message {
  background-color: #ffeeee;
  border: 1px solid #ffcccc;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.error-message button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error-message button:hover {
  background-color: #0055aa;
}

.payment-button {
  margin: 20px 0;
}

.payment-info {
  margin-top: 20px;
  text-align: center;
}

.payment-info button {
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.payment-info button:hover {
  background-color: #218838;
}
```

### 5. Configurar rutas para el checkout

```jsx
// src/App.js (o donde configures tus rutas)
import { Routes, Route } from 'react-router-dom';
import Checkout from './components/Checkout/Checkout';
import PaymentSuccess from './components/Payment/PaymentSuccess';
import PaymentFailure from './components/Payment/PaymentFailure';
import PaymentPending from './components/Payment/PaymentPending';

function App() {
  return (
    <Routes>
      {/* ... otras rutas */}
      <Route path="/checkout/:id" element={<Checkout />} />
      <Route path="/payment/success" element={<PaymentSuccess />} />
      <Route path="/payment/failure" element={<PaymentFailure />} />
      <Route path="/payment/pending" element={<PaymentPending />} />
    </Routes>
  );
}

export default App;
```

## Pruebas y Consideraciones

1. **Usuarios de prueba**: Utiliza las tarjetas de prueba proporcionadas por Mercado Pago para simular diferentes escenarios de pago.

2. **Webhooks**: Asegúrate de que la URL de notificación (webhook) sea accesible desde Internet para recibir actualizaciones de estado de los pagos.

3. **Seguridad**: Nunca expongas tu Access Token en el frontend. Todos los llamados que requieran este token deben hacerse desde el backend.

4. **Producción**: Para pasar a producción, necesitarás obtener credenciales de producción en la cuenta de Mercado Pago Developers.

## Documentación Adicional

- [Documentación oficial de Mercado Pago](https://www.mercadopago.com.ar/developers/es/docs)
- [SDKs de Mercado Pago](https://www.mercadopago.com.ar/developers/es/docs/sdks-library/client-side)
- [Checkout API](https://www.mercadopago.com.ar/developers/es/docs/checkout-api/landing)
