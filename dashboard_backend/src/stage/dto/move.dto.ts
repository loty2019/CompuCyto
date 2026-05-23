import { IsNumber, IsBoolean, IsOptional, Min } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * Move DTO (Data Transfer Object)
 *
 * Validates stage movement request parameters.
 * X, Y, Z are optional - omitted axes will not move.
 *
 * IMPORTANT: Positions are validated against safety limits before sending to hardware.
 * See PositionValidator for safety limit enforcement.
 *
 * @class MoveDto
 */
export class MoveDto {
  /**
   * X axis position in motor steps
   * Optional - if omitted, X axis stays at current position
   * @example 1000
   */
  @ApiProperty({
    description:
      'X axis position in motor steps (validated against safety limits)',
    example: 8800,
    required: false,
  })
  @IsOptional()
  @IsNumber()
  x?: number;

  /**
   * Y axis position in motor steps
   * Optional - if omitted, Y axis stays at current position
   * @example 500
   */
  @ApiProperty({
    description:
      'Y axis position in motor steps (validated against safety limits)',
    example: 11900,
    required: false,
  })
  @IsOptional()
  @IsNumber()
  y?: number;

  /**
   * Z axis position in motor steps
   * Optional - if omitted, Z axis stays at current position
   * @example 100
   */
  @ApiProperty({
    description:
      'Z axis position in motor steps (validated against safety limits)',
    example: 1000,
    required: false,
  })
  @IsOptional()
  @IsNumber()
  z?: number;

  /**
   * Movement mode
   * - true: Relative movement (add to current position)
   * - false: Absolute movement (move to exact position)
   * @example false
   */
  @ApiProperty({
    description:
      'Movement mode: true for relative (incremental), false for absolute',
    example: false,
    default: false,
  })
  @IsBoolean()
  relative: boolean;
}
