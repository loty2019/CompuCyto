import { Controller, Post, Get, Body, UseGuards } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { StageService } from './stage.service';
import { MoveDto } from './dto/move.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

/**
 * Stage Controller
 *
 * Controls microscope stage movement (X, Y, Z axes).
 * All movements are validated against safety limits before being sent to hardware.
 * Requests are proxied to Raspberry Pi controller on port 5000.
 *
 * ⚠️ SAFETY CRITICAL: All position commands are validated before hardware execution
 *
 * @controller /api/v1/stage
 * @protected All endpoints require JWT authentication
 */
@ApiTags('Stage')
@Controller('api/v1/stage')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth('JWT-auth')
export class StageController {
  constructor(private stageService: StageService) {}

  /**
   * Move stage to position
   *
   * Moves stage to absolute or relative position on X, Y, Z axes.
   * Position is validated against safety limits before hardware command.
   *
   * ⚠️ CRITICAL: Positions are validated to prevent hardware damage
   *
   * @route POST /api/v1/stage/move
   * @protected Requires JWT authentication
   */
  @Post('move')
  @ApiOperation({
    summary: 'Move microscope stage',
    description: `Move stage to specified position. Supports absolute and relative movements.
    
    **IMPORTANT**: All positions are validated against configured safety limits:
    - X axis: 0 to MAX_X_POSITION (default: 100mm)
    - Y axis: 0 to MAX_Y_POSITION (default: 100mm)
    - Z axis: 0 to MAX_Z_POSITION (default: 25mm)
    
    Set relative=true for incremental movement from current position.
    Omit axes that should not move (null or undefined).`,
  })
  @ApiBody({ type: MoveDto })
  @ApiResponse({
    status: 200,
    description: 'Stage moved successfully',
    schema: {
      example: {
        success: true,
        position: {
          x: 50.0,
          y: 25.5,
          z: 10.2,
        },
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: 'Position validation failed',
    schema: {
      example: {
        statusCode: 400,
        message:
          'Position validation failed: X position 150.0 exceeds maximum allowed value of 100.0',
        error: 'Bad Request',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Raspberry Pi controller unavailable',
    schema: {
      example: {
        statusCode: 503,
        message: 'Raspberry Pi controller is not available',
        error: 'Service Unavailable',
      },
    },
  })
  async move(@Body() moveDto: MoveDto) {
    return this.stageService.move(
      moveDto.x,
      moveDto.y,
      moveDto.z,
      moveDto.relative,
    );
  }

  /**
   * Get current stage position
   *
   * Retrieves current X, Y, Z coordinates from hardware.
   *
   * @route GET /api/v1/stage/position
   * @protected Requires JWT authentication
   */
  @Get('position')
  @ApiOperation({
    summary: 'Get current stage position',
    description:
      'Query Raspberry Pi for current stage position on all axes. Returns coordinates in millimeters.',
  })
  @ApiResponse({
    status: 200,
    description: 'Position retrieved successfully',
    schema: {
      example: {
        x: 50.0,
        y: 25.5,
        z: 10.2,
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Raspberry Pi controller unavailable',
  })
  async getPosition() {
    return this.stageService.getPosition();
  }

  /**
   * Home all stage axes
   *
   * Moves stage to home position (0, 0, 0).
   * This is the calibration reference point.
   *
   * @route POST /api/v1/stage/home
   * @protected Requires JWT authentication
   */
  @Post('home')
  @ApiOperation({
    summary: 'Home stage to origin',
    description: `Move stage to home position (0, 0, 0).
    
    This triggers hardware homing sequence:
    1. Stage moves to limit switches
    2. Position counters reset to zero
    3. Stage returns to safe home position
    
    **WARNING**: Stage will move rapidly during homing. Ensure workspace is clear.`,
  })
  @ApiResponse({
    status: 200,
    description: 'Stage homed successfully',
    schema: {
      example: {
        success: true,
        position: {
          x: 0,
          y: 0,
          z: 0,
        },
        message: 'Stage homed successfully',
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Raspberry Pi controller unavailable',
  })
  async home() {
    return this.stageService.home();
  }

  /**
   * Emergency stop
   *
   * Immediately halts all stage movement.
   * Use in emergency situations to prevent damage.
   *
   * ⚠️ EMERGENCY: Stops all motion immediately
   *
   * @route POST /api/v1/stage/stop
   * @protected Requires JWT authentication
   */
  @Post('stop')
  @ApiOperation({
    summary: 'Emergency stop',
    description: `**EMERGENCY STOP**: Immediately halt all stage movement.
    
    Use this endpoint when:
    - Stage is moving incorrectly
    - Collision is imminent
    - Emergency situation requires immediate halt
    
    After stop, stage position may need recalibration via homing.`,
  })
  @ApiResponse({
    status: 200,
    description: 'Stage stopped successfully',
    schema: {
      example: {
        success: true,
        message: 'Emergency stop executed',
        timestamp: '2025-01-09T10:30:45.123Z',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Raspberry Pi controller unavailable',
  })
  async stop() {
    return this.stageService.stop();
  }
}
