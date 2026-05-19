import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CameraService } from './camera.service';
import { CameraController } from './camera.controller';
import { Image } from '../images/entities/image.entity';
import { Video } from '../videos/entities/video.entity';
import { UsersModule } from '../users/users.module';
import { StageModule } from '../stage/stage.module';

@Module({
  imports: [
    HttpModule,
    TypeOrmModule.forFeature([Image, Video]),
    UsersModule,
    StageModule,
  ],
  providers: [CameraService],
  controllers: [CameraController],
  exports: [CameraService],
})
export class CameraModule {}
