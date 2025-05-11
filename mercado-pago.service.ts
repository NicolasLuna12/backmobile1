// mercado-pago.service.ts
// Este servicio gestiona todas las operaciones relacionadas con MercadoPago

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

declare var MercadoPago: any;

@Injectable({
  providedIn: 'root'
})
export class MercadoPagoService {
  private apiBase = 'https://backmobile1.onrender.com/api/producto';
  private config: any = null;
  private mercadopago: any = null;
  
  constructor(private http: HttpClient) {}
  
  /**
   * Inicializa el servicio de MercadoPago obteniendo su configuración
   */
  async initialize(): Promise<any> {
    try {
      // Obtener la configuración del backend
      const config = await this.getConfig().toPromise();
      this.config = config;
      
      // Inicializar el SDK de MercadoPago
      this.mercadopago = new MercadoPago(config.publicKey, {
        locale: 'es-AR'
      });
      
      return this.mercadopago;
    } catch (error) {
      console.error('Error al inicializar MercadoPago', error);
      throw error;
    }
  }
  
  /**
   * Obtiene la configuración de MercadoPago desde el backend
   */
  getConfig(): Observable<any> {
    return this.http.get(`${this.apiBase}/mercadopago/bricks-config/`).pipe(
      tap(config => console.log('Configuración obtenida:', config)),
      catchError(this.handleError<any>('getConfig', null))
    );
  }
  
  /**
   * Crea una preferencia de pago para el checkout
   */
  createPreference(items: any[]): Observable<any> {
    return this.http.post(`${this.apiBase}/mercadopago/preference/`, { items }).pipe(
      tap(preference => console.log('Preferencia creada:', preference)),
      catchError(this.handleError<any>('createPreference', null))
    );
  }
  
  /**
   * Procesa un pago utilizando la API de proceso de pago
   */
  processPayment(paymentData: any): Observable<any> {
    return this.http.post(`${this.apiBase}/mercadopago/process-payment/`, paymentData).pipe(
      tap(response => console.log('Pago procesado:', response)),
      catchError(this.handleError<any>('processPayment', null))
    );
  }
  
  /**
   * Renderiza el brick de pago en el contenedor especificado
   */
  async renderPaymentBrick(containerId: string, options: any): Promise<any> {
    if (!this.mercadopago) {
      throw new Error('MercadoPago no está inicializado');
    }
    
    try {
      const bricksBuilder = await this.mercadopago.bricks();
      return bricksBuilder.create('payment', containerId, options);
    } catch (error) {
      console.error('Error al renderizar el brick de pago', error);
      throw error;
    }
  }
  
  /**
   * Obtiene la instancia del SDK de MercadoPago
   */
  getInstance() {
    return this.mercadopago;
  }
  
  /**
   * Obtiene la configuración actual
   */
  getCurrentConfig() {
    return this.config;
  }
  
  /**
   * Maneja errores en las peticiones HTTP
   */
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed:`, error);
      return of(result as T);
    };
  }
}
