import { Controller, Post, Body, UseGuards, Request } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { CameraService } from './camera.service';
import { CaptureDto } from './dto/capture.dto';
import { CaptureResponseDto } from './dto/capture-response.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

/**
 * Camera Controller (Simplified)
 *
 * Handles camera operations that require database persistence.
 * Settings, streaming, and recording control are handled directly by Python service.
 * This controller only handles capture and video stop (which save metadata to DB).
 *
 * @controller /api/v1/camera
 * @protected All endpoints require JWT authentication
 */
@ApiTags('Camera')
@Controller('api/v1/camera')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth('JWT-auth')
export class CameraController {
  constructor(private cameraService: CameraService) {}

  /**
   * Capture an image and save to database
   *
   * @route POST /api/v1/camera/capture
   */
  @Post('capture')
  @ApiOperation({
    summary: 'Capture an image',
    description:
      'Capture image and save metadata to database. For camera settings, call Python service directly.',
  })
  @ApiBody({ type: CaptureDto })
  @ApiResponse({
    status: 200,
    description: 'Image captured and saved to database',
    type: CaptureResponseDto,
  })
  @ApiResponse({ status: 503, description: 'Camera service unavailable' })
  async capture(
    @Request() req,
    @Body() captureDto: CaptureDto,
  ): Promise<CaptureResponseDto> {
    const userId = req.user.id;
    return this.cameraService.capture(
      captureDto.exposure,
      captureDto.gain,
      captureDto.gamma,
      userId,
    );
  }

  /**
   * Stop video recording and save to database
   *
   * @route POST /api/v1/camera/video/stop
   */
  @Post('video/stop')
  @ApiOperation({
    summary: 'Stop video recording',
    description:
      'Stop recording and save video metadata to database. Start/cancel/status are handled by Python service directly.',
  })
  @ApiResponse({
    status: 200,
    description: 'Video recording stopped and saved to database',
  })
  @ApiResponse({ status: 503, description: 'Camera service unavailable' })
  async stopVideoRecording(@Request() req) {
    const userId = req.user.id;
    return this.cameraService.stopVideoRecording(userId);
  }
}
