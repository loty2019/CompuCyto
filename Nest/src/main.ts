import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { ConfigService } from './config/config.service';

/**
 * Bootstrap the NestJS application
 *
 * Application Entry Point
 *
 * This function:
 * 1. Creates the NestJS application
 * 2. Configures Swagger/OpenAPI documentation
 * 3. Configures CORS for frontend communication
 * 4. Enables global validation pipes for DTO validation
 * 5. Starts the HTTP server on configured port
 * 6. Enables WebSocket support for real-time communication
 *
 * @async
 */
async function bootstrap() {
  // Create NestJS application instance with CORS enabled
  const app = await NestFactory.create(AppModule, { cors: true });

  // Get config service for environment variables
  const configService = app.get(ConfigService);

  // ==================== Swagger/OpenAPI Configuration ====================
  // Setup API documentation at /api-docs
  const config = new DocumentBuilder()
    .setTitle('CompuCyto Microscope Control API')
    .setDescription(
      'REST API for controlling microscope hardware, managing images, and running automated jobs.\n\n' +
        '**Getting Started:**\n' +
        '1. Register a user via POST /api/v1/auth/register\n' +
        '2. Login to get JWT token via POST /api/v1/auth/login\n' +
        '3. Use the token in Authorization header for protected endpoints',
    )
    .setVersion('1.0.0')
    .addTag('Auth', 'Authentication and user management')
    .addTag('Camera', 'Camera control and image capture')
    .addTag('Stage', 'Microscope stage movement control')
    .addTag(
      'Microscope',
      'General microscope hardware control (light, focus, filters)',
    )
    .addTag('Health', 'System health monitoring')
    .addTag('Images', 'Image management (Phase 2)')
    .addTag('Jobs', 'Automated job management (Phase 2)')
    .addTag('Positions', 'Saved position management (Phase 2)')
    .addBearerAuth(
      {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        name: 'JWT',
        description: 'Enter JWT token from /auth/login',
        in: 'header',
      },
      'JWT-auth', // This name is referenced in @ApiBearerAuth() decorators
    )
    .addServer('http://localhost:3000', 'Development Server')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api-docs', app, document, {
    customSiteTitle: 'CompuCyto API Docs',
    customfavIcon: 'https://nestjs.com/img/logo-small.svg',
    customCss: '.swagger-ui .topbar { display: none }',
    swaggerOptions: {
      persistAuthorization: true, // Keep auth token between page refreshes
      tagsSorter: 'alpha',
      operationsSorter: 'alpha',
    },
  });

  // ==================== CORS Configuration ====================
  // Enable Cross-Origin Resource Sharing for frontend communication
  // Allows requests from Vue frontend (localhost:5173) and other configured origins
  app.enableCors({
    origin: configService.allowedOrigins, // From ALLOWED_ORIGINS env var
    credentials: true, // Allow cookies/auth headers
  });

  // ==================== Global Validation ====================
  // Enable automatic DTO validation for all endpoints
  // Uses class-validator decorators on DTOs (e.g., @IsEmail, @IsString)
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // Strip properties not in DTO
      forbidNonWhitelisted: true, // Throw error if extra properties provided
      transform: true, // Auto-transform payloads to DTO instances
    }),
  );

  // ==================== Start Server ====================
  const port = configService.port; // From PORT env var (default: 3000)
  const frontendPort = configService.frontendPort; // From FRONTEND_PORT env var (default: 5173)
  await app.listen(port);

  // Log startup information
  // front end is running at port 5173
  console.log(
    `🚀 Application is running on (frontend): http://localhost:${frontendPort}`,
  );
  console.log(
    `📚 API Documentation (Swagger): http://localhost:${port}/api-docs`,
  );
  console.log(`📋 Health check: http://localhost:${port}/api/v1/health`);
  console.log(`🔐 API Base: http://localhost:${port}/api/v1`);
}

// Start the application
void bootstrap();
