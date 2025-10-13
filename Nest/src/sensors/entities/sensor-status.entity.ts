import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from 'typeorm';

export enum SensorStatusType {
  NORMAL = 'normal',
  WARNING = 'warning',
  CRITICAL = 'critical',
}

@Entity('sensor_status')
export class SensorStatus {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'sensor_type', unique: true })
  sensorType: string;

  @Column({ type: 'float', nullable: true })
  value: number;

  @Column({ nullable: true })
  unit: string;

  @Column({
    type: 'enum',
    enum: SensorStatusType,
    default: SensorStatusType.NORMAL,
  })
  status: SensorStatusType;

  @UpdateDateColumn({ name: 'last_updated' })
  lastUpdated: Date;
}
