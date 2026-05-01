import { Controller, Get, UseGuards, Request } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
} from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { UsersService } from './users.service';

/**
 * Users Controller
 *
 * Manages user profile operations.
 * All endpoints require JWT authentication.
 *
 * @controller /api/v1/users
 * @protected All endpoints require JWT authentication
 */
@ApiTags('Users')
@Controller('api/v1/users')
export class UsersController {
  constructor(private usersService: UsersService) {}

  /**
   * Get current user profile
   *
   * Returns the authenticated user's complete profile information.
   *
   * @route GET /api/v1/users/profile
   * @protected Requires JWT authentication
   */
  @Get('profile')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @ApiOperation({
    summary: 'Get current user profile',
    description:
      "Retrieve the authenticated user's profile. Similar to /auth/profile but may include additional user-specific data.",
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
        fullName: 'John Doe',
        labRole: 'Researcher',
        preferences: {},
        createdAt: '2025-10-09T10:30:00.000Z',
        updatedAt: '2025-10-09T10:30:00.000Z',
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Unauthorized - Invalid or missing token',
  })
  async getProfile(@Request() req) {
    return req.user;
  }
}
