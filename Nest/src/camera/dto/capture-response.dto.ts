import { ApiProperty } from '@nestjs/swagger';

/**
 * Capture Response DTO
 *
 * Response structure returned from camera capture endpoint.
 * Contains all metadata about the captured image.
 *
 * @class CaptureResponseDto
 */
export class CaptureResponseDto {
  @ApiProperty({
    description: 'Whether the capture was successful',
    example: true,
  })
  success: boolean;

  @ApiProperty({
    description: 'Database ID of the saved image record (null if not saved)',
    example: 123,
    required: false,
    nullable: true,
  })
  imageId?: number | null;

  @ApiProperty({
    description:
      'Whether the image metadata was successfully saved to database',
    example: true,
  })
  databaseSaved: boolean;

  @ApiProperty({
    description:
      'Warning message if database save failed or other issues occurred',
    example: null,
    required: false,
    nullable: true,
  })
  warning?: string | null;

  @ApiProperty({
    description: 'Filename of the captured image',
    example: 'capture_20250116_103045_123.jpg',
  })
  filename: string;

  @ApiProperty({
    description: 'Full file path where image is stored',
    example: '/path/to/captures/capture_20250116_103045_123.jpg',
  })
  filepath: string;

  @ApiProperty({
    description: 'ISO timestamp when image was captured',
    example: '2025-01-16T10:30:45.123Z',
  })
  capturedAt: string;

  @ApiProperty({
    description: 'Exposure time used (milliseconds)',
    example: 100,
  })
  exposureTime: number;

  @ApiProperty({
    description: 'Gain/sensitivity value used',
    example: 1.5,
  })
  gain: number;

  @ApiProperty({
    description: 'File size in bytes',
    example: 2456789,
  })
  fileSize: number;

  @ApiProperty({
    description: 'Image width in pixels',
    example: 1920,
  })
  width: number;

  @ApiProperty({
    description: 'Image height in pixels',
    example: 1080,
  })
  height: number;

  @ApiProperty({
    description: 'Additional metadata about the capture',
    example: {
      format: 'JPG',
      quality: 95,
      cameraConnected: true,
      simulatedMode: false,
    },
  })
  metadata: Record<string, any>;
}
