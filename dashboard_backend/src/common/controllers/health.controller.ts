import { Controller, Get } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { ConfigService } from '../../config/config.service';
import { CameraService } from '../../camera/camera.service';
import { firstValueFrom, catchError, of } from 'rxjs';
import { DataSource } from 'typeorm';

/**
 * Health Check Controller
 *
 * Provides system health status endpoint for monitoring.
 * No authentication required - public endpoint.
 *
 * Checks:
 * - Database connectivity (if this endpoint responds, DB is working)
 * - Python camera service availability
 * - Raspberry Pi controller availability (direct HTTP check)
 *
 * @controller /api/v1/health
 */
@ApiTags('Health')
@Controller('api/v1/health')
export class HealthController {
  constructor(
    private httpService: HttpService,
    private configService: ConfigService,
    private cameraService: CameraService,
    private dataSource: DataSource,
  ) {}

  /**
   * Check database health with a small query instead of assuming that
   * this controller responding means TypeORM is fully usable.
   */
  private async checkDatabaseHealth(): Promise<boolean> {
    try {
      await this.dataSource.query('SELECT 1');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Check Raspberry Pi health directly
   */
  private async checkPiHealth(): Promise<boolean> {
    try {
      const response = await firstValueFrom(
        this.httpService
          .get(`${this.configService.raspberryPiUrl}/health`, { timeout: 5000 })
          .pipe(catchError(() => of({ data: { healthy: false } }))),
      );
      return response.data?.healthy === true;
    } catch {
      return false;
    }
  }

  /**
   * Health check endpoint
   *
   * Returns overall system health and individual service statuses.
   * Used for monitoring, debugging, and deployment verification.
   *
   * @returns Health status object with service availability
   * @public No authentication required
   */
  @Get()
  @ApiOperation({ summary: 'System health check' })
  @ApiResponse({
    status: 200,
    description: 'Health check completed',
    schema: {
      example: {
        status: 'healthy',
        checks: {
          database: true,
          pythonCamera: true,
          raspberryPi: true,
        },
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  async check() {
    const [database, pythonCamera, raspberryPi] = await Promise.all([
      this.checkDatabaseHealth(),
      this.cameraService.checkHealth().catch(() => false),
      this.checkPiHealth(),
    ]);
    const healthy = database && pythonCamera && raspberryPi;

    return {
      status: healthy ? 'healthy' : 'degraded',
      checks: {
        database,
        pythonCamera,
        raspberryPi,
      },
      timestamp: new Date().toISOString(),
    };
  }
}
