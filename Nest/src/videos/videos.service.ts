import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  Logger,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Video } from './entities/video.entity';
import { ConfigService } from '../config/config.service';
import * as fs from 'fs/promises';
import * as path from 'path';

@Injectable()
export class VideosService {
  private readonly logger = new Logger(VideosService.name);

  constructor(
    @InjectRepository(Video)
    private videoRepository: Repository<Video>,
    private configService: ConfigService,
  ) {}

  async findVideos(
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

    const queryBuilder = this.videoRepository
      .createQueryBuilder('video')
      .leftJoinAndSelect('video.user', 'user')
      .orderBy('video.capturedAt', 'DESC')
      .skip(skip)
      .take(limit);

    // If userId is provided, filter by user
    if (userId !== null) {
      console.log(`🔍 [SERVICE] Adding WHERE clause: video.userId = ${userId}`);
      queryBuilder.where('video.userId = :userId', { userId });
    } else {
      console.log('🔍 [SERVICE] No userId filter - fetching all videos');
    }

    const [videos, total] = await queryBuilder.getManyAndCount();

    console.log('📊 [SERVICE] Database query result:', {
      userId: userId,
      videosFound: videos.length,
      total: total,
      sampleVideos: videos.slice(0, 3).map((vid) => ({
        id: vid.id,
        userId: vid.userId,
        username: vid.user?.username,
        filename: vid.filename,
      })),
    });

    // Auto-cleanup: Check if video files exist and remove database entries for missing ones
    const videosPath = '../backend-python/videos';
    const missingVideos: Video[] = [];

    for (const video of videos) {
      const videoPath = path.join(videosPath, video.filename);
      try {
        await fs.access(videoPath);
        // File exists, keep it
      } catch {
        // File doesn't exist, mark for removal
        this.logger.warn(
          `🗑️ Video file missing, will remove from DB: ${video.filename} (ID: ${video.id})`,
        );
        missingVideos.push(video);
      }
    }

    // Remove missing videos from the results and database
    let validVideos = videos;
    let adjustedTotal = total;

    if (missingVideos.length > 0) {
      // Remove from database
      await this.videoRepository.remove(missingVideos);
      this.logger.log(
        `🧹 Auto-cleanup: Removed ${missingVideos.length} missing videos from database`,
      );

      // Filter out missing videos from results
      const missingIds = new Set(missingVideos.map((vid) => vid.id));
      validVideos = videos.filter((vid) => !missingIds.has(vid.id));
      adjustedTotal = total - missingVideos.length;
    }

    return {
      data: validVideos,
      pagination: {
        page,
        limit,
        total: adjustedTotal,
        totalPages: Math.ceil(adjustedTotal / limit),
      },
    };
  }

  /**
   * Delete a video (database entry and file)
   */
  async deleteVideo(
    videoId: number,
    userId: number,
    isAdmin: boolean,
  ): Promise<{
    success: boolean;
    message: string;
    videoId: number;
    fileDeleted: boolean;
  }> {
    // Find the video
    const video = await this.videoRepository.findOne({
      where: { id: videoId },
    });

    if (!video) {
      throw new NotFoundException(`Video with ID ${videoId} not found`);
    }

    // Check permissions - user can only delete their own videos unless admin
    if (!isAdmin && video.userId !== userId) {
      throw new ForbiddenException(
        'You do not have permission to delete this video',
      );
    }

    // Try to delete the file from disk
    let fileDeleted = false;
    try {
      const videoPath = path.join('../backend-python/videos', video.filename);
      await fs.unlink(videoPath);
      fileDeleted = true;
      this.logger.log(`Deleted file: ${videoPath}`);
    } catch (error) {
      this.logger.warn(
        `Could not delete file ${video.filename}: ${error.message}`,
      );
      // Continue anyway to remove from database
    }

    // Delete from database
    await this.videoRepository.remove(video);
    this.logger.log(
      `Deleted video ${videoId} from database (file deleted: ${fileDeleted})`,
    );

    return {
      success: true,
      message: 'Video deleted successfully',
      videoId,
      fileDeleted,
    };
  }
}
