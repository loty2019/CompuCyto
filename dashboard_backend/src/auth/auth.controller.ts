import { Controller, Post, Body, Get, UseGuards, Request } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { AuthService } from './auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { UsersService } from '../users/users.service';
import { User } from '../users/entities/user.entity';

/**
 * Authentication Controller
 *
 * Handles user registration, login, and profile retrieval.
 * Provides JWT tokens for authenticated access to protected endpoints.
 *
 * @controller /api/v1/auth
 */
@ApiTags('Auth')
@Controller('api/v1/auth')
export class AuthController {
  constructor(
    private authService: AuthService,
    private usersService: UsersService,
  ) {}

  private async localProfile(name = 'Operator', email?: string, avatarIcon?: string) {
    const username = name.trim() || 'Operator';
    const user = await this.usersService.findOrCreateLocalProfile(
      username,
      email,
      avatarIcon,
    );

    return {
      user: this.serializeProfile(user),
    };
  }

  private serializeProfile(user: User) {
    const preferences = user.preferences || {};

    return {
      id: user.id,
      email: user.email,
      username: user.username,
      role: user.role,
      avatarIcon: preferences.avatarIcon || 'microscope',
      profile: {
        id: user.id,
        userId: user.id,
        fullName: user.fullName || user.username,
        labRole: user.labRole,
        preferences,
      },
    };
  }

  @Get('profiles')
  @ApiOperation({
    summary: 'List local operator profiles',
    description: 'Returns saved local operator profiles from the database.',
  })
  @ApiResponse({
    status: 200,
    description: 'Profiles retrieved successfully',
  })
  async getProfiles() {
    const profiles = await this.usersService.findLocalProfiles();

    return {
      profiles: profiles.map((profile) => this.serializeProfile(profile)),
    };
  }

  /**
   * Register a new user
   *
   * Creates a new user account with email, username, and password.
   * Returns JWT token and user profile.
   *
   * @route POST /api/v1/auth/register
   * @public No authentication required
   */
  @Post('register')
  @ApiOperation({
    summary: 'Register new user',
    description:
      'Create a new user account. Email and username must be unique. Password will be hashed before storage.',
  })
  @ApiBody({ type: RegisterDto })
  @ApiResponse({
    status: 201,
    description: 'User successfully registered',
    schema: {
      example: {
        access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        user: {
          id: 1,
          email: 'user@example.com',
          username: 'johndoe',
          role: 'user',
          profile: {
            id: 1,
            userId: 1,
            fullName: null,
            labRole: null,
            preferences: {},
          },
        },
      },
    },
  })
  @ApiResponse({
    status: 409,
    description: 'Email or username already exists',
    schema: {
      example: {
        statusCode: 409,
        message: 'Email already exists',
        error: 'Conflict',
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: 'Validation failed',
    schema: {
      example: {
        statusCode: 400,
        message: [
          'email must be an email',
          'password must be longer than or equal to 6 characters',
        ],
        error: 'Bad Request',
      },
    },
  })
  async register(@Body() registerDto: RegisterDto) {
    return this.localProfile(
      registerDto.username || 'Local Profile',
      registerDto.email,
      registerDto.avatarIcon,
    );
  }

  /**
   * Login existing user
   *
   * Validates credentials and returns JWT token.
   *
   * @route POST /api/v1/auth/login
   * @public No authentication required
   */
  @Post('login')
  @ApiOperation({
    summary: 'Login user',
    description:
      'Authenticate with email and password. Returns JWT token valid for 7 days (configurable).',
  })
  @ApiBody({ type: LoginDto })
  @ApiResponse({
    status: 200,
    description: 'Login successful',
    schema: {
      example: {
        access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        user: {
          id: 1,
          email: 'user@example.com',
          username: 'johndoe',
          role: 'user',
          profile: {
            id: 1,
            fullName: null,
            labRole: null,
            preferences: {},
          },
        },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Invalid credentials',
    schema: {
      example: {
        statusCode: 401,
        message: 'Invalid credentials',
        error: 'Unauthorized',
      },
    },
  })
  async login(@Body() loginDto: LoginDto) {
    const name = loginDto.email?.split('@')[0] || 'Local Profile';
    return this.localProfile(name);
  }

  /**
   * Get current user profile
   *
   * Returns profile of authenticated user from JWT token.
   *
   * @route GET /api/v1/auth/profile
   * @protected Requires valid JWT token
   */
  @Get('profile')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @ApiOperation({
    summary: 'Get current user profile',
    description:
      "Returns authenticated user's profile. Requires valid JWT token in Authorization header.",
  })
  @ApiResponse({
    status: 200,
    description: 'Profile retrieved successfully',
    schema: {
      example: {
        id: 1,
        email: 'user@example.com',
        username: 'johndoe',
        role: 'user',
        createdAt: '2025-10-09T10:30:00.000Z',
        updatedAt: '2025-10-09T10:30:00.000Z',
        profile: {
          id: 1,
          fullName: 'John Doe',
          labRole: 'Researcher',
          preferences: {},
        },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Unauthorized - Invalid or missing token',
    schema: {
      example: {
        statusCode: 401,
        message: 'Unauthorized',
      },
    },
  })
  async getProfile(@Request() req) {
    return req.user;
  }
}
