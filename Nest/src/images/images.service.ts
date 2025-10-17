import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Image } from './entities/image.entity';

@Injectable()
export class ImagesService {
  constructor(
    @InjectRepository(Image)
    private imageRepository: Repository<Image>,
  ) {}

  async findImages(
    userId: number | null,
    page: number = 1,
    limit: number = 20,
  ) {
    const skip = (page - 1) * limit;

    const queryBuilder = this.imageRepository
      .createQueryBuilder('image')
      .leftJoinAndSelect('image.user', 'user')
      .orderBy('image.capturedAt', 'DESC')
      .skip(skip)
      .take(limit);

    // If userId is provided, filter by user
    if (userId !== null) {
      queryBuilder.where('image.userId = :userId', { userId });
    }

    const [images, total] = await queryBuilder.getManyAndCount();

    return {
      data: images,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    };
  }
}
