import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  Index,
} from 'typeorm';

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

@Entity('system_logs')
@Index(['timestamp', 'level', 'component'])
export class SystemLog {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'timestamp' })
  @Index()
  timestamp: Date;

  @Column({
    type: 'enum',
    enum: LogLevel,
    default: LogLevel.INFO,
  })
  @Index()
  level: LogLevel;

  @Column()
  @Index()
  component: string;

  @Column({ type: 'text' })
  message: string;

  @Column({ type: 'jsonb', default: {} })
  details: Record<string, any>;
}
