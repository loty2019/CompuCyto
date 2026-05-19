import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';
import { User } from './entities/user.entity';
import { Image } from '../images/entities/image.entity';
import { Video } from '../videos/entities/video.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User, Image, Video])],
  providers: [UsersService],
  controllers: [UsersController],
  exports: [UsersService],
})
export class UsersModule {}
