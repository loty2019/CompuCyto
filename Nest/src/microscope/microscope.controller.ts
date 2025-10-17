import { Controller, Get, Post, Body, UseGuards } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { MicroscopeService } from './microscope.service';
import { SetLightDto } from './dto/set-light.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

/**
 * Microscope Hardware Controller
 *
 * Controls general microscope hardware components:
 * - Light (LED/halogen illumination)
 * - Focus (future)
 * - Filter wheel (future)
 * - Shutters (future)
 *
 * All hardware commands are proxied to Raspberry Pi or Python service.
 *
 * @controller /api/v1/microscope
 * @protected All endpoints require JWT authentication
 */
@ApiTags('Microscope')
@Controller('api/v1/microscope')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth('JWT-auth')
export class MicroscopeController {
  constructor(private microscopeService: MicroscopeService) {}

  /**
   * Get current light status
   *
   * Queries hardware for current light state and brightness.
   * Called when UI loads to display current state.
   *
   * @route GET /api/v1/microscope/light/status
   * @protected Requires JWT authentication
   */
  @Get('light/status')
  @ApiOperation({
    summary: 'Get current light status',
    description:
      'Query hardware for current light state. Use this when UI loads to show initial state.',
  })
  @ApiResponse({
    status: 200,
    description: 'Light status retrieved successfully',
    schema: {
      example: {
        isOn: true,
        brightness: 75,
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Hardware controller unavailable',
  })
  async getLightStatus() {
    return this.microscopeService.getLightStatus();
  }

  /**
   * Toggle light on/off
   *
   * Switches light between on and off states.
   * Brightness remains at previous setting.
   *
   * @route POST /api/v1/microscope/light/toggle
   * @protected Requires JWT authentication
   */
  @Post('light/toggle')
  @ApiOperation({
    summary: 'Toggle light on/off',
    description:
      'Switch light between on and off states. Brightness setting is preserved.',
  })
  @ApiResponse({
    status: 200,
    description: 'Light toggled successfully',
    schema: {
      example: {
        success: true,
        isOn: false,
        brightness: 75,
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Hardware controller unavailable',
  })
  async toggleLight() {
    return this.microscopeService.toggleLight();
  }

  /**
   * Set light to specific state
   *
   * Set light on/off and optionally adjust brightness.
   *
   * @route POST /api/v1/microscope/light/set
   * @protected Requires JWT authentication
   */
  @Post('light/set')
  @ApiOperation({
    summary: 'Set light to specific state',
    description:
      'Set light on/off with optional brightness control. Brightness range: 0-100.',
  })
  @ApiBody({ type: SetLightDto })
  @ApiResponse({
    status: 200,
    description: 'Light state updated successfully',
    schema: {
      example: {
        success: true,
        isOn: true,
        brightness: 50,
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: 'Invalid brightness value',
    schema: {
      example: {
        statusCode: 400,
        message: 'Brightness must be between 0 and 100',
        error: 'Bad Request',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Hardware controller unavailable',
  })
  async setLight(@Body() setLightDto: SetLightDto) {
    return this.microscopeService.setLight(
      setLightDto.isOn,
      setLightDto.brightness,
    );
  }
}
