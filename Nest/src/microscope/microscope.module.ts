import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { MicroscopeController } from './microscope.controller';
import { MicroscopeService } from './microscope.service';
import { ConfigModule } from '../config/config.module';

/**
 * Microscope Module
 *
 * Handles general microscope hardware controls like:
 * - Light control (on/off, brightness)
 * - Focus control (future)
 * - Filter wheel (future)
 * - Shutter control (future)
 *
 * @module MicroscopeModule
 */
@Module({
  imports: [HttpModule, ConfigModule],
  controllers: [MicroscopeController],
  providers: [MicroscopeService],
  exports: [MicroscopeService],
})
export class MicroscopeModule {}
