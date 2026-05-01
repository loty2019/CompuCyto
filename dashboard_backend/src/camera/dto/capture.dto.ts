import { IsNumber, IsOptional, Min } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * Capture DTO (Data Transfer Object)
 *
 * Validates camera capture request parameters.
 * Both fields are optional - if omitted, camera service will use current settings.
 *
 * @class CaptureDto
 */
export class CaptureDto {
  /**
   * Exposure time in milliseconds
   * Optional - if omitted, uses current camera setting
   * @example 100
   */
  @ApiProperty({
    description: 'Camera exposure time in milliseconds',
    example: 100,
    required: false,
    minimum: 0,
  })
  @IsOptional()
  @IsNumber()
  @Min(0)
  exposure?: number;

  /**
   * Camera gain/sensitivity multiplier
   * Optional - if omitted, uses current camera setting
   * @example 1.5
   */
  @ApiProperty({
    description: 'Camera gain/sensitivity multiplier',
    example: 1.5,
    required: false,
    minimum: 0,
  })
  @IsOptional()
  @IsNumber()
  @Min(0)
  gain?: number;

  /**
   * Camera gamma correction value
   * Optional - if omitted, uses current camera setting
   * @example 1.0
   */
  @ApiProperty({
    description:
      'Camera gamma correction value for brightness/contrast adjustment',
    example: 1.0,
    required: false,
    minimum: 0,
  })
  @IsOptional()
  @IsNumber()
  @Min(0)
  gamma?: number;
}
