import {
  Controller,
  Get,
  Delete,
  Query,
  Request,
  UseGuards,
  Param,
  HttpCode,
  HttpStatus,
  ParseIntPipe,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiQuery,
  ApiParam,
} from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { VideosService } from './videos.service';

/**
 * Videos Controller
 *
 * Manages video retrieval and metadata operations.
 * All endpoints require JWT authentication.
 *
 * @controller /api/v1/videos
 * @protected All endpoints require JWT authentication
 */
@ApiTags('Videos')
@Controller('api/v1/videos')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth('JWT-auth')
export class VideosController {
  constructor(private readonly videosService: VideosService) {}

  /**
   * Get videos with optional filtering and pagination
   *
   * Retrieves videos with support for filtering by user and pagination.
   * Default behavior is to return only the authenticated user's videos.
   *
   * @route GET /api/v1/videos
   * @protected Requires JWT authentication
   */
  @Get()
  @ApiOperation({
    summary: 'Get videos with optional filtering',
    description:
      'Retrieve videos with pagination. Filter by "mine" (default) to get only your videos, or "all" to get all users\' videos (if permitted).',
  })
  @ApiQuery({
    name: 'filter',
    required: false,
    enum: ['mine', 'all'],
    description: 'Filter videos by ownership',
    example: 'mine',
  })
  @ApiQuery({
    name: 'page',
    required: false,
    type: Number,
    description: 'Page number for pagination',
    example: 1,
  })
  @ApiQuery({
    name: 'limit',
    required: false,
    type: Number,
    description: 'Number of items per page',
    example: 20,
  })
  @ApiResponse({
    status: 200,
    description: 'Videos retrieved successfully',
    schema: {
      example: {
        data: [
          {
            id: 1,
            filename: 'recording_20250121_103045_123.avi',
            thumbnailPath:
              '/thumbnails/thumb_recording_20250121_103045_123.jpg',
            capturedAt: '2025-01-21T10:30:45.123Z',
            duration: 30.5,
            frameRate: 25,
            captureFrameRate: 30,
            xPosition: 100.5,
            yPosition: 200.3,
            zPosition: 10.0,
            exposureTime: 100,
            gain: 1.5,
            fileSize: 15456789,
            width: 1920,
            height: 1080,
            encodingFormat: 'H264',
            containerFormat: 'AVI',
            metadata: {},
            userId: 1,
            jobId: null,
          },
        ],
        total: 50,
        page: 1,
        limit: 20,
        totalPages: 3,
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Unauthorized - Invalid or missing token',
  })
  async getVideos(
    @Request() req,
    @Query('filter') filter?: 'mine' | 'all',
    @Query('page') page: number = 1,
    @Query('limit') limit: number = 20,
  ) {
    const userId = req.user.id;
    const effectiveFilter = filter || 'mine';

    console.log('🔍 [CONTROLLER] Videos request received:', {
      requestedFilter: filter,
      effectiveFilter: effectiveFilter,
      userId: userId,
      username: req.user.username,
      page: page,
      limit: limit,
      willQueryByUserId: effectiveFilter === 'mine' ? userId : null,
    });

    const result = await this.videosService.findVideos(
      effectiveFilter === 'mine' ? userId : null,
      page,
      limit,
    );

    console.log('🎬 [CONTROLLER] Returning videos:', {
      filter: effectiveFilter,
      count: result.data.length,
      total: result.pagination.total,
    });

    return result;
  }

  /**
   * Delete a video
   *
   * Removes video from database and deletes the file from disk.
   * Users can only delete their own videos unless they are admin.
   *
   * @route DELETE /api/v1/videos/:id
   * @protected Requires JWT authentication
   */
  @Delete(':id')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Delete a video',
    description:
      'Delete a video by ID. Removes both database entry and physical file. Users can only delete their own videos.',
  })
  @ApiParam({
    name: 'id',
    type: Number,
    description: 'Video ID',
    example: 1,
  })
  @ApiResponse({
    status: 200,
    description: 'Video deleted successfully',
    schema: {
      example: {
        success: true,
        message: 'Video deleted successfully',
        videoId: 1,
      },
    },
  })
  @ApiResponse({
    status: 404,
    description: 'Video not found',
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - Not your video',
  })
  async deleteVideo(
    @Request() req,
    @Param('id', ParseIntPipe) videoId: number,
  ) {
    const userId = req.user.id;
    const isAdmin = req.user.role === 'admin';

    return this.videosService.deleteVideo(videoId, userId, isAdmin);
  }
}
