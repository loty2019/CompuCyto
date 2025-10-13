import { IsEmail, IsString, MinLength, MaxLength } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * Register DTO (Data Transfer Object)
 * 
 * Validates user registration data from the frontend.
 * All fields are required and automatically validated by class-validator.
 * 
 * Validation Rules:
 * - email: Must be valid email format
 * - username: 3-50 characters
 * - password: Minimum 6 characters (will be hashed before storage)
 * 
 * @class RegisterDto
 */
export class RegisterDto {
  /**
   * User's email address (must be unique in database)
   * @example "user@example.com"
   */
  @ApiProperty({
    description: 'User email address (must be unique)',
    example: 'user@example.com',
    format: 'email'
  })
  @IsEmail()
  email: string;

  /**
   * User's username (must be unique in database)
   * @example "johndoe"
   */
  @ApiProperty({
    description: 'Username for login (must be unique)',
    example: 'johndoe',
    minLength: 3,
    maxLength: 50
  })
  @IsString()
  @MinLength(3)
  @MaxLength(50)
  username: string;

  /**
   * User's password (will be hashed with bcrypt before storage)
   * Minimum 6 characters for basic security
   * @example "password123"
   */
  @ApiProperty({
    description: 'User password (will be hashed before storage)',
    example: 'password123',
    minLength: 6,
    maxLength: 100,
    format: 'password'
  })
  @IsString()
  @MinLength(6)
  @MaxLength(100)
  password: string;
}
