import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UsersService } from '../users/users.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { User } from '../users/entities/user.entity';

/**
 * Authentication Service
 *
 * Handles user registration and login with JWT token generation.
 * Works with UsersService to manage user accounts and JwtService to create tokens.
 *
 * @class AuthService
 */
@Injectable()
export class AuthService {
  constructor(
    private usersService: UsersService,
    private jwtService: JwtService,
  ) {}

  /**
   * Register a new user
   *
   * Creates a new user account with hashed password and generates a JWT token.
   * Also creates a user profile automatically via UsersService.
   *
   * @param registerDto - User registration data (email, username, password)
   * @returns Object containing JWT access token and user data
   * @throws ConflictException if email or username already exists
   */
  async register(registerDto: RegisterDto) {
    const user = await this.usersService.create(
      registerDto.email,
      registerDto.username,
      registerDto.password,
    );

    return this.generateTokenResponse(user);
  }

  /**
   * Login existing user
   *
   * Validates user credentials and generates a JWT token.
   *
   * @param loginDto - Login credentials (email, password)
   * @returns Object containing JWT access token and user data
   * @throws UnauthorizedException if credentials are invalid
   */
  async login(loginDto: LoginDto) {
    const user = await this.usersService.findByEmail(loginDto.email);

    if (!user) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await user.validatePassword(loginDto.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    return this.generateTokenResponse(user);
  }

  /**
   * Generate JWT token response
   *
   * Private helper method to create consistent token responses.
   * Excludes sensitive data (like hashed password) from the response.
   *
   * @param user - User entity with profile
   * @returns Object with access_token and sanitized user data
   * @private
   */
  private generateTokenResponse(user: User) {
    // Create JWT payload with user ID (sub), email, and role
    const payload = {
      sub: user.id,
      email: user.email,
      role: user.role,
    };

    // Return access token and sanitized user data (password excluded via @Exclude decorator)
    return {
      access_token: this.jwtService.sign(payload),
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        role: user.role,
        fullName: user.fullName,
        labRole: user.labRole,
        preferences: user.preferences,
      },
    };
  }
}
