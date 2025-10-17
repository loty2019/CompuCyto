import { IsEmail, IsString, MinLength } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * Login DTO (Data Transfer Object)
 *
 * Validates user login credentials from the frontend.
 * Both fields are required and automatically validated by class-validator.
 *
 * @class LoginDto
 */
export class LoginDto {
  /**
   * User's email address
   * @example "user@example.com"
   */
  @ApiProperty({
    description: 'User email address',
    example: 'user@example.com',
    format: 'email',
  })
  @IsEmail()
  email: string;

  /**
   * User's password (plain text - will be compared with hashed password)
   * @example "password123"
   */
  @ApiProperty({
    description: 'User password',
    example: 'password123',
    minLength: 6,
    format: 'password',
  })
  @IsString()
  @MinLength(6)
  password: string;
}
