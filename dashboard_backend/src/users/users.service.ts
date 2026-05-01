import {
  Injectable,
  ConflictException,
  NotFoundException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
  ) {}

  async findById(id: number): Promise<User | null> {
    return this.usersRepository.findOne({
      where: { id },
    });
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.usersRepository.findOne({
      where: { email },
    });
  }

  async findByUsername(username: string): Promise<User | null> {
    return this.usersRepository.findOne({
      where: { username },
    });
  }

  async create(
    email: string,
    username: string,
    password: string,
  ): Promise<User> {
    // Check if user already exists
    const existingEmail = await this.findByEmail(email);
    if (existingEmail) {
      throw new ConflictException('Email already exists');
    }

    const existingUsername = await this.findByUsername(username);
    if (existingUsername) {
      throw new ConflictException('Username already exists');
    }

    // Create and save user
    const user = this.usersRepository.create({
      email,
      username,
      password,
      preferences: {}, // Initialize with empty preferences
    });

    return await this.usersRepository.save(user);
  }

  async updateProfile(
    userId: number,
    updates: {
      fullName?: string;
      labRole?: string;
      preferences?: Record<string, any>;
    },
  ): Promise<User> {
    const user = await this.findById(userId);

    if (!user) {
      throw new NotFoundException('User not found');
    }

    // Update user fields
    if (updates.fullName !== undefined) user.fullName = updates.fullName;
    if (updates.labRole !== undefined) user.labRole = updates.labRole;
    if (updates.preferences !== undefined)
      user.preferences = updates.preferences;

    return this.usersRepository.save(user);
  }
}
