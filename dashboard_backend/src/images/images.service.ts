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
    fallbackOwnerUserId?: number,
  ) {
    await this.syncCaptureFolder(fallbackOwnerUserId ?? userId ?? undefined);
    await this.cleanupIncompleteImages();

    const skip = (page - 1) * limit;

    const queryBuilder = this.imageRepository
      .createQueryBuilder('image')
      .leftJoinAndSelect('image.user', 'user')
      .orderBy('image.capturedAt', 'DESC')
      .skip(skip)
      .take(limit);

    if (userId !== null) {
      queryBuilder.where('image.userId = :userId', { userId });
    }

    const [images, total] = await queryBuilder.getManyAndCount();
    const capturesPath = await this.getCapturesPath();
    const missingImages: Image[] = [];

    for (const image of images) {
      const imagePath = path.join(capturesPath, image.filename);
      try {
        await fs.access(imagePath);
      } catch {
        this.logger.warn(
          `Image file missing, will remove from DB: ${image.filename} (ID: ${image.id})`,
        );
        missingImages.push(image);
      }
    }

    let validImages = images;
    let adjustedTotal = total;

    if (missingImages.length > 0) {
      await this.imageRepository.remove(missingImages);
      this.logger.log(
        `Auto-cleanup: Removed ${missingImages.length} missing images from database`,
      );

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
    const image = await this.imageRepository.findOne({
      where: { id: imageId },
    });

    if (!image) {
      throw new NotFoundException(`Image with ID ${imageId} not found`);
    }

    if (!isAdmin && image.userId !== userId) {
      throw new ForbiddenException('You do not have permission to delete this image');
    }

    let fileDeleted = false;
    try {
      const imagePath = path.join(await this.getCapturesPath(), image.filename);
      await fs.unlink(imagePath);
      fileDeleted = true;
      this.logger.log(`Deleted file: ${imagePath}`);
    } catch (error) {
      this.logger.warn(`Could not delete file ${image.filename}: ${error.message}`);
    }

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

  private async syncCaptureFolder(ownerUserId?: number): Promise<void> {
    if (!ownerUserId) {
      return;
    }

    this.logger.log(
      'Skipping raw capture-folder import because image rows now require camera and stage metadata',
    );
  }

  private async getCapturesPath(): Promise<string> {
    const candidates = [
      this.configService.imagesPath,
      '../camera_backend/captures',
      'camera_backend/captures',
      './captures',
      '../backend-python/captures',
    ].filter(Boolean);

    for (const candidate of candidates) {
      const resolved = path.isAbsolute(candidate)
        ? candidate
        : path.resolve(process.cwd(), candidate);

      try {
        await fs.access(resolved);
        return resolved;
      } catch {
        // Try the next known capture location.
      }
    }

    return path.resolve(process.cwd(), '../camera_backend/captures');
  }

  private async cleanupIncompleteImages(): Promise<void> {
    const incompleteImages = await this.imageRepository
      .createQueryBuilder('image')
      .where('image.xPosition IS NULL')
      .orWhere('image.yPosition IS NULL')
      .orWhere('image.zPosition IS NULL')
      .orWhere('image.exposureTime IS NULL')
      .orWhere('image.gain IS NULL')
      .orWhere('image.gamma IS NULL')
      .orWhere('image.fileSize IS NULL')
      .orWhere('image.width IS NULL')
      .orWhere('image.height IS NULL')
      .getMany();

    if (incompleteImages.length === 0) {
      return;
    }

    const capturesPath = await this.getCapturesPath();

    for (const image of incompleteImages) {
      try {
        await fs.unlink(path.join(capturesPath, image.filename));
      } catch (error) {
        this.logger.warn(
          `Could not delete incomplete image file ${image.filename}: ${error.message}`,
        );
      }
    }

    await this.imageRepository.remove(incompleteImages);
    this.logger.warn(
      `Removed ${incompleteImages.length} old image record(s) missing required capture metadata`,
    );
  }
}
