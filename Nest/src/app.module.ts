import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from './config/config.module';
import { ConfigService } from './config/config.service';
import { getDatabaseConfig } from './config/database.config';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { CameraModule } from './camera/camera.module';
import { StageModule } from './stage/stage.module';
import { MicroscopeModule } from './microscope/microscope.module';
import { ImagesModule } from './images/images.module';
import { VideosModule } from './videos/videos.module';
import { HealthController } from './common/controllers/health.controller';
import { EventsGateway } from './common/websocket/events.gateway';

@Module({
  imports: [
    ConfigModule,
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (configService: ConfigService) =>
        getDatabaseConfig(configService),
    }),
    AuthModule,
    UsersModule,
    CameraModule,
    StageModule,
    MicroscopeModule,
    ImagesModule,
    VideosModule,
  ],
  controllers: [HealthController],
  providers: [EventsGateway],
})
export class AppModule {}
