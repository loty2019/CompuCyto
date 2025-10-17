import {
  Injectable,
  ServiceUnavailableException,
  Logger,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '../config/config.service';
import { PositionValidator, Position } from './validators/position-validator';
import { catchError, firstValueFrom } from 'rxjs';
import { AxiosError } from 'axios';

/**
 * Stage Service
 *
 * HTTP client proxy to the Raspberry Pi motor controller running on port 5000.
 * Handles motor movement with critical safety validation before forwarding commands.
 *
 * IMPORTANT: This service validates all position requests against safety limits
 * before sending commands to the hardware controller. This prevents damage to
 * the microscope stage and attached equipment.
 *
 * @class StageService
 */
@Injectable()
export class StageService {
  private readonly logger = new Logger(StageService.name);
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(
    private httpService: HttpService,
    private configService: ConfigService,
    private positionValidator: PositionValidator,
  ) {
    // Load configuration from environment variables
    this.baseUrl = this.configService.raspberryPiUrl;
    this.timeout = this.configService.serviceTimeout;
  }

  /**
   * Move stage to position
   *
   * Validates position against safety limits, then forwards command to Raspberry Pi.
   * Supports both absolute and relative movements.
   *
   * SAFETY: Position is validated BEFORE sending to hardware. Invalid positions
   * will throw BadRequestException and command will NOT be sent.
   *
   * @param x - Optional X position (omit to keep current)
   * @param y - Optional Y position (omit to keep current)
   * @param z - Optional Z position (omit to keep current)
   * @param relative - If true, treat x/y/z as offsets from current position
   * @returns Move status and target position
   * @throws BadRequestException if position is out of safety limits
   * @throws ServiceUnavailableException if Raspberry Pi is not reachable
   */
  async move(
    x?: number,
    y?: number,
    z?: number,
    relative: boolean = false,
  ): Promise<any> {
    try {
      // STEP 1: Get current position from Raspberry Pi
      const currentPosition = await this.getPosition();

      // STEP 2: Calculate target position (handles absolute vs relative)
      const targetPosition = this.positionValidator.calculateTargetPosition(
        currentPosition,
        { x, y, z },
        relative,
      );

      // STEP 3: Validate against safety limits (throws BadRequestException if invalid)
      this.positionValidator.validatePosition(targetPosition);

      // STEP 4: Send validated move command to Raspberry Pi
      // Always send as absolute position to avoid compounding errors
      const { data } = await firstValueFrom(
        this.httpService
          .post(
            `${this.baseUrl}/move`,
            {
              x: targetPosition.x,
              y: targetPosition.y,
              z: targetPosition.z,
              relative: false, // Always absolute after validation
            },
            { timeout: this.timeout },
          )
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Stage move failed: ${error.message}`);
              throw new ServiceUnavailableException(
                'Stage controller unavailable',
              );
            }),
          ),
      );

      return {
        status: 'moving',
        targetPosition,
        ...data,
      };
    } catch (error) {
      if (error instanceof ServiceUnavailableException) {
        throw error;
      }
      this.logger.error(`Stage move error: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get current stage position
   *
   * Queries Raspberry Pi for current X, Y, Z position in steps.
   *
   * @returns Current position object with x, y, z coordinates
   * @throws ServiceUnavailableException if Raspberry Pi is not reachable
   */
  async getPosition(): Promise<Position> {
    try {
      // GET request to Raspberry Pi for current motor positions
      const { data } = await firstValueFrom(
        this.httpService
          .get(`${this.baseUrl}/position`, { timeout: this.timeout })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(
                `Failed to get stage position: ${error.message}`,
              );
              throw new ServiceUnavailableException(
                'Stage controller unavailable',
              );
            }),
          ),
      );
      return data;
    } catch (error) {
      this.logger.error(`Get position error: ${error.message}`);
      throw new ServiceUnavailableException('Stage controller unavailable');
    }
  }

  /**
   * Home all axes
   *
   * Sends home command to Raspberry Pi to move all axes (X, Y, Z) to origin.
   * This is typically done at startup or after manual intervention.
   *
   * @returns Home operation status
   * @throws ServiceUnavailableException if Raspberry Pi is not reachable
   */
  async home(): Promise<any> {
    try {
      // POST request to initiate homing sequence
      const { data } = await firstValueFrom(
        this.httpService
          .post(`${this.baseUrl}/home`, {}, { timeout: this.timeout })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Stage home failed: ${error.message}`);
              throw new ServiceUnavailableException(
                'Stage controller unavailable',
              );
            }),
          ),
      );
      return data;
    } catch (error) {
      this.logger.error(`Stage home error: ${error.message}`);
      throw new ServiceUnavailableException('Stage controller unavailable');
    }
  }

  /**
   * Emergency stop
   *
   * Immediately halts all motor movement. Critical safety function.
   * Should be called when manual intervention is needed or error is detected.
   *
   * @returns Stop operation status
   * @throws ServiceUnavailableException if Raspberry Pi is not reachable
   */
  async stop(): Promise<any> {
    try {
      // POST request to emergency stop all motors
      const { data } = await firstValueFrom(
        this.httpService
          .post(`${this.baseUrl}/stop`, {}, { timeout: this.timeout })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Stage stop failed: ${error.message}`);
              throw new ServiceUnavailableException(
                'Stage controller unavailable',
              );
            }),
          ),
      );
      return data;
    } catch (error) {
      this.logger.error(`Stage stop error: ${error.message}`);
      throw new ServiceUnavailableException('Stage controller unavailable');
    }
  }

  /**
   * Check Raspberry Pi controller health
   *
   * Pings the Raspberry Pi health endpoint to verify availability.
   * Used by the health check controller.
   *
   * @returns true if service is reachable, false otherwise
   */
  async checkHealth(): Promise<boolean> {
    try {
      // Short timeout for health checks (5 seconds)
      await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/health`, { timeout: 5000 }).pipe(
          catchError(() => {
            throw new Error('Stage controller unavailable');
          }),
        ),
      );
      return true;
    } catch {
      return false;
    }
  }
}
