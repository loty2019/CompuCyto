import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '../../config/config.service';
import { UsersService } from '../../users/users.service';

/**
 * JWT Payload Interface
 * Structure of data encoded in JWT tokens
 */
export interface JwtPayload {
  sub: number;    // User ID (subject)
  email: string;  // User email
  role: string;   // User role (admin/user)
}

/**
 * JWT Strategy
 * 
 * Passport strategy for validating JWT tokens in protected routes.
 * Automatically extracts and validates JWT from Authorization header.
 * 
 * Used by @UseGuards(JwtAuthGuard) on protected endpoints.
 * 
 * Flow:
 * 1. Extract JWT from Authorization header (Bearer token)
 * 2. Verify token signature using JWT_SECRET
 * 3. Extract payload and validate user still exists in database
 * 4. Attach user object to request (available as req.user)
 * 
 * @class JwtStrategy
 */
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    private configService: ConfigService,
    private usersService: UsersService,
  ) {
    // Configure Passport JWT strategy
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(), // Get token from "Authorization: Bearer <token>"
      ignoreExpiration: false,                                    // Reject expired tokens
      secretOrKey: configService.jwtSecret,                      // Secret key for verification
    });
  }

  /**
   * Validate JWT payload
   * 
   * Called automatically by Passport after token is verified.
   * Checks that user still exists in database.
   * 
   * @param payload - Decoded JWT payload (sub, email, role)
   * @returns User object (attached to req.user)
   * @throws UnauthorizedException if user not found
   */
  async validate(payload: JwtPayload) {
    // Look up user by ID from token payload
    const user = await this.usersService.findById(payload.sub);
    
    if (!user) {
      // User was deleted after token was issued
      throw new UnauthorizedException('User not found');
    }
    
    // Return user object - Passport attaches this to request as req.user
    return user;
  }
}
