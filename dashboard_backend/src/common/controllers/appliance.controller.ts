import {
  Controller,
  HttpException,
  HttpStatus,
  Logger,
  Post,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { execFile } from 'child_process';
import { firstValueFrom } from 'rxjs';
import { ConfigService } from '../../config/config.service';

type ApplianceActionResult = {
  success: boolean;
  message: string;
};

@ApiTags('Appliance')
@Controller('api/v1/appliance')
export class ApplianceController {
  private readonly logger = new Logger(ApplianceController.name);

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {}

  @Post('shutdown')
  @ApiOperation({
    summary: 'Power off the full appliance after safely shutting down the Pi',
  })
  @ApiResponse({ status: 202, description: 'Shutdown sequence started' })
  async shutdownAppliance(): Promise<ApplianceActionResult> {
    await this.shutdownPi();
    await this.waitForPiOffline();
    this.scheduleWindowsPowerAction('shutdown');

    return {
      success: true,
      message: 'Raspberry Pi is offline. Windows shutdown has been scheduled.',
    };
  }

  @Post('restart/windows')
  @ApiOperation({ summary: 'Restart the Windows appliance host' })
  @ApiResponse({ status: 202, description: 'Windows restart scheduled' })
  restartWindows(): ApplianceActionResult {
    this.scheduleWindowsPowerAction('restart');

    return {
      success: true,
      message: 'Windows restart has been scheduled.',
    };
  }

  @Post('restart/pi')
  @ApiOperation({ summary: 'Restart the Raspberry Pi controller' })
  @ApiResponse({ status: 202, description: 'Pi restart requested' })
  async restartPi(): Promise<ApplianceActionResult> {
    await this.postPiSystemAction('restart');

    return {
      success: true,
      message: 'Raspberry Pi restart requested.',
    };
  }

  private async shutdownPi(): Promise<void> {
    await this.postPiSystemAction('shutdown');
  }

  private async postPiSystemAction(action: 'shutdown' | 'restart'): Promise<void> {
    try {
      await firstValueFrom(
        this.httpService.post(
          `${this.configService.raspberryPiUrl}/system/${action}`,
          {},
          { timeout: 5000 },
        ),
      );
      this.logger.log(`Raspberry Pi /system/${action} accepted`);
    } catch (error) {
      const message = this.describeError(error);

      if (action === 'restart' && message.includes('404')) {
        throw new HttpException(
          {
            success: false,
            message:
              'The Raspberry Pi API needs to be updated before Pi restart is available.',
          },
          HttpStatus.NOT_FOUND,
        );
      }

      throw new HttpException(
        {
          success: false,
          message: `Raspberry Pi did not accept ${action}. ${message}`,
        },
        HttpStatus.SERVICE_UNAVAILABLE,
      );
    }
  }

  private async waitForPiOffline(): Promise<void> {
    const deadline = Date.now() + 90000;

    while (Date.now() < deadline) {
      await this.sleep(2500);

      try {
        await firstValueFrom(
          this.httpService.get(`${this.configService.raspberryPiUrl}/health`, {
            timeout: 2500,
          }),
        );
      } catch {
        this.logger.log('Raspberry Pi health check failed; treating Pi as offline');
        return;
      }
    }

    throw new HttpException(
      {
        success: false,
        message:
          'Raspberry Pi still responds to health checks. Windows shutdown was not started.',
      },
      HttpStatus.GATEWAY_TIMEOUT,
    );
  }

  private scheduleWindowsPowerAction(action: 'shutdown' | 'restart'): void {
    const args = action === 'shutdown' ? ['/s', '/t', '5'] : ['/r', '/t', '5'];

    execFile('shutdown.exe', args, (error) => {
      if (error) {
        this.logger.error(`Failed to schedule Windows ${action}`, error.stack);
      }
    });
  }

  private describeError(error: unknown): string {
    if (error instanceof Error) {
      return error.message;
    }

    return String(error);
  }

  private sleep(milliseconds: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
  }
}
