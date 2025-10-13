import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CameraService } from './camera.service';
import { CameraController } from './camera.controller';
import { Image } from '../images/entities/image.entity';

@Module({
  imports: [
    HttpModule,
    TypeOrmModule.forFeature([Image]),
  ],
  providers: [CameraService],
  controllers: [CameraController],
  exports: [CameraService],
})
export class CameraModule {}
