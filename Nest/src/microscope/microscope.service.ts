import { Injectable, ServiceUnavailableException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '../config/config.service';
import { firstValueFrom, catchError } from 'rxjs';

/**
 * Microscope Service
 * 
 * Handles communication with microscope hardware controllers.
 * Proxies requests to Raspberry Pi or Python camera service.
 * 
 * Hardware Control Flow:
 * 1. Frontend calls NestJS API
 * 2. This service proxies to hardware controller (Pi/Python)
 * 3. Hardware controller sends GPIO/Serial commands
 * 4. Physical hardware responds
 * 5. State returned to frontend
 * 
 * @service MicroscopeService
 */
@Injectable()
export class MicroscopeService {
  constructor(
    private httpService: HttpService,
    private configService: ConfigService,
  ) {}

  /**
   * Get current light status from hardware
   * 
   * Queries the hardware controller for current light state.
   * 
   * @returns Current light status (on/off, brightness)
   * @throws ServiceUnavailableException if hardware is not responding
   */
  async getLightStatus() {
    try {
      // Query Raspberry Pi for current light state
      const response = await firstValueFrom(
        this.httpService.get(
          `${this.configService.raspberryPiUrl}/led/state`,
          {
            timeout: this.configService.serviceTimeout,
          }
        )
      );
      
      return {
        isOn: response.data.is_on, // Pi returns 'is_on' (snake_case)
        brightness: response.data.brightness || 100,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      throw new ServiceUnavailableException(
        'Microscope hardware controller is not available'
      );
    }
  }

  /**
   * Toggle light on/off
   * 
   * Switches light between on and off states.
   * Brightness setting is preserved.
   * 
   * @returns New light status
   * @throws ServiceUnavailableException if hardware is not responding
   */
  async toggleLight() {
    try {
      const response = await firstValueFrom(
        this.httpService.post(
          `${this.configService.raspberryPiUrl}/led/toggle`,
          {},
          {
            timeout: this.configService.serviceTimeout,
          }
        )
      );
      
      return {
        success: true,
        isOn: response.data.is_on,
        brightness: response.data.brightness || 100,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      throw new ServiceUnavailableException(
        'Microscope hardware controller is not available'
      );
    }
  }

  /**
   * Set light to specific state with brightness
   * 
   * Sets light on/off and optionally adjusts brightness.
   * If brightness is omitted, previous setting is maintained.
   * 
   * @param isOn - Turn light on (true) or off (false)
   * @param brightness - Optional brightness level (0-100)
   * @returns New light status
   * @throws ServiceUnavailableException if hardware is not responding
   */
  async setLight(isOn: boolean, brightness?: number) {
    try {
      const payload: any = { isOn };
      if (brightness !== undefined) {
        payload.brightness = brightness;
      }

      const response = await firstValueFrom(
        this.httpService.post(
          `${this.configService.raspberryPiUrl}/light/set`,
          payload,
          {
            timeout: this.configService.serviceTimeout,
          }
        )
      );
      
      return {
        success: true,
        isOn: response.data.isOn,
        brightness: response.data.brightness || 100,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      throw new ServiceUnavailableException(
        'Microscope hardware controller is not available'
      );
    }
  }

  /**
   * Check Raspberry Pi controller health
   * 
   * Pings the Raspberry Pi health endpoint to verify availability.
   * Used by the health check controller.
   * 
   * @returns true if Raspberry Pi is reachable and healthy, false otherwise
   */
  async checkHealth(): Promise<boolean> {
    try {
      // Short timeout for health checks (5 seconds)
      const response = await firstValueFrom(
        this.httpService.get(`${this.configService.raspberryPiUrl}/health`, { timeout: 5000 }).pipe(
          catchError(() => {
            throw new Error('Raspberry Pi controller unavailable');
          }),
        ),
      );
      
      // Verify the response body indicates healthy status
      return response.data?.healthy === true;
    } catch {
      return false;
    }
  }
}
