import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  Logger,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Image } from './entities/image.entity';
import { ConfigService } from '../config/config.service';
import * as fs from 'fs/promises';
import * as path from 'path';

@Injectable()
export class ImagesService {
  private readonly logger = new Logger(ImagesService.name);

  constructor(
    @InjectRepository(Image)
    private imageRepository: Repository<Image>,
    private configService: ConfigService,
  ) {}

  async findImages(
    userId: number | null,
    page: number = 1,
    limit: number = 20,
  ) {
    const skip = (page - 1) * limit;

    console.log('🗄️ [SERVICE] Building database query:', {
      userId: userId,
      filteringByUser: userId !== null,
      page: page,
      limit: limit,
      skip: skip,
    });

    const queryBuilder = this.imageRepository
      .createQueryBuilder('image')
      .leftJoinAndSelect('image.user', 'user')
      .orderBy('image.capturedAt', 'DESC')
      .skip(skip)
      .take(limit);

    // If userId is provided, filter by user
    if (userId !== null) {
      console.log(`🔍 [SERVICE] Adding WHERE clause: image.userId = ${userId}`);
      queryBuilder.where('image.userId = :userId', { userId });
    } else {
      console.log('🔍 [SERVICE] No userId filter - fetching all images');
    }

    const [images, total] = await queryBuilder.getManyAndCount();

    console.log('📊 [SERVICE] Database query result:', {
      userId: userId,
      imagesFound: images.length,
      total: total,
      sampleImages: images.slice(0, 3).map((img) => ({
        id: img.id,
        userId: img.userId,
        username: img.user?.username,
        filename: img.filename,
      })),
    });

    // Auto-cleanup: Check if image files exist and remove database entries for missing ones
    const capturesPath = '../backend-python/captures';
    const missingImages: Image[] = [];

    for (const image of images) {
      const imagePath = path.join(capturesPath, image.filename);
      try {
        await fs.access(imagePath);
        // File exists, keep it
      } catch {
        // File doesn't exist, mark for removal
        this.logger.warn(
          `🗑️ Image file missing, will remove from DB: ${image.filename} (ID: ${image.id})`,
        );
        missingImages.push(image);
      }
    }

    // Remove missing images from the results and database
    let validImages = images;
    let adjustedTotal = total;

    if (missingImages.length > 0) {
      // Remove from database
      await this.imageRepository.remove(missingImages);
      this.logger.log(
        `🧹 Auto-cleanup: Removed ${missingImages.length} missing images from database`,
      );

      // Filter out missing images from results
      const missingIds = new Set(missingImages.map((img) => img.id));
      validImages = images.filter((img) => !missingIds.has(img.id));
      adjustedTotal = total - missingImages.length;
    }

    return {
      data: validImages,
      pagination: {
        page,
        limit,
        total: adjustedTotal,
        totalPages: Math.ceil(adjustedTotal / limit),
      },
    };
  }

  /**
   * Delete an image (database entry and file)
   */
  async deleteImage(
    imageId: number,
    userId: number,
    isAdmin: boolean,
  ): Promise<{
    success: boolean;
    message: string;
    imageId: number;
    fileDeleted: boolean;
  }> {
    // Find the image
    const image = await this.imageRepository.findOne({
      where: { id: imageId },
    });

    if (!image) {
      throw new NotFoundException(`Image with ID ${imageId} not found`);
    }

    // Check permissions - user can only delete their own images unless admin
    if (!isAdmin && image.userId !== userId) {
      throw new ForbiddenException(
        'You do not have permission to delete this image',
      );
    }

    // Try to delete the file from disk
    let fileDeleted = false;
    try {
      const imagePath = path.join('../backend-python/captures', image.filename);
      await fs.unlink(imagePath);
      fileDeleted = true;
      this.logger.log(`Deleted file: ${imagePath}`);
    } catch (error) {
      this.logger.warn(
        `Could not delete file ${image.filename}: ${error.message}`,
      );
      // Continue anyway to remove from database
    }

    // Delete from database
    await this.imageRepository.remove(image);
    this.logger.log(
      `Deleted image ${imageId} from database (file deleted: ${fileDeleted})`,
    );

    return {
      success: true,
      message: 'Image deleted successfully',
      imageId,
      fileDeleted,
    };
  }
}
