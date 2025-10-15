import { Injectable } from '@nestjs/common';
import { ConfigService as NestConfigService } from '@nestjs/config';

/**
 * Configuration Service
 * 
 * Centralized access to environment variables with type safety and default values.
 * All configuration is loaded from .env file and accessed through typed getters.
 * 
 * This service is marked as @Global in ConfigModule, so it's available everywhere
 * without importing the module.
 * 
 * @class ConfigService
 */
@Injectable()
export class ConfigService {
  constructor(private configService: NestConfigService) {}

  // ==================== Database Configuration ====================

  /**
   * PostgreSQL database host
   * @default 'localhost'
   */
  get databaseHost(): string {
    return this.configService.get<string>('DATABASE_HOST', 'localhost');
  }

  /**
   * PostgreSQL database port
   * @default 5432
   */
  get databasePort(): number {
    return this.configService.get<number>('DATABASE_PORT', 5432);
  }

  /**
   * PostgreSQL database username
   * @default 'postgres'
   */
  get databaseUser(): string {
    return this.configService.get<string>('DATABASE_USER', 'postgres');
  }

  /**
   * PostgreSQL database password
   * @default 'postgres'
   */
  get databasePassword(): string {
    return this.configService.get<string>('DATABASE_PASSWORD', 'postgres');
  }

  /**
   * PostgreSQL database name
   * @default 'microscope_db'
   */
  get databaseName(): string {
    return this.configService.get<string>('DATABASE_NAME', 'microscope_db');
  }

  // ==================== JWT Configuration ====================

  /**
   * JWT secret key for signing tokens
   * IMPORTANT: Change this in production to a strong random string
   * @default 'default-secret-change-me'
   */
  get jwtSecret(): string {
    return this.configService.get<string>('JWT_SECRET', 'default-secret-change-me');
  }

  /**
   * JWT token expiration time
   * @default '7d' (7 days)
   */
  get jwtExpiresIn(): string {
    return this.configService.get<string>('JWT_EXPIRES_IN', '7d');
  }

  // ==================== External Services ====================

  /**
   * Python camera service base URL
   * @default 'http://localhost:8001'
   */
  get pythonCameraUrl(): string {
    return this.configService.get<string>('PYTHON_CAMERA_URL', 'http://localhost:8001');
  }

  /**
   * Raspberry Pi motor controller base URL
   * @default 'http://raspberrypi.local:5000'
   */
  get raspberryPiUrl(): string {
    return this.configService.get<string>('RASPBERRY_PI_URL', 'http://raspberrypi.local:8000');
  }

  /**
   * HTTP request timeout for external services (milliseconds)
   * @default 30000 (30 seconds)
   */
  get serviceTimeout(): number {
    return this.configService.get<number>('SERVICE_TIMEOUT', 30000);
  }

  // ==================== Redis Configuration ====================

  /**
   * Redis server host (for Bull queue in Phase 2)
   * @default 'localhost'
   */
  get redisHost(): string {
    return this.configService.get<string>('REDIS_HOST', 'localhost');
  }

  /**
   * Redis server port (for Bull queue in Phase 2)
   * @default 6379
   */
  get redisPort(): number {
    return this.configService.get<number>('REDIS_PORT', 6379);
  }

  // ==================== Server Configuration ====================

  /**
   * NestJS server port
   * @default 3000
   */
  get port(): number {
    return this.configService.get<number>('PORT', 3000);
  }

  /**
   * Node environment (development, production, test)
   * @default 'development'
   */
  get nodeEnv(): string {
    return this.configService.get<string>('NODE_ENV', 'development');
  }

  /**
   * Check if running in development mode
   * @returns true if NODE_ENV === 'development'
   */
  get isDevelopment(): boolean {
    return this.nodeEnv === 'development';
  }

  /**
   * Check if running in production mode
   * @returns true if NODE_ENV === 'production'
   */
  get isProduction(): boolean {
    return this.nodeEnv === 'production';
  }

  // ==================== CORS Configuration ====================

  /**
   * Allowed CORS origins (comma-separated in .env)
   * @default ['http://localhost:5173']
   */
  get allowedOrigins(): string[] {
    const origins = this.configService.get<string>('ALLOWED_ORIGINS', 'http://localhost:5173');
    return origins.split(',').map(origin => origin.trim());
  }

  // ==================== File Storage ====================

  /**
   * Path to store captured images
   * @default './images'
   */
  get imagesPath(): string {
    return this.configService.get<string>('IMAGES_PATH', './images');
  }

  /**
   * Path to store image thumbnails
   * @default './thumbnails'
   */
  get thumbnailsPath(): string {
    return this.configService.get<string>('THUMBNAILS_PATH', './thumbnails');
  }

  // ==================== Safety Limits (CRITICAL) ====================

  /**
   * Maximum X axis position in motor steps
   * SAFETY LIMIT: Prevents stage from moving beyond physical bounds
   * @default 10000
   */
  get maxXPosition(): number {
    return this.configService.get<number>('MAX_X_POSITION', 10000);
  }

  /**
   * Maximum Y axis position in motor steps
   * SAFETY LIMIT: Prevents stage from moving beyond physical bounds
   * @default 10000
   */
  get maxYPosition(): number {
    return this.configService.get<number>('MAX_Y_POSITION', 10000);
  }

  /**
   * Maximum Z axis position in motor steps
   * SAFETY LIMIT: Prevents stage from moving beyond physical bounds
   * @default 5000
   */
  get maxZPosition(): number {
    return this.configService.get<number>('MAX_Z_POSITION', 5000);
  }

  /**
   * Minimum X axis position in motor steps
   * SAFETY LIMIT: Prevents stage from moving beyond physical bounds
   * @default 0
   */
  get minXPosition(): number {
    return this.configService.get<number>('MIN_X_POSITION', 0);
  }

  /**
   * Minimum Y axis position in motor steps
   * SAFETY LIMIT: Prevents stage from moving beyond physical bounds
   * @default 0
   */
  get minYPosition(): number {
    return this.configService.get<number>('MIN_Y_POSITION', 0);
  }

  /**
   * Minimum Z axis position in motor steps
   * SAFETY LIMIT: Prevents stage from moving beyond physical bounds
   * @default 0
   */
  get minZPosition(): number {
    return this.configService.get<number>('MIN_Z_POSITION', 0);
  }

  // ==================== Sensor Polling (Phase 2) ====================

  /**
   * Sensor polling interval when stage is idle (milliseconds)
   * @default 5000 (5 seconds)
   */
  get sensorPollInterval(): number {
    return this.configService.get<number>('SENSOR_POLL_INTERVAL', 5000);
  }

  /**
   * Sensor polling interval when stage is moving (milliseconds)
   * @default 1000 (1 second)
   */
  get sensorPollIntervalMoving(): number {
    return this.configService.get<number>('SENSOR_POLL_INTERVAL_MOVING', 1000);
  }

  // ==================== Temperature Thresholds ====================

  /**
   * Temperature warning threshold (Celsius)
   * @default 40
   */
  get tempWarningThreshold(): number {
    return this.configService.get<number>('TEMP_WARNING_THRESHOLD', 40);
  }

  /**
   * Temperature critical threshold (Celsius)
   * @default 45
   */
  get tempCriticalThreshold(): number {
    return this.configService.get<number>('TEMP_CRITICAL_THRESHOLD', 45);
  }
}
