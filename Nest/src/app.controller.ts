import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';
import {
  ApiOperation,
  ApiResponse,
  ApiExcludeController,
} from '@nestjs/swagger';

/**
 * App Controller
 *
 * Root controller for basic application info.
 * This is excluded from Swagger documentation as it's not part of the main API.
 */
@ApiExcludeController()
@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  /**
   * Root endpoint
   * Returns basic application information
   *
   * @route GET /
   * @public No authentication required
   */
  @Get()
  @ApiOperation({
    summary: 'Get application info',
    description:
      'Returns basic welcome message. Not part of the main API - use /api/v1 endpoints instead.',
  })
  @ApiResponse({
    status: 200,
    description: 'Application info',
    schema: {
      example:
        'CompuCyto Microscope Control API - Visit /api-docs for documentation',
    },
  })
  getHello(): string {
    return this.appService.getHello();
  }
}
