import { IsBoolean, IsNumber, IsOptional, Min, Max } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * Set Light DTO (Data Transfer Object)
 * 
 * Validates request to set microscope light state.
 * 
 * @class SetLightDto
 */
export class SetLightDto {
  /**
   * Turn light on or off
   * @example true
   */
  @ApiProperty({
    description: 'Turn light on (true) or off (false)',
    example: true,
  })
  @IsBoolean()
  isOn: boolean;

  /**
   * Light brightness level (0-100)
   * Optional - if omitted, previous brightness is maintained
   * @example 75
   */
  @ApiProperty({
    description: 'Light brightness percentage (0-100)',
    example: 75,
    required: false,
    minimum: 0,
    maximum: 100,
  })
  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100)
  brightness?: number;
}
