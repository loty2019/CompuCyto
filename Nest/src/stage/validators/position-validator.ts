import { Injectable, BadRequestException } from '@nestjs/common';
import { ConfigService } from '../../config/config.service';

/**
 * Position interface
 * Represents X, Y, Z coordinates in motor steps
 */
export interface Position {
  x: number;
  y: number;
  z: number;
}

/**
 * Position Validator
 * 
 * CRITICAL SAFETY COMPONENT: Validates all stage positions against configurable
 * safety limits before allowing movement commands to be sent to hardware.
 * 
 * This prevents damage to:
 * - Microscope stage motors
 * - Attached camera equipment
 * - Sample slides
 * - Physical structure
 * 
 * Safety limits are configured via environment variables (MAX_X_POSITION, etc.)
 * 
 * @class PositionValidator
 */
@Injectable()
export class PositionValidator {
  constructor(private configService: ConfigService) {}

  /**
   * Validate position against safety limits
   * 
   * Checks that X, Y, Z coordinates are within configured min/max bounds.
   * Throws BadRequestException if any axis is out of range.
   * 
   * IMPORTANT: This is the last line of defense before sending commands
   * to hardware. All position changes MUST pass through this validation.
   * 
   * @param position - Target position to validate
   * @throws BadRequestException if position is out of safety limits
   */
  validatePosition(position: Position): void {
    const { x, y, z } = position;

    // Validate X axis is within bounds
    if (x < this.configService.minXPosition || x > this.configService.maxXPosition) {
      throw new BadRequestException(
        `X position ${x} is out of range [${this.configService.minXPosition}, ${this.configService.maxXPosition}]`,
      );
    }

    // Validate Y axis is within bounds
    if (y < this.configService.minYPosition || y > this.configService.maxYPosition) {
      throw new BadRequestException(
        `Y position ${y} is out of range [${this.configService.minYPosition}, ${this.configService.maxYPosition}]`,
      );
    }

    // Validate Z axis is within bounds
    if (z < this.configService.minZPosition || z > this.configService.maxZPosition) {
      throw new BadRequestException(
        `Z position ${z} is out of range [${this.configService.minZPosition}, ${this.configService.maxZPosition}]`,
      );
    }
  }

  /**
   * Calculate target position
   * 
   * Computes the final target position from current position and move request.
   * Handles both absolute and relative movements.
   * 
   * @param currentPosition - Current X, Y, Z position from Raspberry Pi
   * @param move - Requested movement (x, y, z can be undefined)
   * @param relative - If true, add move values to current position; if false, use move values directly
   * @returns Calculated target position
   */
  calculateTargetPosition(
    currentPosition: Position,
    move: { x?: number; y?: number; z?: number },
    relative: boolean,
  ): Position {
    if (relative) {
      // Relative movement: add offsets to current position
      return {
        x: currentPosition.x + (move.x || 0),
        y: currentPosition.y + (move.y || 0),
        z: currentPosition.z + (move.z || 0),
      };
    } else {
      // Absolute movement: use requested values, keep current if not specified
      return {
        x: move.x !== undefined ? move.x : currentPosition.x,
        y: move.y !== undefined ? move.y : currentPosition.y,
        z: move.z !== undefined ? move.z : currentPosition.z,
      };
    }
  }
}
