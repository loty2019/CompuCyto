import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { UsersService } from '../../users/users.service';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private readonly usersService: UsersService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const profileName = String(request.headers['x-profile-name'] || 'Operator').trim();
    const profileEmail = request.headers['x-profile-email']
      ? String(request.headers['x-profile-email'])
      : undefined;
    const profileIcon = request.headers['x-profile-icon']
      ? String(request.headers['x-profile-icon'])
      : undefined;
    const user = await this.usersService.findOrCreateLocalProfile(
      profileName || 'Operator',
      profileEmail,
      profileIcon,
    );

    request.user = request.user || {
      id: user.id,
      email: user.email,
      username: user.username,
      role: user.role,
      fullName: user.fullName,
      preferences: user.preferences || {},
    };

    return true;
  }
}
