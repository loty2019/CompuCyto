import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  UpdateDateColumn,
  OneToMany,
  BeforeInsert,
  BeforeUpdate,
} from 'typeorm';
import { ApiProperty, ApiHideProperty } from '@nestjs/swagger';
import * as bcrypt from 'bcrypt';
import { Image } from '../../images/entities/image.entity';
import { Video } from '../../videos/entities/video.entity';
import { Exclude } from 'class-transformer';

/**
 * User Role Enum
 * Defines available user roles in the system
 */
export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
}

/**
 * User Entity
 *
 * Represents a system user with authentication credentials and profile information.
 * Passwords are automatically hashed using bcrypt before storage.
 *
 * Relationships:
 * - One-to-Many with Image (images captured by this user)
 * - One-to-Many with Video (videos recorded by this user)
 *
 * @entity users
 */
@Entity('users')
export class User {
  @ApiProperty({ description: 'Unique user identifier', example: 1 })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({
    description: 'User email address (unique)',
    example: 'user@example.com',
  })
  @Column({ unique: true })
  email: string;

  @ApiProperty({
    description: 'Username for login (unique)',
    example: 'johndoe',
  })
  @Column({ unique: true })
  username: string;

  @ApiHideProperty()
  @Column()
  @Exclude()
  password: string;

  @ApiProperty({
    description: 'User role',
    enum: UserRole,
    example: UserRole.USER,
  })
  @Column({
    type: 'enum',
    enum: UserRole,
    default: UserRole.USER,
  })
  role: UserRole;

  @ApiProperty({
    description: 'User full name',
    example: 'John Doe',
    required: false,
    nullable: true,
  })
  @Column({ name: 'full_name', nullable: true })
  fullName?: string;

  @ApiProperty({
    description: 'User lab role',
    example: 'Researcher',
    required: false,
    nullable: true,
  })
  @Column({ name: 'lab_role', nullable: true })
  labRole?: string;

  @ApiProperty({
    description: 'User preferences',
    example: { theme: 'dark', notifications: true },
  })
  @Column({ type: 'jsonb', default: {} })
  preferences: Record<string, any>;

  @ApiProperty({
    description: 'Account creation timestamp',
    example: '2025-10-09T10:30:00.000Z',
  })
  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @ApiProperty({
    description: 'Last update timestamp',
    example: '2025-10-09T10:30:00.000Z',
  })
  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  // Relationships
  @OneToMany(() => Image, (image) => image.user)
  images: Image[];

  @OneToMany(() => Video, (video) => video.user)
  videos: Video[];

  @BeforeInsert()
  @BeforeUpdate()
  async hashPassword() {
    if (this.password && !this.password.startsWith('$2b$')) {
      this.password = await bcrypt.hash(this.password, 10);
    }
  }

  async validatePassword(password: string): Promise<boolean> {
    return bcrypt.compare(password, this.password);
  }
}
