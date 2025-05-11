// EJEMPLO DE INTEGRACIÓN PARA ANGULAR (checkout.component.ts)
// Este código es para utilizar en tu componente de Angular

import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';

declare var MercadoPago: any;

@Component({
  selector: 'app-checkout',
  template: `
    <div class="checkout-container">
      <h2>Finalizar compra</h2>
      <div *ngIf="loading">Cargando...</div>
      <div *ngIf="error" class="error">{{ error }}</div>
      
      <!-- Contenedor para el Brick de MercadoPago -->
      <div id="payment-brick-container"></div>
      
      <!-- Botón alternativo por si prefieres el flujo de checkout redirect -->
      <button *ngIf="preferenceId" (click)="redirectToCheckout()">
        Pagar con MercadoPago (Redirect)
      </button>
    </div>
  `,
  styles: [`
    .checkout-container {
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
    }
    .error {
      color: red;
      margin: 10px 0;
    }
  `]
})
export class CheckoutComponent implements OnInit {
  @ViewChild('paymentBrick') paymentBrick: ElementRef;
  
  // Configuración de MercadoPago
  public mpConfig: any = null;
  public mp: any = null;
  public preferenceId: string = '';
  public initPoint: string = '';
  public loading: boolean = true;
  public error: string = '';
  
  // Datos del carrito/compra (ejemplo)
  public cartItems = [
    {
      id: '1',
      title: 'Producto ejemplo',
      description: 'Descripción del producto',
      quantity: 1,
      currency_id: 'ARS',
      unit_price: 100.00
    }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.getMercadoPagoConfig()
      .then(() => this.createPreference())
      .then(() => this.initMercadoPago())
      .catch(error => {
        console.error('Error en la inicialización:', error);
        this.error = 'Error al inicializar el pago. Por favor, intenta nuevamente.';
        this.loading = false;
      });
  }

  // 1. Obtener configuración desde el backend
  async getMercadoPagoConfig() {
    try {
      this.mpConfig = await this.http.get('https://backmobile1.onrender.com/api/producto/mercadopago/bricks-config/').toPromise();
      console.log('Configuración de MercadoPago:', this.mpConfig);
    } catch (error) {
      console.error('Error al obtener la configuración:', error);
      throw error;
    }
  }

  // 2. Crear preferencia para obtener un ID
  async createPreference() {
    try {
      const response: any = await this.http.post('https://backmobile1.onrender.com/api/producto/mercadopago/preference/', {
        items: this.cartItems
      }).toPromise();
      
      console.log('Respuesta backend MercadoPago:', response);
      this.preferenceId = response.preference_id;
      this.initPoint = response.init_point;
    } catch (error) {
      console.error('Error al crear preferencia:', error);
      throw error;
    }
  }

  // 3. Inicializar MercadoPago y renderizar Brick
  async initMercadoPago() {
    try {
      // Cargar SDK
      this.mp = new MercadoPago(this.mpConfig.publicKey, {
        locale: 'es-AR'
      });
      
      console.log('SDK de Mercado Pago cargado correctamente');
      
      // Inicializar Brick
      this.renderPaymentBrick();
    } catch (error) {
      console.error('Error al inicializar MercadoPago:', error);
      throw error;
    } finally {
      this.loading = false;
    }
  }

  // 4. Renderizar el Brick de Pago
  async renderPaymentBrick() {
    try {
      const bricksBuilder = await this.mp.bricks();
      
      // Configuración del Brick
      const settings = {
        initialization: {
          amount: this.getTotalAmount(),
          preferenceId: this.preferenceId,
          payer: {
            email: 'test@test.com',
            entity_type: 'individual'
          }
        },
        callbacks: {
          onReady: () => {
            console.log('Brick listo');
            this.loading = false;
          },
          onSubmit: (formData) => {
            console.log('onSubmit called with formData:', formData);
            return this.processPayment(formData);
          },
          onError: (error) => {
            console.error('Error en el Brick:', error);
            this.error = 'Error en el procesamiento del pago.';
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
      
      console.log('Creando Payment Brick con la configuración proporcionada');
      
      bricksBuilder.create(
        'payment',
        'payment-brick-container',
        settings
      );
    } catch (error) {
      console.error('Error al renderizar el Brick:', error);
      this.error = 'Error al cargar el formulario de pago.';
    }
  }

  // 5. Procesar el pago
  async processPayment(formData) {
    try {
      console.log('Procesando pago con datos:', formData);
      
      // Enviar datos del formulario al endpoint de process-payment
      const response: any = await this.http.post(
        this.mpConfig.api_base_url + this.mpConfig.process_payment_url,
        formData
      ).toPromise();
      
      console.log('Respuesta de procesamiento de pago:', response);
      
      // Manejar respuesta
      if (response.status === 'approved') {
        console.log('Pago aprobado, redirigiendo a página de éxito');
        window.location.href = this.mpConfig.success_url;
        return { status: 'approved' };
      } else {
        console.warn('Pago no aprobado:', response.status_detail);
        
        // Redireccionar según el estado
        if (response.status === 'rejected') {
          window.location.href = this.mpConfig.failure_url;
        } else if (response.status === 'pending') {
          window.location.href = this.mpConfig.pending_url;
        }
        
        return { status: response.status };
      }
    } catch (error) {
      console.error('Error procesando el pago:', error);
      this.error = 'Error al procesar el pago. Por favor, intenta nuevamente.';
      return { status: 'error' };
    }
  }

  // 6. Método alternativo: Redireccionar al Checkout de MercadoPago
  redirectToCheckout() {
    if (this.initPoint) {
      window.location.href = this.initPoint;
    } else {
      this.error = 'No se pudo obtener la URL de pago.';
    }
  }

  // Método auxiliar para calcular el total del carrito
  getTotalAmount() {
    return this.cartItems.reduce((total, item) => {
      return total + (item.unit_price * item.quantity);
    }, 0);
  }
}
