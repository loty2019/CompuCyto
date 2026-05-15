import { Injectable, ConflictException, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { ILike, Repository } from 'typeorm';
import { User } from './entities/user.entity';

const localProfileEmail = (username: string): string =>
  `${username.toLowerCase().replace(/[^a-z0-9]+/g, '.')}@cytocore.local`;

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

  async findLocalProfiles(): Promise<User[]> {
    return this.usersRepository.find({
      where: { email: ILike('%@cytocore.local') },
      order: { username: 'ASC' },
    });
  }

  async create(email: string, username: string, password: string): Promise<User> {
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

  async findOrCreateLocalProfile(
    username: string,
    email?: string,
    avatarIcon?: string,
  ): Promise<User> {
    const safeUsername = username.trim() || 'Operator';
    const safeEmail = email?.trim() || localProfileEmail(safeUsername);

    let user =
      (await this.findByUsername(safeUsername)) || (await this.findByEmail(safeEmail));

    const preferences = {
      ...(user?.preferences || {}),
      ...(avatarIcon ? { avatarIcon } : {}),
    };

    if (user) {
      let changed = false;

      if (!user.fullName) {
        user.fullName = safeUsername;
        changed = true;
      }

      if (avatarIcon && user.preferences?.avatarIcon !== avatarIcon) {
        user.preferences = preferences;
        changed = true;
      }

      return changed ? this.usersRepository.save(user) : user;
    }

    user = this.usersRepository.create({
      email: safeEmail,
      username: safeUsername,
      password: 'local-profile',
      fullName: safeUsername,
      preferences,
    });

    return this.usersRepository.save(user);
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
    if (updates.preferences !== undefined) user.preferences = updates.preferences;

    return this.usersRepository.save(user);
  }
}
