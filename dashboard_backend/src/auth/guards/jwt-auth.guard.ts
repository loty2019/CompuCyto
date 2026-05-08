import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const profileId = Number(request.headers['x-profile-id']) || 1;
    const profileName = String(request.headers['x-profile-name'] || 'Operator');

    request.user = request.user || {
      id: profileId,
      email: `${profileName.toLowerCase().replace(/[^a-z0-9]+/g, '.')}@cytocore.local`,
      username: profileName,
      role: 'operator',
    };

    return true;
  }
}
