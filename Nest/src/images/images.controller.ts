import { Controller, Get, Query, Request, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { ImagesService } from './images.service';

@Controller('api/v1/images')
@UseGuards(JwtAuthGuard)
export class ImagesController {
  constructor(private readonly imagesService: ImagesService) {}

  @Get()
  async getImages(
    @Request() req,
    @Query('filter') filter?: 'mine' | 'all',
    @Query('page') page: number = 1,
    @Query('limit') limit: number = 20,
  ) {
    const userId = req.user.userId;
    const effectiveFilter = filter || 'mine';
    
    return this.imagesService.findImages(
      effectiveFilter === 'mine' ? userId : null,
      page,
      limit,
    );
  }
}
