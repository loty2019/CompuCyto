import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { User } from '../../users/entities/user.entity';

@Entity('positions')
@Index(['userId', 'name'])
export class Position {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'user_id' })
  userId: number;

  @Column()
  name: string;

  @Column({ type: 'text', nullable: true })
  description: string;

  @Column({ name: 'x_position', type: 'float' })
  xPosition: number;

  @Column({ name: 'y_position', type: 'float' })
  yPosition: number;

  @Column({ name: 'z_position', type: 'float' })
  zPosition: number;

  @Column({ name: 'camera_settings', type: 'jsonb', default: {} })
  cameraSettings: Record<string, any>;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  // Relationships
  @ManyToOne(() => User, (user) => user.positions)
  @JoinColumn({ name: 'user_id' })
  user: User;
}
