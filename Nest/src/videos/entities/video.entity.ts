import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';
import { Job } from '../../jobs/entities/job.entity';
import { User } from '../../users/entities/user.entity';

/**
 * Video Entity
 *
 * Represents a recorded microscope video with metadata.
 * Videos are linked to users and optionally to automated jobs.
 *
 * @entity videos
 */
@Entity('videos')
@Index(['jobId', 'capturedAt'])
@Index(['userId', 'capturedAt'])
export class Video {
  @ApiProperty({ description: 'Unique video identifier', example: 1 })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({
    description: 'Associated job ID (if part of automated job)',
    example: 5,
    nullable: true,
  })
  @Column({ name: 'job_id', nullable: true })
  jobId: number;

  @ApiProperty({ description: 'User who recorded the video', example: 1 })
  @Column({ name: 'user_id' })
  userId: number;

  @ApiProperty({
    description: 'Video filename',
    example: 'recording_20250121_103045_123.avi',
  })
  @Column({ unique: true })
  filename: string;

  @ApiProperty({
    description: 'Path to thumbnail image',
    example: '/thumbnails/thumb_recording_20250121_103045_123.jpg',
    nullable: true,
  })
  @Column({ name: 'thumbnail_path', nullable: true })
  thumbnailPath: string;

  @ApiProperty({
    description: 'Timestamp when video recording started',
    example: '2025-01-21T10:30:45.123Z',
  })
  @Column({ name: 'captured_at', type: 'timestamp' })
  @Index()
  capturedAt: Date;

  @ApiProperty({
    description: 'Video duration in seconds',
    example: 30.5,
    nullable: true,
  })
  @Column({ type: 'float', nullable: true })
  duration: number;

  @ApiProperty({
    description: 'Video frame rate (fps)',
    example: 25,
    nullable: true,
  })
  @Column({ name: 'frame_rate', type: 'float', nullable: true })
  frameRate: number;

  @ApiProperty({
    description: 'Camera frame rate during capture (fps)',
    example: 30,
    nullable: true,
  })
  @Column({ name: 'capture_frame_rate', type: 'float', nullable: true })
  captureFrameRate: number;

  @ApiProperty({
    description: 'Stage X position when recorded (mm)',
    example: 100.5,
    nullable: true,
  })
  @Column({ name: 'x_position', type: 'float', nullable: true })
  xPosition: number;

  @ApiProperty({
    description: 'Stage Y position when recorded (mm)',
    example: 200.3,
    nullable: true,
  })
  @Column({ name: 'y_position', type: 'float', nullable: true })
  yPosition: number;

  @ApiProperty({
    description: 'Stage Z position when recorded (mm)',
    example: 10.0,
    nullable: true,
  })
  @Column({ name: 'z_position', type: 'float', nullable: true })
  zPosition: number;

  @ApiProperty({
    description: 'Exposure time in milliseconds',
    example: 100,
    nullable: true,
  })
  @Column({ name: 'exposure_time', nullable: true })
  exposureTime: number;

  @ApiProperty({
    description: 'Camera gain/sensitivity',
    example: 1.5,
    nullable: true,
  })
  @Column({ type: 'float', nullable: true })
  gain: number;

  @ApiProperty({
    description: 'Camera gamma correction value',
    example: 1.0,
    nullable: true,
  })
  @Column({ type: 'float', nullable: true })
  gamma: number;

  @ApiProperty({
    description: 'File size in bytes',
    example: 15456789,
    nullable: true,
  })
  @Column({ name: 'file_size', type: 'bigint', nullable: true })
  fileSize: number;

  @ApiProperty({
    description: 'Video width in pixels',
    example: 1920,
    nullable: true,
  })
  @Column({ nullable: true })
  width: number;

  @ApiProperty({
    description: 'Video height in pixels',
    example: 1080,
    nullable: true,
  })
  @Column({ nullable: true })
  height: number;

  @ApiProperty({
    description: 'Video encoding format',
    example: 'H264',
    nullable: true,
  })
  @Column({ name: 'encoding_format', nullable: true })
  encodingFormat: string;

  @ApiProperty({
    description: 'Video container format',
    example: 'AVI',
    nullable: true,
  })
  @Column({ name: 'container_format', nullable: true })
  containerFormat: string;

  @ApiProperty({
    description: 'Additional metadata',
    example: { bitrate: 8000000, decimation: 1 },
  })
  @Column({ type: 'jsonb', default: {} })
  metadata: Record<string, any>;

  // Relationships
  @ManyToOne(() => Job, (job) => job.videos, { nullable: true })
  @JoinColumn({ name: 'job_id' })
  job: Job;

  @ManyToOne(() => User, (user) => user.videos)
  @JoinColumn({ name: 'user_id' })
  user: User;
}
