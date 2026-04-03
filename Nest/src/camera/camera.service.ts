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
 * Camera Service (Simplified)
 *
 * Handles camera operations that require database persistence.
 * Frontend calls Python camera service directly for settings/streaming.
 * This service only handles capture and video stop (which save to DB).
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
    this.baseUrl = this.configService.pythonCameraUrl;
    this.timeout = this.configService.serviceTimeout;
  }

  /**
   * Capture an image and save metadata to database
   *
   * @param exposure - Optional exposure time in milliseconds
   * @param gain - Optional gain value
   * @param gamma - Optional gamma correction value
   * @param userId - ID of the user capturing the image
   * @returns Image metadata with database ID
   */
  async capture(
    exposure?: number,
    gain?: number,
    gamma?: number,
    userId?: number,
  ): Promise<any> {
    try {
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

      if (data && data.success && data.filename) {
        if (!userId) {
          this.logger.warn(`Image captured without userId: ${data.filename}`);
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
            filepath: data.filepath,
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
          this.logger.log(`Image saved: ID ${savedImage.id}, ${data.filename}`);

          return {
            ...data,
            imageId: savedImage.id,
            databaseSaved: true,
            warning: null,
          };
        } catch (dbError) {
          this.logger.error(`DB save failed for ${data.filename}: ${dbError.message}`);
          return {
            ...data,
            imageId: null,
            databaseSaved: false,
            warning: `Image captured but database save failed: ${dbError.message}`,
          };
        }
      }

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
   * Check Python camera service health
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
   * Stop video recording and save metadata to database
   *
   * @param userId - ID of the user who recorded the video
   * @returns Video metadata with database ID
   */
  async stopVideoRecording(userId?: number): Promise<any> {
    try {
      const { data } = await firstValueFrom(
        this.httpService
          .post(`${this.baseUrl}/video/record/stop`, null, {
            timeout: 30000,
          })
          .pipe(
            catchError((error: AxiosError) => {
              this.logger.error(`Failed to stop video recording: ${error.message}`);
              throw new ServiceUnavailableException('Camera service unavailable');
            }),
          ),
      );

      this.logger.log(`Video recording stopped: ${data.filename || 'unknown'}`);

      if (data && data.success && data.filename) {
        if (!userId) {
          this.logger.warn(`Video recorded without userId: ${data.filename}`);
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
            filepath: data.filepath,
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
          this.logger.log(`Video saved: ID ${savedVideo.id}, ${data.filename}`);

          return {
            ...data,
            videoId: savedVideo.id,
            databaseSaved: true,
            warning: null,
          };
        } catch (dbError) {
          this.logger.error(`DB save failed for ${data.filename}: ${dbError.message}`);
          return {
            ...data,
            videoId: null,
            databaseSaved: false,
            warning: `Video recorded but database save failed: ${dbError.message}`,
          };
        }
      }

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
}
