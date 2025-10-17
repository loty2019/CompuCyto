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
 * Image Entity
 *
 * Represents a captured microscope image with metadata.
 * Images are linked to users and optionally to automated jobs.
 *
 * @entity images
 */
@Entity('images')
@Index(['jobId', 'capturedAt'])
@Index(['userId', 'capturedAt'])
export class Image {
  @ApiProperty({ description: 'Unique image identifier', example: 1 })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({
    description: 'Associated job ID (if part of automated job)',
    example: 5,
    nullable: true,
  })
  @Column({ name: 'job_id', nullable: true })
  jobId: number;

  @ApiProperty({ description: 'User who captured the image', example: 1 })
  @Column({ name: 'user_id' })
  userId: number;

  @ApiProperty({
    description: 'Image filename',
    example: 'capture_20250116_103045_123.jpg',
  })
  @Column({ unique: true })
  filename: string;

  @ApiProperty({
    description: 'Path to thumbnail image',
    example: '/thumbnails/thumb_capture_20250116_103045_123.jpg',
    nullable: true,
  })
  @Column({ name: 'thumbnail_path', nullable: true })
  thumbnailPath: string;

  @ApiProperty({
    description: 'Timestamp when image was captured',
    example: '2025-01-16T10:30:45.123Z',
  })
  @Column({ name: 'captured_at', type: 'timestamp' })
  @Index()
  capturedAt: Date;

  @ApiProperty({
    description: 'Stage X position when captured (mm)',
    example: 100.5,
    nullable: true,
  })
  @Column({ name: 'x_position', type: 'float', nullable: true })
  xPosition: number;

  @ApiProperty({
    description: 'Stage Y position when captured (mm)',
    example: 200.3,
    nullable: true,
  })
  @Column({ name: 'y_position', type: 'float', nullable: true })
  yPosition: number;

  @ApiProperty({
    description: 'Stage Z position when captured (mm)',
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
    example: 2456789,
    nullable: true,
  })
  @Column({ name: 'file_size', nullable: true })
  fileSize: number;

  @ApiProperty({
    description: 'Image width in pixels',
    example: 1920,
    nullable: true,
  })
  @Column({ nullable: true })
  width: number;

  @ApiProperty({
    description: 'Image height in pixels',
    example: 1080,
    nullable: true,
  })
  @Column({ nullable: true })
  height: number;

  @ApiProperty({
    description: 'Additional metadata',
    example: { format: 'JPG', quality: 95 },
  })
  @Column({ type: 'jsonb', default: {} })
  metadata: Record<string, any>;

  // Relationships
  @ManyToOne(() => Job, (job) => job.images, { nullable: true })
  @JoinColumn({ name: 'job_id' })
  job: Job;

  @ManyToOne(() => User, (user) => user.images)
  @JoinColumn({ name: 'user_id' })
  user: User;
}
