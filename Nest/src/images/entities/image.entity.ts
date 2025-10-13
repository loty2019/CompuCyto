import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { Job } from '../../jobs/entities/job.entity';
import { User } from '../../users/entities/user.entity';

@Entity('images')
@Index(['jobId', 'capturedAt'])
@Index(['userId', 'capturedAt'])
export class Image {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'job_id', nullable: true })
  jobId: number;

  @Column({ name: 'user_id' })
  userId: number;

  @Column({ unique: true })
  filename: string;

  @Column({ name: 'thumbnail_path', nullable: true })
  thumbnailPath: string;

  @Column({ name: 'captured_at', type: 'timestamp' })
  @Index()
  capturedAt: Date;

  @Column({ name: 'x_position', type: 'float', nullable: true })
  xPosition: number;

  @Column({ name: 'y_position', type: 'float', nullable: true })
  yPosition: number;

  @Column({ name: 'z_position', type: 'float', nullable: true })
  zPosition: number;

  @Column({ name: 'exposure_time', nullable: true })
  exposureTime: number;

  @Column({ type: 'float', nullable: true })
  gain: number;

  @Column({ name: 'file_size', nullable: true })
  fileSize: number;

  @Column({ nullable: true })
  width: number;

  @Column({ nullable: true })
  height: number;

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
