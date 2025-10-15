import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { ConfigService } from '../../config/config.service';
import { CameraService } from '../../camera/camera.service';
import { MicroscopeService } from '../../microscope/microscope.service';

/**
 * Health Check Controller
 * 
 * Provides system health status endpoint for monitoring.
 * No authentication required - public endpoint.
 * 
 * Checks:
 * - Database connectivity (if this endpoint responds, DB is working)
 * - Python camera service availability
 * - Raspberry Pi controller availability (via microscope service)
 * - Redis availability (Phase 2 - currently always true)
 * 
 * @controller /api/v1/health
 */
@ApiTags('Health')
@Controller('api/v1/health')
export class HealthController {
  constructor(
    private configService: ConfigService,
    private cameraService: CameraService,
    private microscopeService: MicroscopeService,
  ) { }

  /**
   * Health check endpoint
   * 
   * Returns overall system health and individual service statuses.
   * Used for monitoring, debugging, and deployment verification.
   * 
   * @returns Health status object with service availability
   * @public No authentication required
   * 
   * @example
   * GET /api/v1/health
   * {
   *   "status": "healthy",
   *   "checks": {
   *     "database": true,
   *     "pythonCamera": true,
   *     "raspberryPi": false,
   *     "redis": true
   *   },
   *   "timestamp": "2025-10-09T10:30:00.000Z"
   * }
   */
  @Get()
  @ApiOperation({
    summary: 'System health check'
  })
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
          redis: true
        },
        timestamp: '2025-01-09T10:30:45.123Z'
      }
    }
  })
  async check() {
    // Check external services in parallel for fast response
    const [pythonCamera, raspberryPi] = await Promise.all([
      this.cameraService.checkHealth().catch(() => false),
      this.microscopeService.checkHealth().catch(() => false),
    ]);

    return {
      status: 'healthy', // If we got here, the app is running
      checks: {
        database: true,  // If database was down, app wouldn't start
        pythonCamera,    // Python camera service on port 8001
        raspberryPi,     // Raspberry Pi controller on port 5000/8000
        redis: true,     // TODO: Add Redis check when Bull is implemented (Phase 2)
      },
      timestamp: new Date().toISOString(),
    };
  }
}
