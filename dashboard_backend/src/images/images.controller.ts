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
import { ImagesService } from './images.service';

/**
 * Images Controller
 *
 * Manages image retrieval and metadata operations.
 * All endpoints require JWT authentication.
 *
 * @controller /api/v1/images
 * @protected All endpoints require JWT authentication
 */
@ApiTags('Images')
@Controller('api/v1/images')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth('JWT-auth')
export class ImagesController {
  constructor(private readonly imagesService: ImagesService) {}

  /**
   * Get images with optional filtering and pagination
   *
   * Retrieves images with support for filtering by user and pagination.
   * Default behavior is to return only the authenticated user's images.
   *
   * @route GET /api/v1/images
   * @protected Requires JWT authentication
   */
  @Get()
  @ApiOperation({
    summary: 'Get images with optional filtering',
    description:
      'Retrieve images with pagination. Filter by "mine" (default) to get only your images, or "all" to get all users\' images (if permitted).',
  })
  @ApiQuery({
    name: 'filter',
    required: false,
    enum: ['mine', 'all'],
    description: 'Filter images by ownership',
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
    description: 'Images retrieved successfully',
    schema: {
      example: {
        data: [
          {
            id: 1,
            filename: 'capture_20250116_103045_123.jpg',
            thumbnailPath: '/thumbnails/thumb_capture_20250116_103045_123.jpg',
            capturedAt: '2025-01-16T10:30:45.123Z',
            xPosition: 100.5,
            yPosition: 200.3,
            zPosition: 10.0,
            exposureTime: 100,
            gain: 1.5,
            fileSize: 2456789,
            width: 1920,
            height: 1080,
            metadata: {},
            userId: 1,
            jobId: null,
          },
        ],
        total: 100,
        page: 1,
        limit: 20,
        totalPages: 5,
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Unauthorized - Invalid or missing token',
  })
  async getImages(
    @Request() req,
    @Query('filter') filter?: 'mine' | 'all',
    @Query('page') page: number = 1,
    @Query('limit') limit: number = 20,
  ) {
    const userId = req.user.id; // Changed from req.user.userId to req.user.id
    const effectiveFilter = filter || 'mine';

    console.log('🔍 [CONTROLLER] Images request received:', {
      requestedFilter: filter,
      effectiveFilter: effectiveFilter,
      userId: userId,
      username: req.user.username,
      page: page,
      limit: limit,
      willQueryByUserId: effectiveFilter === 'mine' ? userId : null,
    });

    const result = await this.imagesService.findImages(
      effectiveFilter === 'mine' ? userId : null,
      page,
      limit,
    );

    console.log('📸 [CONTROLLER] Returning images:', {
      filter: effectiveFilter,
      count: result.data.length,
      total: result.pagination.total,
    });

    return result;
  }

  /**
   * Delete an image
   *
   * Removes image from database and deletes the file from disk.
   * Users can only delete their own images unless they are admin.
   *
   * @route DELETE /api/v1/images/:id
   * @protected Requires JWT authentication
   */
  @Delete(':id')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Delete an image',
    description:
      'Delete an image by ID. Removes both database entry and physical file. Users can only delete their own images.',
  })
  @ApiParam({
    name: 'id',
    type: Number,
    description: 'Image ID',
    example: 1,
  })
  @ApiResponse({
    status: 200,
    description: 'Image deleted successfully',
    schema: {
      example: {
        success: true,
        message: 'Image deleted successfully',
        imageId: 1,
      },
    },
  })
  @ApiResponse({
    status: 404,
    description: 'Image not found',
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - Not your image',
  })
  async deleteImage(
    @Request() req,
    @Param('id', ParseIntPipe) imageId: number,
  ) {
    const userId = req.user.id;
    const isAdmin = req.user.role === 'admin';

    return this.imagesService.deleteImage(imageId, userId, isAdmin);
  }
}
