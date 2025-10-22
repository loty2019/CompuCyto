import {
  Controller,
  Post,
  Get,
  Put,
  Body,
  UseGuards,
  Request,
} from '@nestjs/common';
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
 * Camera Controller
 *
 * Manages camera operations including image capture, settings management,
 * and preview streaming. All requests are proxied to the Python camera
 * service running on port 8001.
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
   * Capture an image
   *
   * Triggers camera to capture a single image with specified settings.
   * Returns image data and metadata.
   *
   * @route POST /api/v1/camera/capture
   * @protected Requires JWT authentication
   */
  @Post('capture')
  @ApiOperation({
    summary: 'Capture an image',
    description:
      'Trigger camera to capture a single image. Optionally specify exposure time (ms) and gain. Image is saved to disk and metadata stored in database.',
  })
  @ApiBody({ type: CaptureDto })
  @ApiResponse({
    status: 200,
    description: 'Image captured successfully',
    type: CaptureResponseDto,
  })
  @ApiResponse({
    status: 500,
    description: 'Camera service error',
    schema: {
      example: {
        statusCode: 500,
        message: 'Camera not responding',
        error: 'Internal Server Error',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
    schema: {
      example: {
        statusCode: 503,
        message: 'Python camera service is not available',
        error: 'Service Unavailable',
      },
    },
  })
  async capture(
    @Request() req,
    @Body() captureDto: CaptureDto,
  ): Promise<CaptureResponseDto> {
    const userId = req.user.id; // Extract user ID from JWT token
    return this.cameraService.capture(
      captureDto.exposure,
      captureDto.gain,
      captureDto.gamma,
      userId,
    );
  }

  /**
   * Get camera settings
   *
   * Retrieves current camera configuration and capabilities.
   *
   * @route GET /api/v1/camera/settings
   * @protected Requires JWT authentication
   */
  @Get('settings')
  @ApiOperation({
    summary: 'Get camera settings',
    description:
      'Retrieve current camera configuration including exposure, gain, resolution, and available modes.',
  })
  @ApiResponse({
    status: 200,
    description: 'Camera settings retrieved',
    schema: {
      example: {
        exposure: 100,
        gain: 1.5,
        resolution: '1920x1080',
        frameRate: 30,
        whiteBalance: 'auto',
        focusMode: 'continuous',
        availableResolutions: ['640x480', '1280x720', '1920x1080', '3840x2160'],
        exposureRange: { min: 1, max: 10000 },
        gainRange: { min: 1.0, max: 16.0 },
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
  })
  async getSettings() {
    return this.cameraService.getSettings();
  }

  /**
   * Update camera settings
   *
   * Modifies camera configuration parameters.
   *
   * @route PUT /api/v1/camera/settings
   * @protected Requires JWT authentication
   */
  @Put('settings')
  @ApiOperation({
    summary: 'Update camera settings',
    description:
      'Modify camera configuration. Only provided fields will be updated. Settings are validated against camera capabilities.',
  })
  @ApiBody({
    schema: {
      example: {
        exposure: 200,
        gain: 2.0,
        resolution: '1920x1080',
        whiteBalance: 'manual',
        focusMode: 'manual',
      },
    },
  })
  @ApiResponse({
    status: 200,
    description: 'Settings updated successfully',
    schema: {
      example: {
        success: true,
        updatedSettings: {
          exposure: 200,
          gain: 2.0,
          resolution: '1920x1080',
          whiteBalance: 'manual',
          focusMode: 'manual',
        },
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: 'Invalid settings',
    schema: {
      example: {
        statusCode: 400,
        message: 'Exposure value 15000 exceeds maximum allowed value of 10000',
        error: 'Bad Request',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
  })
  async updateSettings(
    @Body() settings: { exposure?: number; gain?: number; gamma?: number },
  ) {
    return this.cameraService.updateSettings(settings);
  }

  /**
   * Get camera preview stream URL
   *
   * Returns URL for live video preview stream (MJPEG or WebRTC).
   *
   * @route GET /api/v1/camera/preview
   * @protected Requires JWT authentication
   */
  @Get('preview')
  @ApiOperation({
    summary: 'Get preview stream URL',
    description:
      'Returns URL for live camera preview stream. Stream format depends on Python service configuration (MJPEG, WebRTC, or HLS).',
  })
  @ApiResponse({
    status: 200,
    description: 'Preview URL retrieved',
    schema: {
      example: {
        streamUrl: 'http://localhost:8001/camera/stream',
        format: 'MJPEG',
        resolution: '1280x720',
        frameRate: 30,
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
  })
  async getPreview() {
    return this.cameraService.getPreviewUrl();
  }

  /**
   * Start video recording
   *
   * @route POST /api/v1/camera/video/start
   * @protected Requires JWT authentication
   */
  @Post('video/start')
  @ApiOperation({
    summary: 'Start video recording',
    description:
      'Start recording video from camera. Optionally specify duration, frame rate, and decimation.',
  })
  @ApiBody({
    schema: {
      example: {
        duration: 30,
        playbackFrameRate: 25,
        decimation: 1,
      },
    },
    required: false,
  })
  @ApiResponse({
    status: 200,
    description: 'Video recording started',
    schema: {
      example: {
        success: true,
        message: 'Video recording started',
        filename: 'recording_20251022_120811_231.avi',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
  })
  async startVideoRecording(
    @Body()
    body?: {
      duration?: number;
      playbackFrameRate?: number;
      decimation?: number;
    },
  ) {
    return this.cameraService.startVideoRecording(
      body?.duration,
      body?.playbackFrameRate,
      body?.decimation,
    );
  }

  /**
   * Stop video recording
   *
   * @route POST /api/v1/camera/video/stop
   * @protected Requires JWT authentication
   */
  @Post('video/stop')
  @ApiOperation({
    summary: 'Stop video recording',
    description:
      'Stop recording video and finalize the file. Video metadata will be saved to database.',
  })
  @ApiResponse({
    status: 200,
    description: 'Video recording stopped and saved',
    schema: {
      example: {
        success: true,
        message: 'Video recording completed',
        filename: 'recording_20251022_120811_231.avi',
        videoId: 1,
        databaseSaved: true,
        duration: 30.5,
        fileSize: 15456789,
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
  })
  async stopVideoRecording(@Request() req) {
    const userId = req.user.id;
    return this.cameraService.stopVideoRecording(userId);
  }

  /**
   * Cancel video recording
   *
   * @route POST /api/v1/camera/video/cancel
   * @protected Requires JWT authentication
   */
  @Post('video/cancel')
  @ApiOperation({
    summary: 'Cancel video recording',
    description: 'Cancel ongoing video recording without saving.',
  })
  @ApiResponse({
    status: 200,
    description: 'Video recording canceled',
    schema: {
      example: {
        success: true,
        message: 'Video recording canceled',
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
  })
  async cancelVideoRecording() {
    return this.cameraService.cancelVideoRecording();
  }

  /**
   * Get video recording status
   *
   * @route GET /api/v1/camera/video/status
   * @protected Requires JWT authentication
   */
  @Get('video/status')
  @ApiOperation({
    summary: 'Get video recording status',
    description: 'Check if video is currently being recorded.',
  })
  @ApiResponse({
    status: 200,
    description: 'Recording status retrieved',
    schema: {
      example: {
        is_recording: true,
        elapsed: 15.3,
        metadata: {},
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Python camera service unavailable',
  })
  async getVideoRecordingStatus() {
    return this.cameraService.getVideoRecordingStatus();
  }
}
