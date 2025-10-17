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
import { Job } from '../../jobs/entities/job.entity';
import { Position } from '../../positions/entities/position.entity';
import { Image } from '../../images/entities/image.entity';
import { Exclude } from 'class-transformer';

/**
 * User Role Enum
 * Defines available user roles in the system
 */
export enum UserRole {
  ADMIN = 'admin', // Full system access
  USER = 'user', // Standard user access
}

/**
 * User Entity
 *
 * Represents a system user with authentication credentials and profile information.
 * Passwords are automatically hashed using bcrypt before storage.
 *
 * Relationships:
 * - One-to-Many with Job (jobs created by this user)
 * - One-to-Many with Position (saved positions created by this user)
 * - One-to-Many with Image (images captured by this user)
 *
 * Security:
 * - Password is excluded from all JSON responses via @Exclude decorator
 * - Automatic bcrypt hashing on insert/update via @BeforeInsert/@BeforeUpdate
 *
 * @entity users
 */
@Entity('users')
export class User {
  @ApiProperty({ description: 'Unique user identifier', example: 1 })
  @PrimaryGeneratedColumn()
  id: number;

  /**
   * User's email address (unique, used for login)
   */
  @ApiProperty({
    description: 'User email address (unique)',
    example: 'user@example.com',
  })
  @Column({ unique: true })
  email: string;

  /**
   * User's username (unique, used for display)
   */
  @ApiProperty({
    description: 'Username for login (unique)',
    example: 'johndoe',
  })
  @Column({ unique: true })
  username: string;

  /**
   * User's hashed password
   * IMPORTANT: This field is excluded from JSON responses via @Exclude decorator
   * Password is automatically hashed before saving via @BeforeInsert/@BeforeUpdate hooks
   */
  @ApiHideProperty()
  @Column()
  @Exclude()
  password: string;

  /**
   * User's role (admin or user)
   */
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

  /**
   * User's full name (optional)
   */
  @ApiProperty({
    description: 'User full name',
    example: 'John Doe',
    required: false,
    nullable: true,
  })
  @Column({ name: 'full_name', nullable: true })
  fullName?: string;

  /**
   * User's lab role (optional)
   */
  @ApiProperty({
    description: 'User lab role',
    example: 'Researcher',
    required: false,
    nullable: true,
  })
  @Column({ name: 'lab_role', nullable: true })
  labRole?: string;

  /**
   * User preferences stored as JSON (default: empty object)
   */
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

  // ==================== Relationships ====================

  /**
   * One-to-Many relationship with Job
   * All jobs created by this user
   */
  @OneToMany(() => Job, (job) => job.user)
  jobs: Job[];

  /**
   * One-to-Many relationship with Position
   * All saved positions created by this user
   */
  @OneToMany(() => Position, (position) => position.user)
  positions: Position[];

  /**
   * One-to-Many relationship with Image
   * All images captured by this user
   */
  @OneToMany(() => Image, (image) => image.user)
  images: Image[];

  // ==================== Methods ====================

  /**
   * Automatically hash password before insert or update
   *
   * Only hashes if password is not already hashed (doesn't start with $2b$)
   * Uses bcrypt with 10 salt rounds
   *
   * @hook BeforeInsert
   * @hook BeforeUpdate
   */
  @BeforeInsert()
  @BeforeUpdate()
  async hashPassword() {
    // Only hash if password exists and is not already hashed
    if (this.password && !this.password.startsWith('$2b$')) {
      this.password = await bcrypt.hash(this.password, 10);
    }
  }

  /**
   * Validate password against stored hash
   *
   * @param password - Plain text password to check
   * @returns true if password matches, false otherwise
   */
  async validatePassword(password: string): Promise<boolean> {
    return bcrypt.compare(password, this.password);
  }
}
