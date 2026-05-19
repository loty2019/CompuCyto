import { Injectable, ConflictException, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { ILike, Repository } from 'typeorm';
import { User } from './entities/user.entity';
import { Image } from '../images/entities/image.entity';
import { Video } from '../videos/entities/video.entity';

const localProfileEmail = (username: string): string =>
  `${username.toLowerCase().replace(/[^a-z0-9]+/g, '.')}@cytocore.local`;

const localProfileCacheTtlMs = 30_000;
const archivedMediaEmail = 'archived-media@cytocore.system';
const archivedMediaUsername = 'Archived media';

@Injectable()
export class UsersService {
  private readonly localProfileCache = new Map<
    string,
    { user: User; expiresAt: number }
  >();

  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
    @InjectRepository(Image)
    private imagesRepository: Repository<Image>,
    @InjectRepository(Video)
    private videosRepository: Repository<Video>,
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

  private async findOrCreateArchivedMediaOwner(): Promise<User> {
    const existing = await this.findByEmail(archivedMediaEmail);

    if (existing) {
      return existing;
    }

    let username = archivedMediaUsername;
    let suffix = 2;

    while (await this.findByUsername(username)) {
      username = `${archivedMediaUsername} ${suffix}`;
      suffix += 1;
    }

    const user = this.usersRepository.create({
      email: archivedMediaEmail,
      username,
      password: 'local-profile',
      fullName: username,
      preferences: { hiddenProfile: true },
    });

    return this.usersRepository.save(user);
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
    const cacheKey = `${safeUsername}\0${safeEmail}\0${avatarIcon ?? ''}`;
    const cached = this.localProfileCache.get(cacheKey);

    if (cached && cached.expiresAt > Date.now()) {
      return cached.user;
    }

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

      const savedUser = changed ? await this.usersRepository.save(user) : user;
      this.localProfileCache.set(cacheKey, {
        user: savedUser,
        expiresAt: Date.now() + localProfileCacheTtlMs,
      });
      return savedUser;
    }

    user = this.usersRepository.create({
      email: safeEmail,
      username: safeUsername,
      password: 'local-profile',
      fullName: safeUsername,
      preferences,
    });

    const savedUser = await this.usersRepository.save(user);
    this.localProfileCache.set(cacheKey, {
      user: savedUser,
      expiresAt: Date.now() + localProfileCacheTtlMs,
    });
    return savedUser;
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

  async deleteLocalProfile(userId: number): Promise<{
    deletedProfileId: number;
    reassignedImages: number;
    reassignedVideos: number;
  }> {
    const user = await this.findById(userId);

    if (!user || !user.email.toLowerCase().endsWith('@cytocore.local')) {
      throw new NotFoundException('Profile not found');
    }

    const archivedOwner = await this.findOrCreateArchivedMediaOwner();

    const [imagesResult, videosResult] = await Promise.all([
      this.imagesRepository.update({ userId }, { userId: archivedOwner.id }),
      this.videosRepository.update({ userId }, { userId: archivedOwner.id }),
    ]);

    await this.usersRepository.remove(user);
    this.localProfileCache.clear();

    return {
      deletedProfileId: userId,
      reassignedImages: imagesResult.affected ?? 0,
      reassignedVideos: videosResult.affected ?? 0,
    };
  }
}
