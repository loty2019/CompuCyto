import { Injectable, ServiceUnavailableException, Logger } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ConfigService } from '../config/config.service';
import { Image } from '../images/entities/image.entity';
import { Video } from '../videos/entities/video.entity';
import { catchError, firstValueFrom } from 'rxjs';
import { AxiosError } from 'axios';

/**
 * Camera Service
 *
 * HTTP client proxy to the Python camera service running on port 8001.
 * All camera operations are forwarded to the external Python service.
 * This service never controls hardware directly - it only orchestrates.
 *
 * @class CameraService
 */
@Injectable()
export class CameraService {
  private readonly logger = new Logger(CameraService.name);
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(
    private httpService: HttpService,
    private configService: ConfigService,
    @InjectRepository(Image)
    private imageRepository: Repository<Image>,
    @InjectRepository(Video)
    private videoRepository: Repository<Video>,
  ) {
    // Load configuration from environment variables
    this.baseUrl = this.configService.pythonCameraUrl;
    this.timeout = this.configService.serviceTimeout;
  }

  /**
   * Capture an image
   *
   * Forwards capture request to Python camera service.
   * The Python service handles actual camera hardware interaction.
   * Saves image metadata to database with user ID.
   *
   * @param exposure - Optional exposure time in milliseconds
   * @param gain - Optional gain value
   * @param gamma - Optional gamma correction value
   * @param userId - ID of the user capturing the image
   * @returns Image metadata from Python service (filename, path, dimensions, etc.)
   * @throws ServiceUnavailableException if Python service is not reachable
   */
  async capture(
    exposure?: number,
    gain?: number,
    gamma?: number,
    userId?: number,
  ): Promise<any> {
    try {
      // Send POST request to Python service with capture parameters
      const { data } = await firstValueFrom(
        this.httpService
          .post(
            `${this.baseUrl}/capture`,
            { exposure, gain, gamma },
            { timeout: this.timeout },
          )
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Camera capture failed: ${error.message}`);
              throw new ServiceUnavailableException('Camera service unavailable');
            }),
          ),
      );

      // Attempt to save image metadata to database with user ID
      if (data && data.success && data.filename) {
        if (!userId) {
          this.logger.warn(
            `Image captured but not saved to database: No userId provided. Filename: ${data.filename}`,
          );
          return {
            ...data,
            imageId: null,
            databaseSaved: false,
            warning: 'Image captured but not saved to database: User not authenticated',
          };
        }

        try {
          const image = this.imageRepository.create({
            userId: userId,
            filename: data.filename,
            capturedAt: new Date(data.capturedAt),
            exposureTime: data.exposureTime,
            gain: data.gain,
            gamma: data.gamma ?? null,
            fileSize: data.fileSize,
            width: data.width,
            height: data.height,
            metadata: data.metadata,
          });

          const savedImage = await this.imageRepository.save(image);
          this.logger.log(
            `Image saved to database: ID ${savedImage.id}, filename: ${data.filename}`,
          );

          // Return combined response with database ID
          return {
            ...data,
            imageId: savedImage.id,
            databaseSaved: true,
            warning: null,
          };
        } catch (dbError) {
          // Database save failed - log error but still return success since image was captured
          this.logger.error(
            `Database save failed for captured image ${data.filename}: ${dbError.message}`,
          );
          return {
            ...data,
            imageId: null,
            databaseSaved: false,
            warning: `Image captured successfully but database save failed: ${dbError.message}`,
          };
        }
      }

      // Python service returned unsuccessful response
      this.logger.error(`Camera capture unsuccessful: ${JSON.stringify(data)}`);
      return {
        ...data,
        imageId: null,
        databaseSaved: false,
        warning: 'Camera capture returned unsuccessful response',
      };
    } catch (error) {
      this.logger.error(`Camera capture error: ${error.message}`);
      throw new ServiceUnavailableException('Camera service unavailable');
    }
  }

  /**
   * Get current camera settings
   *
   * Retrieves current exposure, gain, resolution, and available resolutions
   * from the Python camera service.
   *
   * @returns Camera settings object
   * @throws ServiceUnavailableException if Python service is not reachable
   */
  async getSettings(): Promise<any> {
    try {
      // GET request to Python service for current camera settings
      const { data } = await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/settings`, { timeout: this.timeout }).pipe(
          catchError((error: AxiosError) => {
            this.logger.error(`Failed to get camera settings: ${error.message}`);
            throw new ServiceUnavailableException('Camera service unavailable');
          }),
        ),
      );
      return data;
    } catch (error) {
      this.logger.error(`Get camera settings error: ${error.message}`);
      throw new ServiceUnavailableException('Camera service unavailable');
    }
  }

  /**
   * Update camera settings
   *
   * Sends new exposure/gain/gamma settings to Python camera service.
   *
   * @param settings - Partial camera settings to update
   * @returns Updated camera settings
   * @throws ServiceUnavailableException if Python service is not reachable
   */
  async updateSettings(settings: {
    exposure?: number;
    gain?: number;
    gamma?: number;
  }): Promise<any> {
    try {
      // PUT request to Python service to update settings
      const { data } = await firstValueFrom(
        this.httpService
          .put(`${this.baseUrl}/settings`, settings, { timeout: this.timeout })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Failed to update camera settings: ${error.message}`);
              throw new ServiceUnavailableException('Camera service unavailable');
            }),
          ),
      );
      return data;
    } catch (error) {
      this.logger.error(`Update camera settings error: ${error.message}`);
      throw new ServiceUnavailableException('Camera service unavailable');
    }
  }

  /**
   * Get video preview stream URL
   *
   * Returns the URL for the MJPEG video stream from Python service.
   * Frontend should connect directly to this URL for live video.
   *
   * @returns Object containing the stream URL
   */
  async getPreviewUrl(): Promise<{ streamUrl: string }> {
    // Return the video feed URL - frontend connects directly
    return {
      streamUrl: `${this.baseUrl}/video/feed`,
    };
  }

  /**
   * Check Python camera service health
   *
   * Pings the Python service health endpoint to verify availability.
   * Used by the health check controller.
   *
   * @returns true if service is reachable, false otherwise
   */
  async checkHealth(): Promise<boolean> {
    try {
      await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/health`, { timeout: 5000 }).pipe(
          catchError(() => {
            throw new Error('Camera service unavailable');
          }),
        ),
      );
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Start video recording
   *
   * Forwards recording request to Python camera service.
   *
   * @param duration - Recording duration in seconds
   * @param playbackFrameRate - Playback frame rate in fps
   * @param decimation - Frame decimation factor
   * @returns Recording metadata
   */
  async startVideoRecording(
    duration?: number,
    playbackFrameRate?: number,
    decimation?: number,
  ): Promise<any> {
    try {
      const params: any = {};
      if (duration !== undefined) params.duration = duration;
      if (playbackFrameRate !== undefined) params.playback_frame_rate = playbackFrameRate;
      if (decimation !== undefined) params.decimation = decimation;

      const { data } = await firstValueFrom(
        this.httpService
          .post(`${this.baseUrl}/video/record/start`, null, {
            params,
            timeout: this.timeout,
          })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Failed to start video recording: ${error.message}`);
              throw new ServiceUnavailableException('Camera service unavailable');
            }),
          ),
      );

      this.logger.log(`Video recording started: ${data.filename || 'unknown'}`);
      return data;
    } catch (error) {
      this.logger.error(`Start video recording error: ${error.message}`);
      throw new ServiceUnavailableException('Camera service unavailable');
    }
  }

  /**
   * Stop video recording and save to database
   *
   * Stops recording, retrieves metadata from Python service,
   * and saves video metadata to database with user ID.
   *
   * @param userId - ID of the user who recorded the video
   * @returns Video metadata with database ID
   */
  async stopVideoRecording(userId?: number): Promise<any> {
    try {
      const { data } = await firstValueFrom(
        this.httpService
          .post(`${this.baseUrl}/video/record/stop`, null, {
            timeout: 30000, // 30 second timeout for video processing
          })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Failed to stop video recording: ${error.message}`);
              throw new ServiceUnavailableException('Camera service unavailable');
            }),
          ),
      );

      this.logger.log(`Video recording stopped: ${data.filename || 'unknown'}`);

      // Attempt to save video metadata to database with user ID
      if (data && data.success && data.filename) {
        if (!userId) {
          this.logger.warn(
            `Video recorded but not saved to database: No userId provided. Filename: ${data.filename}`,
          );
          return {
            ...data,
            videoId: null,
            databaseSaved: false,
            warning: 'Video recorded but not saved to database: User not authenticated',
          };
        }

        try {
          const video = this.videoRepository.create({
            userId: userId,
            filename: data.filename,
            capturedAt: new Date(data.capturedAt),
            duration: data.duration ?? null,
            frameRate: data.playback_frame_rate ?? null,
            captureFrameRate: data.capture_frame_rate ?? null,
            exposureTime: data.exposure_time ?? null,
            gain: data.gain ?? null,
            gamma: data.gamma ?? null,
            fileSize: data.file_size ?? null,
            width: data.width ?? null,
            height: data.height ?? null,
            encodingFormat: data.encoding_format ?? null,
            containerFormat: data.container_format ?? null,
            metadata: data.metadata ?? {},
          });

          const savedVideo = await this.videoRepository.save(video);
          this.logger.log(
            `Video saved to database: ID ${savedVideo.id}, filename: ${data.filename}`,
          );

          // Return combined response with database ID
          return {
            ...data,
            videoId: savedVideo.id,
            databaseSaved: true,
            warning: null,
          };
        } catch (dbError) {
          // Database save failed - log error but still return success since video was recorded
          this.logger.error(
            `Database save failed for recorded video ${data.filename}: ${dbError.message}`,
          );
          return {
            ...data,
            videoId: null,
            databaseSaved: false,
            warning: `Video recorded successfully but database save failed: ${dbError.message}`,
          };
        }
      }

      // Python service returned unsuccessful response
      this.logger.error(`Video recording unsuccessful: ${JSON.stringify(data)}`);
      return {
        ...data,
        videoId: null,
        databaseSaved: false,
        warning: 'Video recording returned unsuccessful response',
      };
    } catch (error) {
      this.logger.error(`Stop video recording error: ${error.message}`);
      throw new ServiceUnavailableException('Camera service unavailable');
    }
  }

  /**
   * Cancel video recording
   *
   * Cancels ongoing video recording.
   *
   * @returns Cancellation result
   */
  async cancelVideoRecording(): Promise<any> {
    try {
      const { data } = await firstValueFrom(
        this.httpService
          .post(`${this.baseUrl}/video/record/cancel`, null, {
            timeout: this.timeout,
          })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Failed to cancel video recording: ${error.message}`);
              throw new ServiceUnavailableException('Camera service unavailable');
            }),
          ),
      );

      this.logger.log('Video recording canceled');
      return data;
    } catch (error) {
      this.logger.error(`Cancel video recording error: ${error.message}`);
      throw new ServiceUnavailableException('Camera service unavailable');
    }
  }

  /**
   * Get video recording status
   *
   * Checks if video is currently being recorded.
   *
   * @returns Recording status
   */
  async getVideoRecordingStatus(): Promise<any> {
    try {
      const { data } = await firstValueFrom(
        this.httpService
          .get(`${this.baseUrl}/video/record/status`, {
            timeout: this.timeout,
          })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Failed to get recording status: ${error.message}`);
              throw new ServiceUnavailableException('Camera service unavailable');
            }),
          ),
      );

      return data;
    } catch (error) {
      this.logger.error(`Get recording status error: ${error.message}`);
      throw new ServiceUnavailableException('Camera service unavailable');
    }
  }
}
