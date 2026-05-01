import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { StageService } from './stage.service';
import { StageController } from './stage.controller';
import { PositionValidator } from './validators/position-validator';

@Module({
  imports: [HttpModule],
  providers: [StageService, PositionValidator],
  controllers: [StageController],
  exports: [StageService],
})
export class StageModule {}
